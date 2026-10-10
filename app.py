"""
English Description -> Malayalam Voice Output
Uses Google Translate with a MyMemory API fallback, caches successful translations
and audio, and reports translation and voice errors separately.

Install:
    python -m pip install streamlit deep-translator gTTS requests

Run:
    python -m streamlit run app.py
"""

from io import BytesIO
import requests
import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS

st.set_page_config(
    page_title="English to Malayalam Voice Translator",
    page_icon="🔊",
    layout="centered",
)

st.title("English to Malayalam Voice Translator")
st.write("Enter an English description to translate it into Malayalam and hear it spoken.")


@st.cache_data(show_spinner=False, ttl=3600)
def translate_text(english_text: str) -> str:
    """Try Google Translate first, then MyMemory if Google is rate-limited."""
    text = english_text.strip()
    if not text:
        raise ValueError("Please enter an English description.")

    google_error = None
    try:
        result = GoogleTranslator(source="en", target="ml").translate(text)
        if result and result.strip():
            return result.strip()
        google_error = "Google Translate returned an empty result."
    except Exception as exc:
        google_error = str(exc)

    # Fallback service; it has separate usage limits and may occasionally be unavailable.
    try:
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": "en|ml"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("responseStatus") == 200:
            result = data.get("responseData", {}).get("translatedText", "")
            if result and result.strip():
                return result.strip()
        fallback_error = data.get("responseDetails") or "MyMemory returned no translation."
    except Exception as exc:
        fallback_error = str(exc)

    raise RuntimeError(
        "Both translation services failed.\n"
        f"Google Translate: {google_error}\n"
        f"MyMemory fallback: {fallback_error}"
    )


@st.cache_data(show_spinner=False, ttl=3600)
def make_audio(malayalam_text: str) -> bytes:
    """Generate MP3 audio and cache it for repeated identical text."""
    buffer = BytesIO()
    gTTS(text=malayalam_text, lang="ml", slow=False).write_to_fp(buffer)
    return buffer.getvalue()


english_text = st.text_area(
    "English description",
    placeholder="Example: A person is crossing the road while a car approaches.",
    height=150,
)

if st.button("Translate and Speak", type="primary"):
    if not english_text.strip():
        st.warning("Please enter an English description first.")
    else:
        try:
            with st.spinner("Translating into Malayalam..."):
                malayalam_text = translate_text(english_text.strip())
            st.subheader("Malayalam translation")
            st.text_area("Translated text", value=malayalam_text, height=150, disabled=True)
        except Exception as error:
            st.error("Translation failed. The translation services may be temporarily unavailable.")
            st.caption(str(error))
            st.stop()

        try:
            with st.spinner("Generating Malayalam voice..."):
                audio_bytes = make_audio(malayalam_text)
            st.subheader("Voice output")
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                label="Download Malayalam audio (MP3)",
                data=audio_bytes,
                file_name="malayalam_voice.mp3",
                mime="audio/mpeg",
            )
        except Exception as error:
            st.error(
                "Translation succeeded, but Malayalam voice generation failed. "
                "The speech service may be temporarily unavailable or rate-limited."
            )
            st.caption(str(error))
