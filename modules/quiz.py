import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY6")
)

model = genai.GenerativeModel("gemini-2.5-flash")


def estimate_question_count(topics, text):

    word_count = len(text.split())

    if word_count < 800:
        return min(5, max(3, len(topics)))

    elif word_count < 2500:
        return min(10, max(6, len(topics) + 2))

    else:
        return min(15, max(10, len(topics) + 3))


def generate_quiz(content, api_key=None):

    topics = content.get("topics", [])
    summary = content.get("summary", "")
    full_text = summary + " " + str(topics)

    num_questions = estimate_question_count(topics, full_text)

    # -------------------------
    # Build structured topic input
    # -------------------------
    topic_block = ""

    for i, t in enumerate(topics):
        topic_block += f"""
TOPIC {i+1}:
Title: {t.get('title')}
Explanation: {t.get('explanation')}
Key Points: {t.get('key_points')}
"""

    # -------------------------
    # PROMPT
    # -------------------------
    prompt = f"""
You are an expert exam setter and AI tutor.

Generate a HIGH-QUALITY quiz strictly from the given topics.

STRICT RULES:
1. Each question must belong to exactly ONE topic.
2. Do NOT repeat questions or concepts.
3. Focus on understanding, not memorization.
4. Avoid vague questions.
5. Ensure balanced difficulty.

QUIZ SIZE:
Generate exactly {num_questions} questions.

DIFFICULTY DISTRIBUTION:
- 40% easy
- 40% medium
- 20% hard

IMPORTANT OUTPUT RULE:
- "answer" MUST be EXACT OPTION TEXT (not A/B/C/D)

OUTPUT FORMAT (STRICT JSON ONLY):

[
  {{
    "question": "...",
    "options": [
      "option 1",
      "option 2",
      "option 3",
      "option 4"
    ],
    "answer": "exact text of correct option",
    "topic": "exact topic title",
    "difficulty": "easy | medium | hard"
  }}
]

TOPICS:
{topic_block}

SUMMARY (context only):
{summary}
"""

    try:
        response = model.generate_content(prompt)

        text = response.text.strip()

        # remove markdown if present
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        quiz = json.loads(text)

        # -------------------------
        # VALIDATION FIX (VERY IMPORTANT)
        # -------------------------
        cleaned_quiz = []

        for q in quiz:
            if (
                "question" in q and
                "options" in q and
                "answer" in q and
                isinstance(q["options"], list) and
                len(q["options"]) == 4
            ):
                cleaned_quiz.append(q)

        return cleaned_quiz

    except Exception as e:
        print("Quiz generation error:", e)
        return []