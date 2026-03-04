# Please install OpenAI SDK first: `pip3 install openai`
import os
import openai
import streamlit as st

st.title("DeepSleek Chat")
client = openai.OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="")