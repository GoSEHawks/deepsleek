import os
import streamlit as st
import transformers

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
if "HF_TOKEN" not in st.secrets:
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

hf_token = st.secrets["HF_TOKEN"]

# Set the token as an environment variable — this is the safest approach.
# It avoids calling whoami/login (which throws on expired tokens) while still
# authenticating every HuggingFace download automatically.
os.environ["HF_TOKEN"] = hf_token


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙ Settings")

    st.markdown("**Model ID**")
    st.markdown(
        "[🔗 Browse trending models on HuggingFace →](https://huggingface.co/models?library=transformers&sort=trending)"
    )
    model_name = st.text_input(
        "Model ID",
        value="microsoft/phi-2",
        placeholder="e.g. mistralai/Mistral-7B-Instruct-v0.2",
        label_visibility="collapsed",
        help="Paste any text-generation model ID from HuggingFace.",
    )
    if not model_name.strip():
        model_name = "microsoft/phi-2"
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
    import transformers
    return transformers.pipeline("text-generation", model=model_id)


# Bust the cache only when the model ID actually changes
if st.session_state.get("loaded_model_name") != model_name:
    st.session_state.pop("loaded_model", None)

if "loaded_model" not in st.session_state:
    with st.spinner(f"Loading **{short_name}** — this may take a minute on first run…"):
        try:
            st.session_state.loaded_model = load_pipeline(model_name)
            st.session_state.loaded_model_name = model_name
        except Exception as e:
            err = str(e)
            if "401" in err or "Unauthorized" in err or "expired" in err or "invalid" in err.lower():
                st.error(
                    "**HF_TOKEN is expired or invalid.**\n\n"
                    "Please update your token:\n"
                    "1. Generate a new token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)\n"
                    "2. Update `HF_TOKEN` in your Streamlit **Settings → Secrets**\n"
                    "3. Restart the app.",
                    icon="🔑",
                )
            elif "403" in err or "gated" in err.lower() or "access" in err.lower():
                st.error(
                    f"**Access denied for `{model_name}`.**\n\n"
                    "This may be a gated model that requires you to accept its terms first.\n"
                    "Visit the model page on HuggingFace, accept the terms, then try again.",
                    icon="🚫",
                )
            else:
                st.error(f"❌ Failed to load `{model_name}`:\n\n{e}")
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
            # Try chat template first (Zephyr, Mistral-Instruct, Llama-chat etc.)
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

            except Exception as template_err:
                if "chat_template" not in str(template_err):
                    raise template_err

                # Fallback: model has no chat template — flatten to plain text prompt
                prompt = ""
                for m in api_messages:
                    if m["role"] == "system":
                        prompt += f"### System:\n{m['content']}\n\n"
                    elif m["role"] == "user":
                        prompt += f"### User:\n{m['content']}\n\n"
                    elif m["role"] == "assistant":
                        prompt += f"### Assistant:\n{m['content']}\n\n"
                prompt += "### Assistant:\n"

                result = pipe(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                )
                # Strip the echoed prompt — return only the new generated text
                response = result[0]["generated_text"][len(prompt):].strip()

            placeholder.markdown(response)

        except Exception as e:
            response = f"❌ Error during generation: {e}"
            placeholder.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})