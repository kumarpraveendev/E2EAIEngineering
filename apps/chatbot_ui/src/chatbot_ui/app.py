import streamlit as st
import chatbot_ui.core.config as setting
import requests


import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Ecommerce Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)



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

if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant", "content":"Hello, how are you?"}]

if "used_context" not in st.session_state:
    st.session_state.used_context = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

with st.sidebar:

    suggestions_tab, = st.tabs(["🔍 Suggestions"])

    with suggestions_tab:
        if st.session_state.used_context:
            for idx, item in enumerate(st.session_state.used_context):
                st.caption(item.get('description', 'No description'))
                if 'image_url' in item:
                    st.image(item["image_url"], width=250)
                st.caption(f"Price: {item['price']} USD")
                st.divider()
        else:
            st.info("No suggestions yet")            


if prompt := st.chat_input("Hello! How can I assist you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):
        state,output=api_call("post",f"{setting.config.API_URL.rstrip('/')}/agent",json={"query":prompt})
        if state and "answer" in output:
            answer=output["answer"]
            used_context=output.get("used_context",[])
            st.session_state.used_context=used_context
        else:
            answer=output.get("message","Sorry, something went wrong. Please try again.")
            st.error(answer)
        st.write(answer)
    st.session_state.messages.append({"role":"assistant","content":answer})
    st.rerun()

  