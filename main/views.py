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
    if request.method == 'POST':
        allowed, block_message = request_limit_check(request)
        prompt = request.POST.get('prompt', '')
        if not allowed:
            # Blocked: show block message as reply
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'reply': block_message, 'prompt': prompt, 'blocked': True})
            return render(request, "index.html", {'reply': block_message, 'prompt': prompt, 'blocked': True})
        try:
            reply = ask_gemini(prompt)
        except Exception as ex:
            reply = f"Error: {ex}"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'reply': reply, 'prompt': prompt})
        return render(request, "index.html", {'reply': reply, 'prompt': prompt})
    return render(request, "index.html")


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

def request_limit_check(request):
    now = get_now()
    user = request.user if request.user.is_authenticated else None

    if user:
        window = timedelta(hours=5)
        max_requests = 30
        obj, created = RequestCount.objects.get_or_create(user=user, defaults={
            'window_start': now,
            'requests': 0,
        })
        # If window expired or not set, reset
        if obj.window_start is None or now - obj.window_start > window:
            obj.window_start = now
            obj.requests = 1
            obj.save()
            return True, None
        elif obj.requests < max_requests:
            obj.requests += 1
            obj.save()
            return True, None
        else:
            reset_time = obj.window_start + window
            # Ensure reset_time is Asia/Kolkata tz aware
            reset_time = reset_time.astimezone(ASIA_KOLKATA)
            wait_seconds = max(0, int((reset_time - now).total_seconds()))
            wait_hours = wait_seconds // 3600
            wait_minutes = (wait_seconds % 3600) // 60
            message = (
                f"Request limit reached (30 per 5 hours). "
                f"Try again in {wait_hours}h {wait_minutes}m, or after {reset_time.strftime('%d-%m-%Y %I:%M %p')}"
            )
            return False, message
    else:
        window = timedelta(hours=24)
        max_requests = 5
        ip = get_client_ip(request)
        obj, created = RequestCount.objects.get_or_create(ip_address=ip, defaults={
            'window_start': now,
            'requests': 0,
        })
        if obj.window_start is None or now - obj.window_start > window:
            obj.window_start = now
            obj.requests = 1
            obj.save()
            return True, None
        elif obj.requests < max_requests:
            obj.requests += 1
            obj.save()
            return True, None
        else:
            reset_time = obj.window_start + window
            reset_time = reset_time.astimezone(ASIA_KOLKATA)
            wait_seconds = max(0, int((reset_time - now).total_seconds()))
            wait_hours = wait_seconds // 3600
            wait_minutes = (wait_seconds % 3600) // 60
            message = (
                f"Request limit reached (5 per 24 hours). "
                f"Try again in {wait_hours}h {wait_minutes}m, or after {reset_time.strftime('%d-%m-%Y %I:%M %p')}. "
                f"Sign up or login for more requests!"
            )
            return False, message
