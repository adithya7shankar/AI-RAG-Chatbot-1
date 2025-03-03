# filepath: AI-RAG-Chatbot/backend/services/gpt_service.py

import openai
import os
from flask import current_app

class GPTService:
    def __init__(self, api_key=None):
        # Try to get API key from parameter, environment variable, or Flask config
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        
        # If still no API key, try to get from Flask config (only works in request context)
        if not self.api_key:
            try:
                self.api_key = current_app.config.get('OPENAI_API_KEY')
            except RuntimeError:
                # Not in Flask context, will need to set API key later
                pass
        
        if self.api_key:
            openai.api_key = self.api_key

    def generate_response(self, prompt, context=None, model="gpt-3.5-turbo", max_tokens=150):
        try:
            messages = []
            
            # Add context if provided
            if context:
                if isinstance(context, list):
                    context_text = "\n".join(context)
                else:
                    context_text = str(context)
                
                messages.append({
                    "role": "system", 
                    "content": f"Use the following information to answer the user's question:\n{context_text}"
                })
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message['content']
        except Exception as e:
            try:
                current_app.logger.error(f"Error generating response: {e}")
            except RuntimeError:
                # Not in Flask context
                print(f"Error generating response: {e}")
            return "Sorry, I couldn't generate a response at this time."
