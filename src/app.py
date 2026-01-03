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
    initial_sidebar_state="collapsed"
)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except:
        return None

supabase = init_supabase()

# Initialize Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ API Key Error: Check secrets.toml")
    st.stop()

# Load Animation
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_ai = load_lottieurl("https://lottie.host/02a52df2-2591-45da-9694-87890f5d7293/63126e7b-c36f-4091-a67b-240a9243764b.json")

# ==========================================
# 2. CORE ENGINES (PISTON & DB)
# ==========================================
def run_code_in_piston(source_code):
    """Execute code securely via Piston API"""
    api_url = "https://emkc.org/api/v2/piston/execute"
    payload = {"language": "python", "version": "3.10.0", "files": [{"content": source_code}]}
    try:
        response = requests.post(api_url, json=payload)
        result = response.json()
        if "run" in result:
            return result["run"]["stdout"], result["run"]["stderr"]
    except: pass
    return "Error", "System Execution Failed"

def get_user_stats(email):
    """Fetch/Create User Stats from Supabase"""
    if not supabase: return {"xp": 0, "level": 1} # Fallback
    try:
        response = supabase.table("user_stats").select("*").eq("email", email).execute()
        if response.data: return response.data[0]
        else:
            # Create new user automatically
            new_user = {"email": email, "xp": 0, "level": 1, "streak": 1}
            supabase.table("user_stats").insert(new_user).execute()
            return new_user
    except: return {"xp": 0, "level": 1}

