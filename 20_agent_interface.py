import streamlit as st
import requests


st.set_page_config(
    page_title="GramSwaram AI",
    page_icon="🌾",
)


st.title("🌾 GramSwaram AI")
st.write("Ask your farming questions")


API_URL = "http://localhost:7777/agents/farmer-api-agent/runs"


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


prompt = st.chat_input("Ask a farming question...")


if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    response = requests.post(
        API_URL,
        data={
            "message": prompt,
            "stream": "false",
        },
    )

    if response.status_code == 200:

        result = response.json()

        answer = result["content"]

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        with st.chat_message("assistant"):
            st.write(answer)

    else:

        st.error(
            f"API Error: {response.status_code}"
        )