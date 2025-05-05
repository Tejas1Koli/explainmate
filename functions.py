import json
import requests
import pandas as pd
from google.oauth2 import service_account
import streamlit as st
from pyairtable import Table

def get_structured_explanation(prompt, style, api_key):
    headers = {
        "HTTP-Referer": "https://explainmate.streamlit.app",
        "Authorization": f"Bearer {api_key}"
    }

    system_prompt = """You are an expert tutor that explains concepts clearly and precisely. 
    When explaining mathematical concepts:
    1. Write in a continuous paragraph format
    2. For mathematical formulas, enclose them in ```latex ... ``` tags
    3. use separate blocks or bullet points
    4. Keep explanations flowing naturally with formulas with latex.
    5. Use proper LaTeX syntax for formulas
    when explaining other concepts:
    1. Use clear and detailed explaination with headings and points
    2. Avoid jargon and complex terms
    3. Provide examples and analogies to illustrate points
    4. Use simple language and focus on intuitive understanding
    5. Keep explanations flowing naturally with examples integrated into the text"""

    if style == "Technical":
        system_prompt += "\nUse technical language and provide detailed mathematical explanations."
    else:
        system_prompt += "\nUse simple language and focus on intuitive understanding."

    data = {
        "model": "deepseek/deepseek-prover-v2:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Explain this concept: {prompt}"}
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }

    try:
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
