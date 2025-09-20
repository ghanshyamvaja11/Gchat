import uuid
import pytz
from datetime import timedelta
from .utils import get_client_ip, get_now
from .models import RequestCount
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types
import re
load_dotenv()

User = get_user_model()

ASIA_KOLKATA = pytz.timezone('Asia/Kolkata')

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
    # Common patterns for FAQ responses
    common_patterns = [
        (re.compile(r"\bwho\s+are\s+you\b", re.I),
         "I am G Chat, your AI chat assistant."),
        (re.compile(r"\bwho\s+(developed|made|created)\s+you\b", re.I),
         "I was developed by Ghanshyam Vaja, founder of CodMinds.com."),
        (re.compile(r"\bwho\s+is\s+(your\s+)?founder\b", re.I),
         "Ghanshyam Vaja is my founder and the creator of CodMinds.com."),
        (re.compile(r"\bwhat\s+is\s+codminds(\.com)?\b", re.I),
         "CodMinds is a web & software development startup founded by Ghanshyam Vaja."),
        (re.compile(r"\bwho\s+is\s+ghanshyam\s+vaja\b", re.I),
         "Ghanshyam Vaja is a developer, entrepreneur and founder of CodMinds.com."),
        (re.compile(r"\bhello\b", re.I), "Hello! How can I assist you today?"),
        (re.compile(r"\bhi\b", re.I), "Hi! How can I help you?"),
        (re.compile(r"\byour\s+name\b", re.I), "My name is G Chat."),
        (re.compile(r"\bwhat\s+can\s+you\s+do\b", re.I),
         "I can answer questions, help with coding and much more. Just ask!"),
    ]

    def get_common_answer(prompt):
        p = prompt.strip().lower()
        for pattern, answer in common_patterns:
            if pattern.search(p):
                return answer
        return None

    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')

        # ------------------------------
        # RATE LIMIT CHECK
        # ------------------------------
        allowed, block_message, new_device_cookie = request_limit_check(
            request)

        if not allowed:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                response = JsonResponse(
                    {'reply': block_message, 'prompt': prompt, 'blocked': True})
            else:
                response = render(request, "index.html", {
                                  'reply': block_message, 'prompt': prompt, 'blocked': True})

            # Set device_id cookie if new
            if new_device_cookie:
                response.set_cookie("device_id", request.COOKIES.get("device_id") or str(uuid.uuid4()),
                                    max_age=60*60*24*365, httponly=True)
            return response

        # ------------------------------
        # PATTERN MATCHING
        # ------------------------------
        faq_reply = get_common_answer(prompt)
        if faq_reply:
            reply = faq_reply
        else:
            try:
                reply = ask_gemini(prompt)
            except Exception as ex:
                reply = f"Error: {ex}"

        # Return response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            response = JsonResponse({'reply': reply, 'prompt': prompt})
        else:
            response = render(request, "index.html", {
                              'reply': reply, 'prompt': prompt})

        # Set device_id cookie if new
        if new_device_cookie:
            response.set_cookie("device_id", request.COOKIES.get("device_id") or str(uuid.uuid4()),
                                max_age=60*60*24*365, httponly=True)

        return response

    return render(request, "index.html")


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        if not username or not email or not password:
            error = "All fields are required."
            if is_ajax(request):
                return JsonResponse({'success': False, 'error': error})
            return render(request, 'index.html', {'signup_error': error})
        if User.objects.filter(username=username).exists():
            error = "Username already exists."
            if is_ajax(request):
                return JsonResponse({'success': False, 'error': error})
            return render(request, 'index.html', {'signup_error': error})
        if User.objects.filter(email=email).exists():
            error = "Email already exists."
            if is_ajax(request):
                return JsonResponse({'success': False, 'error': error})
            return render(request, 'index.html', {'signup_error': error})
        user = User.objects.create_user(
            username=username, email=email, password=password)
        login(request, user)
        return redirect('index')
    return redirect('index')


def is_ajax(request):
    # Django 3.1+ removed is_ajax(), so check manually
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        if not username or not email or not password:
            error = "All fields are required."
            if is_ajax(request):
                return JsonResponse({'success': False, 'error': error})
            return render(request, 'index.html', {'signup_error': error})
        if User.objects.filter(username=username).exists():
            error = "Username already exists."
            if is_ajax(request):
                return JsonResponse({'success': False, 'error': error})
            return render(request, 'index.html', {'signup_error': error})
        if User.objects.filter(email=email).exists():
            error = "Email already exists."
            if is_ajax(request):
                return JsonResponse({'success': False, 'error': error})
            return render(request, 'index.html', {'signup_error': error})
        user = User.objects.create_user(
            username=username, email=email, password=password)
        login(request, user)
        return redirect('index')
    return redirect('index')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        remember_me = request.POST.get('remember_me') == 'on'
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if remember_me:
                request.session.set_expiry(2592000)  # 30 days
            else:
                request.session.set_expiry(0)  # Browser close
            if is_ajax(request):
                return JsonResponse({'success': True})
            return redirect('index')
        else:
            error = "Invalid username or password."
            if is_ajax(request):
                return JsonResponse({'success': False, 'error': error})
            return render(request, 'index.html', {'login_error': error})
    return redirect('index')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('index')


def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")

def request_limit_check(request):
    now = get_now()
    user = request.user if request.user.is_authenticated else None

    # 1️⃣ Get device_id for guest
    device_id = request.COOKIES.get("device_id")
    if not device_id:
        device_id = str(uuid.uuid4())
        new_device_cookie = True
    else:
        new_device_cookie = False

    ip = get_client_ip(request)

    # 2️⃣ Set window & max_requests
    if user:
        window = timedelta(hours=5)
        max_requests = 30
        lookup = {"user": user, "device_id": device_id}
    else:
        window = timedelta(hours=24)
        max_requests = 5
        lookup = {"user": None, "device_id": device_id}

    # 3️⃣ Get or create the record
    obj, created = RequestCount.objects.get_or_create(
        **lookup,
        defaults={"window_start": now, "requests": 0, "ip_address": ip},
    )

    # Always update IP if changed
    if obj.ip_address != ip:
        obj.ip_address = ip
        obj.save(update_fields=["ip_address"])

    # 4️⃣ Check if window expired
    if obj.window_start is None or (now - obj.window_start) > window:
        # Reset counter
        obj.window_start = now
        obj.requests = 1
        obj.save(update_fields=["window_start", "requests"])
        return True, None, new_device_cookie

    # 5️⃣ If still under limit
    if obj.requests < max_requests:
        obj.requests += 1
        obj.save(update_fields=["requests"])
        return True, None, new_device_cookie

    # 6️⃣ Limit reached
    reset_time = obj.window_start + window
    wait_seconds = max(0, int((reset_time - now).total_seconds()))
    wait_hours = wait_seconds // 3600
    wait_minutes = (wait_seconds % 3600) // 60

    if user:
        message = (
            f"Request limit reached ({max_requests} per {int(window.total_seconds()/3600)} hours). "
            f"Try again in {wait_hours}h {wait_minutes}m, "
            f"or after {reset_time.strftime('%d-%m-%Y %I:%M %p')}."
        )
    else:
        message = (
            f"Request limit reached ({max_requests} per {int(window.total_seconds()/3600)} hours). "
            f"Try again in {wait_hours}h {wait_minutes}m, "
            f"or after {reset_time.strftime('%d-%m-%Y %I:%M %p')}. "
            f"Sign up or login for more requests!"
        )

    return False, message, new_device_cookie