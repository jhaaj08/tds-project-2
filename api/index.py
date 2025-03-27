# main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import zipfile
import pandas as pd
from io import BytesIO
import httpx

app = FastAPI()

# === AI Proxy Configuration ===
AIPROXY_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjEwMDU3NDVAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.QIzF-en4LaXJxOYQgwh9W1dgvn1QvLJL6_40g98vZU0"

# === Helper: LLM Query Function ===
async def query_llm(question: str) -> str:
    headers = {
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for Data Science assignments."},
            {"role": "user", "content": question}
        ],
        "temperature": 0
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(AIPROXY_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

# === API Endpoint ===
@app.post("/api/")
async def get_answer(question: str = Form(...), file: UploadFile = File(None)):
    # Case 1: File is uploaded (zip with CSV)
    if file:
        try:
            contents = await file.read()
            with zipfile.ZipFile(BytesIO(contents)) as z:
                for filename in z.namelist():
                    if filename.endswith(".csv"):
                        with z.open(filename) as f:
                            df = pd.read_csv(f)
                            if "answer" in df.columns:
                                return {"answer": str(df["answer"].iloc[0])}
                            else:
                                return {"answer": "No 'answer' column found in CSV."}
                return {"answer": "No CSV file found inside the ZIP."}
        except Exception as e:
            return {"answer": f"Error processing file: {str(e)}"}

    # Case 2: Text-only question → use LLM
    try:
        llm_answer = await query_llm(question)
        return {"answer": llm_answer}
    except Exception as e:
        return {"answer": f"LLM Error: {str(e)}"}