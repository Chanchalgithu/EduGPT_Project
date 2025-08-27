import streamlit as st
import os
import random
import datetime
import time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# ---------- SETTINGS ----------
load_dotenv()

# 🛡️ Secure API key loading - NO PRINTING
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    st.error("❌ OPENAI_API_KEY not found in environment variables!")
    st.stop()

MODEL_LLM = "gpt-4o-mini"
USERS_FILE = "users.csv"
SESSION_FILE = "session.csv"
SESSION_DURATION = 6 * 60 * 60   # 6 hours

# Initialize OpenAI client
try:
    client = OpenAI(api_key=API_KEY)
except Exception as e:
    st.error(f"❌ Failed to initialize OpenAI client: {e}")
    st.stop()

# ---------- SIMPLE ANSWER FUNCTION ----------
def answer_query(query, context=""):
    """Simple OpenAI-based question answering"""
    try:
        if context:
            prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer this question based on the context provided:"
        else:
            prompt = f"Question: {query}\n\nProvide a helpful educational answer:"

        response = client.chat.completions.create(
            model=MODEL_LLM,
            messages=[
                {"role": "system", "content": "You are EduGPT, a helpful educational assistant. Provide clear, accurate, and educational responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

# ---------- USER MANAGEMENT ----------
def load_users():
    """Load users from CSV file"""
    try:
        if os.path.exists(USERS_FILE):
            return pd.read_csv(USERS_FILE)
        else:
            return pd.DataFrame(columns=["username", "password", "phone"])
    except Exception:
        return pd.DataFrame(columns=["username", "password", "phone"])

def save_user(username, password, phone):
    """Save new user to CSV file"""
    try:
        df = load_users()
        if username in df["username"].values:
            return False
        new_row = pd.DataFrame([[username, password, phone]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(USERS_FILE, index=False)
        return True
    except Exception:
        return False

# ---------- SESSION MANAGEMENT ----------
def load_session():
    """Load session from file"""
    try:
        if os.path.exists(SESSION_FILE):
            df = pd.read_csv(SESSION_FILE)
            if len(df) > 0:
                return {"username": df.iloc[0]["username"], "login_time": float(df.iloc[0]["login_time"])}
    except Exception:
        pass
    return None

def save_session(username):
    """Save session to file"""
    try:
        now = time.time()
        df = pd.DataFrame([[username, now]], columns=["username", "login_time"])
        df.to_csv(SESSION_FILE, index=False)
    except Exception:
        pass

def clear_session():
    """Clear session file"""
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception:
        pass

def is_session_valid():
    """Check if session is valid"""
    session = load_session()
    if session:
        now = time.time()
        if now - session["login_time"] < SESSION_DURATION:
            st.session_state["logged_in"] = True
            st.session_state["username"] = session["username"]
            return True
        else:
            clear_session()
    return False

# ---------- OTP SYSTEM ----------
def send_otp(phone):
    """Generate and 'send' OTP (demo mode)"""
    otp = str(random.randint(1000, 9999))
    st.session_state["otp_store"] = {phone: otp}
    return otp

# ---------- LOGIN / SIGNUP PAGE ----------
def login_signup():
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🎓 EduGPT</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Your AI Educational Assistant</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        choice = st.radio("Choose option:", ["Login", "Signup"], horizontal=True)

        if choice == "Signup":
            st.subheader("📝 Create Account")
            with st.form("signup_form", clear_on_submit=False):
                username = st.text_input("👤 Username")
                password = st.text_input("🔒 Password", type="password")
                phone = st.text_input("📱 Phone Number")

                send_otp_btn = st.form_submit_button("📩 Send OTP")
                if send_otp_btn and phone:
                    otp = send_otp(phone)
                    st.success(f"📱 OTP sent to {phone}")
                    st.info(f"Demo OTP: **{otp}**")

                otp_input = st.text_input("🔢 Enter OTP")
                signup_btn = st.form_submit_button("✅ Create Account")

                if signup_btn:
                    if not all([username, password, phone, otp_input]):
                        st.error("❌ Please fill all fields!")
                    elif "otp_store" in st.session_state and phone in st.session_state["otp_store"]:
                        if st.session_state["otp_store"][phone] == otp_input:
                            if save_user(username, password, phone):
                                st.success("🎉 Account created successfully! Please login.")
                                del st.session_state["otp_store"]
                            else:
                                st.error("❌ Username already exists!")
                        else:
                            st.error("❌ Invalid OTP!")
                    else:
                        st.error("❌ Please request OTP first!")

        else:  # Login
            st.subheader("🔑 Login")
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("👤 Username")
                password = st.text_input("🔒 Password", type="password")
                login_btn = st.form_submit_button("🚀 Login")

                if login_btn:
                    if not username or not password:
                        st.error("❌ Please enter both username and password!")
                    else:
                        df = load_users()
                        user_exists = ((df["username"] == username) & (df["password"] == password)).any()
                        
                        if user_exists:
                            st.session_state["logged_in"] = True
                            st.session_state["username"] = username
                            save_session(username)
                            st.success(f"🎉 Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password!")

# ---------- MAIN APPLICATION ----------
def main_app():
    st.set_page_config(page_title="EduGPT 🎓", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
            .chat-message {
                background: #f0f2f6;
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
            }
            @media (max-width: 768px) {
                .block-container {
                    padding: 1rem !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "history" not in st.session_state:
        st.session_state.history = {}

    today = datetime.date.today().strftime("%Y-%m-%d")
    if today not in st.session_state.history:
        st.session_state.history[today] = []

    # Sidebar
    with st.sidebar:
        st.header(f"👋 Welcome, {st.session_state.get('username', 'User')}")
        
        st.subheader("💬 Chat History")
        if st.session_state.history[today]:
            for i, chat in enumerate(st.session_state.history[today][-5:]):  # Show last 5 chats
                with st.expander(f"Chat {i+1}", expanded=False):
                    st.markdown(f"**Q:** {chat['q'][:50]}...")
                    if st.button(f"🗑️ Delete", key=f"del_{i}"):
                        st.session_state.history[today].pop(i)
                        st.rerun()
        else:
            st.info("No chat history yet.")

        st.divider()
        
        if st.button("🆕 New Chat", type="primary"):
            st.session_state.history[today] = []
            st.rerun()

        if st.button("🗑️ Clear All History"):
            st.session_state.history = {today: []}
            st.rerun()

        if st.button("🚪 Logout"):
            clear_session()
            st.session_state["logged_in"] = False
            if "username" in st.session_state:
                del st.session_state["username"]
            st.rerun()

    # Main content
    st.markdown('<div class="main-header"><h1 style="color: white; text-align: center; margin: 0;">🎓 EduGPT - Your AI Tutor</h1></div>', unsafe_allow_html=True)

    # File upload (optional)
    uploaded_file = st.file_uploader(
        "📎 Upload a document (optional)",
        type=['txt', 'pdf', 'docx'],
        help="Upload a document to ask questions about its content"
    )
    
    file_context = ""
    if uploaded_file:
        try:
            if uploaded_file.type == "text/plain":
                file_context = str(uploaded_file.read(), "utf-8")
                st.success(f"✅ Text file uploaded: {uploaded_file.name}")
            else:
                st.info(f"📄 File uploaded: {uploaded_file.name} (basic parsing)")
                file_context = f"Content from {uploaded_file.name}"
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

    # Chat interface
    st.subheader("💭 Ask me anything!")
    
    # Display recent chat history
    if st.session_state.history[today]:
        st.subheader("Recent Conversations:")
        for chat in st.session_state.history[today][-3:]:  # Show last 3 conversations
            st.markdown(f'<div class="chat-message"><strong>🙋 You:</strong> {chat["q"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-message"><strong>🤖 EduGPT:</strong> {chat["a"]}</div>', unsafe_allow_html=True)

    # Input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_question = st.text_input(
                "Type your question here:",
                placeholder="e.g., Explain photosynthesis, Help with math problem, What is AI?",
                key="question_input"
            )
        
        with col2:
            submitted = st.form_submit_button("🚀 Ask", type="primary")

    # Process question
    if submitted and user_question.strip():
        with st.spinner("🤔 Thinking..."):
            answer = answer_query(user_question, file_context)

        # Save to history
        st.session_state.history[today].append({
            "q": user_question,
            "a": answer
        })

        # Display answer
        st.markdown("### 🎯 Answer:")
        st.markdown(f'<div class="chat-message">{answer}</div>', unsafe_allow_html=True)

        # Auto-scroll to answer
        st.rerun()

# ---------- APP ENTRY POINT ----------
def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Check for valid session
    if not st.session_state["logged_in"]:
        is_session_valid()

    # Route to appropriate page
    if st.session_state["logged_in"]:
        main_app()
    else:
        login_signup()

if __name__ == "__main__":
    main()
