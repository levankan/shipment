from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Profile
from django.contrib.auth import authenticate, login



def home(request):
    return render(request, 'custom_auth/home.html')  # Render home template

def about(request):
    return render(request, 'custom_auth/about.html')  # Render about template










def sign_up(request):
    if request.method == 'POST':
        # Retrieve form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        repeat_email = request.POST.get('repeat_email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        security_question = request.POST.get('security_question')
        security_answer = request.POST.get('security_answer')

        # Validation checks
        errors = []
        if email != repeat_email:
            errors.append("Emails do not match.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        if len(password) < 12:
            errors.append("Password must be at least 12 characters long.")

        if User.objects.filter(username=username).exists():
            errors.append("Username is already taken.")

        if User.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")

        # If there are validation errors, show them and return
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('sign_up')

        # Create user and save profile
        try:
            # Create the User object
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Update the Profile object
            profile = user.profile  # Access the related Profile object
            profile.phone_number = phone_number
            profile.email = email
            profile.security_question = security_question
            profile.security_answer = security_answer
            profile.save()

            # Success message
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('sign_up')

    return render(request, 'custom_auth/sign_up.html')








#login view

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        # Validate username and password
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('login')

        if len(password) < 12:
            messages.error(request, "Password must be at least 12 characters long.")
            return redirect('login')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in
            login(request, user)

            # Set session expiry for "Remember Me"
            if remember_me:
                request.session.set_expiry(2409600)  # 4 weeks
            else:
                request.session.set_expiry(0)  # Session ends on browser close

            messages.success(request, "You have successfully logged in.")
            return redirect('home')  # Redirect to home page or dashboard
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'custom_auth/login.html')  # Render the login page
