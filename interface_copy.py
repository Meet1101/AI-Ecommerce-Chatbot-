from Hello_copy import QA
import streamlit as st
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr

bot = QA()

st.set_page_config(page_title="E-commerce Chatbot")
with st.sidebar:
    st.title('E-commerce Chatbot')

# Function for generating LLM response
def generate_response(input):
    result = bot.qa({"query": input})
    return result['result']

def text_to_speech(text, output_file="output.mp3"):
    tts = gTTS(text=text, lang="en")
    tts.save(output_file)
    return output_file

def convert_audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)  # Read the entire audio file
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio"
    except sr.RequestError as e:
        return "Could not request results; {0}".format(e)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Welcome, let's unveil your future"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
query_option = st.radio("Choose query option:", ("Type Query", "Record Query"))

if query_option == "Type Query":
    user_query = st.text_input("Enter your query:")
    if st.button("Submit"):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
        response = generate_response(user_query)
        with st.chat_message("assistant"):
            with st.spinner("Getting your answer from mystery stuff.."):
                response = generate_response(user_query)  # Use user_query for type query
                audio_content = text_to_speech(response)  # Generate audio file
                st.audio(audio_content, format='audio/mpeg')  # Play audio
                st.write(response)

elif query_option == "Record Query":
    if st.button('Start Recording'):
        with st.spinner('Recording...'):
            duration = 10  # Recording duration in seconds
            fs = 44100  # Sample rate
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
            sd.wait()  # Wait until recording is finished

        # Save recorded audio to a file
        audio_file = 'recorded_audio.wav'
        sf.write(audio_file, recording, fs)

        # Convert recorded audio to text
        text_input = convert_audio_to_text(audio_file) 
        st.session_state.messages.append({"role": "user", "content": text_input})
        with st.chat_message("user"):
            st.write(text_input)

        # Generate a new response
        with st.chat_message("assistant"):
            with st.spinner("Getting your answer from mystery stuff.."):
                response = generate_response(text_input)
                audio_content = text_to_speech(response)
                st.audio('output.mp3', format='audio/mpeg')
                st.write(response)
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)