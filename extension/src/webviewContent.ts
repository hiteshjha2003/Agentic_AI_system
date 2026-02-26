// This file contains the HTML payload injected into the webview
export function getWebviewContent(extensionUri: vscode.Uri): string {
  const nonce = getNonce();

  // You can also bundle your own main.py as base64 or fetch from disk
  // For simplicity we assume your Streamlit code lives in a string here
  // In production → read from file or use webpack to inline
  const pythonCode = `
import streamlit as st
import time

st.set_page_config(page_title="SambaNova Agent (stlite)", layout="wide")

st.title("SambaNova Code Agent – stlite edition")
st.markdown("Running **entirely in browser** via WebAssembly + Pyodide")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to analyze?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # Simulate streaming (real version would call your backend via fetch)
        for chunk in ["Thinking...", "Retrieving context...", "Analyzing with Llama-3.3-70B...", "Found issue: potential null pointer."]:
            full_response += chunk + " "
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.4)
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.sidebar.header("Controls")
if st.sidebar.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("stlite • Pyodide • SambaNova backend proxy via fetch")
  `.trim();

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SambaNova Agent (stlite)</title>
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src ${webview.cspSource} https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline' 'unsafe-eval'; connect-src *;">
  <style>
    html, body, #root { margin:0; padding:0; height:100%; }
    #root { display: flex; flex-direction: column; }
    .stApp { flex: 1; }
  </style>
</head>
<body>
  <div id="root"></div>

  <script type="module">
    import { StliteKernel } from "https://cdn.jsdelivr.net/npm/@stlite/kernel@0.5.0/+esm";
    import { StliteApp } from "https://cdn.jsdelivr.net/npm/@stlite/app@0.5.0/+esm";

    const kernel = await StliteKernel.load({
      // Mount your main.py
      files: {
        "/app/main.py": ${JSON.stringify(pythonCode)},
      },
      // You can also mount requirements.txt if needed
      requirements: [
        // "streamlit==1.38.0",           // usually not needed – stlite has built-in
        // "requests", "pandas"           // add pure-python packages here
      ]
    });

    const app = new StliteApp(kernel, document.getElementById("root"));

    // Optional: listen for messages from extension
    window.addEventListener("message", (event) => {
      const message = event.data;
      if (message.command === "setSelection") {
        // You could expose selected code to Streamlit via some hack
        console.log("Received selection:", message.code);
      }
    });

    // Cleanup on dispose
    window.addEventListener("beforeunload", () => {
      kernel.dispose();
    });
  </script>
</body>
</html>`;
}

function getNonce() {
  let text = "";
  const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}