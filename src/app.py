import streamlit as st
from groq import Groq
import requests
from supabase import create_client, Client
from streamlit_lottie import st_lottie
import graphviz

# ==========================================
# 1. CONFIG & INIT
# ==========================================
st.set_page_config(
    page_title="Pylo | SanRu Labs",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded" # 1. FORCE OPEN
)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except: return None

supabase = init_supabase()

# Initialize Groq
try: client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except: st.error("⚠️ API Key Error"); st.stop()

# Load Animation
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_ai = load_lottieurl("https://lottie.host/02a52df2-2591-45da-9694-87890f5d7293/63126e7b-c36f-4091-a67b-240a9243764b.json")

# ==========================================
# 2. CORE ENGINES
# ==========================================
def run_code_in_piston(source_code):
    api_url = "https://emkc.org/api/v2/piston/execute"
    payload = {"language": "python", "version": "3.10.0", "files": [{"content": source_code}]}
    try:
        response = requests.post(api_url, json=payload)
        result = response.json()
        if "run" in result: return result["run"]["stdout"], result["run"]["stderr"]
    except: pass
    return "Error", "System Execution Failed"

def get_user_stats(email):
    if not supabase: return {"xp": 0, "level": 1}
    try:
        response = supabase.table("user_stats").select("*").eq("email", email).execute()
        if response.data: return response.data[0]
        else:
            new_user = {"email": email, "xp": 0, "level": 1, "streak": 1}
            supabase.table("user_stats").insert(new_user).execute()
            return new_user
    except: return {"xp": 0, "level": 1}

