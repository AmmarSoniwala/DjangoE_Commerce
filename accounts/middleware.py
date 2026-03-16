from services.auth import get_user
from django.http import HttpResponseRedirect

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user = get_user(request)
        if isinstance(user, HttpResponseRedirect):
            exempt_paths = [
                '/accounts/login/', 
                '/accounts/signup/', 
                '/accounts/forgot-password/', 
                '/accounts/verify-otp/', 
                '/admin/'
            ]
            if any(request.path.startswith(path) for path in exempt_paths):
                user = None
            else:
                return user
            
        if user:
            print(f"User: {user.email} trying to accesss {request.path}")
            
        response = self.get_response(request)
        
        if user:
            print(f"User: {user.email} accessed {request.path}")
        return response