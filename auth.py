import streamlit as st
import urllib.parse
from supabase_config import supabase

def validate_url(url):
    """Validate that the URL is properly formatted"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def login_form():
    """Display login form and handle authentication"""
    st.title("🔒 Welcome to ExplainMate")
    
    # Check Supabase configuration
    url = supabase.supabase_url
    if not validate_url(url):
        st.error("""
        ⚠️ Invalid Supabase URL configuration! 
        
        Please ensure your SUPABASE_URL in .env:
        1. Starts with https://
        2. Does not end with a slash
        3. Is in the format: https://your-project-id.supabase.co
        """)
        st.stop()
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("🔑 Login", use_container_width=True):
            if not email or not password:
                st.error("Please fill in all fields")
                return
                
            with st.spinner("Logging in..."):
                try:
                    # Sign in and get session
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    
                    # Store session in Streamlit session state
                    st.session_state["user"] = res.user
                    st.session_state["session"] = res.session
                    
                    # Store session in browser storage
                    st.session_state["auth_token"] = res.session.access_token
                    st.session_state["refresh_token"] = res.session.refresh_token
                    
                    st.success("Logged in successfully!")
                    st.rerun()
                except Exception as e:
                    error_msg = str(e).lower()
                    if "invalid login" in error_msg:
                        st.error("Invalid email or password")
                    elif "network" in error_msg or "connection" in error_msg:
                        st.error("Connection failed. Please check your Supabase configuration.")
                    else:
                        st.error(f"Login failed: {str(e)}")
    
    with tab2:
        st.subheader("Create Account")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("✨ Sign Up", use_container_width=True):
            if not email or not password or not confirm_password:
                st.error("Please fill in all fields")
                return
                
            if password != confirm_password:
                st.error("Passwords do not match")
                return
                
            if len(password) < 6:
                st.error("Password must be at least 6 characters long")
                return
                
            with st.spinner("Creating account..."):
                try:
                    res = supabase.auth.sign_up({"email": email, "password": password})
                    st.success("Account created! Please check your email to verify your account.")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "already registered" in error_msg:
                        st.error("This email is already registered")
                    elif "network" in error_msg or "connection" in error_msg:
                        st.error("Connection failed. Please check your Supabase configuration in .env")
                    else:
                        st.error(f"Sign up failed: {str(e)}")

def logout():
    """Handle user logout"""
    if st.button("🚪 Logout"):
        with st.spinner("Logging out..."):
            # Clear all auth-related session state
            for key in ["user", "session", "auth_token", "refresh_token"]:
                if key in st.session_state:
                    st.session_state.pop(key)
            
            # Sign out from Supabase
            supabase.auth.sign_out()
            st.rerun()

def check_auth():
    """Always check the Supabase session for authentication, per user/browser."""
    try:
        # Always check Supabase session on every request
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state['user'] = session.user
            st.session_state['session'] = session
            return True
        else:
            # No valid session, show login
            login_form()
            st.stop()
    except Exception as e:
        print(f"Error checking auth: {str(e)}")
        login_form()
        st.stop()
    return True