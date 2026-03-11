from accounts.models import User
import jwt
import os

def is_admin(email):
    user = User.objects.get(email=email)
    return user.super_user

def authenticated(request):
    access_token = request.COOKIES.get('access_token')
    refresh_token = request.COOKIES.get('refresh_token')
    try:
        jwt.decode(access_token, key=os.getenv('ACCESS_TOKEN_SECRET'), algorithms=['HS256'])
        return True
    except jwt.InvalidTokenError:
        try:
            jwt.decode(refresh_token, key=os.getenv('REFRESH_TOKEN_SECRET'), algorithms=['HS256'])
            return True
        except jwt.InvalidTokenError:
            return False
        
def get_user(request):
    access_token = request.COOKIES.get('access_token')
    refresh_token = request.COOKIES.get('refresh_token')
    try:
        payload = jwt.decode(access_token, key=os.getenv('ACCESS_TOKEN_SECRET'), algorithms=['HS256'])
        return User.objects.get(email=payload['email'])
    except jwt.InvalidTokenError:
        try:
            payload = jwt.decode(refresh_token, key=os.getenv('REFRESH_TOKEN_SECRET'), algorithms=['HS256'])
            return User.objects.get(email=payload['email'])
        except jwt.InvalidTokenError:
            return None
