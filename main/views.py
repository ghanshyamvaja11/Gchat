import os
from django.shortcuts import render
from django.http import JsonResponse
from dotenv import load_dotenv

# Correct import!
import google.generativeai as genai
from google.generativeai import types

load_dotenv()


def ask_gemini(prompt):
    # API key from env
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    response = genai.GenerativeModel("gemini-2.5-flash").generate_content(
        prompt,
        generation_config=types.GenerationConfig(temperature=0.1)
    )
    return response.text


def index(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        try:
            reply = ask_gemini(prompt)
        except Exception as ex:
            reply = f"Error: {ex}"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'reply': reply, 'prompt': prompt})
        return render(request, "index.html", {'reply': reply, 'prompt': prompt})
    return render(request, "index.html")
