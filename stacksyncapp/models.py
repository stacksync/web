#encoding:utf-8

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, token_id, expdate, password=None):
        user = self.model(username = username, token_id = token_id, expdate = expdate)
        user.set_password(password)
        user.save(using=self._db)
        # <--snip-->
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True, db_index=True)
    token_id = models.TextField()
    expdate = models.DateTimeField()
	
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['token_id']

	

    def get_full_name(self):
        # For this case we return email. Could also be User.first_name User.last_name if you have these fields
        return self.username

    def get_token_id(self):
        return self.token_id
	
    def set_token_id(self, token_id):
        self.token_id = token_id

    def get_expdate(self):
        return self.expdate
	
    def set_expdate(self, expdate):
        self.expdate = expdate
 
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

    






