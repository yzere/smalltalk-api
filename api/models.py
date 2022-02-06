from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
# from django.contrib.auth import User

# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have an username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser):
    # userID               = models.UUIDField(primary_key = True,
    #                                         default = uuid.uuid4,
    #                                         editable = False,
    #                                         unique=True)
    email                = models.EmailField(verbose_name='email', max_length=255, unique=True)

    username             = models.CharField(max_length=255, unique=True)
    date_joined          = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login           = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin             = models.BooleanField(default=False)
    is_active            = models.BooleanField(default=True)
    is_staff             = models.BooleanField(default=False)
    is_superuser         = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True



class Circle(models.Model):
    circleID            = models.UUIDField(primary_key = True,
                                           default = uuid.uuid4,
                                           editable = False,
                                           unique=True)
    name                = models.CharField(max_length=255)
    localization        = models.CharField(max_length=255)                    #do zmiany
    description         = models.TextField()
    admins              = models.ForeignKey(User, on_delete=models.CASCADE)
    expireDate          = models.DateTimeField()
    creationDate        = models.DateTimeField(auto_now_add=True)
    maxUsers            = models.IntegerField()
    reportsID           = models.CharField(max_length=255)                    #do zmiany
    usersID             = models.CharField(max_length=255)                    #do zmiany
    stats               = models.CharField(max_length=255)                    #do zmiany

    def __str__(self):
        return self.name

class Report(models.Model):

    REPORT_REASON = (
        ('A', '1'),
        ('B', '2'),
        ('C', '3'),
        ('D', '4'),
        ('E', '5'),
        ('F', '6'),
        ('G', '7')
    )


    reportID                = models.UUIDField(primary_key = True,
                                               default = uuid.uuid4,
                                               editable = False,
                                               unique=True)
    reason                  = models.CharField(choices=REPORT_REASON, max_length=30, default='A')
    description             = models.TextField(max_length=255)
    reportedUserID          = models.CharField(max_length=255, null=True)               #do zmiany
    reportingUserID         = models.CharField(max_length=255, null=True)               #do zmiany
    responsibleCircleID     = models.CharField(max_length=255)                          #do zmiany

    def __str__(self):
        return self.reason

class Message(models.Model):
    messageID               = models.UUIDField(primary_key = True,
                                               default = uuid.uuid4,
                                               editable = False,
                                               unique=True)
    sendTime                = models.CharField(max_length=255)         #do zmiany
    senderUserID            = models.CharField(max_length=255)         #do zmiany
    reciverUserID           = models.CharField(max_length=255)         #do zmiany

    def __str__(self):
        return self.sendTime