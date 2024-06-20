from django.shortcuts import render
from .serializers import UserSerializer, UserChangeSerializer, ChangeUserPhotoSerializers, LoginSerializers
from rest_framework import generics, permissions
from .models import User, NEW, COD_VERIFIED, VIA_EMAIL, VIA_PHONE
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from datetime import datetime
from shared.utils import send_email, send_phone
from rest_framework_simplejwt.views import TokenObtainPairView



class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    

class VerifyApiView(APIView):
    permission_class = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')
        
        self.check_verify(user, code)
        return Response(
            data = {
                "success":True,
                "auth_status": user.auth_status,
                "access":user.token()['access'],
                "refresh":user.token()['refresh_token']
            }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_code.filter(expiration__gte=datetime.now(), code=code, is_confirmed=False)
            
            
        if not verifies.exists():
            data = {
                "message": "Tasdiqlash kodi xato yoki eskirgan🤷"
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = COD_VERIFIED
            user.save()
                
        return True
        
             
class GetNewVerifyCode(APIView):
    permission_classes = [IsAuthenticated, ]  

    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verify(user)
            
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_phone(user.phone_number, code)
    

    @staticmethod
    def check_verify(user):
        verifies = user.verify_code.filter(expiration__gte=datetime.now(), is_confirmed=False)
        
        if verifies.exists():
            data = {
                 "message": "Kechirasiz, tasdiqlash kodingiz hali ham faol."
            }
            raise ValidationError(data)
        
        
class UserChangeInformation(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserChangeSerializer
    http_method_names = ['patch','put']
    
    def get_object(self):
        return  self.request.user
    def update(self, request, *args, **kwargs):
        super(UserChangeInformation, self).update(request, *args, **kwargs)
        
        data = {
            "message":"User muvafaqiyatli yangilandi!",
            "auth_status": self.request.user.auth_status
        }
        
        return Response(data)
    

class ChangeUserPhoto(APIView):
    permission_classes = [IsAuthenticated, ]
    
    def put(self, request, *args, **kwargs):
        serializer = ChangeUserPhotoSerializers(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            return Response(
                {
                    'message': "RASM O'RNATILDI!"
                }
            )
        return Response(serializer.errors, status=400)
    
    
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializers
    
