import google.generativeai as genai
import os

class AIClient:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.chat = self.model.start_chat(history=[])
        print(f"AI Client initialized with gemini-1.5-flash-latest model and chat session started.")

    def get_response(self, message):
        """Get a response from Google's Gemini API"""
        print(f"Getting AI response for: {message[:30]}...")
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            print(f"Exception in AI client: {e}")
            return f"Error: {str(e)}"
