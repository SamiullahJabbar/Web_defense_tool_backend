from rest_framework import viewsets
from .models import Website
from .serializers import WebsiteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import AutomationHistory
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import BlockedIP, Website
from rest_framework.permissions import IsAuthenticated


class WebsiteViewSet(viewsets.ModelViewSet):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer


from rest_framework.permissions import IsAuthenticated

class BlockedIPListAPIView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        user = request.user
        
        if not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=401)

        website = Website.objects.filter(user=user).first()

        if not website:
            return Response({"message": "No website found for user."}, status=404)

        blocked_ips = BlockedIP.objects.filter(website=website)

        data = [
            {
                "ip_address": ip.ip_address,
                "blocked_at": ip.blocked_at,
                "is_permanent": ip.is_permanent,
                "unblock_at": ip.unblock_at,
                "block_reason": ip.block_reason
            }
            for ip in blocked_ips
        ]

        return Response(data)



from rest_framework.permissions import IsAdminUser

class AutomationHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        user = request.user 
        logs = AutomationHistory.objects.filter(user=user).order_by('-executed_at')[:50]  

        data = [
            {
                'task_name': log.task_name,
                'status': log.status,
                'message': log.message,
                'executed_at': log.executed_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for log in logs
        ]
        return Response(data)




from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
class loginAPI(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            tokens = RefreshToken.for_user(user)
            return Response({
                'access': str(tokens.access_token),
                'refresh': str(tokens),
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "✅ Logout successful. Token blacklisted."})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

