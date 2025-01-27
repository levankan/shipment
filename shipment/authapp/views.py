from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if credentials authenticate successfully
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after login
        else:
            # Add debugging information
            print("Authentication failed. Invalid credentials.")
            return render(request, 'authapp/login.html', {'error': 'Invalid credentials'})

    return render(request, 'authapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout



@login_required
def home(request):
    return render(request, 'authapp/home.html')



@login_required
def sales_home(request):
    return render(request, 'sales/sales.html')
