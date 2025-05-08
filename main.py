import streamlit as st
import re
import requests
import datetime
from functions import get_structured_explanation, log_feedback
from notes import save_note, load_notes, delete_note
from image_processing import extract_text_from_image
from export_notes import export_notes_to_pdf

def show_notes_window():
    notes = load_notes()
    if notes:
        st.title("📝 Saved Notes")
        for idx, note in enumerate(notes):
            st.subheader(f"📌 {note['question'][:50]}...")
            st.write(f"**Date:** {note['timestamp']}")
            # Edit mode state
            edit_key = f"edit_{idx}"
            if st.session_state.get(edit_key, False):
                # Show editable text area with current note content as lines
                current_content = "\n".join(note['content'])
                new_content = st.text_area("Edit note (one point per line):", value=current_content, key=f"edit_area_{idx}")
                col_save, col_cancel = st.columns([1, 1])
                with col_save:
                    if st.button("💾 Save", key=f"save_{idx}"):
                        from notes import update_note
                        if update_note(idx, new_content):
                            st.success("Note updated!")
                            st.session_state[edit_key] = False
                            st.rerun()
                        else:
                            st.error("Failed to update note.")
                with col_cancel:
                    if st.button("Cancel", key=f"cancel_{idx}"):
                        st.session_state[edit_key] = False
                        st.rerun()
            else:
                # Show note as bullet points
                st.markdown("<ul>" + "".join([f"<li>{point}</li>" for point in note['content']]) + "</ul>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    pdf_bytes = export_notes_to_pdf([note])
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"note_{idx+1}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{idx}"
                    )
                with col2:
                    if st.button("✏️ Edit", key=f"edit_btn_{idx}"):
                        st.session_state[edit_key] = True
                        st.rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        if delete_note(idx):
                            st.session_state["show_notes_window"] = False
                            st.session_state["main_content_hidden"] = False
                            st.session_state["reload"] = True
                            st.rerun()
    else:
        st.info("No saved notes yet. Your notes will appear here.")

# --- CONFIG ---
st.set_page_config(page_title="ExplainMate AI", layout="wide")
openrouter_api_key = st.secrets["OPENROUTER_API_KEY"] if "OPENROUTER_API_KEY" in st.secrets else "your-api-key-here"
airtable_api_key = st.secrets["AIRTABLE_API_KEY"]
airtable_base_id = st.secrets["AIRTABLE_BASE_ID"]
airtable_table_name = st.secrets["AIRTABLE_TABLE_NAME"]

# Remove sidebar and add View Notes button to main area (top right)
col_main, col_btn = st.columns([6, 1])
with col_btn:
    if st.button("📝 View Notes"):
        st.session_state["show_notes_window"] = True
        st.session_state["main_content_hidden"] = True
        st.rerun()

if st.session_state.get("show_notes_window", False):
    show_notes_window()
    if st.button("⬅️ Back to Main App"):
        st.session_state["show_notes_window"] = False
        st.session_state["main_content_hidden"] = False
        st.rerun()
    st.stop()

# Main content area (only show if not viewing notes)
if not st.session_state.get("main_content_hidden", False):
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
