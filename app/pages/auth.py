import streamlit as st
from src.database.database import get_database_url, get_engine, get_session_maker, Base
from src.database.auth_crud import authenticate_user, create_user

@st.cache_resource
def get_db_engine():
    url = get_database_url()
    if "postgresql://user:password@localhost/dbname" in url:
        url = "sqlite:///:memory:"
    engine = get_engine(url)
    from src.database.models import User
    Base.metadata.create_all(bind=engine)
    return engine

def get_db_session():
    engine = get_db_engine()
    SessionLocal = get_session_maker(engine)
    return SessionLocal()

def render():
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0 1rem 0;'>
            <h1 style='font-size: 3rem; color: #1E3A8A; margin-bottom: 0.5rem;'>EMIPredict AI 🏦</h1>
            <h3 style='color: #4B5563; font-weight: normal; margin-top: 0;'>Authentication Portal</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Login to your account")
                login_email = st.text_input("Email", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_pass")
                submit_login = st.form_submit_button("Login", type="primary", use_container_width=True)
                
                if submit_login:
                    if not login_email or not login_password:
                        st.error("Please provide both email and password.")
                    else:
                        with get_db_session() as db:
                            user = authenticate_user(db, login_email, login_password)
                            if user:
                                st.session_state.is_authenticated = True
                                st.session_state.user_id = user.id
                                st.session_state.user_email = user.email
                                st.session_state.user_role = user.role
                                st.success("Login successful! Redirecting...")
                                st.rerun()
                            else:
                                st.error("Invalid email or password.")
                                
        with tab2:
            with st.form("signup_form"):
                st.subheader("Create a new account")
                signup_email = st.text_input("Email", key="signup_email")
                signup_password = st.text_input("Password", type="password", key="signup_pass")
                signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
                submit_signup = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
                
                if submit_signup:
                    if not signup_email or not signup_password:
                        st.error("Please provide both email and password.")
                    elif signup_password != signup_confirm:
                        st.error("Passwords do not match.")
                    else:
                        with get_db_session() as db:
                            from src.database.auth_crud import get_user_by_email
                            existing_user = get_user_by_email(db, signup_email)
                            if existing_user:
                                st.error("Email is already registered.")
                            else:
                                try:
                                    user = create_user(db, signup_email, signup_password, role="user")
                                    st.success("Account created successfully! Please log in.")
                                except Exception as e:
                                    st.error(f"Error creating account: {e}")
