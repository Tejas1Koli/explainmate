import json
import os
from datetime import datetime

NOTES_FILE = "saved_notes.json"

def save_note(question, note_content):
    """Save a note with the given question and content"""
    try:
        # Load existing notes
        notes = load_notes()
        
        # Create new note entry
        note_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "content": note_content
        }
        
        # Add new note to the list
        notes.append(note_entry)
        
        # Save back to file
        with open(NOTES_FILE, 'w') as f:
            json.dump(notes, f, indent=4)
        
        return True
    except Exception as e:
        print(f"Error saving note: {str(e)}")
        return False

def load_notes():
    """Load all saved notes"""
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading notes: {str(e)}")
        return []

def delete_note(index):
    """Delete a note by its index"""
    try:
        notes = load_notes()
        if 0 <= index < len(notes):
            notes.pop(index)
            with open(NOTES_FILE, 'w') as f:
                json.dump(notes, f, indent=4)
            return True
        return False
    except Exception as e:
        print(f"Error deleting note: {str(e)}")
        return False