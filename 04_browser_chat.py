import streamlit as st
import requests
import json


st.title("🤖 Agno Ollama Assistant")

prompt = st.chat_input("Ask something...")

if prompt:
    st.chat_message("user").write(prompt)

    response = requests.post(
        "http://localhost:7777/agents/ollama-assistant/runs",
        data={
            "message": prompt,
        },
        stream=True,
    )

    if response.ok:
        assistant_message = ""

        for line in response.iter_lines(decode_unicode=True):

            if not line:
                continue

            if line.startswith("data:"):
                data = line[5:].strip()

                try:
                    event_data = json.loads(data)

                    # Get text from streaming events
                    if "content" in event_data:
                        content = event_data["content"]

                        if isinstance(content, str):
                            assistant_message += content

                except json.JSONDecodeError:
                    continue

        if assistant_message:
            st.chat_message("assistant").write(assistant_message)
        else:
            st.warning("No assistant response received.")

    else:
        st.error(f"Error: {response.text}")

