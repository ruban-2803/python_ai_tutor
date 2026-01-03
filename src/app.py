import streamlit as st
from groq import Groq
import graphviz
from streamlit_lottie import st_lottie
import requests

# ==========================================
# 1. CONFIG & ASSETS
# ==========================================
st.set_page_config(
    page_title="Pylo | SanRu Labs",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_ai = load_lottieurl("https://lottie.host/02a52df2-2591-45da-9694-87890f5d7293/63126e7b-c36f-4091-a67b-240a9243764b.json")

# ==========================================
# 2. DARK MODE CSS & SECURITY FIXES
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@300;400;600&display=swap');
    
    /* GLOBAL DARK THEME */
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        color: #E0E0E0; 
    }
    
    /* BACKGROUND */
    .stApp {
        background-color: #0E1117;
        background-image: radial-gradient(circle at 50% 50%, #161B22 0%, #0E1117 100%);
    }

    /* --- NUCLEAR OPTION: HIDE UI --- */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stManageAppButton"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    .stDeployButton { display: none !important; }

    /* --- LOGIN CARD --- */
    .login-container {
        background: rgba(20, 20, 30, 0.7);
        backdrop-filter: blur(12px);
        padding: 50px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* TYPOGRAPHY */
    .product-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(90deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        text-shadow: 0 0 20px rgba(255, 75, 75, 0.3);
    }
    
    .tagline { font-size: 14px; color: #AAA; margin-bottom: 30px; letter-spacing: 1px; text-transform: uppercase; }

    /* INPUTS & BUTTONS */
    .stTextInput input {
        background-color: #1F2329 !important; color: white !important;
        border: 1px solid #333; border-radius: 10px; padding: 12px;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%);
        color: white; padding: 14px 0px; border-radius: 10px; border: none; width: 100%;
        text-transform: uppercase; letter-spacing: 1.5px; font-weight: bold;
    }
    div.stButton > button:hover {
        transform: translateY(-2px); box-shadow: 0 10px 25px rgba(255, 75, 75, 0.4);
    }
    
    /* LOCK SCREEN & EDITOR */
    .lock-card {
        background-color: #1a1a2e; border: 1px solid #FF4B4B; padding: 40px;
        border-radius: 15px; text-align: center; margin-top: 50px;
    }
    .stTextArea textarea { 
        font-family: 'Courier New', monospace; 
        background-color: #111 !important; 
        color: #00FF99 !important; 
        border: 1px solid #333;
    }
    
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. AUTHENTICATION LOGIC
# ==========================================
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = "demo"
    
    if st.session_state.authenticated:
        st.markdown("""<style>[data-testid="stSidebar"] { display: block; }</style>""", unsafe_allow_html=True)
        return True
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.write(""); st.write(""); st.write("")
        if lottie_ai: st_lottie(lottie_ai, height=500, key="ai_anim")
    with col2:
        st.write(""); st.write("")
        with st.container():
            st.markdown('<div class="product-title">Pylo</div>', unsafe_allow_html=True)
            st.markdown('<p class="tagline">Intelligent Coding Environment.<br>Powered by <b>SanRu Labs</b>.</p>', unsafe_allow_html=True)
            
            email = st.text_input("ACCESS ID", placeholder="student@sanru.com")
            password = st.text_input("SECURE KEY", type="password", placeholder="••••••••")
            
            st.write("")
            if st.button("INITIALIZE SYSTEM"):
                users_db = st.secrets.get("users", {})
                user_found = False
                for _, details in users_db.items():
                    if details["email"] == email and details["password"] == password:
                        st.session_state.authenticated = True
                        st.session_state.user_name = details["name"]
                        if email == "admin@pylo.com": st.session_state.user_role = "admin"
                        else: st.session_state.user_role = "demo"
                        user_found = True
                        st.rerun()
                if not user_found: st.error("❌ ACCESS DENIED")
    return False

if not check_login(): st.stop()

# ==========================================
# 4. MAIN DASHBOARD
# ==========================================
st.markdown("""<style>[data-testid="stSidebar"] { display: block; }</style>""", unsafe_allow_html=True)

try: client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except: st.error("⚠️ API Key Error"); st.stop()

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
    st.markdown('<h2 style="color:white; font-family:Orbitron;">Pylo 🧬</h2>', unsafe_allow_html=True)
    st.caption("by SanRu Labs")
    if st.session_state.user_role == "admin": st.success("⚡ ADMIN MODE")
    else: st.warning("🧪 DEMO MODE")
    st.divider()
    st.write(f"User: **{st.session_state.user_name}**")
    
    st.subheader("📍 Roadmap")
    current_level = st.radio("Chapter:", list(SYLLABUS.keys()))
    
    is_locked = False
    if st.session_state.user_role == "demo" and "Level 1" not in current_level and "Level 2" not in current_level:
        is_locked = True
    
    if is_locked: st.error("🔒 LOCKED")
    else: st.info(f"{SYLLABUS[current_level]}")
    
    st.divider()
    if st.button("Log Out"): st.session_state.authenticated = False; st.rerun()

def show_lock_screen(feature_name):
    st.markdown(f"""<div class="lock-card"><h1 style='color:#FF4B4B; font-family:Orbitron;'>🔒 RESTRICTED</h1><h3 style='color:white;'>{feature_name} is a PRO feature.</h3><p style='color:#AAA;'>Upgrade your SanRu Labs license.</p></div>""", unsafe_allow_html=True)

# --- NEW 4-TAB LAYOUT ---
st.title("Pylo 🧬")
tab_vis, tab_learn, tab_arena, tab_codegen = st.tabs(["👁️ Visualizer", "🧠 Learn", "⚔️ Arena", "⚡ Generator"])

# TAB 1: VISUALIZER (CORE FEATURE)
with tab_vis:
    st.header("👁️ Logic Visualizer")
    col_v1, col_v2 = st.columns([1, 1.5])
    
    with col_v1:
        st.caption("Paste your Python code below:")
        vis_code = st.text_area("Code Input:", height=200, placeholder="x = 10\nif x > 5:\n    print('Hello')")
        if st.button("✨ Visualize Flow", type="primary"):
            if vis_code:
                st.session_state.vis_trigger = vis_code
    
    with col_v2:
        with st.container(height=500, border=True):
            if "vis_trigger" in st.session_state:
                with st.spinner("Drawing Flowchart..."):
                    graph_req = f"Convert this Python code to Graphviz DOT code. Return ONLY code inside ```dot blocks: {st.session_state.vis_trigger}"
                    try:
                        g_resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content": graph_req}])
                        dot_code = g_resp.choices[0].message.content
                        if "```dot" in dot_code: dot_code = dot_code.split("```dot")[1].split("```")[0]
                        elif "```" in dot_code: dot_code = dot_code.split("```")[1].split("```")[0]
                        st.graphviz_chart(dot_code)
                    except:
                        st.error("Could not visualize code syntax.")
            else:
                st.info("👈 Enter code on the left to generate a diagram.")

# TAB 2: LEARN (CHATBOT)
with tab_learn:
    if is_locked:
        show_lock_screen(f"Tuition for {current_level}")
    else:
        st.header("🧠 AI Tutor")
        system_prompt = f"You are Pylo. Level: {current_level}. Topics: {SYLLABUS[current_level]}. Keep it short."
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Hello! I am ready to teach. Ask me anything about this topic."}]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        if prompt := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages, stream=True)
            with st.chat_message("assistant"):
                response = st.write_stream(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
            st.session_state.messages.append({"role": "assistant", "content": response})

# TAB 3: ARENA (CHALLENGE)
with tab_arena:
    st.header(f"⚔️ {current_level} Challenge")
    if "arena_attempts" not in st.session_state: st.session_state.arena_attempts = 0
    col_q, col_code = st.columns([1, 1.5])
    
    if "current_challenge" not in st.session_state: st.session_state.current_challenge = "Awaiting Generation..."
        
    with col_q:
        if st.button("🎲 Generate Problem", type="primary"):
            if st.session_state.user_role == "demo" and st.session_state.arena_attempts >= 2:
                st.error("🚫 TRIAL LIMIT REACHED (2/2)")
            else:
                st.session_state.arena_attempts += 1
                with st.spinner("Computing..."):
                    q_prompt = f"Create a short Python coding challenge for {current_level}."
                    q_resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": q_prompt}])
                    st.session_state.current_challenge = q_resp.choices[0].message.content
        if st.session_state.user_role == "demo": st.caption(f"Trial Usage: {st.session_state.arena_attempts}/2")
        st.markdown(st.session_state.current_challenge)

    with col_code:
        st.subheader("Solution Terminal:")
        user_code = st.text_area("Input Code...", height=300, key="code_editor_arena")
        if st.button("🚀 Execute & Grade"):
            with st.spinner("Analyzing..."):
                grade_prompt = f"Task: {st.session_state.current_challenge}. User Code: {user_code}. Grade it."
                grade_resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": grade_prompt}])
                st.success("Analysis Complete"); st.markdown(grade_resp.choices[0].message.content)

# TAB 4: GENERATOR (CODEGEN)
with tab_codegen:
    if st.session_state.user_role == "demo": show_lock_screen("Instant Code Generator")
    else:
        st.header("⚡ Instant Generator")
        col_gen_in, col_gen_out = st.columns([1, 1.5])
        with col_gen_in:
            gen_prompt = st.text_area("System Requirements:", height=300)
            gen_click = st.button("✨ Compile Script", type="primary", use_container_width=True)
        with col_gen_out:
            with st.container(height=600, border=True):
                if gen_click and gen_prompt:
                    with st.spinner("Architecting..."):
                        sys_gen = "Write complete Python code. Return ONLY code inside ```python blocks."
                        try:
                            gen_resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": sys_gen}, {"role": "user", "content": gen_prompt}])
                            full_res = gen_resp.choices[0].message.content
                            clean_code = full_res.split("```python")[1].split("```")[0] if "```python" in full_res else full_res
                            st.session_state.generated_code = full_res; st.session_state.clean_code = clean_code
                        except: st.error("Generation Failed")
                if "generated_code" in st.session_state:
                    st.markdown(st.session_state.generated_code)
                    st.download_button(label="📥 Download Module", data=st.session_state.clean_code, file_name="script.py")
