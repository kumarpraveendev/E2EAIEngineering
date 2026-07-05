import streamlit as st
import chatbot_ui.core.config as setting
import requests


import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def api_call(method,url,**kwargs):

    def _show_error_popup(message):
        """show error message as a popu in the top right corner. """
        st.session_state["error popup"]={
            "visible": True,
            "message":message,
        }

    try:


        response=getattr(requests,method)(url,**kwargs)

        try:
            response_data=response.json()
        except requests.exceptions.JSONDecodeError:
            response_data={"message": "invalid response format from server"}

        if response.ok:
            return True,response_data

        return False,response_data

    except requests.exceptions.ConnectionError:
         _show_error_popup("Connection Error, check your network connection")
         return False,{"message": "Connection error"}

    except requests.exceptions.ReadTimeout:
         _show_error_popup("Request Timeout, try again")
         return False,{"message": "Request timeout"}

    except Exception as e:
        _show_error_popup(f"An unexpected error has occurred {str(e)}")
        return False,{"message": str(e)}






# Streamlit App
with st.sidebar:
    st.title("setting")

    provider = st.selectbox("Select Provider", ["openai", "google", "groq"])
    if provider == "google":
        model_name = st.selectbox("Select Model", ["gemini-2.5-flash"])
    elif provider == "openai":
        model_name = st.selectbox("Select Model", ["gpt-5-nano", "gpt-5-mini"])
    elif provider == "groq":
        model_name = st.selectbox("Select Model", ["llama-3.3-70b-versatile"])

    st.session_state.provider = provider
    st.session_state.model_name = model_name


if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant", "content":"Hello, how are you?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if prompt := st.chat_input("Hello! How can I assist you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):
        output=api_call("post",f"{setting.config.API_URL.rstrip('/')}/chat",json={"provider":st.session_state.provider,"model_name":st.session_state.model_name,"messages":st.session_state.messages})
        response_data=output[1]
        answer=response_data["message"]
        st.write(answer)
    st.session_state.messages.append({"role":"assistant","content":answer})

  