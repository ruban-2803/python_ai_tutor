import streamlit as st
from groq import Groq
import graphviz

# ==========================================
# 1. APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="PyCoach AI",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a Pro Look
st.markdown("""
<style>
    /* Chat bubbles */
    .stChatMessage { border-radius: 10px; }
    
    /* Heading Colors */
    h1 { color: #306998; } /* Python Blue */
    h2, h3 { color: #FFD43B; } /* Python Yellow */
    
    /* FIX: Force black text in code editors so it is visible */
    .stTextArea textarea { 
        font-family: 'Courier New', monospace; 
        background-color: #f0f2f6; 
        color: #000000 !important; 
        border: 1px solid #ccc;
    }
    
    /* Download Button Style */
    div[data-testid="stDownloadButton"] button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTICATION SYSTEM
# ==========================================
def check_login():
    """Simple Gatekeeper System using Secrets"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    # Login UI
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg", width=120)
    with col2:
        st.title("🔐 PyCoach Login")
        st.caption("Sign in to access your AI Tutor & Tools.")
    
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In", type="primary"):
        # Check against secrets.toml
        users_db = st.secrets.get("users", {})
        
        user_found = False
        for _, details in users_db.items():
            if details["email"] == email and details["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user_name = details["name"]
                st.session_state.user_email = email
                user_found = True
                st.rerun()
        
        if not user_found:
            st.error("❌ Invalid Email or Password")
            
    return False

# Stop the app here if not logged in
if not check_login():
    st.stop()

# ==========================================
# 3. MAIN APP LOGIC
# ==========================================

# Setup Groq Client
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ API Key missing! Please check your secrets.toml")
    st.stop()

# Define the Learning Path
SYLLABUS = {
    "Level 1: The Basics": "Variables, Strings, Integers, Float, Print(), Input()",
    "Level 2: Logic & Decisions": "Booleans, If/Else, Elif, Comparison Operators",
    "Level 3: Looping": "For Loops, While Loops, Range(), Break/Continue",
    "Level 4: Data Structures": "Lists, Dictionaries, Tuples, Sets, Slicing",
    "Level 5: Functions": "Defining Functions, Arguments, Return, Scope",
    "Level 6: Advanced (Pro)": "Classes, OOP, APIs, Libraries, Error Handling"
}

# --- SIDEBAR ---
with st.sidebar:
    st.title(f"👨‍💻 {st.session_state.user_name}")
    st.caption(f"ID: {st.session_state.user_email}")
    st.divider()
    
    st.subheader("📍 Learning Roadmap")
    current_level = st.radio("Current Chapter:", list(SYLLABUS.keys()))
    
    st.info(f"**Focus Topics:**\n{SYLLABUS[current_level]}")
    
    st.divider()
    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.rerun()

# --- MAIN TABS ---
st.title("PyCoach AI 🐍")
tab_tutor, tab_arena, tab_codegen = st.tabs(["🤖 AI Tutor", "⚔️ Challenge Arena", "⚡ Code Generator"])

# ==========================================
# TAB 1: AI TUTOR + VISUALIZER
# ==========================================
with tab_tutor:
    col_chat, col_vis = st.columns([1.5, 1])
    
    # Context-aware System Prompt
    system_prompt = f"""
    You are PyCoach, a friendly but strict Python Tutor.
    CURRENT LEVEL: {current_level}
    TOPICS: {SYLLABUS[current_level]}
    
    Rules:
    1. Only teach concepts relevant to the current level.
    2. If the user asks about advanced topics, politely tell them to change the level.
    3. Keep answers concise.
    """
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Ready to learn! Ask me a question or ask me to 'Visualize' code."}]

    with col_chat:
        # Render Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Input Handling
        if prompt := st.chat_input("Ex: What is a variable? OR Visualize this loop..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # AI Response
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                stream=True
            )
            with st.chat_message("assistant"):
                response = st.write_stream(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Trigger Visualizer Logic
            if "visualize" in prompt.lower() or "draw" in prompt.lower() or "flowchart" in prompt.lower():
                st.session_state.trigger_visualizer = True
            else:
                st.session_state.trigger_visualizer = False

    with col_vis:
        st.caption("🕸️ Logic Visualizer")
        if st.session_state.get("trigger_visualizer"):
            with st.spinner("Generating Flowchart..."):
                last_msg = st.session_state.messages[-1]["content"]
                graph_req = f"Convert this Python logic to Graphviz DOT code. Return ONLY code inside ```dot``` blocks. No text.: {last_msg}"
                
                try:
                    # Use smaller model for fast graph gen
                    g_resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content": graph_req}])
                    dot_code = g_resp.choices[0].message.content
                    
                    # Clean markdown wrapper
                    if "```dot" in dot_code: dot_code = dot_code.split("```dot")[1].split("```")[0]
                    elif "```" in dot_code: dot_code = dot_code.split("```")[1].split("```")[0]
                    
                    st.graphviz_chart(dot_code)
                except:
                    st.warning("Could not visualize this logic.")
        else:
            st.info("💡 Tip: Type 'Visualize this if statement' to see a diagram here.")

# ==========================================
# TAB 2: CHALLENGE ARENA
# ==========================================
with tab_arena:
    st.header(f"⚔️ {current_level} Challenge")
    col_q, col_code = st.columns([1, 1.5])
    
    if "current_challenge" not in st.session_state:
        st.session_state.current_challenge = "Click 'Generate' to start!"
        
    with col_q:
        st.info("👋 Test your skills.")
        if st.button("🎲 Generate New Problem", type="primary"):
            with st.spinner("Creating problem..."):
                q_prompt = f"Create a short coding challenge for {current_level}. Include input/output examples."
                q_resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": q_prompt}]
                )
                st.session_state.current_challenge = q_resp.choices[0].message.content
        
        st.markdown("### Task:")
        st.markdown(st.session_state.current_challenge)

    with col_code:
        st.subheader("Your Solution:")
        user_code = st.text_area("Write Python code here...", height=300, key="code_editor")
        
        if st.button("🚀 Submit & Grade"):
            if len(user_code) < 5:
                st.warning("Write some code first!")
            else:
                with st.spinner("Grading..."):
                    grade_prompt = f"""
                    Role: Senior Python Interviewer.
                    Task: {st.session_state.current_challenge}
                    Student Code: {user_code}
                    
                    Output:
                    1. Score (0-100)
                    2. Does it run?
                    3. Efficiency Feedback
                    """
                    grade_resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": grade_prompt}]
                    )
                    st.success("Grading Complete!")
                    st.markdown(grade_resp.choices[0].message.content)

# ==========================================
# TAB 3: CODE GENERATOR (UTILITY)
# ==========================================
with tab_codegen:
    st.header("⚡ Instant Code Generator")
    st.caption("Describe a tool, script, or game, and I will write the file for you.")
    
    col_gen_in, col_gen_out = st.columns([1, 1.5])
    
    with col_gen_in:
        gen_prompt = st.text_area("Requirements:", height=150, placeholder="Ex: Create a snake game using pygame...")
        if st.button("✨ Generate Script", type="primary", use_container_width=True):
            if not gen_prompt:
                st.warning("Please enter requirements.")
            else:
                with st.spinner("Coding..."):
                    sys_gen = "You are a Python Expert. Write complete, working code based on the user prompt. Return ONLY the code inside ```python blocks."
                    
                    try:
                        gen_resp = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": sys_gen},
                                {"role": "user", "content": gen_prompt}
                            ]
                        )
                        full_res = gen_resp.choices[0].message.content
                        
                        # Extract code
                        clean_code = full_res
                        if "```python" in full_res:
                            clean_code = full_res.split("```python")[1].split("```")[0]
                        elif "```" in full_res:
                            clean_code = full_res.split("```")[1].split("```")[0]
                            
                        st.session_state.generated_code = full_res
                        st.session_state.clean_code = clean_code
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
    with col_gen_out:
        if "generated_code" in st.session_state:
            st.subheader("🐍 Result:")
            st.markdown(st.session_state.generated_code)
            st.download_button(
                label="📥 Download .py File",
                data=st.session_state.clean_code,
                file_name="generated_script.py",
                mime="text/x-python",
                type="primary"
            )
        else:
            st.info("👈 Code will appear here.")
