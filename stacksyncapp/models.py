#encoding:utf-8

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, access_token_secret, access_token_key, password=None):
        user = self.model(username = username, access_token_secret = access_token_secret, access_token_key = access_token_key)
        user.set_password(password)
        user.save(using=self._db)
        # <--snip-->
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True, db_index=True)
    access_token_secret = models.TextField()
    access_token_key = models.TextField()

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['token_id']



    def get_full_name(self):
        # For this case we return email. Could also be User.first_name User.last_name if you have these fields
        return self.username

    def get_access_token_key(self):
        return self.access_token_key
	
    def set_access_token_key(self, access_token_key):
        self.access_token_key = access_token_key

    def get_access_token_secret(self):
        return self.access_token_secret
	
    def set_access_token_secret(self, access_token_secret):
        self.access_token_secret = access_token_secret
 
    def get_short_name(self):
        # For this case we return email. Could also be User.first_name if you have this field
        return self.username
 
    def __unicode__(self):
        return self.username
 
    def has_perm(self, perm, obj=None):
        # Handle whether the user has a specific permission?"
        return True
 
    def has_module_perms(self, app_label):
        # Handle whether the user has permissions to view the app `app_label`?"
        return True
 
    @property
    def is_staff(self):
        # Handle whether the user is a member of staff?"
        return self.is_admin

    






