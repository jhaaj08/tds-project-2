import openai

openai.api_base = "https://aiproxy.sanand.workers.dev/openai"
openai.api_key = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjEwMDU3NDVAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.QIzF-en4LaXJxOYQgwh9W1dgvn1QvLJL6_40g98vZU0"

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "What is 2 + 2?"}
    ]
)

print(response.choices[0].message.content)