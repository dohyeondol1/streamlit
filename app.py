import streamlit as st
from openai import OpenAI

@st.cache_data
def get_openai_response(prompt, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def main():
    st.session_state.key = st.text_input("API Key", value=st.session_state.get("key", ""), type="password")
    st.header("Ask Anything")
    st.session_state.prompt = st.text_input("Your Question?", value=st.session_state.get("prompt", ""))
    
    if st.button("Submit"):
        response = get_openai_response(st.session_state.prompt, st.session_state.key)
        st.markdown(f"**Question:** {st.session_state.prompt}")
        st.markdown(f"**Answer:** {response}")

if __name__ == "__main__":
    main()