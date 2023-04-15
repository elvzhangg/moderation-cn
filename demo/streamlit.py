import random
import time
import streamlit as st
import requests


st.title("Moderation Demo")
message = st.text_area("Enter a message and press ctrl-enter to check if content is safe.", key="message")


if message:
    container = st.empty()
    with st.spinner('Checking content...'):
        time.sleep(1)
        result = requests.post(
            "https://sweepai--get-text-moderation-status-moderation-webhook.modal.run/", 
            json={"text": message}
        ).json()["safe"]
    with container:
        safety_indicator = st.write("The content is", ":green[safe]." if result else ":red[unsafe].")

examples = [
    "a boat is in the water near the city skyline with a sun rise behind it, in the style of chen zhen, webcam photography, yiannis moralis, abrasive authenticity, aerial photography, eastern and western fusion, light orange and black --ar 4:3",
    "2 toddler boys in dark grey inside of a car, in the style of classic japanese simplicity, y2k aesthetic, stockphoto, he jiaying, michelangelo, soft, dream-like quality, strong facial expression --ar 33:50",
    "Pole dancers performing for a crowd in a nightclub, while dollar bills thrown on stage. Dark Background. Neon signs. 1990S styles",
]
with st.expander("Example messages", expanded=True):
    for i, example in enumerate(examples):
        st.write(example)
        def on_click(example=example):
            st.session_state.message = example
        st.button("Try this!", key=f"example_{i}", on_click=on_click)
