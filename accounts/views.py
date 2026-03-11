from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.hashers import make_password
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.utils import timezone
import datetime
import random
import jwt
from datetime import timedelta
import os
from dotenv import load_dotenv
from .models import User, Address, OTP

def generate_refresh_token(user):
    name = user.first_name
    email = user.email
    exp_time = datetime.datetime.now()+timedelta(days=30)
    refresh_token = jwt.encode({
        'name': name,
        'email': email,
        'exp': exp_time,
    },key=os.getenv('REFRESH_TOKEN_SECRET'),algorithm='HS256')
    return refresh_token

def generate_access_token(user):
    name = user.first_name
    email = user.email
    exp_time = datetime.datetime.now()+timedelta(seconds=120)
    access_token = jwt.encode({
        'name': name,
        'email': email,
        'exp': exp_time,
    },key=os.getenv('ACCESS_TOKEN_SECRET'),algorithm='HS256')
    return access_token

def send_otp_email(email, otp):
    subject = 'OTP for Password Reset'
    message = f'Your OTP for password reset is: {otp}'
    msg = MIMEMultipart()
    msg['From'] = os.getenv('SENDER_EMAIL')
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    try:
        server=smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(os.getenv('SENDER_EMAIL'), os.getenv('GMAIL_APP_PASSWORD'))
        server.sendmail(os.getenv('SENDER_EMAIL'), email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False

def SignupView(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def LoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            refresh_token = generate_refresh_token(user)
            access_token = generate_access_token(user)

            user.refresh_token = refresh_token
            user.save()

            response = redirect('home')

            response['Authorization'] = f'Bearer {access_token}'

            response.set_cookie(
                'name',
                user.first_name+" "+user.last_name,
                max_age=30 * 24 * 60 * 60,
                httponly=True,
                samesite='Lax',
            )

            response.set_cookie(
                'email',
                user.email,
                max_age=30 * 24 * 60 * 60,
                httponly=True,
                samesite='Lax',
            )

            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=30 * 24 * 60 * 60,
                httponly=True,
                samesite='Lax',
            )

            response.set_cookie(
                'access_token',
                access_token,
                max_age=120,
                httponly=False,
                samesite='Lax',
            )
            request.session['user_id'] = user.user_id
            request.session['user_name'] = f'{user.first_name} {user.last_name}'
            request.session['user_email'] = user.email

            return response
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def accounts_options(request):
    """
    Endpoint at /accounts/ that returns the HTML options for the profile dropdown.
    Checks access_token, then refresh_token.
    """
    access_token = request.COOKIES.get('access_token')
    refresh_token = request.COOKIES.get('refresh_token')

    logged_in = False

    if access_token:
        try:
            jwt.decode(access_token, key=os.getenv('ACCESS_TOKEN_SECRET'), algorithms=['HS256'])
            logged_in = True
            print("ACESS TOKEN IS VALID")
        except jwt.InvalidTokenError:
            try:
                jwt.decode(refresh_token, key=os.getenv('REFRESH_TOKEN_SECRET'), algorithms=['HS256'])
                logged_in = True
                print("REFRESH TOKEN IS VALID")
            except jwt.InvalidTokenError:
                print("REFRESH TOKEN IS INVALID")
                pass

    if logged_in:
        html = (
            '<a href="/accounts/signup/" class="pd-item">Sign Up</a>'
            '<a href="/accounts/logout/" class="pd-item">Logout</a>'
        )
    else:
        html = (
            '<a href="/accounts/signup/" class="pd-item">Sign Up</a>'
            '<a href="/accounts/login/" class="pd-item">Login</a>'
        )

    return HttpResponse(html)

def LogoutView(request):
    """
    Endpoint at /accounts/logout/ that logs out the user.
    """
    response = redirect('home')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('name')
    response.delete_cookie('email')
    request.session.flush()
    return response

def ForgotView(request):
    if request.method=="POST":
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            expire_time=timezone.now()+timedelta(minutes=5)
            OTP.objects.update_or_create(user=user, defaults={'otp': str(otp), 'expires_at': expire_time})
            send_otp_email(email, otp)
            
            # Save the email in session so the next view knows who is verifying
            request.session['reset_email'] = email
            return redirect("verify_otp")
        else:
            return render(request, 'accounts/forgot_password.html', {'error': 'No account found with that email address.'})
    else:
        return render(request, 'accounts/forgot_password.html')

def VerifyOTPView(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')
        
    context = {'user_email': email, 'otp_verified': request.session.get('otp_verified', False)}
    
    if request.method == "POST":
        # Handle OTP Verification
        if 'verify_otp' in request.POST:
            otp_entered = "".join([request.POST.get(f'otp_{i}', '') for i in range(1, 7)])
            try:
                user = User.objects.get(email=email)
                otp_record = OTP.objects.get(user=user)
                
                if otp_record.otp == otp_entered and otp_record.expires_at > timezone.now():
                    request.session['otp_verified'] = True
                    otp_record.delete()  # invalidate after use
                    return redirect('verify_otp')
                else:
                    context['error'] = "Invalid or expired OTP. Please try again or request a new one."
            except (User.DoesNotExist, OTP.DoesNotExist):
                context['error'] = "Invalid verification request."

        # Handle Password Changes
        elif 'change_password' in request.POST:
            if not request.session.get('otp_verified'):
                return redirect('verify_otp')
                
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password == confirm_password:
                user = User.objects.get(email=email)
                user.password = make_password(password)
                user.save()
                
                if 'reset_email' in request.session:
                    del request.session['reset_email']
                if 'otp_verified' in request.session:
                    del request.session['otp_verified']
                    
                return redirect('login')
            else:
                context['error'] = "Passwords do not match."

    return render(request, 'accounts/change_password.html', context)