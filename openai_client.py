
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_teacher_prompt(level: str, topic: str):
    return f"""
You are an English teacher. Your student is level {level}.
Topic: {topic}.

Rules:
- Speak naturally, ask questions to keep conversation.
- Correct student's mistakes at the end like a teacher.
- Give short feedback and tips.
- End each reply with a follow-up question.
"""
