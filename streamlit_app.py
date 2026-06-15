import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Ticket Analytics",
    page_icon="🎫"
)

st.title("🎫 AI Ticket Analytics System")

question = st.text_input(
    "Ask a question about support tickets",
    placeholder="How many tickets are currently open?"
)

if st.button("Submit"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            response = requests.post(
                f"{API_URL}/query",
                json={"query": question}
            )

            result = response.json()

            st.subheader("Answer")
            st.json(result)

        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")

if st.button("Show Anomalies"):

    try:
        response = requests.get(
            f"{API_URL}/anomalies"
        )

        result = response.json()

        st.subheader("Anomalies")
        st.json(result)

    except Exception as e:
        st.error(f"Error: {e}")