def update_xp(email, amount):
    if not supabase: return 0, 1
    try:
        current = get_user_stats(email)
        new_xp = current["xp"] + amount
        new_level = (new_xp // 100) + 1
        if new_level > 6: new_level = 6
        supabase.table("user_stats").update({"xp": new_xp, "level": new_level}).eq("email", email).execute()
        return new_xp, new_level
    except: return 0, 1

# ==========================================
# 3. CSS Styling (THE SIDEBAR LOCK)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
    .stApp { background-color: #0E1117; background-image: radial-gradient(circle at 50% 50%, #161B22 0%, #0E1117 100%); }
    
    /* --- 1. RESTORE HEADER (For Mobile Support) --- */
    header { visibility: visible !important; }
    
    /* --- 2. HIDE THE SIDEBAR TOGGLE ARROW (THE LOCK) --- */
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    
    /* --- 3. CLEAN UP UI --- */
    footer { display: none; }
    .stDeployButton { display: none; }
    [data-testid="stDecoration"] { display: none; }
    [data-testid="stSidebar"] { border-right: 1px solid #333; }
    
    /* CARDS */
    .stat-card { background: #1F2329; border: 1px solid #333; padding: 15px; border-radius: 10px; text-align: center; }
    .xp-text { font-size: 24px; font-weight: bold; color: #FF4B4B; font-family: 'Orbitron'; }
    .label-text { font-size: 10px; color: #888; text-transform: uppercase; }
    
    /* CHAT BUBBLES */
    .stChatMessage { background-color: rgba(255,255,255,0.05); border-radius: 10px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. AUTH FLOW
# ==========================================
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = "student"

    if st.session_state.authenticated: return True
    
    # LOGIN SCREEN (Force Sidebar Hidden Here)
    st.markdown("""<style>[data-testid="stSidebar"] { display: none; }</style>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.write(""); st.write("")
        if lottie_ai: st_lottie(lottie_ai, height=500, key="ai_anim")
    with col2:
        st.write(""); st.write("")
        with st.container():
            st.markdown('<h1 style="font-family:Orbitron; font-size:48px; color:#FF4B4B;">Pylo</h1>', unsafe_allow_html=True)
            st.caption("The AI Tutor that Grows with You.")
            
            email = st.text_input("Email", placeholder="student@sanru.com")
            password = st.text_input("Password", type="password")
            
            if st.button("Start Learning", type="primary"):
                if email and password:
                    users_db = st.secrets.get("users", {})
                    role = "student"
                    name = "Student"
                    
                    for _, d in users_db.items():
                        if d["email"] == email and d["password"] == password:
                            role = "admin" if email == "admin@pylo.com" else "demo"
                            name = d["name"]
                    
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name = name
                    st.session_state.user_role = role
                    
                    if supabase:
                        stats = get_user_stats(email)
                        st.session_state.xp = stats.get('xp', 0)
                        st.session_state.level = stats.get('level', 1)
                    else:
                        st.session_state.xp = 0; st.session_state.level = 1
                    st.rerun()
    return False

if not check_login(): st.stop()

# ==========================================
# 5. SYLLABUS & CONTENT
# ==========================================
SYLLABUS = {
    1: {"title": "The Basics", "desc": "Variables & Data Types"},
    2: {"title": "Making Decisions", "desc": "If, Else, Booleans"},
    3: {"title": "Looping", "desc": "For & While Loops"},
    4: {"title": "Data Structures", "desc": "Lists & Dictionaries"},
    5: {"title": "Functions", "desc": "Reusable Code"},
    6: {"title": "Object Oriented", "desc": "Classes & Objects"}
}

# --- STATIC SIDEBAR (LOCKED OPEN) ---
with st.sidebar:
    st.markdown('<h2 style="font-family:Orbitron; color:white;">Pylo 🧬</h2>', unsafe_allow_html=True)
    
    # 1. USER PROFILE
    st.caption(f"Logged in as: {st.session_state.user_name}")
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="stat-card"><div class="xp-text">{st.session_state.xp}</div><div class="label-text">XP</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card"><div class="xp-text">{st.session_state.level}</div><div class="label-text">LEVEL</div></div>', unsafe_allow_html=True)
    
    st.write("")
    st.progress(min((st.session_state.xp % 100) / 100, 1.0))
    st.caption(f"Next Level at {(st.session_state.level * 100)} XP")
    
    st.divider()
    
    # 2. SYLLABUS
    st.subheader("🗺️ Your Journey")
    for lvl, info in SYLLABUS.items():
        if lvl < st.session_state.level:
            st.markdown(f"✅ **Level {lvl}: {info['title']}**")
        elif lvl == st.session_state.level:
            st.markdown(f"📍 **Level {lvl}: {info['title']}** (Current)")
        else:
            st.markdown(f"🔒 *Level {lvl}: {info['title']}*")
            
    st.divider()
    if st.button("Log Out"): st.session_state.authenticated = False; st.rerun()

# ==========================================
# 6. MAIN APP
# ==========================================
curr_lvl_info = SYLLABUS[st.session_state.level]

st.title(f"Level {st.session_state.level}: {curr_lvl_info['title']}")
st.caption(curr_lvl_info['desc'])

# TABS
tab_class, tab_lab, tab_arena = st.tabs(["🧠 The Classroom", "🧪 The Lab", "⚔️ The Boss Fight"])

# --- TAB 1: THE CLASSROOM (SCROLLABLE CHAT) ---
with tab_class:
    # 1. CHAT CONTAINER (Scrollable)
    chat_container = st.container(height=500)
    
    # Initialize Chat
    if "messages" not in st.session_state:
        intro_msg = f"Welcome to Level {st.session_state.level}. I am Pylo, your teacher. We are learning **{curr_lvl_info['title']}**. Shall we start?"
        st.session_state.messages = [{"role": "assistant", "content": intro_msg}]

    # Display Chat INSIDE container
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    # 2. INPUT BAR (Automatically pins to bottom of Tab)
    if prompt := st.chat_input("Answer Pylo or ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display User Message
        with chat_container:
            with st.chat_message("user"): st.markdown(prompt)
        
            # Generate & Display AI Response
            system_prompt = f"""
            You are Pylo, a Python teacher. Student Level: {st.session_state.level}.
            Topic: {curr_lvl_info['title']}.
            GOAL: Teach step-by-step. Ask 1 question at a time.
            Keep it short.
            """
            
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                    stream=True
                )
                response = st.write_stream(chunk.choices[0].delta.content for chunk in stream if chunk.choices[0].delta.content)
            
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- TAB 2: THE LAB ---
with tab_lab:
    st.info("💡 **Tip:** Test your code here to see the Flowchart.")
    col_v1, col_v2 = st.columns([1, 1.5])
    with col_v1:
        vis_code = st.text_area("Type Code:", height=200, placeholder="x = 10\nprint(x)")
        if st.button("👁️ Visualize", type="primary"):
             if vis_code: st.session_state.vis_trigger = vis_code
    with col_v2:
        with st.container(height=500, border=True):
            if "vis_trigger" in st.session_state:
                with st.spinner("Drawing..."):
                    try:
                        req = f"Convert Python to Graphviz DOT (only code): {st.session_state.vis_trigger}"
                        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content": req}])
                        dot = res.choices[0].message.content
                        if "```dot" in dot: dot = dot.split("```dot")[1].split("```")[0]
                        st.graphviz_chart(dot)
                    except: st.error("Error.")
            else: st.markdown("### 👈 Draw Your Code")

# --- TAB 3: THE ARENA ---
with tab_arena:
    st.error(f"🛑 **Exam:** Pass this to unlock Level {st.session_state.level + 1}.")
    c1, c2 = st.columns([1, 1.5])
    if "curr_chal" not in st.session_state: st.session_state.curr_chal = "Click Generate Exam."
    
    with c1:
        if st.button("🎲 Generate Exam"):
            with st.spinner("Creating..."):
                p = f"Create a Python coding problem about {curr_lvl_info['title']}."
                r = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":p}])
                st.session_state.curr_chal = r.choices[0].message.content
        st.markdown(st.session_state.curr_chal)
    
    with c2:
        ans = st.text_area("Solution:", height=300)
        if st.button("🚀 Submit Exam"):
            out, err = run_code_in_piston(ans)
            if err: st.error(f"❌ Error:\n{out}")
            else:
                st.success(f"✅ Output:\n{out}")
                grade_p = f"Problem: {st.session_state.curr_chal}\nCode: {ans}\nOutput: {out}\nCorrect? YES or NO."
                grade_res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":grade_p}])
                
                if "YES" in grade_res.choices[0].message.content.upper():
                    st.balloons()
                    nx, nl = update_xp(st.session_state.user_email, 100)
                    st.session_state.xp = nx; st.session_state.level = nl
                    st.toast(f"🎉 LEVEL UP! Level {nl}")
                    st.rerun()
                else: st.warning("⚠️ Incorrect.")
