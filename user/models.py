from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator 
from shared.models import BaseModel
from datetime import datetime, timedelta 
from rest_framework_simplejwt.tokens import RefreshToken
import random
import uuid
 


ORDINARY_USER, MANAGER, ADMIN = ("ordinary_user", "manager", "admin")
VIA_EMAIL, VIA_PHONE = ("via_email", "via_phone")
NEW, COD_VERIFIED, DONE, PHOTO_DONE = ("new", "cod_verified", "done", "photo_done")

PHONE_EXPIRE = 10
EMAIL_EXPIRE = 10

class User(AbstractUser, BaseModel):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN),
    )
    AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (COD_VERIFIED, COD_VERIFIED),
        (DONE, DONE),
        (PHOTO_DONE,PHOTO_DONE)
    )
    
    user_roles = models.CharField(max_length=250, choices=USER_ROLES, default="ordinary_user", null=True)
    auth_type = models.CharField(max_length=250, choices=AUTH_TYPE, null=True)
    auth_status = models.CharField(max_length=250, choices=AUTH_STATUS, default="new", null=True)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="images/profile/", validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    


    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 100) % 10) for _ in range(4)])
        UserConfirmation.objects.create(user_id=self.id, verify_type=verify_type, code=code)
        return code
    
    def make_username(self):
        if not self.username:
            temp_username = f'instagram-{uuid.uuid4().__str__().split( "-"[-1])}'
            while User.objects.filter(username=temp_username):
                temp_username = f"{temp_username}{random.randit(0, 9)}"
            
            self.username = temp_username
            
            
            
    def make_password(self):
        if not self.password:
            temp_pasword = f"instagram-{uuid.uuid4().__str__().split( "-"[-1])}" 
            self.pasword = temp_pasword
            
            
            
    def hashing_password(self):
        if not self.password.startswith("pbkdf2_sha256"):
            self.set_password(self.password)
            
    def make_email(self):
        if self.email:
            oddiy_email = self.email.lower()
            self.email = oddiy_email
            
            
    def token(self):
        refresh = RefreshToken.for_user(self)
        print(f"access: {str(refresh.access_token)}, refresh_token: {str(refresh)}")
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }
            
            
            
    def clean(self):
        self.hashing_password()
        self.make_email()
        self.make_username()
        self.make_password()
        
        
    def save(self, *args, **kawargs):
        self.clean()
        super(User,self).save(*args, **kawargs)



class UserConfirmation(BaseModel):
    AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
        
    verify_type = models.CharField(choices=AUTH_TYPE, max_length=250)
    code = models.CharField(max_length=4)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="verify_code")
    expiration = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)
    

    
    
    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expiration = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
        else:
            self.expiration = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)
            
            
            
            
