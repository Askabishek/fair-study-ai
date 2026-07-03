import os
import base64
import pathlib
import io
from groq import Groq
import pypdf
from gtts import gTTS

class MultimodalAgent:
    def __init__(self, api_key: str):
        # Initializing the Groq Client
        self.client = Groq(api_key=api_key)
        self.text_model = "llama-3.3-70b-versatile"
        self.vision_model = "llama-3.2-90b-vision-preview"
        self.audio_model = "whisper-large-v3"

    def process_study_input(self, file_path: str, user_prompt: str) -> str:
        """ Handles complex files (PDF, Images, Audio) along with a text prompt using Groq. """
        path = pathlib.Path(file_path)
        ext = path.suffix.lower()

        # 1. Image Processing (Vision)
        if ext in ['.png', '.jpg', '.jpeg', '.webp']:
            with open(path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Formulate MIME type
            mime_type = "image/jpeg"
            if ext == ".png":
                mime_type = "image/png"
            elif ext == ".webp":
                mime_type = "image/webp"
                
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ]
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages
            )
            return response.choices[0].message.content

        # 2. Audio Processing (Transcription + Text Completion)
        elif ext in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
            with open(path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.audio_model,
                )
            transcript = transcription.text
            
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful study assistant. Analyze the audio transcript provided below."
                },
                {
                    "role": "user", 
                    "content": f"Audio Transcript:\n{transcript}\n\nUser Request: {user_prompt}"
                }
            ]
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=messages
            )
            return response.choices[0].message.content

        # 3. PDF Processing (Text Extraction + Text Completion)
        elif ext == '.pdf':
            reader = pypdf.PdfReader(path)
            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text() or ""
                
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful study assistant. Analyze the document text provided below."
                },
                {
                    "role": "user", 
                    "content": f"Document Text:\n{extracted_text}\n\nUser Request: {user_prompt}"
                }
            ]
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=messages
            )
            return response.choices[0].message.content

        # 4. Standard Text Files or default fallback
        else:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except Exception:
                file_content = "[Binary/Unsupported File Content]"
                
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful study assistant. Analyze the file content provided below."
                },
                {
                    "role": "user", 
                    "content": f"File Content:\n{file_content}\n\nUser Request: {user_prompt}"
                }
            ]
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=messages
            )
            return response.choices[0].message.content
        
    def generate_voice_response(self, text_content: str):
        """ Configures gTTS to return an audio file instead of plain text, matching Gemini return shape """
        tts = gTTS(text=text_content, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # We return a mock parts structure that mimics Gemini response.parts
        class MockPart:
            class MockInlineData:
                def __init__(self, data_bytes):
                    self.data = data_bytes
            def __init__(self, data_bytes):
                self.inline_data = self.MockInlineData(data_bytes)
                
        return [MockPart(fp.read())]
