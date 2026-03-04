import os
import streamlit as st
from openai import OpenAI

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DeepSleek Chat",
    page_icon="💬",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap');

/* ── Reset & base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e4dc !important;
    font-family: 'DM Mono', monospace !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

/* ── Main container ── */
.main .block-container {
    max-width: 760px !important;
    padding: 2rem 1.5rem 6rem !important;
}

/* ── Title ── */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
    letter-spacing: -0.03em !important;
    color: #e8e4dc !important;
    margin-bottom: 0.2rem !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
}

/* User bubble */
[data-testid="stChatMessage"][data-testid*="user"],
div[data-testid="stChatMessageContent"]:has(~ div[aria-label="user avatar"]) {
    background: transparent !important;
}

.stChatMessage {
    gap: 0.75rem !important;
}

/* Avatar */
[data-testid="stChatMessageAvatarUser"] > div,
[data-testid="stChatMessageAvatarAssistant"] > div {
    background: #1a1a24 !important;
    border: 1px solid #2a2a38 !important;
    border-radius: 6px !important;
    font-size: 0.75rem !important;
}

/* Message content area */
[data-testid="stChatMessageContent"] {
    background: #13131c !important;
    border: 1px solid #222230 !important;
    border-radius: 10px !important;
    padding: 0.85rem 1.1rem !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    color: #ddd8ce !important;
}

/* ── Input bar ── */
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
    caret-color: #7b6ef6 !important;
}

[data-testid="stChatInputContainer"] textarea:focus {
    border-color: #7b6ef6 !important;
    box-shadow: 0 0 0 2px rgba(123,110,246,0.15) !important;
    outline: none !important;
}

[data-testid="stChatInputContainer"] button {
    background: #7b6ef6 !important;
    border-radius: 8px !important;
    border: none !important;
}

[data-testid="stChatInputContainer"] button:hover {
    background: #9585ff !important;
}

/* ── Sidebar ── */
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
    text-align: left !important;
    transition: border-color 0.15s !important;
}

[data-testid="stSidebar"] button:hover {
    border-color: #7b6ef6 !important;
    background: #1e1e2e !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a38; border-radius: 4px; }

/* ── Accent tag ── */
.model-tag {
    display: inline-block;
    background: #1a1a26;
    border: 1px solid #7b6ef6;
    color: #7b6ef6;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 0.5rem;
    vertical-align: middle;
}

/* ── Thinking spinner ── */
.thinking {
    color: #555566;
    font-size: 0.8rem;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙ Settings")

    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=os.environ.get("DEEPSEEK_API_KEY", ""),
        placeholder="sk-...",
        help="Get your key at platform.deepseek.com",
    )

    model = st.selectbox(
        "Model",
        ["deepseek-chat", "deepseek-reasoner"],
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
        "Powered by DeepSeek API</div>",
        unsafe_allow_html=True,
    )


# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown(
    f'<h1>DeepSleek Chat <span class="model-tag">{model}</span></h1>',
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render history ────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Send a message…"):

    if not api_key:
        st.error("⚠ Please enter your DeepSeek API key in the sidebar.")
        st.stop()

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build message list for the API
    api_messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Stream assistant response
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=temperature,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"❌ Error: {e}"
            placeholder.markdown(full_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )