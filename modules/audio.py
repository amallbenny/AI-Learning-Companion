import os
from gtts import gTTS


def generate_audio(text, output_path):

    try:
        # ensure folder exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # safety check
        if not text or len(text.strip()) == 0:
            return False

        # limit extremely large audio requests (prevents gTTS crash)
        text = text[:3000]

        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_path)

        return True

    except Exception as e:
        print(f"Audio generation failed: {e}")
        return False