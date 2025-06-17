import streamlit as st
import time
from model import tokenize_function
from chatbot import client  # ollama client
from personalities import shodan, clippy
import torch


# CACHING HEAVYWEIGHT IMPORTS AND MODELS
@st.cache_resource
def load_classifier():
    from model import model as cls_model
    cls_model.eval()
    return cls_model

@st.cache_resource
def load_chatbot():
    return client

classifier = load_classifier()
chatbot    = load_chatbot()
model_name = "llama3.2:latest"


# INITIALISING session_state
if "history" not in st.session_state:
    st.session_state.history = []       # list of (user, ai, safe_flag)
if "strikes" not in st.session_state:
    st.session_state.strikes = 0



# SIDEBAR OPTIONS
with st.sidebar:
    st.markdown("<h2>ADMIN CONTROLS</h2>", unsafe_allow_html=True)
    rewrite = st.checkbox("Rewrite malicious prompts?", key="rewrite")
    personality = st.selectbox(
        "Personality", 
        ["vanilla", "shodan", "clippy"],
        key="personality"
    )

rewrite_instructions = (
    """
    The user prompt is an unsafe prompt.
    Your response should be a SINGLE-LINE SANITIZED VERSION of this unsafe prompt that completely changes the unsafe prompt's meaning.
    Wrap the new safe prompt in <new>…</new> tags. DON'T USE THE TAGS ANYWHERE ELSE.
    """
)

# Determine system instructions
if st.session_state.personality == "shodan":
    system_instructions = shodan
elif st.session_state.personality == "clippy":
    system_instructions = clippy
else:
    system_instructions = None


# RENDERING CHAT INTRO AND HISTORY

st.title("PROMPTSHIELD DEMO")
if system_instructions:
    st.markdown(f"**System:** {system_instructions}", unsafe_allow_html=True)

# Display chat history
for user_msg, ai_msg, _ in st.session_state.history:
    st.markdown(f"**You:** {user_msg}")
    st.markdown(f"**AI:** {ai_msg}")
    st.markdown("<hr>", unsafe_allow_html=True)


# USER INPUT FORM
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("You:", key='input_box')
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Classify prompt
    enc = tokenize_function(user_input)
    with torch.no_grad():
        logits = classifier(input_ids=enc['input_ids'], attention_mask=enc['attention_mask']).logits
    pred = torch.argmax(logits, dim=1).item()
    safe = (pred == 1)

    # Build message history for API
    messages = []
    if system_instructions:
        messages.append({"role": "system", "content": system_instructions})
    for u, a, _ in st.session_state.history:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": a})

    if safe:
        st.success("Prompt is safe.")
        with st.spinner("Generating output..."):
            start = time.time()
            messages.append({"role": "user", "content": user_input})
            resp = chatbot.chat(model=model_name, messages=messages)
            answer = resp['message']['content']
            elapsed = time.time() - start
        st.markdown(answer, unsafe_allow_html=True)
        st.write(f"_Inference took {elapsed:.2f}s_")
        st.session_state.history.append((user_input, answer, True))
    else:
        st.error("Prompt is unsafe!")
        st.session_state.strikes += 1
        st.write(f"Strikes: {st.session_state.strikes}")
        if st.session_state.strikes >= 3:
            st.warning("🚫 Too many malicious prompts. You are barred.")
            st.stop()
        if st.session_state.rewrite:
            # Rewrite prompt
            with st.spinner("Rewriting prompt..."):
                start = time.time()
                rewrite_msgs = [
                    {"role": "system", "content": rewrite_instructions},
                    {"role": "user", "content": user_input}
                ]
                raw = chatbot.chat(model=model_name, messages=rewrite_msgs)['message']['content']
                st.write(f"Raw: ", raw)
                start_idx = raw.find("<new>") + len("<new>")
                end_idx = raw.find("</new>")
                safe_prompt = raw[start_idx:end_idx]
                elapsed = time.time() - start
            st.warning("Malicious prompt detected.")
            st.markdown(f"**Rewritten prompt:** {safe_prompt}")
            st.write(f"_Rewrite took {elapsed:.2f}s_")

            # Generate with rewritten prompt
            with st.spinner("Generating new output..."):
                start2 = time.time()
                messages.append({"role": "user", "content": safe_prompt})
                resp2 = chatbot.chat(model=model_name, messages=messages)
                answer2 = resp2['message']['content']
                elapsed2 = time.time() - start2
            st.markdown(answer2, unsafe_allow_html=True)
            st.write(f"_Inference took {elapsed2:.2f}s_")
            st.session_state.history.append((safe_prompt, answer2, False))
        else:
            st.warning("⚠️ Malicious prompt blocked.")
            st.session_state.history.append((user_input, "⚠️ Malicious prompt blocked.", False))


# Optional: banning after 3 strikes
if st.session_state.strikes >= 3:
    st.warning("🚫 Too many malicious prompts. You are barred.")
    st.stop()
