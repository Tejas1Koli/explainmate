import json
import os
from datetime import datetime

NOTES_FILE = "saved_notes.json"

def save_note(question, note_content):
    """Save a note with the given question and content (as bullet points)"""
    try:
        notes = load_notes()
        # Split content into bullet points (ignore empty lines)
        points = [line.strip() for line in note_content.split('\n') if line.strip()]
        note_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "content": points
        }
        notes.append(note_entry)
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
                notes = json.load(f)
                # Backward compatibility: convert string content to list
                for note in notes:
                    if isinstance(note.get("content"), str):
                        note["content"] = [line.strip() for line in note["content"].split('\n') if line.strip()]
                return notes
        return []
    except Exception as e:
        print(f"Error loading notes: {str(e)}")
        return []

def update_note(index, new_content):
    """Update a note's content by its index (as bullet points)"""
    try:
        notes = load_notes()
        if 0 <= index < len(notes):
            points = [line.strip() for line in new_content.split('\n') if line.strip()]
            notes[index]["content"] = points
            with open(NOTES_FILE, 'w') as f:
                json.dump(notes, f, indent=4)
            return True
        return False
    except Exception as e:
        print(f"Error updating note: {str(e)}")
        return False

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