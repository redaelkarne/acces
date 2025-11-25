from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse

class EnsureEmailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if email is missing or invalid
            if not request.user.email or '@' not in request.user.email:
                # Get the login URL
                login_url = reverse('login')
                
                # If we are not already on the login page, logout and redirect
                if request.path_info != login_url:
                    logout(request)
                    return redirect('login')
        
        response = self.get_response(request)
        return response
