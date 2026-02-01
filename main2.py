from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import base64

from openai_client import get_openai_client, build_teacher_prompt

app = FastAPI()

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# Teacher chat endpoint
# -------------------
@app.post("/api/teacher_chat/")
async def teacher_chat(
    audio: UploadFile = File(...),
    level: str = Form(...),
    topic: str = Form(...),
    history: str = Form("")
):
    client = get_openai_client()

    # 1️⃣ Transcribir audio
    try:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=(audio.filename, audio.file, audio.content_type),
        )
        user_text = transcript.text
    except Exception as e:
        return JSONResponse({"error": f"Error transcribing audio: {str(e)}"}, status_code=500)

    # 2️⃣ Construir mensajes GPT
    messages = [{"role": "system", "content": build_teacher_prompt(level, topic)}]
    if history:
        try:
            messages.extend(json.loads(history))
        except:
            pass
    messages.append({"role": "user", "content": user_text})

    # 3️⃣ Responder como teacher
    try:
        gpt_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=messages
        )
        teacher_text = gpt_resp.choices[0].message.content
    except Exception as e:
        return JSONResponse({"error": f"Error GPT: {str(e)}"}, status_code=500)

    # 4️⃣ Generar TTS
    try:
        tts = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=teacher_text
        )
        audio_base64 = base64.b64encode(tts.read()).decode("utf-8")
    except Exception as e:
        return JSONResponse({"error": f"Error TTS: {str(e)}"}, status_code=500)

    return {
        "user_text": user_text,
        "reply_text": teacher_text,
        "reply_audio": audio_base64
    }
