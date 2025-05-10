from datetime import datetime
from supabase_config import supabase, get_user_id, refresh_session

def handle_auth_error(func):
    """Decorator to handle authentication errors and session refresh"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "JWT" in str(e) or "authentication" in str(e).lower():
                # Try to refresh the session
                if refresh_session():
                    # Retry the operation
                    return func(*args, **kwargs)
            raise
    return wrapper

@handle_auth_error
def save_note(question, note_content):
    """Save a note with the given question and content"""
    try:
        user_id = get_user_id()
        if not user_id:
            raise Exception("User not authenticated")
            
        note_entry = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "content": note_content.strip()
        }
        
        result = supabase.table('notes').insert(note_entry).execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"Error saving note: {str(e)}")
        return False

@handle_auth_error
def load_notes():
    """Load all saved notes for the current user"""
    try:
        user_id = get_user_id()
        if not user_id:
            return []
            
        result = supabase.table('notes')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
            
        return result.data if result.data else []
    except Exception as e:
        print(f"Error loading notes: {str(e)}")
        return []

@handle_auth_error
def update_note(note_id, new_content):
    """Update a note's content by its ID (as bullet points)"""
    try:
        user_id = get_user_id()
        if not user_id:
            raise Exception("User not authenticated")
            
        points = [line.strip() for line in new_content.split('\n') if line.strip()]
        result = supabase.table('notes')\
            .update({"content": points})\
            .eq('id', note_id)\
            .eq('user_id', user_id)\
            .execute()
            
        return len(result.data) > 0
    except Exception as e:
        print(f"Error updating note: {str(e)}")
        return False

@handle_auth_error
def delete_note(note_id):
    """Delete a note by its ID"""
    try:
        user_id = get_user_id()
        if not user_id:
            raise Exception("User not authenticated")
            
        result = supabase.table('notes')\
            .delete()\
            .eq('id', note_id)\
            .eq('user_id', user_id)\
            .execute()
            
        return len(result.data) > 0
    except Exception as e:
        print(f"Error deleting note: {str(e)}")
        return False