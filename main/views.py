from django.shortcuts import render
from django.http import HttpResponse
import google.generativeai as genai
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
        text = request.POST.get('prompt').lower()
        prompt = request.POST.get('prompt')
        reply = "Hi, I am G Chat."
        if "who are you" in text:
            return render(request, 'index.html', {'prompt': prompt, 'reply': reply})

        elif "what is your name" in text or "your name" in text:
            reply = "My name is G Chat."
            return render(request, 'index.html', {'prompt': prompt, 'reply': reply})
        
        elif "who created you" in text or "who developed you" in text:
            reply="Ghanshyam Vaja Developed Me."
            return render(request, 'index.html', {'prompt': prompt, 'reply': reply})
        
        else:
            pattern = r'[^\w\s]'
            text = convo.last.text
            reply = re.sub(pattern, '', text)
            return render(request, 'index.html', {'prompt': prompt, 'reply': reply})
    return render(request, "index.html")
