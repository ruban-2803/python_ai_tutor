import streamlit as st
from groq import Groq
import requests
from supabase import create_client, Client # NEW IMPORT

# ==========================================
# 1. CONFIG & DB CONNECTION
# ==========================================
st.set_page_config(page_title="Pylo | SanRu Labs", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

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
# 2. DB FUNCTIONS (GAMIFICATION)
# ==========================================
def get_user_stats(email):
    """Fetch XP, Level, Streak from Supabase"""
    try:
        response = supabase.table("user_stats").select("*").eq("email", email).execute()
        if response.data:
            return response.data[0]
        else:
            # If user not in DB, create them
            new_user = {"email": email, "xp": 0, "level": 1, "streak": 1}
            supabase.table("user_stats").insert(new_user).execute()
            return new_user
    except:
        return {"xp": 0, "level": 1, "streak": 0}

def update_xp(email, amount):
    """Add XP to user"""
    try:
        # Get current XP
        current = get_user_stats(email)
        new_xp = current["xp"] + amount
        
        # Level Up Logic (Every 100 XP = 1 Level)
        new_level = (new_xp // 100) + 1
        if new_level > 6: new_level = 6 # Max level
        
        supabase.table("user_stats").update({"xp": new_xp, "level": new_level}).eq("email", email).execute()
        return new_xp, new_level
    except Exception as e:
        print(e)
        return 0, 1

def run_code_in_piston(source_code):
    """Execute code securely"""
    api_url = "https://emkc.org/api/v2/piston/execute"
    payload = {"language": "python", "version": "3.10.0", "files": [{"content": source_code}]}
    try:
        response = requests.post(api_url, json=payload)
        result = response.json()
        if "run" in result:
            return result["run"]["stdout"], result["run"]["stderr"]
    except: pass
    return "Error", "System Failure"

# ==========================================
# 3. CSS & UI
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
    .stApp { background-color: #0E1117; background-image: radial-gradient(circle at 50% 50%, #161B22 0%, #0E1117 100%); }
    
    /* HIDE UI */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    
    /* GAMIFICATION CARDS */
    .stat-card {
        background: #1F2329; border: 1px solid #333; padding: 15px; border-radius: 10px; text-align: center;
    }
    .xp-text { font-size: 24px; font-weight: bold; color: #FF4B4B; font-family: 'Orbitron'; }
    .label-text { font-size: 12px; color: #888; text-transform: uppercase; }
    
    /* OTHER STYLES (Login, etc - Same as before) */
    .login-container { background: rgba(20, 20, 30, 0.7); backdrop-filter: blur(12px); padding: 50px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .product-title { font-family: 'Orbitron'; font-size: 48px; font-weight: 900; background: linear-gradient(90deg, #FF4B4B, #FF914D); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stTextInput input { background-color: #1F2329 !important; color: white !important; border: 1px solid #333; }
    div.stButton > button { background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%); color: white; border: none; font-weight: bold; }
    .stTextArea textarea { font-family: 'Courier New', monospace; background-color: #111 !important; color: #00FF99 !important; }
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. LOGIN LOGIC
# ==========================================
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        st.markdown("""<style>[data-testid="stSidebar"] { display: block; }</style>""", unsafe_allow_html=True)
        return True
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.write(""); st.write("")
        if lottie_ai: st_lottie(lottie_ai, height=500, key="ai_anim")
    with col2:
        st.write(""); st.write("")
        with st.container():
            st.markdown('<div class="product-title">Pylo</div>', unsafe_allow_html=True)
            st.caption("Intelligent Coding Environment. Powered by SanRu Labs.")
            
            email = st.text_input("ACCESS ID", placeholder="student@sanru.com")
            password = st.text_input("SECURE KEY", type="password", placeholder="••••••••")
            
            if st.button("INITIALIZE SYSTEM"):
                users_db = st.secrets.get("users", {})
                for _, details in users_db.items():
                    if details["email"] == email and details["password"] == password:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_name = details["name"]
                        st.session_state.user_role = "admin" if email == "admin@pylo.com" else "demo"
                        
                        # FETCH STATS FROM DB
                        stats = get_user_stats(email)
                        st.session_state.xp = stats['xp']
                        st.session_state.level = stats['level']
                        st.rerun()
                st.error("❌ ACCESS DENIED")
    return False

if not check_login(): st.stop()

# ==========================================
# 5. DASHBOARD
# ==========================================
st.markdown("""<style>[data-testid="stSidebar"] { display: block; }</style>""", unsafe_allow_html=True)

SYLLABUS = {
    1: "The Basics (Variables)", 2: "Logic (If/Else)", 3: "Looping (For/While)",
    4: "Data Structures (Lists)", 5: "Functions", 6: "Advanced (OOP)"
}

with st.sidebar:
    st.markdown('<h2 style="color:white; font-family:Orbitron;">Pylo 🧬</h2>', unsafe_allow_html=True)
    if st.session_state.user_role == "admin": st.success("⚡ ADMIN")
    else: st.warning("🧪 DEMO")
    
    # --- GAMIFICATION STATS ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="xp-text">{st.session_state.xp}</div><div class="label-text">TOTAL XP</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="xp-text">{st.session_state.level}</div><div class="label-text">LEVEL</div></div>', unsafe_allow_html=True)
    
    st.write("")
    st.progress(min((st.session_state.xp % 100) / 100, 1.0), text=f"Progress to Level {st.session_state.level + 1}")
    
    st.divider()
    st.subheader("📍 Roadmap")
    # Only show levels up to user's current level
    selected_level_name = st.radio("Chapter:", [v for k,v in SYLLABUS.items()])
    
    # Simple map back to int
    current_level_num = [k for k,v in SYLLABUS.items() if v == selected_level_name][0]
    
    if st.button("Log Out"): st.session_state.authenticated = False; st.rerun()

# TABS
st.title("Pylo 🧬")
tab_vis, tab_learn, tab_arena, tab_codegen = st.tabs(["👁️ Visualizer", "🧠 Learn", "⚔️ Arena", "⚡ Generator"])

# (Tab 1 & 2 & 4 are same as before - abbreviated for length, insert previous code here)
# ... [Insert Visualizer, Learn, Generator Code from previous response] ... 
# I will only provide the UPDATED ARENA Tab which uses the DB.

with tab_vis:
    st.header("👁️ Logic Visualizer")
    col_v1, col_v2 = st.columns([1, 1.5])
    with col_v1:
        vis_code = st.text_area("Code Input:", height=200, placeholder="x=10")
        if st.button("✨ Visualize"): st.session_state.vis_trigger = vis_code
    with col_v2:
        if "vis_trigger" in st.session_state:
            with st.spinner("Drawing..."):
                try:
                    graph_req = f"Convert to Graphviz DOT (only code): {st.session_state.vis_trigger}"
                    g_resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content": graph_req}])
                    dot = g_resp.choices[0].message.content.split("```dot")[1].split("```")[0]
                    st.graphviz_chart(dot)
                except: st.error("Error drawing graph.")

with tab_learn:
    st.header("🧠 Tutor")
    if prompt := st.chat_input("Ask Pylo..."):
         # ... (Standard Chat Logic) ...
         st.info("Pylo is thinking...") # Placeholder for brevity

# --- UPDATED ARENA TAB (EARN XP) ---
with tab_arena:
    st.header(f"⚔️ Level {current_level_num} Challenge")
    col_q, col_code = st.columns([1, 1.5])
    
    if "current_challenge" not in st.session_state: st.session_state.current_challenge = "Click Generate!"
    
    with col_q:
        if st.button("🎲 New Problem", type="primary"):
             q_prompt = f"Create a Python challenge for Level {current_level_num}."
             q_resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": q_prompt}])
             st.session_state.current_challenge = q_resp.choices[0].message.content
        st.markdown(st.session_state.current_challenge)
    
    with col_code:
        user_code = st.text_area("Solution:", height=300, key="arena_code")
        if st.button("🚀 Run & Submit"):
            # 1. Run Code
            out, err = run_code_in_piston(user_code)
            
            # 2. Check Result (Simple Check: No Error)
            if err:
                st.error(f"❌ Execution Failed:\n{out}")
            else:
                st.success(f"✅ Output:\n{out}")
                
                # 3. AI Grading
                grade_req = f"Task: {st.session_state.current_challenge}. Code: {user_code}. Output: {out}. Did they pass? Answer YES or NO."
                grade_resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": grade_req}])
                
                if "YES" in grade_resp.choices[0].message.content.upper():
                    st.balloons()
                    # 4. UPDATE DB (EARN XP)
                    new_xp, new_lvl = update_xp(st.session_state.user_email, 20)
                    st.session_state.xp = new_xp
                    st.session_state.level = new_lvl
                    st.toast(f"🎉 +20 XP! Total: {new_xp}")
                    st.rerun() # Refresh sidebar
                else:
                    st.warning("⚠️ Logic Incorrect. Try again.")

with tab_codegen:
    st.header("⚡ Generator")
    # ... (Same Generator Logic) ...
