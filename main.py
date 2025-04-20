import streamlit as st
import requests


# --- CONFIG ---
st.set_page_config(page_title="ExplainMate AI", layout="centered")
openrouter_api_key = st.secrets["OPENROUTER_API_KEY"] if "OPENROUTER_API_KEY" in st.secrets else "your-api-key-here"

# --- UI ---
st.title("🧠 ExplainMate AI")
st.subheader("Get clear, structured explanations with LaTeX rendering")

query = st.text_input("Enter a concept or question", placeholder="e.g. What is dot product?")
mode = st.selectbox("Choose explanation type", ["Simple", "Technical"])

# --- API Call Function ---
def get_explanation(prompt, style):
    system_prompt = f"You are a helpful tutor. Give a clear, step by step explanation of the following concept.Use LaTeX where needed."
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gmoonshotai/kimi-vl-a3b-thinking:free",  # Use a direct instruct/chat model
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return "Error: Could not generate explanation."

# --- Display Output ---
if query:
    with st.spinner("Generating explanation..."):
        output = get_explanation(query, mode)
    st.markdown("### 📘 Explanation")
    try:
        # 1. Fix malformed LaTeX: \left$...\right$ -> \left(...\right)
        output = re.sub(r'\\left\$(.*?)\\right\$', lambda m: f'\\left({m.group(1).strip()}\\right)', output)
        # 2. Convert (( ... )) and \( ... \) to $ ... $
        output = re.sub(r'\(\((.*?)\)\)', lambda m: f'${m.group(1).strip()}$', output)
        output = re.sub(r'\\\((.*?)\\\)', lambda m: f'${m.group(1).strip()}$', output)
        # 3. Convert ( ... ) with LaTeX commands to $ ... $
        output = re.sub(r'\(([^\)]*(?:\\sqrt|\\frac|\\cdot|\\mathbf|\\text|\\sum|\\int|\\Rightarrow|\\leq|\\geq|\\neq|\\approx|\\alpha|\\beta|\\gamma|\\theta|\\lambda|\\pi|\\infty|\\dots)[^\)]*)\)', lambda m: f'${m.group(1).strip()}$', output)
        # 4. Convert $\(...\)$ to $...$ (remove escaped parens)
        output = re.sub(r'\$\\\((.*?)\\\)\$', lambda m: f'${m.group(1).strip()}$', output)
        # 5. Convert $\[...\]$ to $$...$$ (block math)
        output = re.sub(r'\$\\\[(.*?)\\\]\$', lambda m: f'$$ {m.group(1).strip()} $$', output, flags=re.DOTALL)
        # 6. Convert $$...$$ and \[...\] to st.latex blocks
        block_latex = re.compile(r'(\$\$.*?\$\$|\\\[.*?\\\])', re.DOTALL)
        pos = 0
        for match in block_latex.finditer(output):
            if match.start() > pos:
                st.markdown(output[pos:match.start()], unsafe_allow_html=True)
            latex_code = match.group(0)
            if latex_code.startswith('$$'):
                latex_code = latex_code.strip('$$')
            elif latex_code.startswith('\\['):
                latex_code = latex_code[2:-2]
            st.latex(latex_code.strip())
            pos = match.end()
        if pos < len(output):
            st.markdown(output[pos:], unsafe_allow_html=True)
    except Exception as e:
        st.error("Error rendering content. Showing raw output.")
        st.code(output)
    with st.expander("Show raw LaTeX code"):
        st.code(output)

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ by Tejas · [GitHub](https://github.com/Tejas1Koli)")


