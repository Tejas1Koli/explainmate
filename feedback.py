import streamlit as st
from datetime import datetime
from supabase_config import supabase, get_user_id

def submit_feedback(message: str, is_helpful: bool) -> bool:
    """Submit feedback to Supabase.
    
    Args:
        message: User's feedback message
        is_helpful: Whether feedback was marked helpful
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        user_id = get_user_id()
        
        data = {
            "user_id": user_id,
            "message": message,
            "is_helpful": is_helpful,
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase.table('feedback').insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Failed to submit feedback: {str(e)}")
        return False

def feedback_component():
    """Streamlit component for collecting feedback."""
    with st.form("feedback_form"):
        feedback_text = st.text_area("Your feedback (optional)", 
                                   placeholder="What did you like or dislike?")
        
        col1, col2 = st.columns(2)
        with col1:
            helpful = st.form_submit_button("👍 Helpful")
        with col2:
            not_helpful = st.form_submit_button("👎 Not Helpful")
        
        if helpful or not_helpful:
            success = submit_feedback(
                message=feedback_text,
                is_helpful=helpful
            )
            if success:
                st.success("Thank you for your feedback!")
            return True
    return False
