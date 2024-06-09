import streamlit as st
from openai import OpenAI
import urllib.request
from PIL import Image

@st.cache_data
def generate_image(prompt, api_key, image_path='img.png'):
    client = OpenAI(api_key=api_key)
    response = client.images.generate(model="dall-e-3", prompt=prompt)
    image_url = response.data[0].url
    urllib.request.urlretrieve(image_url, image_path)
    img = Image.open(image_path)
    return img

def main():
    st.session_state.key = st.text_input("API Key", value=st.session_state.get("key", ""), type="password")
    st.header("Generate Image with DALL-E 3")
    st.session_state.request = st.text_input("Prompt", value=st.session_state.get("request", ""))
    
    if st.button("Generate"):
        if st.session_state.key and st.session_state.request:
            img = generate_image(st.session_state.request, st.session_state.key)
            st.image(img, use_column_width=True)
        else:
            st.warning("Please provide both an API key and a prompt.")

if __name__ == "__main__":
    main()