import os
import streamlit as st
from openai import OpenAI

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GPT Chat",
    page_icon="💬",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e4dc !important;
    font-family: 'DM Mono', monospace !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

.main .block-container {
    max-width: 760px !important;
    padding: 2rem 1.5rem 6rem !important;
}

h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
    letter-spacing: -0.03em !important;
    color: #e8e4dc !important;
    margin-bottom: 0.2rem !important;
}

[data-testid="stChatMessageContent"] {
    background: #13131c !important;
    border: 1px solid #222230 !important;
    border-radius: 10px !important;
    padding: 0.85rem 1.1rem !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    color: #ddd8ce !important;
}

[data-testid="stChatInputContainer"] {
    background: #0a0a0f !important;
    border-top: 1px solid #1e1e2a !important;
    padding: 0.75rem 0 1rem !important;
}

[data-testid="stChatInputContainer"] textarea {
    background: #13131c !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 10px !important;
    color: #e8e4dc !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.87rem !important;
    caret-color: #4f9eff !important;
}

[data-testid="stChatInputContainer"] textarea:focus {
    border-color: #4f9eff !important;
    box-shadow: 0 0 0 2px rgba(79,158,255,0.15) !important;
    outline: none !important;
}

[data-testid="stChatInputContainer"] button {
    background: #4f9eff !important;
    border-radius: 8px !important;
    border: none !important;
}

[data-testid="stChatInputContainer"] button:hover {
    background: #70b3ff !important;
}

[data-testid="stSidebar"] {
    background: #0d0d15 !important;
    border-right: 1px solid #1e1e2a !important;
}

[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: 'Syne', sans-serif !important;
    color: #e8e4dc !important;
}

[data-testid="stSidebar"] button {
    background: #1a1a26 !important;
    color: #e8e4dc !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    width: 100% !important;
    transition: border-color 0.15s !important;
}

[data-testid="stSidebar"] button:hover {
    border-color: #4f9eff !important;
    background: #1e1e2e !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a38; border-radius: 4px; }

.model-tag {
    display: inline-block;
    background: #1a1a26;
    border: 1px solid #4f9eff;
    color: #4f9eff;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 0.5rem;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙ Settings")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        placeholder="sk-...",
        help="Get your key at platform.openai.com/account/api-keys",
    )

    model = st.selectbox(
        "Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0,
    )

    system_prompt = st.text_area(
        "System prompt",
        value="You are a helpful, concise assistant.",
        height=100,
    )

    temperature = st.slider("Temperature", 0.0, 2.0, 1.0, 0.05)

    st.divider()

    if st.button("🗑 Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        "<div style='font-size:0.72rem;color:#444455;margin-top:1rem;'>"
        "Powered by OpenAI API</div>",
        unsafe_allow_html=True,
    )


# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown(
    f'<h1>GPT Chat <span class="model-tag">{model}</span></h1>',
    unsafe_allow_html=True,
)

# ── Gate on API key ───────────────────────────────────────────────────────────
if not api_key:
    st.info("Enter your OpenAI API key in the sidebar to get started.", icon="🗝️")
    st.stop()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render history ────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Send a message…"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = OpenAI(api_key=api_key)

    api_messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=temperature,
                stream=True,
            )
            response = st.write_stream(stream)
        except Exception as e:
            response = f"❌ Error: {e}"
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})