from email import contentmanager
from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth import User


class CustomUser(AbstractUser):
    user_ID = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.user_ID)





class Profile(models.Model):
    profile_ID              = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE)
    stats                   = models.CharField(max_length=50, blank=True, null=True)
    social_link             = models.CharField(max_length=50, blank=True, null=True)
    name                    = models.CharField(max_length=50, blank=True, null=True)
    contact                 = models.CharField(max_length=50, blank=True, null=True)
    user_circles_IDs        = models.ManyToManyField('Circle', blank=True,)

    def __str__(self):
        return str(self.profile_ID)





class Circle(models.Model):
    circle_ID               = models.AutoField(primary_key=True)
    name                    = models.CharField(max_length=50, blank=True, null=True)
    localization            = models.CharField(max_length=50, blank=True, null=True)
    description             = models.CharField(max_length=50, blank=True, null=True)
    expire_date             = models.CharField(max_length=50, blank=True, null=True)
    creation_date           = models.CharField(max_length=50, blank=True, null=True)
    max_users               = models.CharField(max_length=50, blank=True, null=True)
    stats                   = models.CharField(max_length=50, blank=True, null=True)
    admin_users_IDs         = models.ForeignKey(Profile, related_name='admin_users_IDs', on_delete=models.CASCADE)
    reports_IDs             = models.ForeignKey('Report', blank=True, null=True, on_delete=models.SET_NULL)
    users_IDs               = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.circle_ID)







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

    report_ID               = models.AutoField(primary_key=True)
    reason                  = models.CharField(choices=REPORT_REASON, max_length=50, default='A')
    description             = models.CharField(max_length=50, blank=True, null=True)
    reported_user_ID        = models.ForeignKey(Profile, related_name='reported_user_ID', on_delete=models.CASCADE)
    reporting_user_ID       = models.ForeignKey(Profile, related_name='reporting_user_ID', on_delete=models.CASCADE)
    responsible_circle_ID   = models.ForeignKey(Circle, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.report_ID)





class WaitingRoom(models.Model):
    room_ID                     = models.AutoField(primary_key=True)
    users_that_want_to_join_IDs = models.OneToOneField(Profile, null=True, on_delete=models.SET_NULL)
    active_sessions_IDs         = models.ForeignKey('ActiveSession', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.room_ID)






class ActiveSession(models.Model):
    session_ID              = models.AutoField(primary_key=True)
    member1_ID              = models.OneToOneField(WaitingRoom, to_field='users_that_want_to_join_IDs', related_name='member1', unique=True, on_delete=models.CASCADE)
    member2_ID              = models.OneToOneField(WaitingRoom, to_field='users_that_want_to_join_IDs', related_name='member2', unique=True, on_delete=models.CASCADE)
    messages_IDs            = models.ForeignKey('Message', blank=True,  on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.session_ID)







class Message(models.Model):
    message_ID              = models.AutoField(primary_key=True)
    send_time               = models.CharField(max_length=50, blank=True, null=True)
    attachments_URL         = models.CharField(max_length=50, blank=True, null=True)
    type                    = models.CharField(max_length=50, blank=True, null=True)
    content                 = models.CharField(max_length=50, blank=True, null=True)
    sender_ID               = models.ForeignKey(Profile, related_name='sender_ID', on_delete=models.CASCADE)
    reciver_ID              = models.ForeignKey(Profile, related_name='reciver_ID', on_delete=models.CASCADE) 
    active_session_ID       = models.ForeignKey(ActiveSession, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.message_ID)