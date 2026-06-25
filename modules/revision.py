import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY6")
)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_simplified_explanation(topic_title, explanation):

    prompt = f"""
You are a patient teacher.

Simplify the following topic for a beginner.

Rules:
1. Keep it VERY simple.
2. Use short sentences.
3. Avoid technical jargon.
4. Use examples only if necessary.
5. Focus on understanding, not theory depth.

TOPIC:
{topic_title}

EXPLANATION:
{explanation}

Return format:

{{
  "simple_explanation": "...",
  "key_points": [
    "point 1",
    "point 2"
  ]
}}
"""

    response = model.generate_content(prompt)

    return response.text


def generate_ultra_simple_explanation(topic_title, explanation):

    prompt = f"""
You are explaining to a student who completely did NOT understand the topic.

Make it EXTREMELY simple (ELI5 style).

Rules:
- Use very basic words
- Use analogies
- No technical terms unless explained
- Make it very short

TOPIC:
{topic_title}

CONTENT:
{explanation}

Return format:

{{
  "eli5_explanation": "...",
  "analogy": "..."
}}
"""

    response = model.generate_content(prompt)

    return response.text