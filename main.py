import os
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HF Chat",
    page_icon="🤗",
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
    caret-color: #f97316 !important;
}
[data-testid="stChatInputContainer"] textarea:focus {
    border-color: #f97316 !important;
    box-shadow: 0 0 0 2px rgba(249,115,22,0.15) !important;
    outline: none !important;
}
[data-testid="stChatInputContainer"] button {
    background: #f97316 !important;
    border-radius: 8px !important;
    border: none !important;
}
[data-testid="stChatInputContainer"] button:hover {
    background: #fb923c !important;
}
[data-testid="stSidebar"] {
    background: #0d0d15 !important;
    border-right: 1px solid #1e1e2a !important;
}
[data-testid="stSidebar"] h2 {
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
    border-color: #f97316 !important;
    background: #1e1e2e !important;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a38; border-radius: 4px; }
.model-tag {
    display: inline-block;
    background: #1a1a26;
    border: 1px solid #f97316;
    color: #f97316;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 0.5rem;
    vertical-align: middle;
}
.hf-note {
    font-size: 0.78rem;
    color: #555566;
    line-height: 1.5;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── Secrets gate — runs before anything else ──────────────────────────────────
try:
    hf_token = st.secrets["HF_TOKEN"]
except (KeyError, FileNotFoundError):
    hf_token = os.environ.get("HF_TOKEN", "")

if not hf_token:
    st.error(
        "**HF_TOKEN is not set.**\n\n"
        "You must add your HuggingFace token as a Streamlit secret before using this app:\n\n"
        "1. Go to your app's **Settings → Secrets** in Streamlit Cloud, "
        "or create `.streamlit/secrets.toml` locally\n"
        "2. Add the line:\n"
        "```toml\nHF_TOKEN = \"hf_your_token_here\"\n```\n"
        "3. Get a token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)\n\n"
        "Then restart the app.",
        icon="🔑",
    )
    st.stop()

# Log in to HuggingFace Hub globally so ALL downloads are authenticated.
# This is the most reliable way — it sets the token at the huggingface_hub
# level rather than relying on it being threaded through every API call.
from huggingface_hub import login as hf_login
hf_login(token=hf_token, add_to_git_credential=False)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙ Settings")

    st.markdown("**Model ID**")
    st.markdown(
        "[🔗 Browse trending models on HuggingFace →](https://huggingface.co/models?library=transformers&sort=trending)"
    )
    model_name = st.text_input(
        "Model ID",
        value="HuggingFaceH4/zephyr-7b-beta",
        placeholder="e.g. mistralai/Mistral-7B-Instruct-v0.2",
        label_visibility="collapsed",
        help="Paste any text-generation model ID from HuggingFace.",
    )
    if not model_name.strip():
        model_name = "HuggingFaceH4/zephyr-7b-beta"
    else:
        model_name = model_name.strip()

    system_prompt = st.text_area(
        "System prompt",
        value="You are a helpful, concise assistant.",
        height=100,
    )

    max_new_tokens = st.slider("Max new tokens", 64, 1024, 256, 32)
    temperature = st.slider("Temperature", 0.01, 2.0, 0.7, 0.05)
    top_p = st.slider("Top-p", 0.1, 1.0, 0.95, 0.05)

    st.divider()

    if st.button("🗑 Clear conversation"):
        st.session_state.messages = []
        st.session_state.pop("loaded_model", None)
        st.rerun()

    if st.button("🔄 Reload model"):
        st.session_state.pop("loaded_model", None)
        st.session_state.pop("loaded_model_name", None)
        st.rerun()

    st.markdown(
        "<div class='hf-note'>Models are downloaded & cached on first load.<br>"
        "Large models (7B+) require a GPU and ~14 GB RAM.<br>"
        "Only <code>text-generation</code> models with a chat template will work correctly.</div>",
        unsafe_allow_html=True,
    )


# ── Title ─────────────────────────────────────────────────────────────────────
short_name = model_name.split("/")[-1] if "/" in model_name else model_name
st.markdown(
    f'<h1>HF Chat <span class="model-tag">{short_name}</span></h1>',
    unsafe_allow_html=True,
)


# ── Load / cache the pipeline ─────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_pipeline(model_id: str):
    """
    Token auth is handled globally via hf_login() above.
    We don't pass the token here to avoid cache-busting on every rerun.
    """
    from transformers import pipeline as hf_pipeline
    import torch

    return hf_pipeline(
        task="text-generation",
        model=model_id,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )


# Bust the cache only when the model ID actually changes
if st.session_state.get("loaded_model_name") != model_name:
    st.session_state.pop("loaded_model", None)

if "loaded_model" not in st.session_state:
    with st.spinner(f"Loading **{short_name}** — this may take a minute on first run…"):
        try:
            st.session_state.loaded_model = load_pipeline(model_name)
            st.session_state.loaded_model_name = model_name
        except Exception as e:
            st.error(f"❌ Failed to load model: {e}")
            st.stop()

pipe = st.session_state.loaded_model


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

    api_messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_thinking…_")

        try:
            result = pipe(
                api_messages,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
            )

            generated = result[0]["generated_text"]

            if isinstance(generated, list):
                assistant_turns = [m for m in generated if m["role"] == "assistant"]
                response = assistant_turns[-1]["content"].strip() if assistant_turns else str(generated)
            else:
                response = generated.strip()

            placeholder.markdown(response)

        except Exception as e:
            response = f"❌ Error during generation: {e}"
            placeholder.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})