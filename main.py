import streamlit as st
import re
import requests
import datetime
from functions import get_structured_explanation, log_feedback
from notes import save_note, load_notes, delete_note
from image_processing import extract_text_from_image

# --- CONFIG ---
st.set_page_config(page_title="ExplainMate AI", layout="wide")
openrouter_api_key = st.secrets["OPENROUTER_API_KEY"] if "OPENROUTER_API_KEY" in st.secrets else "your-api-key-here"
airtable_api_key = st.secrets["AIRTABLE_API_KEY"]
airtable_base_id = st.secrets["AIRTABLE_BASE_ID"]
airtable_table_name = st.secrets["AIRTABLE_TABLE_NAME"]

# Sidebar for displaying saved notes
with st.sidebar:
    st.header("📝 Saved Notes")
    notes = load_notes()
    if notes:
        for idx, note in enumerate(notes):
            with st.expander(f"📌 {note['question'][:50]}..."):
                st.write(f"**Date:** {note['timestamp']}")
                st.write(note['content'])
                if st.button("🗑️ Delete", key=f"delete_{idx}"):
                    if delete_note(idx):
                        st.rerun()
    else:
        st.info("No saved notes yet. Your notes will appear here.")

# Main content area
st.title("🧠 ExplainMate AI")
st.subheader("Get clear, comprehensive explanations")

# Add image upload option
tab1, tab2 = st.tabs(["📝 Text Input", "📷 Upload Image"])

with tab1:
    query = st.text_input("Enter a concept or question", placeholder="e.g. What is dot product?")

with tab2:
    uploaded_image = st.file_uploader("Upload handwritten notes or image", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        try:
            extracted_text = extract_text_from_image(uploaded_image)
            if extracted_text:
                query = st.text_area("Extracted text (edit if needed):", value=extracted_text)
            else:
                st.warning("Couldn't extract text from image. Please try another image or enter text manually.")
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

mode = st.selectbox("Choose explanation type", ["Simple", "Technical"])

# --- Cache Wrapper ---
@st.cache_data(show_spinner=False)
def cached_explanation(prompt, style, api_key):
    return get_structured_explanation(prompt, style, api_key)

# --- Display Output ---
if query:
    with st.spinner("Thinking..."):
        try:
            output = cached_explanation(query, mode, openrouter_api_key)
            if not output:
                st.error("Could not generate explanation. Please try again.")
                with st.expander("Debug Information"):
                    st.info("• API Key: ✓ Found in secrets.toml\n• Model: gryphe/mythomist-7b:free\n• Status: Failed to get response")
            else:
                # Process the text with inline LaTeX
                current_text = ""
                latex_pattern = r'```latex\s*([\s\S]*?)```'
                last_end = 0
                
                for match in re.finditer(latex_pattern, output):
                    current_text += output[last_end:match.start()].strip()
                    if current_text:
                        st.write(current_text)
                        current_text = ""
                    latex_content = match.group(1).strip()
                    st.latex(latex_content)
                    last_end = match.end()
                
                remaining_text = output[last_end:].strip()
                if remaining_text:
                    st.write(remaining_text)

                # Notes section
                st.markdown("---")
                st.subheader("📝 Take Notes")
                note_content = st.text_area("Your notes for this concept:", height=150)
                if st.button("💾 Save Note"):
                    if note_content.strip():
                        if save_note(query, note_content):
                            st.success("Note saved successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to save note. Please try again.")
                    else:
                        st.warning("Please enter some content for your note.")

                # Feedback section
                st.markdown("---")
                col1, col2 = st.columns(2)
                feedback = None
                with col1:
                    if st.button("👍 Helpful"):
                        feedback = "helpful"
                with col2:
                    if st.button("👎 Not Helpful"):
                        feedback = "not helpful"

                if feedback:
                    timestamp = datetime.datetime.now().isoformat()
                    log_feedback(
                        airtable_api_key,
                        airtable_base_id,
                        airtable_table_name,
                        query,
                        output,
                        feedback,
                        timestamp
                    )
                    st.success("Feedback logged! Thank you.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

st.markdown("---")
st.markdown("Made with ❤️ by Tejas · [GitHub](https://github.com/Tejas1Koli)")
