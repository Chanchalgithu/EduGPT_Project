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
    
    # Enhanced Custom CSS with Robotics Theme
    st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                backdrop-filter: blur(4px);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            .chat-message {
                background: linear-gradient(145deg, #f0f2f6, #e6e9ef);
                padding: 1.2rem;
                border-radius: 15px;
                margin: 0.8rem 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                border-left: 4px solid #667eea;
            }
            .chat-item {
                background: linear-gradient(145deg, #ffffff, #f8f9fa);
                border: 1px solid #e9ecef;
                border-radius: 12px;
                padding: 12px;
                margin: 8px 0;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                transition: all 0.3s ease;
                position: relative;
            }
            .chat-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
                border-color: #667eea;
            }
            .chat-content {
                font-size: 14px;
                color: #495057;
                margin-bottom: 8px;
                line-height: 1.4;
            }
            .chat-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .chat-time {
                font-size: 11px;
                color: #6c757d;
            }
            .delete-btn {
                background: none;
                border: none;
                color: #dc3545;
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 16px;
                transition: all 0.2s ease;
            }
            .delete-btn:hover {
                background-color: #dc3545;
                color: white;
                transform: scale(1.1);
            }
            .new-chat-btn {
                background: linear-gradient(135deg, #4CAF50, #45a049) !important;
                color: white !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 12px 24px !important;
                font-weight: 600 !important;
                font-size: 16px !important;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
                transition: all 0.3s ease !important;
                width: 100% !important;
                margin-bottom: 15px !important;
            }
            .new-chat-btn:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
            }
            .delete-all-btn {
                background: linear-gradient(135deg, #ff6b6b, #ee5a52) !important;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                padding: 10px 20px !important;
                font-weight: 500 !important;
                box-shadow: 0 3px 12px rgba(255, 107, 107, 0.3) !important;
                transition: all 0.3s ease !important;
                width: 100% !important;
                margin-bottom: 15px !important;
            }
            .delete-all-btn:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 5px 16px rgba(255, 107, 107, 0.4) !important;
            }
            .sidebar-header {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            .history-section {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                border: 1px solid #e9ecef;
            }
            @media (max-width: 768px) {
                .block-container {
                    padding: 1rem !important;
                }
                .chat-item {
                    padding: 10px;
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

    # Sidebar with Enhanced Design
    with st.sidebar:
        # Welcome Header
        st.markdown(f"""
            <div class="sidebar-header">
                <h3 style="margin: 0;">👋 Welcome</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">{st.session_state.get('username', 'User')}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # New Chat Button with Enhanced Styling
        if st.button("🚀 New Chat", key="new_chat", help="Start a fresh conversation"):
            st.session_state.history[today] = []
            st.rerun()

        # Delete All History Button
        if st.button("🗑️ Clear All History", key="delete_all", help="Delete all chat history"):
            st.session_state.history = {today: []}
            st.success("✅ All chat history cleared!")
            st.rerun()

        # Chat History Section
        st.markdown("""
            <div class="history-section">
                <h4 style="margin-top: 0; color: #495057;">💬 Chat History</h4>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.history[today]:
            for i, chat in enumerate(st.session_state.history[today]):
                # Create unique key for each chat item
                chat_key = f"chat_{i}_{len(chat['q'])}"
                
                # Display chat item with three dots menu
                st.markdown(f"""
                    <div class="chat-item">
                        <div class="chat-content">
                            <strong>Q:</strong> {chat['q'][:60]}{'...' if len(chat['q']) > 60 else ''}
                        </div>
                        <div class="chat-actions">
                            <span class="chat-time">Chat {i+1}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Three dots menu for individual chat deletion
                col1, col2, col3 = st.columns([3, 1, 1])
                with col3:
                    if st.button("⋮", key=f"menu_{chat_key}", help="Delete this chat"):
                        st.session_state.history[today].pop(i)
                        st.success(f"✅ Chat {i+1} deleted!")
                        st.rerun()
        else:
            st.markdown("""
                <div style="text-align: center; padding: 20px; color: #6c757d;">
                    <p>🤖 No conversations yet</p>
                    <p style="font-size: 12px;">Start chatting to see history here</p>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        
        # Logout Button
        if st.button("🚪 Logout", key="logout", help="Sign out from your account"):
            clear_session()
            st.session_state["logged_in"] = False
            if "username" in st.session_state:
                del st.session_state["username"]
            st.rerun()

    # Main content with Enhanced Header
    st.markdown("""
        <div class="main-header">
            <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem;">
                🤖 EduGPT
            </h1>
            <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 10px 0 0 0; font-size: 1.2rem;">
                Your Advanced AI Educational Assistant
            </p>
        </div>
    """, unsafe_allow_html=True)

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
        st.subheader("🔄 Recent Conversations:")
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

