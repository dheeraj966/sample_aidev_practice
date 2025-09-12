import google.generativeai as genai
import os

class AIClient:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is missing. Please check your .env file.")
        print(f"Initializing AI Client with key: ...{api_key[-4:]}")
        genai.configure(api_key=api_key)
        self.model_name = 'gemini-1.5-flash-latest'
        self.model = genai.GenerativeModel(self.model_name)
        self.chat = self.model.start_chat(history=[])
        print(f"AI Client initialized with {self.model_name} model and chat session started.")

    def get_response(self, message):
        """Get a response from Google's Gemini API"""
        print(f"Getting AI response for: {message[:30]}...")
        print(f"Using model: {self.model_name}")
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            print(f"Exception in AI client: {e}")
            return f"Error: {str(e)}"