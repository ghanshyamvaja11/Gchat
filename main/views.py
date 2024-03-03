from django.shortcuts import render
from django.http import HttpResponse
import google.generativeai as genai
import pyttsx3
import re
import os
from dotenv import load_dotenv


def index(request):
    if request.method == 'POST':
        load_dotenv()
        API_KEY = os.getenv('API_KEY')
        genai.configure(api_key=API_KEY)

        # Set up the model
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[
        ])

        convo.send_message(request.POST.get('prompt'))
        if True:
            prompt = request.POST.get('prompt')
            # # Initialize the Text-to-Speech engine
            engine = pyttsx3.init()

            # Set properties (optional)
            engine.setProperty('rate', 150)    # Speed of speech
            engine.setProperty('volume', 0.9)   # Volume level
            # # Speak the text
            # # Define a regex pattern to match symbols
            pattern = r'[^\w\s]'
            text = convo.last.text
            # # Remove symbols using regex substitution
            reply = re.sub(pattern, '', text)
            # engine.say(reply)
            # engine.runAndWait()

            # return HttpResponse(reply)
            return render(request, 'index.html', {'prompt': prompt, 'reply': reply})
    return render(request, "index.html")
