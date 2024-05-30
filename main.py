import pyautogui
import pywhatkit
import speech_recognition as sr
import win32com.client
import webbrowser
import datetime
import time
import requests
import streamlit as st
from streamlit_chat import message
import itertools
import wolframalpha
from bardapi import Bard
import os
from streamlit_lottie import st_lottie
import logging

# Set environment variables securely
os.environ['_Bard_API_KEY'] = 'XQg-gkLZvRlAhRMJtYGexOKX9caTb7p2AwINXnMUNJLTxpsHcxG53LIEf8NydU7lEz2q6w.'
client = wolframalpha.Client('LRWXK2-Y7YLTJRWT6')
counter = itertools.count()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def speaknex(sampletext, max_length=200):
    speaker = win32com.client.Dispatch("SAPI.Spvoice")
    if len(sampletext) <= max_length:
        speaker.Speak(sampletext)
    else:
        speaker.Speak(sampletext[:max_length])
        speaker.Speak("And you can read the rest of the information")

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speaknex("Good Morning!")
    elif hour >= 12 and hour < 18:
        speaknex("Good Afternoon!")
    else:
        speaknex("Good Evening!")
    speaknex("Hello, I am Nexus. Please tell me how may I help you")

def commandnex():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 0.6
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except Exception as e:
            speaknex("Can you please Speak Again...")
            logging.error("Speech recognition error: %s", e)
            return None

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        logging.error("Error fetching Lottie animation: %s", r.status_code)
        return None
    return r.json()

lottie_coding = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_ok9cq9zj.json")

def decrease_volume():
    for _ in range(5):
        pyautogui.press("volumedown")
        time.sleep(0.1)  # Small delay to ensure the key press is registered
    speaknex("Volume decreased")

def increase_volume():
    for _ in range(5):
        pyautogui.press("volumeup")
        time.sleep(0.1)  # Small delay to ensure the key press is registered
    speaknex("Volume increased")

def front(para):
    if 'generate' not in st.session_state:
        st.session_state['generate'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if text:
        st.session_state.generate.append(para)
        st.session_state.past.append(text)

    unique_key = f"{next(counter)}"
    message(text, is_user=True, key=unique_key + '_user')
    message(para, key=unique_key)

    speaknex(para)

if __name__ == "__main__":
    st_lottie(lottie_coding, height=300, key="coding")
    st.title("Nexus A.I Voice Assistant")
    wishMe()

    while True:
        print("Listening...")
        text = commandnex()
        if not text:
            continue
        print("Understanding...")

        sites = [["youtube", "https://youtube.com"], ["wikipedia", "https://wikipedia.com"],
                 ["Instagram", "https://instagram.com"], ["Twitter", "https://twitter.com"],
                 ["Google", "https://google.com"]]
        webcom = False

        for site in sites:
            if f"Open {site[0]}".lower() in text.lower():
                front(f"Opening {site[0]}")
                webbrowser.open(site[1])
                webcom = True

        if webcom:
            continue

        if "increase volume" in text.lower():
            increase_volume()

        elif "decrease volume" in text.lower():
            decrease_volume()

        elif "the time" in text.lower():
            timenowhour = datetime.datetime.now().strftime("%H")
            timenowmin = datetime.datetime.now().strftime("%M")
            front(f"The time is {timenowhour} hour and {timenowmin} minute")

        elif "play" in text.lower():
            song = text.replace('play', '').strip()
            front('Playing ' + song)
            pywhatkit.playonyt(song)

        else:
            url = f"https://api.duckduckgo.com/?q={text}&format=json"
            response = requests.get(url)
            data = response.json()
            abstract = data.get('Abstract')

            if abstract:
                front(abstract)
            else:
                try:
                    res = client.query(text)
                    output = next(res.results).text
                    front(output)
                except StopIteration:
                    speaknex("No results found.")
                except Exception as e:
                    logging.error("Error querying Wolfram Alpha: %s", e)
                    front(Bard().get_answer(text)['content'])