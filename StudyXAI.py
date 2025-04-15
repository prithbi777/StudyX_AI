# IMPORTING REQUIRED LIBRARIES
import os
import streamlit as st
import openai
from dotenv import load_dotenv
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





# RELAX MODE
if mode == "Relax Mode":
    st.subheader("🎵 Relax Mode - Music Player")

    # Initialize uploaded songs list if not present
    if "uploaded_songs" not in st.session_state:
        st.session_state.uploaded_songs = []

    # File uploader for song selection (multiple songs allowed)
    uploaded_file = st.file_uploader("Choose a song", type=["mp3", "wav"], key="song_uploader", accept_multiple_files=True)

    # If files are uploaded, add them to the session state
    if uploaded_file:
        for file in uploaded_file:
            if file.name not in [song.name for song in st.session_state.uploaded_songs]:
                st.session_state.uploaded_songs.append(file)
                st.success(f"Uploaded: {file.name}")

    # Show the list of uploaded songs
    if st.session_state.uploaded_songs:
        st.write("### Uploaded Songs:")
        for song in st.session_state.uploaded_songs:
            st.markdown(f"- {song.name}")

        # Select song from the uploaded list to play
        selected_song = st.selectbox("Select a song to play", [song.name for song in st.session_state.uploaded_songs])

        # Find the song object based on selection
        song_to_play = next(song for song in st.session_state.uploaded_songs if song.name == selected_song)

        if st.button(f"▶️ Play {song_to_play.name}"):
            st.audio(song_to_play, format="audio/mp3")
            st.success(f"Playing: {song_to_play.name}")

    else:
        st.warning("No songs uploaded yet. Please upload a song to start.")







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
