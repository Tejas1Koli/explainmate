import streamlit as st
import requests
import re

# --- CONFIG ---
st.set_page_config(page_title="ExplainMate AI", layout="centered")
openrouter_api_key = st.secrets["OPENROUTER_API_KEY"] if "OPENROUTER_API_KEY" in st.secrets else "your-api-key-here"

# --- UI ---
st.title("🧠 ExplainMate AI")
st.subheader("Get clear, structured explanations with LaTeX rendering")

query = st.text_input("Enter a concept or question", placeholder="e.g. What is dot product?")
mode = st.selectbox("Choose explanation type", ["Simple", "Technical"])

#prompt style
def generate_system_prompt(style):
    prompt = (
        "You are a helpful tutor who explains concepts step-by-step.\n"
        "- Use LaTeX for all math expressions.\n"
        "- Always wrap math content inside triple backticks like this: ```latex ... ```.\n"
        "- Avoid using inline LaTeX like $...$ or $$...$$.\n"
        "- Add examples with solved steps.\n"
        "- Always use mathematical equations or expressions when user ask maths related concepts.\n"
    )
    if style == "Technical":
        prompt += (
            "- Use proper mathematical terminology, symbols, and stepwise derivation.\n"
            "- Make sure every equation is inside a code block.\n"
            "- Do not use plain text math like 2^2 or x_1. Always wrap it in ```latex ... ```.\n"
        )
    else:
        prompt += "- Keep it beginner-friendly with simple words but use mathematical expression when needed.\n"
    return prompt


# --- API Call Function ---
def get_explanation(prompt, style):
    system_prompt = generate_system_prompt(style)
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "nvidia/llama-3.1-nemotron-nano-8b-v1:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"Error: Could not generate explanation. Status: {response.status_code}. Response: {response.text}"

# --- Cache Wrapper ---
@st.cache_data(show_spinner=False)
def cached_explanation(prompt, style):
    return get_explanation(prompt, style)

# --- Markdown Cleaner ---
def clean_italics(text):
    parts = re.split(r'(\$.*?\$|\$\$.*?\$\$)', text)
    for i, part in enumerate(parts):
        if not (part.startswith('$') and part.endswith('$')) and not (part.startswith('$$') and part.endswith('$$')):
            part = re.sub(r'(?<!\*)\*(?!\*)', '', part)
            part = re.sub(r'(?<!_)_(?!_)', '', part)
            parts[i] = part
    return ''.join(parts)

# --- LaTeX Block Renderer ---
def render_latex_blocks(text):
    # Match code blocks with 2 or more backticks, optional spaces, and latex (case-insensitive)
    pattern = re.compile(r'`{2,}\s*[lL][aA][tT][eE][xX]\s*([\s\S]*?)`{2,}', re.MULTILINE)
    pos = 0
    remaining_text = ""
    for match in pattern.finditer(text):
        if match.start() > pos:
            remaining_text += text[pos:match.start()]
        st.latex(match.group(1).strip())
        pos = match.end()
    if pos < len(text):
        remaining_text += text[pos:]
    return remaining_text

# --- Inline LaTeX Renderer ---
def render_inline_latex(text):
    parts = re.split(r'(\$\$.*?\$\$|\$.*?\$)', text)
    for part in parts:
        part = part.strip()
        if part.startswith("$$") and part.endswith("$$"):
            st.latex(part[2:-2].strip())
        elif part.startswith("$") and part.endswith("$"):
            st.latex(part[1:-1].strip())
        elif part:
            st.markdown(part, unsafe_allow_html=True)

# --- Display Output ---
if query:
    with st.spinner("Generating explanation..."):
        output = cached_explanation(query, mode)
    st.markdown("### 📘 Explanation")

    try:
        output = clean_italics(output)
        clean_text = render_latex_blocks(output)
        render_inline_latex(clean_text)
    except Exception as e:
        st.error("Error rendering content. Showing raw output.")
        st.code(output)

    with st.expander("Show raw LaTeX code"):
        st.code(output)

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ by Tejas · [GitHub](https://github.com/Tejas1Koli)")
