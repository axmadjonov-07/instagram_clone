from rest_framework import serializers
from .models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE, COD_VERIFIED, DONE, PHOTO_DONE
from shared.utils import check_email_or_phone, send_email
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import  authenticate

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)
        
        
    class Meta:
        model = User
        fields = (
            "id",
            "auth_type",
            "auth_status"
        )
    
    extra_kwargs = {
        "auth_type":{"read_only": True, "required": False},
        "auth_status":{"read_only": True, "required": False},
    }
    
    def create(self, validation_data):
        user = super(UserSerializer, self).create(validation_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.email, code)
            
        user.save()
        return user
    
    def validate(self, data):
        super(UserSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data
    
    def auth_validate(self, data): 
        user_input = str(data.get("email_phone_number")).lower()
        
        input_type = check_email_or_phone(user_input)   
        
        if input_type == "email":
            data = {
                'email':user_input,
                'auth_type':VIA_EMAIL
            }
        elif input_type == "phone":
            data = {
                'phone':user_input,
                'auth_type':VIA_PHONE
            }
        else:
            data = {
                "status":False,
                "message": "EMAIL YOKI TELEFON RAQAMDA XATOLIK BOR"
            }
            raise ValidationError(data)
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance) 
        representation['tokens'] = instance.token() 
        return representation
         
         
class UserChangeSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, max_length=200, required=True)
    last_name = serializers.CharField(write_only=True, max_length=200, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    
    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        
        
        if password != confirm_password:
            raise ValidationError(
                {
                    "message":"PAROL MOS TUSHMAYABTI!"
                }
            )
        if password:
            validate_password(password)
            validate_password(confirm_password)
            
        return data
    def validate_first_name(self, first_name):
        if len(first_name) < 3 or len(first_name) > 600:   #'''(+585 Хьюберт Блейн Вольфшлегельштайнхаузенбергедорф-старший )'''
            data = {
                "message":"Ism 3 tadan ko'proq 600 tadan kamroq belgidan iborat bo'lishi kerak:"
            }
            raise ValidationError(data)
        if first_name.isdigit():
            data = {
                "message":"ISM FAQAT RAQAMLARDAN IBORAT BO'LISHI MUMKIN EMAS!"
            }
            raise ValidationError(data)
        return first_name
        
        
    def validate_last_name(self, last_name):
        if len(last_name) < 3 or len(last_name) > 600:
            data = {
                "message":"Familiya 3 tadan ko'proq 600 tadan kamroq belgidan iborat bo'lishi kerak:"
            }
            raise ValidationError(data)
        if last_name.isdigit():
            data = {
                "message":"FAMILIYA FAQAT RAQAMLARDAN IBORAT BO'LISHI MUMKIN EMAS!"
            }
            raise ValidationError(data)
        return last_name
        
        
    def validate_username(self, username):
        if len(username) < 3 or len(username) > 30:
            data = {
                "message":"Username 3 tadan ko'proq 600 tadan kamroq belgidan iborat bo'lishi kerak:"
            }
            raise ValidationError(data)
        if username.isdigit():
            data = {
                "message":"USERNAME FAQAT RAQAMLARDAN IBORAT BO'LISHI MUMKIN EMAS!"
            }
            raise ValidationError(data)
        
        
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.username = validated_data.get("username", instance.username)
        instance.password = validated_data.get("password", instance.password)
        
        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))
        if instance.auth_status == COD_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance
        
            
class ChangeUserPhotoSerializers(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    
    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save()
            
        return instance
    
    
class LoginSerializers(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)
        
    def auth_validate(self, data):
        user_input = data.get('userinput')
        username = None
        
        try:
            if check_user_type(user_input) == 'username':
                username = user_input
            elif check_user_type(user_input) == 'email':
                user = self.get_user(email__ieaxact=user_input)
                username = user.username
            elif check_user_type(user_input) == 'phone':
                user = self.get_user(phone_number=user_input)
                username = user.username
            else:
                raise ValidationError({
                    "message":"Siz xato login malumotlarini kiritingiz!"
                })
                
            authentication_kwargs = {
                self.username_field: username,
                'password': data['password']
            }
        
            hozirgi_user = User.objects.filter(username__iexact=username).first()
            
            if hozirgi_user is not None and hozirgi_user.auth_status in [NEW, CODE_VERIFIED]:
                raise ValidationError(
                    {
                        "message":"Siz to'liq ro'yhatdan o'tmagansiz!"
                    }
                )
            user = authenticate(**authentication_kwargs)
            
            if user is not None:
                self.user = user
            else:
                raise ValidationError(
                    {
                        "message":"SIZ LOGIN QILA OLMAYSIZ!"
                    }
                )
        except Exception:
            raise ValidationError({
                "message":"XATOLIK YUZ BERDI!"
            })
            
    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_DONE]:
            raise PermissionDenied("SIZ LOGIN QILA OLMAYSIZ!")
        
        data = self.user.token()
        data["authstatus"] = self.user.auth_status
        data["name"] = self.user.first_name
        
        return data
    
    def get_user(self, **kwargs):
        user = User.objects.filter(**kwargs)
        if not user.exists():
            raise ValidationError({
                "message":"XATOLIK!"
            })
        return user.first()
             