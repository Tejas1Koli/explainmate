import streamlit as st
from supabase import create_client, Client

# Get Supabase credentials from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Failed to initialize Supabase client. Please check your credentials in secrets.toml. Error: {str(e)}")
    st.stop()

def init_session():
    """Initialize or restore user session"""
    try:
        # Check if we have a stored session first
        if 'user' in st.session_state and st.session_state['user']:
            return True
            
        # Try to get session from Supabase
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state['user'] = session.user
            st.session_state['session'] = session
            return True
            
        return False
    except Exception as e:
        print(f"Error initializing session: {str(e)}")
        return False


def get_user_id():
    """Get the current user's ID from the session"""
    try:
        if 'user' in st.session_state and st.session_state['user']:
            return st.session_state['user'].id
            
        # Try to initialize session if not present
        if init_session():
            return st.session_state['user'].id
            
        return None
    except Exception as e:
        print(f"Error getting user ID: {str(e)}")
        return None


def refresh_session():
    """Refresh the user's session if needed"""
    try:
        if 'session' in st.session_state:
            # Get fresh session
            session = supabase.auth.get_session()
            if session:
                # Update session in session state
                st.session_state['session'] = session
                return True
        return False
    except Exception as e:
        print(f"Error refreshing session: {str(e)}")
        return False

# Initialize session when module is imported
init_session()