"""
Auth views: Register, Login, Me, Admin user list.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from apps.core.permissions import IsAdmin

User = get_user_model()


class RegisterView(APIView):
    """
    POST /api/auth/register
    Public. Registers Student or Mentor accounts only.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = _get_tokens(user)
        return Response(
            {
                'success': True,
                'message': 'Registration successful.',
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': tokens,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login
    Public. Returns JWT access + refresh tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data['email'].lower(),
            password=serializer.validated_data['password'],
        )

        if user is None:
            return Response(
                {'success': False, 'error': {'code': 401, 'message': 'Invalid email or password.'}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.status != 'Active':
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'Account is inactive.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = _get_tokens(user)
        return Response(
            {
                'success': True,
                'message': 'Login successful.',
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': tokens,
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout
    Accepts refresh token and blacklists it (best-effort).
    Frontend should clear stored tokens.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass  # Best-effort blacklist; frontend clears tokens regardless
        return Response({'success': True, 'message': 'Logged out successfully.'})


class MeView(APIView):
    """
    GET /api/auth/me
    Returns the currently authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                'success': True,
                'data': UserSerializer(request.user).data,
            }
        )


class AdminUserListView(APIView):
    """
    GET /api/admin/users
    Admin-only: lists all users with roles.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all().order_by('-created_at')
        return Response(
            {
                'success': True,
                'data': UserSerializer(users, many=True).data,
            }
        )


# ---------- helpers ----------

def _get_tokens(user):
    refresh = RefreshToken.for_user(user)
    # Embed role in token payload for frontend convenience
    refresh['role'] = user.role
    refresh['name'] = user.name
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }
