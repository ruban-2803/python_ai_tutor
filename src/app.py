import streamlit as st
from groq import Groq
import graphviz

# 1. APP CONFIGURATION
st.set_page_config(
    page_title="PyCoach AI",
    page_icon="🐍",
    layout="wide", # Wide layout to show Flowcharts side-by-side
    initial_sidebar_state="expanded"
)

# 2. CUSTOM STYLES
st.markdown("""
<style>
    .stChatMessage { border-radius: 10px; }
    h1 { color: #306998; } /* Python Blue */
    h3 { color: #FFD43B; } /* Python Yellow */
</style>
""", unsafe_allow_html=True)

# 3. SETUP API
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing! Please add GROQ_API_KEY to secrets.toml")
    st.stop()

# --- THE SYLLABUS ENGINE ---
# This dictionary defines the "Scope" of each chapter.
SYLLABUS = {
    "Level 1: The Basics": {
        "topics": "Print statements, Variables, Strings, Integers, Floats, Basic Math (+ - * /)",
        "forbidden": "Loops, Functions, Lists, If/Else, Classes"
    },
    "Level 2: Logic & Decisions": {
        "topics": "Booleans (True/False), If Statements, Elif, Else, Comparison Operators (==, !=, >)",
        "forbidden": "Loops, Functions, Dictionaries"
    },
    "Level 3: Looping": {
        "topics": "For Loops, While Loops, Range(), Break, Continue",
        "forbidden": "Functions, Classes, list comprehensions"
    },
    "Level 4: Data Structures": {
        "topics": "Lists, Dictionaries, Tuples, Sets, Indexing, Slicing",
        "forbidden": "Classes, Lambdas"
    },
    "Level 5: Functions (Pro)": {
        "topics": "Defining Functions, Arguments, Return statements, Scope",
        "forbidden": "Classes, Decorators"
    }
}

# 4. SIDEBAR INTERFACE
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg", width=60)
    st.title("PyCoach 🐍")
    
    # Progress Selection
    st.subheader("📍 Your Roadmap")
    current_level = st.radio("Select Chapter:", list(SYLLABUS.keys()))
    
    # Show what's in this chapter
    st.info(f"**Focus:** {SYLLABUS[current_level]['topics']}")
    st.warning(f"**Locked:** {SYLLABUS[current_level]['forbidden']}")
    
    st.divider()
    
    # Tools
    # Tools
    if st.button("🗑️ Reset Chat"):
        # Delete the key so the 'Initialize Chat' block runs again
        if "messages" in st.session_state:
            del st.session_state["messages"]
        if "trigger_visualizer" in st.session_state:
            del st.session_state["trigger_visualizer"]
        st.rerun()
        
# 5. MAIN LOGIC & SYSTEM PROMPT
# We dynamically build the prompt based on the Sidebar Selection
system_prompt = f"""
You are PyCoach, a strict but encouraging Python Tutor.
CURRENT CHAPTER: {current_level}
ALLOWED TOPICS: {SYLLABUS[current_level]['topics']}
FORBIDDEN TOPICS: {SYLLABUS[current_level]['forbidden']}

RULES:
1. ONLY teach concepts from the ALLOWED TOPICS.
2. If the user asks about a Forbidden Topic (e.g., asking about Loops in Level 1), politely refuse and say "That's in Level 3! Let's master {current_level} first."
3. Keep explanations short and code snippets simple.
4. If asked to "Visualize" or "Draw", provide a Graphviz DOT code block.
"""

st.title(f"{current_level}")
st.caption("Ask questions, write code, or request a challenge!")

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"Welcome to **{current_level}**! Ready to learn? Ask me anything or click 'Challenge Me'."}]

# 6. LAYOUT: CHAT (Left) vs VISUALIZER (Right)
col_chat, col_vis = st.columns([1.5, 1])

with col_chat:
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ex: What is a variable? OR Give me a challenge"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Response
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                temperature=0.7,
                stream=True
            )
            
            with st.chat_message("assistant"):
                response = st.write_stream(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Check if we should update the visualizer (Simple Keyword Check)
            if "visualize" in prompt.lower() or "draw" in prompt.lower() or "flowchart" in prompt.lower():
                st.session_state.trigger_visualizer = True
            else:
                st.session_state.trigger_visualizer = False
                
        except Exception as e:
            st.error(f"Error: {e}")

# 7. THE VISUALIZER ENGINE (Right Column)
with col_vis:
    st.subheader("🕸️ Logic Visualizer")
    st.caption("Ask the bot to 'Visualize this code' to see the flowchart.")
    
    # We use a separate AI call to generate the graph strictly
    if st.session_state.get("trigger_visualizer"):
        with st.spinner("Generating Flowchart..."):
            # Get the last code snippet from the chat (simplified logic)
            last_bot_msg = st.session_state.messages[-1]["content"]
            
            graph_prompt = f"""
            Take the following Python explanation/code and convert the Logic Flow into a Graphviz DOT script.
            Return ONLY the DOT code inside ```dot ... ``` blocks. No other text.
            
            CONTENT TO VISUALIZE:
            {last_bot_msg}
            """
            
            try:
                graph_response = client.chat.completions.create(
                    model="llama-3.1-8b-instant", # Use fast model for graphs
                    messages=[{"role": "user", "content": graph_prompt}],
                    temperature=0
                )
                
                dot_code = graph_response.choices[0].message.content
                
                # Clean up the code block markdown
                if "```dot" in dot_code:
                    dot_code = dot_code.split("```dot")[1].split("```")[0]
                elif "```" in dot_code:
                     dot_code = dot_code.split("```")[1].split("```")[0]
                
                st.graphviz_chart(dot_code)
                
            except Exception as e:
                st.warning("Could not visualize this logic.")

    # Manual Code Visualizer (Optional Feature)
    with st.expander("Visualize Your Own Code"):
        user_code = st.text_area("Paste Python Code here:")
        if st.button("Draw Flowchart"):
            st.session_state.trigger_visualizer = True
            # We treat this as a "system" message to force visualization
            st.session_state.messages.append({"role": "assistant", "content": user_code})
            st.rerun()
