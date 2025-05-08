import json
import requests
import pandas as pd
from google.oauth2 import service_account
import streamlit as st
from pyairtable import Table

def get_structured_explanation(prompt, style, api_key, stream_callback=None):
    headers = {
        "HTTP-Referer": "https://explainmate.streamlit.app",
        "Authorization": f"Bearer {api_key}"
    }

    system_prompt = """You are an expert tutor that explains concepts clearly and precisely. 
    When explaining mathematical concepts:
    important = Never show your thought process, reasoning steps, or any chain-of-thought. Only output the final explanation in clear paragraphs.
    1. Write in a discrete paragraph format, do not output your thought process
    2. For mathematical formulas, enclose them in ```latex ... ``` tags
    3. use separate blocks or bullet points
    4. Keep explanations flowing naturally with formulas with latex.
    5. Use proper LaTeX syntax for formulas
    when explaining other concepts:
    6. Use clear and detailed explaination with headings and points
    7. Avoid jargon and complex terms
    8. Provide examples and analogies to illustrate points
    9. Use simple language and focus on intuitive understanding
    10. Keep explanations flowing naturally with examples integrated into the text
    11. explain in just 512 tokens"""

    if style == "Technical":
        system_prompt += "\nUse technical language and provide detailed mathematical explanations."
    else:
        system_prompt += "\nUse simple language and focus on intuitive understanding."

    data = {
        "model": "nvidia/llama-3.3-nemotron-super-49b-v1:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Explain this concept: {prompt}"}
        ],
        "temperature": 0.4,
        "max_tokens": 800,
        "stream": True if stream_callback else False
    }

    # Streaming logic
    if stream_callback:
        try:
            with requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                stream=True,
                timeout=60
            ) as response:
                response.raise_for_status()
                buffer = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.startswith('data: '):
                        payload = line[6:]
                        if payload.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(payload)
                            delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                buffer += delta
                                # Streamlit UI update: accumulate and update placeholder
                                stream_callback(delta)
                                st.experimental_rerun()  # Force Streamlit to update UI after each chunk
                        except Exception:
                            continue
                return buffer if buffer else None
        except Exception:
            # Fallback to normal (non-streaming) mode
            pass
    # Fallback: normal response
    try:
        data["stream"] = False
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def log_feedback(airtable_api_key, base_id, table_name, query, explanation, feedback, timestamp):
    try:
        # Only use the date part (YYYY-MM-DD) for the timestamp field
        date_only = timestamp.split("T")[0] if "T" in timestamp else timestamp
        table = Table(airtable_api_key, base_id, table_name)
        table.create({
            "timestamp": date_only,
            "query": query,
            "explanation": explanation,
            "feedback": feedback
        })
    except Exception as e:
        print(f"Error logging feedback to Airtable: {str(e)}")
