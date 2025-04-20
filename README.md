# ExplainMate AI

ExplainMate AI is a Streamlit web app that provides clear, structured explanations for math and science concepts, with support for LaTeX rendering. Just enter a question or concept, and get an instant, well-formatted answer powered by a large language model (LLM).

## Features
- Simple and technical explanation modes
- Beautiful LaTeX rendering for math formulas
- Easy-to-use web interface
- Powered by OpenRouter LLM API (bring your own API key)

## How to Run
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "explain mate"
   ```
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv explainmate
   source explainmate/bin/activate
   ```
3. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set your OpenRouter API key:**
   - Create a file at `.streamlit/secrets.toml` with this content:
     ```toml
     OPENROUTER_API_KEY = "your-api-key-here"
     ```
5. **Run the app:**
   ```bash
   streamlit run main.py
   ```

## File Structure
- `main.py` — Main Streamlit app
- `requirements.txt` — Python dependencies
- `README.md` — This file
- `.streamlit/secrets.toml` — Your API key (not committed)
- `explainmate/` — Python virtual environment (not committed)

## Notes
- Do **not** commit your API key or the `explainmate/` folder to GitHub.
- For best results, use a modern browser.

## License
MIT License

---
Made with ❤️ by Tejas
