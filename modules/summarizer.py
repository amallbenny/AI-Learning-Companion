import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY6")
)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_learning_content(text):

    prompt = f"""
You are an expert teacher.

Analyze the educational content below.

Return ONLY valid JSON.

Format STRICTLY like this:

{{
  "summary": "overall summary",

  "topics": [
    {{
      "title": "topic title",

      "explanation": "easy to understand explanation",

      "key_points": [
        "point 1",
        "point 2"
      ]

      // IMPORTANT RULE:
      // ONLY include "examples" field IF real examples exist in the document.
      // If no examples exist, DO NOT include the "examples" field at all.
    }}
  ]
}}

STRICT RULES:

1. Identify all major topics.
2. Explain each topic clearly.
3. Include key points for every topic.
4. DO NOT add empty fields.
5. DO NOT include "examples": [] if no examples exist.
6. DO NOT include the examples heading unless real examples are present in the document.
7. Return ONLY valid JSON. No markdown.

DOCUMENT:
{text}
"""

    response = model.generate_content(prompt)

    return json.loads(response.text)