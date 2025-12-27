import streamlit as st
from groq import Groq
import graphviz

# 1. APP CONFIGURATION
st.set_page_config(
    page_title="PyCoach AI",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CUSTOM STYLES
st.markdown("""
<style>
    .stChatMessage { border-radius: 10px; }
    h1 { color: #306998; }
    .stTextArea textarea { font-family: 'Courier New', monospace; background-color: #f0f2f6; }
</style>
""", unsafe_allow_html=True)

# 3. SETUP API & LOGIN
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    col1, col2 = st.columns([1,2])
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg", width=100)
    with col2:
        st.title("🔐 PyCoach Login")
        st.caption("Sign in to access the Challenge Arena.")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In", type="primary"):
        users_db = st.secrets.get("users", {})
        for _, details in users_db.items():
            if details["email"] == email and details["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user_name = details["name"]
                st.rerun()
        st.error("❌ Invalid Credentials")
    return False

if not check_login():
    st.stop()

# --- APP START ---

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing API Key in Secrets!")
    st.stop()

# SYLLABUS DEFINITION
SYLLABUS = {
    "Level 1: The Basics": "Variables, Strings, Ints, Print()",
    "Level 2: Logic": "Booleans, If/Else, Comparisons",
    "Level 3: Looping": "For Loops, While Loops, Range()",
    "Level 4: Lists & Dicts": "Lists, Indexing, Dictionaries",
    "Level 5: Functions": "Def, Return, Arguments"
}

# SIDEBAR
with st.sidebar:
    st.title(f"👨‍💻 {st.session_state.user_name}")
    st.subheader("📍 Roadmap")
    current_level = st.radio("Chapter:", list(SYLLABUS.keys()))
    st.info(f"**Focus:** {SYLLABUS[current_level]}")
    
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()

# --- MAIN INTERFACE TABS ---
st.title("PyCoach AI 🐍")
tab_tutor, tab_arena = st.tabs(["🤖 AI Tutor", "⚔️ Challenge Arena"])

# === TAB 1: THE TUTOR (Original Chat + Visualizer) ===
with tab_tutor:
    col_chat, col_vis = st.columns([1.5, 1])
    
    system_prompt = f"You are a Python Tutor. Current Chapter: {current_level}. Keep answers short."
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm ready to teach."}]

    with col_chat:
        # Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat Input
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
            
            # Logic for Visualizer Trigger
            if "visualize" in prompt.lower() or "flowchart" in prompt.lower():
                st.session_state.trigger_visualizer = True
            else:
                st.session_state.trigger_visualizer = False

    with col_vis:
        st.caption("🕸️ Logic Visualizer")
        if st.session_state.get("trigger_visualizer"):
            with st.spinner("Drawing logic..."):
                last_msg = st.session_state.messages[-1]["content"]
                graph_req = f"Convert this Python logic to Graphviz DOT code. Return ONLY code inside ```dot``` blocks: {last_msg}"
                
                try:
                    g_resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content": graph_req}])
                    dot_code = g_resp.choices[0].message.content
                    # Cleanup
                    if "```dot" in dot_code: dot_code = dot_code.split("```dot")[1].split("```")[0]
                    elif "```" in dot_code: dot_code = dot_code.split("```")[1].split("```")[0]
                    st.graphviz_chart(dot_code)
                except:
                    st.warning("Could not visualize.")

# === TAB 2: THE CHALLENGE ARENA (New!) ===
with tab_arena:
    st.header(f"⚔️ {current_level} Challenge")
    
    col_q, col_code = st.columns([1, 1.5])
    
    # Session State for Challenge
    if "current_challenge" not in st.session_state:
        st.session_state.current_challenge = "Click 'Generate' to start!"
    
    with col_q:
        st.info("👋 Use this space to test your skills.")
        if st.button("🎲 Generate New Problem", type="primary"):
            with st.spinner("Creating a unique problem..."):
                # Ask AI for a problem based on the level
                prompt_q = f"Create a beginner coding challenge for {current_level}. Requirements: 1. Clear Instructions. 2. Example Input/Output. Keep it short."
                q_resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_q}]
                )
                st.session_state.current_challenge = q_resp.choices[0].message.content
        
        st.markdown("### Problem:")
        st.markdown(st.session_state.current_challenge)

    with col_code:
        st.subheader("Your Solution:")
        user_code = st.text_area("Write Python code here...", height=300, key="code_editor")
        
        if st.button("🚀 Submit & Grade"):
            if len(user_code) < 5:
                st.warning("Write some code first!")
            else:
                with st.spinner("Grading..."):
                    # Grading Prompt
                    grade_prompt = f"""
                    You are a Senior Engineer. 
                    Problem: {st.session_state.current_challenge}
                    User Code: {user_code}
                    
                    Task: 
                    1. Give a Score (0-100).
                    2. Did it run? (Yes/No)
                    3. Feedback: How to improve efficiency or style.
                    """
                    
                    grade_resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": grade_prompt}]
                    )
                    
                    st.success("Grading Complete!")
                    st.markdown(grade_resp.choices[0].message.content)
