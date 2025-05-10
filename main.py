import streamlit as st
import re
import requests
import datetime
from functions import get_structured_explanation, log_feedback
from notes import save_note, load_notes, delete_note, update_note
from image_processing import extract_text_from_image
from export_notes import export_notes_to_pdf
from auth import check_auth, logout

# --- CONFIG ---
st.set_page_config(page_title="ExplainMate AI", layout="wide")
openrouter_api_key = st.secrets["OPENROUTER_API_KEY"] if "OPENROUTER_API_KEY" in st.secrets else "your-api-key-here"
airtable_api_key = st.secrets["AIRTABLE_API_KEY"]
airtable_base_id = st.secrets["AIRTABLE_BASE_ID"]
airtable_table_name = st.secrets["AIRTABLE_TABLE_NAME"]

# Check authentication before proceeding
check_auth()

# Add user info and logout in the top right
col_main, col_user, col_btn = st.columns([4, 1, 1])
with col_user:
    st.write(f"👤 {st.session_state['user'].email}")
with col_btn:
    if st.button("📝 View Notes"):
        st.session_state["show_notes_window"] = True
    logout()

# Show notes window if requested
if st.session_state.get("show_notes_window", False):
    st.title("📝 Saved Notes")
    notes = load_notes()
    if notes:
        for note in notes:
            with st.expander(f"📌 {note['content'][:50]}..."):
                st.write(note['content'])
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"🗑️ Delete", key=f"delete_{note['id']}"):
                        if delete_note(note['id']):
                            st.rerun()
                with col2:
                    pdf_bytes = export_notes_to_pdf([note])
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"note_{note['id']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{note['id']}")
    else:
        st.info("No saved notes yet")
    if st.button("Close"):
        st.session_state["show_notes_window"] = False
        st.rerun()

if not st.session_state.get("main_content_hidden", False):
    st.title("🧠 ExplainMate AI")
    st.subheader("Get clear, comprehensive explanations")

    # Add image upload option
    tab1, tab2 = st.tabs(["📝 Text Input", "📷 Upload Image"])

    with tab1:
        # Initialize all session state variables
        if 'last_output' not in st.session_state:
            st.session_state.last_output = ""
        if 'last_query' not in st.session_state:
            st.session_state.last_query = ""
        if 'input_reset' not in st.session_state:
            st.session_state.input_reset = False

        # Display previous output if exists
        if st.session_state.last_output:
            st.markdown(st.session_state.last_output)

        # Handle query input with preserved state
        query = st.text_input(
            "Enter a concept or question",
            value=st.session_state.last_query if not st.session_state.input_reset else "",
            key="query_input"
        )
        
        # Reset the input reset flag after using it
        if st.session_state.input_reset:
            st.session_state.input_reset = False

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
                                st.session_state.last_output = output
                                st.session_state.last_query = query
                                st.session_state.input_reset = True  # Will clear input on next render
                                st.rerun()
                            else:
                                st.error("Failed to save note. Please try again.")



                    # Show warning if note_content exists but is empty (after save attempt)
                    if note_content is not None and not note_content.strip():
                        st.warning("Please enter some content for your note.")

                    # Feedback section
                    st.markdown("---")
                    from feedback import feedback_component
                    feedback_component()

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    st.markdown("---")
    st.markdown("Made with ❤️ by Tejas · ")