def update_xp(email, amount):
    """Add XP and Check Level Up"""
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
# 3. UI STYLING (CSS - FIXED)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
    .stApp { background-color: #0E1117; background-image: radial-gradient(circle at 50% 50%, #161B22 0%, #0E1117 100%); }

    /* --- SIDEBAR MENU FIX --- */
    /* We DO NOT hide the header anymore, so the hamburger menu stays visible */
    
    /* Hide just the "Manage App" button and Decoration */
    [data-testid="stDecoration"] { display: none; }
    .stDeployButton { display: none; }
    
    /* Hide the 3-dot menu and Github Icon (Toolbar) */
    [data-testid="stToolbar"] { visibility: hidden; }
    
    /* Hide Footer */
    footer { display: none; }

    /* Login Card */
    .login-container { background: rgba(20, 20, 30, 0.7); backdrop-filter: blur(12px); padding: 50px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    
    /* Gamification Cards */
    .stat-card { background: #1F2329; border: 1px solid #333; padding: 10px; border-radius: 8px; text-align: center; }
    .xp-text { font-size: 22px; font-weight: bold; color: #FF4B4B; font-family: 'Orbitron'; }
    .label-text { font-size: 10px; color: #888; text-transform: uppercase; }
    .lock-card { background-color: #1a1a2e; border: 1px solid #FF4B4B; padding: 40px; border-radius: 15px; text-align: center; margin-top: 50px; }
    
    /* Inputs */
    .stTextInput input { background-color: #1F2329 !important; color: white !important; border: 1px solid #333; }
    .stTextArea textarea { font-family: 'Courier New', monospace; background-color: #111 !important; color: #00FF99 !important; border: 1px solid #333; }
    
    /* Typography */
    .product-title { font-family: 'Orbitron'; font-size: 48px; font-weight: 900; background: linear-gradient(90deg, #FF4B4B, #FF914D); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .tagline { font-size: 14px; color: #AAA; letter-spacing: 1px; text-transform: uppercase; }
    
    /* Initial Sidebar State */
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. AUTH & LOGIN FLOW (OPEN ACCESS)
# ==========================================
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = "student"

    # IF LOGGED IN: FORCE SIDEBAR TO BE VISIBLE
    if st.session_state.authenticated:
        st.markdown("""
        <style>
            [data-testid="stSidebar"] { 
                display: block !important; 
            }
        </style>
        """, unsafe_allow_html=True)
        return True
    
    # LOGIN SCREEN
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
                if not email or not password:
                    st.warning("⚠️ Enter Email & Password")
                else:
                    # 1. Determine Role (Admin vs Student)
                    users_db = st.secrets.get("users", {})
                    user_role = "student"
                    user_name = "Student"
                    
                    # Check if Admin credentials
                    for _, details in users_db.items():
                        if details["email"] == email and details["password"] == password:
                            user_role = "admin" if email == "admin@pylo.com" else "demo"
                            user_name = details["name"]
                    
                    # 2. Login
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name = user_name
                    st.session_state.user_role = user_role
                    
                    # 3. Sync with DB
                    if supabase:
                        with st.spinner("Syncing Database..."):
                            stats = get_user_stats(email)
                            st.session_state.xp = stats.get('xp', 0)
                            st.session_state.level = stats.get('level', 1)
                    else:
                        st.session_state.xp = 0
                        st.session_state.level = 1
                        
                    st.rerun()
    return False

if not check_login(): st.stop()

# ==========================================
# 5. MAIN DASHBOARD
# ==========================================

SYLLABUS = {
    1: "The Basics (Variables)", 2: "Logic (If/Else)", 3: "Looping (For/While)",
    4: "Data Structures (Lists)", 5: "Functions", 6: "Advanced (OOP)"
}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<h2 style="color:white; font-family:Orbitron;">Pylo 🧬</h2>', unsafe_allow_html=True)
    if st.session_state.user_role == "admin": st.success("⚡ ADMIN MODE")
    elif st.session_state.user_role == "demo": st.warning("🧪 DEMO MODE")
    else: st.info("🎓 STUDENT MODE")
    
    # GAMIFICATION STATS
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="stat-card"><div class="xp-text">{st.session_state.xp}</div><div class="label-text">TOTAL XP</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card"><div class="xp-text">{st.session_state.level}</div><div class="label-text">LEVEL</div></div>', unsafe_allow_html=True)
    
    st.write("")
    st.progress(min((st.session_state.xp % 100) / 100, 1.0), text=f"Next Level: {st.session_state.level + 1}")
    
    st.divider()
    st.subheader("📍 Roadmap")
    selected_level_name = st.radio("Chapter:", [v for k,v in SYLLABUS.items()])
    current_level_num = [k for k,v in SYLLABUS.items() if v == selected_level_name][0]
    
    # Lock Logic (Example: Students locked to Level 2 max unless they have XP)
    is_locked = False
    # Example Rule: If Demo/Student and Level > 2 -> Locked
    if st.session_state.user_role != "admin" and current_level_num > 2: is_locked = True
    
    if is_locked: st.error("🔒 LOCKED (Pro)")
    else: st.info(f"Unit: {selected_level_name}")
    
    st.divider()
    if st.button("Log Out"): st.session_state.authenticated = False; st.rerun()

def show_lock_screen(feature_name):
    st.markdown(f"""<div class="lock-card"><h1 style='color:#FF4B4B; font-family:Orbitron;'>🔒 RESTRICTED</h1><h3 style='color:white;'>{feature_name} is a PRO feature.</h3><p style='color:#AAA;'>Upgrade license to unlock.</p></div>""", unsafe_allow_html=True)

# --- 4-TAB SYSTEM ---
st.title("Pylo 🧬")
tab_vis, tab_learn, tab_arena, tab_codegen = st.tabs(["👁️ Visualizer", "🧠 Learn", "⚔️ Arena", "⚡ Generator"])

# TAB 1: VISUALIZER
with tab_vis:
    st.header("👁️ Logic Visualizer")
    col_v1, col_v2 = st.columns([1, 1.5])
    with col_v1:
        st.caption("Paste Python Code:")
        vis_code = st.text_area("Code Input:", height=200, placeholder="x=10\nif x>5:\n  print('Hi')")
        if st.button("✨ Visualize", type="primary"): 
            if vis_code: st.session_state.vis_trigger = vis_code
    with col_v2:
        with st.container(height=500, border=True):
            if "vis_trigger" in st.session_state:
                with st.spinner("Rendering Flowchart..."):
                    try:
                        graph_req = f"Convert to Graphviz DOT code (only code): {st.session_state.vis_trigger}"
                        g_resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content": graph_req}])
                        dot = g_resp.choices[0].message.content
                        if "```dot" in dot: dot = dot.split("```dot")[1].split("```")[0]
                        st.graphviz_chart(dot)
                    except: st.error("Visualization Failed.")
            else: st.info("👈 Enter code to visualize.")

# TAB 2: LEARN
with tab_learn:
    if is_locked: show_lock_screen("AI Tutor")
    else:
        st.header("🧠 AI Tutor")
        if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Ready to teach!"}]
        for msg in st.session_state.messages: 
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Ask Pylo..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            sys_p = f"You are Pylo. Topic: {selected_level_name}. Keep it short."
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_p}]+st.session_state.messages)
            bot_reply = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant"): st.markdown(bot_reply)

# TAB 3: ARENA (XP SYSTEM)
with tab_arena:
    st.header(f"⚔️ Challenge: {selected_level_name}")
    col_q, col_code = st.columns([1, 1.5])
    
    if "current_challenge" not in st.session_state: st.session_state.current_challenge = "Click Generate!"
    if "arena_attempts" not in st.session_state: st.session_state.arena_attempts = 0
    
    with col_q:
        if st.button("🎲 New Problem", type="primary"):
            # Check limits for non-admins
            if st.session_state.user_role != "admin" and st.session_state.arena_attempts >= 3:
                st.error("🚫 DAILY LIMIT REACHED")
            else:
                st.session_state.arena_attempts += 1
                q_p = f"Create a Python challenge for {selected_level_name}."
                q_r = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":q_p}])
                st.session_state.current_challenge = q_r.choices[0].message.content
        st.markdown(st.session_state.current_challenge)
    
    with col_code:
        user_code = st.text_area("Solution:", height=300, key="arena_code")
        if st.button("🚀 Run & Submit"):
            out, err = run_code_in_piston(user_code)
            if err: st.error(f"❌ Error:\n{out}")
            else:
                st.success(f"✅ Output:\n{out}")
                grade_req = f"Task: {st.session_state.current_challenge}. Code: {user_code}. Output: {out}. Did they pass? Answer YES or NO."
                grade_res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":grade_req}])
                if "YES" in grade_res.choices[0].message.content.upper():
                    st.balloons()
                    if supabase:
                        nx, nl = update_xp(st.session_state.user_email, 20)
                        st.session_state.xp = nx
                        st.session_state.level = nl
                        st.toast(f"🎉 +20 XP! Total: {nx}")
                        st.rerun()
                else: st.warning("⚠️ Logic Incorrect.")

# TAB 4: GENERATOR
with tab_codegen:
    if st.session_state.user_role != "admin": show_lock_screen("Code Generator")
    else:
        st.header("⚡ Instant Generator")
        c1, c2 = st.columns([1, 1.5])
        with c1:
            req = st.text_area("Requirements:", height=300)
            if st.button("✨ Generate"): 
                with st.spinner("Coding..."):
                    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Write Python code for: {req}"}])
                    st.session_state.gen_code = res.choices[0].message.content
        with c2:
            with st.container(height=600, border=True):
                if "gen_code" in st.session_state: st.markdown(st.session_state.gen_code)
