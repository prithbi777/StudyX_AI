# IMPORTING REQUIRED LIBRARIES
import os
import streamlit as st
import openai
from dotenv import load_dotenv
import pygame
import atexit

# LOAD ENV VARIABLES FROM .ENV FILE
load_dotenv()

# CONFIGURE OPENAI API KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

# CONFIGURE STREAMLIT PAGE
st.set_page_config(
    page_title="StudyX",
    page_icon="📚",
    layout="centered"
)

# INIT CHAT HISTORY
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# PAGE TITLE
st.markdown("<h1 style='text-align: center;'>StudyX AI 📚</h1>", unsafe_allow_html=True)

# SIDEBAR OPTIONS
with st.sidebar:
    st.markdown(
        """
        <h1 style="text-align: center; color: aqua; font-weight: bold;">
            StudyX AI Modes
        </h1>
        <hr style="border: 2px solid blue;">
        """,
        unsafe_allow_html=True
    )
    mode = st.radio(
        "**Choose a mode:**",
        ("Chat Mode", "Answer Questions", "Summarize Notes", "Generate Quiz", "Relax Mode"),
        index=0
    )

# FUNCTION TO GENERATE AI RESPONSE
def generate_response(prompt, max_tokens=150):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error: {e}"

# MUSIC PLAYER FUNCTIONS
def play_song(song_path):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    st.session_state.is_playing = True
    st.session_state.is_paused = False

def pause_song():
    pygame.mixer.music.pause()
    st.session_state.is_paused = True

def resume_song():
    pygame.mixer.music.unpause()
    st.session_state.is_paused = False

def stop_song():
    pygame.mixer.music.stop()
    st.session_state.is_playing = False
    st.session_state.is_paused = False

# Stop music when app exits
def stop_music_on_exit():
    try:
        pygame.mixer.music.stop()
    except:
        pass

atexit.register(stop_music_on_exit)

# RELAX MODE
if mode == "Relax Mode":
    st.subheader("🎵 Relax Mode - Music Player")

    # Initialize pygame mixer
    if "music_initialized" not in st.session_state:
        pygame.mixer.init()
        st.session_state.music_initialized = True
        st.session_state.is_playing = False
        st.session_state.is_paused = False
        st.session_state.current_song = None

    music_dir = "//media//prithbi//Prithbiraj//Python//Music_Player_Using_Python//Songs"

    try:
        song_files = os.listdir(music_dir)
        song_titles = [file.title() for file in song_files]
        selected_song = st.selectbox("🎶 Select a song to play:", song_titles)

        if st.button("▶️ Play Selected Song"):
            song_path = os.path.join(music_dir, song_files[song_titles.index(selected_song)])
            play_song(song_path)
            st.session_state.current_song = song_path
            st.success(f"Playing: {selected_song}")

        if st.button("⏸ Pause"):
            if st.session_state.is_playing and not st.session_state.is_paused:
                pause_song()
                st.info("Music paused.")

        if st.button("▶️ Resume"):
            if st.session_state.is_paused:
                resume_song()
                st.success("Music resumed.")

        if st.button("⏹ Stop"):
            stop_song()
            st.warning("Music stopped.")

    except Exception as e:
        st.error(f"Failed to load music: {e}")

# OTHER MODES
else:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("💬 Ask Anything")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        if mode == "Chat Mode":
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    *st.session_state.chat_history
                ]
            )
            assistant_response = response.choices[0].message["content"]

        elif mode == "Answer Questions":
            prompt = f"Answer the following question in detail: {user_prompt}"
            assistant_response = generate_response(prompt)

        elif mode == "Summarize Notes":
            prompt = f"Summarize the following notes in a concise and clear way: {user_prompt}"
            assistant_response = generate_response(prompt)

        elif mode == "Generate Quiz":
            prompt = f"Generate a multiple-choice quiz with 5 questions on the topic: {user_prompt}. Include the correct answers."
            assistant_response = generate_response(prompt, max_tokens=300)

        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
