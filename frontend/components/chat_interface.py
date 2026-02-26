# components/chat_interface.py
import streamlit as st
import websocket
import json
import time

from components.header import show_header

show_header()

def render_chat(initial_context: str = ""):
    """
    Live Chat with WebSocket streaming.
    Optional initial_context is prepended to the first user message or system prompt.
    """
    st.subheader("💬 Ask about any result")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show existing history
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    prompt = st.chat_input("Ask the agent anything…")
    if prompt:
        # Prepend initial context only on first message (or always if you prefer)
        full_prompt = f"{initial_context}\n\n{prompt}" if initial_context and len(st.session_state.chat_history) == 0 else prompt

        st.session_state.chat_history.append(("user", full_prompt))
        with st.chat_message("user"):
            st.markdown(full_prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full = ""

            try:
                ws = websocket.WebSocket()
                ws.connect(f"{st.session_state.backend_url.replace('http', 'ws')}/ws")
                ws.send(json.dumps({
                    "type": "analyze",
                    "payload": {
                        "query": full_prompt,
                        "analysis_type": "explain",
                        "stream": True
                    },
                    "workspace_id": st.session_state.workspace_id
                }))

                while True:
                    data = ws.recv()
                    msg = json.loads(data)
                    if msg["type"] == "analysis_chunk":
                        full += msg["content"]
                        placeholder.markdown(full + " ▌")
                    elif msg["type"] == "complete":
                        break
                ws.close()
            except Exception as e:
                st.warning(f"WebSocket failed: {e}. Using simulation.")
                for word in ["Thinking…", "Retrieving context…", "Generating answer…", "Done."]:
                    full += word + " "
                    placeholder.markdown(full + " ▌")
                    time.sleep(0.3)

            placeholder.markdown(full)
            st.session_state.chat_history.append(("assistant", full))