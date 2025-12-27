import streamlit as st
from groq import Groq
import graphviz

# ==========================================
# 1. APP CONFIGURATION & PRO UI STYLING
# ==========================================
st.set_page_config(
    page_title="Pylo | SanRu Labs",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LOAD GOOGLE FONTS & CUSTOM CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@300;400;600&display=swap');

    /* GLOBAL FONT CHANGE */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* --- 1. BRANDING STYLES (PYLO + SANRU) --- */
    .product-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 38px;
        font-weight: 800;
        color: #222;
        margin-bottom: 0px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .powered-by {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        color: #888;
        margin-top: -8px;
        margin-bottom: 25px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 500;
    }
    
    .sanru-gradient {
        background: linear-gradient(90deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-family: 'Orbitron', sans-serif;
    }

    /* --- 2. LOGIN CARD STYLING --- */
    /* Target the container to look like a floating card */
    div[data-testid="stVerticalBlock"] > div:has(div.product-title) {
        background-color: white;
        padding: 50px;
        border-radius: 24px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        text-align: center;
    }

    /* --- 3. INPUT FIELDS & BUTTONS --- */
    .stTextInput label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: #555;
        letter-spacing: 1px;
    }
    .stTextInput input {
        border-radius: 10px;
        border: 1px solid #eee;
        padding: 12px;
        font-size: 14px;
    }
    .stTextInput input:focus {
        border-color: #FF4B4B;
        box-shadow: 0 0 8px rgba(255, 75, 75, 0.1);
    }
    div.stButton > button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%);
        color: white;
        border: none;
        padding: 14px 24px;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 14px;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 75, 75, 0.3);
        color: white;
    }

    /* --- 4. GENERAL UI FIXES --- */
    .stChatMessage { border-radius: 15px; border: 1px solid #eee; }
    
    /* Code Editor Black Text Fix */
    .stTextArea textarea { 
        font-family: 'Courier New', monospace; 
        background-color: #f8f9fa; 
        color: #000000 !important; 
        border: 1px solid #ddd;
    }
    
    /* Download Button Full Width */
    div[data-testid="stDownloadButton"] button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIN SYSTEM (Branding: PYLO)
# ==========================================
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    # 3-Column Squeeze for Centered Card
    col1, col2, col3 = st.columns([1, 0.7, 1]) 
    
    with col2:
        # BRANDING
        st.markdown('<div class="product-title">Pylo</div>', unsafe_allow_html=True)
        st.markdown('<div class="powered-by">Powered by <span class="sanru-gradient">SanRu Labs</span></div>', unsafe_allow_html=True)
        
        st.divider()
        st.caption("Sign in to your intelligent workspace.")
        
        email = st.text_input("Email", placeholder="student@sanru.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        st.write("")
        if st.button("Enter Dashboard", type="primary", use_container_width=True):
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
                st.error("❌ Access Denied")
            
    return False

if not check_login():
    st.stop()

# ==========================================
# 3. MAIN APP LOGIC
# ==========================================

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ System Error: Missing API Key.")
    st.stop()

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
    st.markdown('<div class="product-title" style="font-size:26px;">Pylo</div>', unsafe_allow_html=True)
    st.markdown('<div class="powered-by">by <span class="sanru-gradient">SanRu Labs</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg", width=50)
    st.write(f"User: **{st.session_state.user_name}**")
    
    st.subheader("📍 Roadmap")
    current_level = st.radio("Chapter:", list(SYLLABUS.keys()))
    st.info(f"{SYLLABUS[current_level]}")
    
    st.markdown("---")
    if st.button("Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# --- TABS ---
st.title("Pylo 🧬")
tab_tutor, tab_arena, tab_codegen = st.tabs(["🤖 Tutor & Visuals", "⚔️ Challenge Arena", "⚡ Code Generator"])

# TAB 1: TUTOR
with tab_tutor:
    col_chat, col_vis = st.columns([1.5, 1])
    system_prompt = f"You are Pylo, a friendly Python Tutor. Level: {current_level}. Topics: {SYLLABUS[current_level]}. Keep it short."
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi, I'm Pylo! Ready to learn? Ask me to 'Visualize' code."}]

    with col_chat:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                stream=True
            )
            with st.chat_message("assistant"):
                response = st.write_stream(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            if "visualize" in prompt.lower() or "draw" in prompt.lower():
                st.session_state.trigger_visualizer = True
            else:
                st.session_state.trigger_visualizer = False

    with col_vis:
        st.caption("🕸️ Logic Visualizer")
        if st.session_state.get("trigger_visualizer"):
            with st.spinner("Generating Flowchart..."):
                last_msg = st.session_state.messages[-1]["content"]
                graph_req = f"Convert to Graphviz DOT code. Return ONLY code in ```dot blocks: {last_msg}"
                try:
                    g_resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content": graph_req}])
                    dot_code = g_resp.choices[0].message.content
                    if "```dot" in dot_code: dot_code = dot_code.split("```dot")[1].split("```")[0]
                    elif "```" in dot_code: dot_code = dot_code.split("```")[1].split("```")[0]
                    st.graphviz_chart(dot_code)
                except:
                    st.warning("Could not visualize.")

# TAB 2: ARENA
with tab_arena:
    st.header(f"⚔️ {current_level} Challenge")
    col_q, col_code = st.columns([1, 1.5])
    
    if "current_challenge" not in st.session_state:
        st.session_state.current_challenge = "Click 'Generate' to start!"
        
    with col_q:
        st.info("👋 Test your skills.")
        if st.button("🎲 Generate New Problem", type="primary"):
            with st.spinner("Creating problem..."):
                q_prompt = f"Create a short coding challenge for {current_level}."
                q_resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": q_prompt}])
                st.session_state.current_challenge = q_resp.choices[0].message.content
        st.markdown(st.session_state.current_challenge)

    with col_code:
        st.subheader("Your Solution:")
        user_code = st.text_area("Write Python code here...", height=300, key="code_editor")
        if st.button("🚀 Submit & Grade"):
            with st.spinner("Grading..."):
                grade_prompt = f"Task: {st.session_state.current_challenge}. User Code: {user_code}. Grade it."
                grade_resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": grade_prompt}])
                st.success("Grading Complete!")
                st.markdown(grade_resp.choices[0].message.content)

# TAB 3: CODE GENERATOR (STICKY SCROLL)
with tab_codegen:
    st.header("⚡ Instant Code Generator")
    
    col_gen_in, col_gen_out = st.columns([1, 1.5])
    
    # Left Column: Sticky Input
    with col_gen_in:
        st.caption("Describe your tool:")
        gen_prompt = st.text_area("Requirements:", height=300, placeholder="Ex: Create a snake game using pygame...")
        
        generate_clicked = st.button("✨ Generate Script", type="primary", use_container_width=True)
    
    # Right Column: Scrollable Output
    with col_gen_out:
        with st.container(height=600, border=True):
            st.subheader("🐍 Generated Script")
            
            if generate_clicked and gen_prompt:
                with st.spinner("Coding..."):
                    sys_gen = "You are a Python Expert. Write complete code. Return ONLY code inside ```python blocks."
                    try:
                        gen_resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": sys_gen}, {"role": "user", "content": gen_prompt}])
                        full_res = gen_resp.choices[0].message.content
                        clean_code = full_res.split("```python")[1].split("```")[0] if "```python" in full_res else full_res
                        
                        st.session_state.generated_code = full_res
                        st.session_state.clean_code = clean_code
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            if "generated_code" in st.session_state:
                st.markdown(st.session_state.generated_code)
                st.download_button(label="📥 Download .py File", data=st.session_state.clean_code, file_name="generated_script.py", mime="text/x-python", type="primary")
            else:
                st.info("👈 Enter requirements on the left. The code will appear here.")
