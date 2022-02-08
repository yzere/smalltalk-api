from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth import User


class CustomUser(AbstractUser):

    def __str__(self):
            return self.email

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

    reason                  = models.CharField(choices=REPORT_REASON, max_length=30, default='A')
    description             = models.TextField(max_length=255)
    reportedUserID          = models.CharField(max_length=255, null=True)               #do zmiany
    reportingUserID         = models.CharField(max_length=255, null=True)               #do zmiany
    responsibleCircleID     = models.CharField(max_length=255)                          #do zmiany

    def __str__(self):
        return self.reason

class Circle(models.Model):
    name                = models.CharField(max_length=255)
    # For further development
    # localization        = models.CharField(max_length=255)
    description         = models.TextField()
    admins              = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    expireDate          = models.DateTimeField()
    creationDate        = models.DateTimeField(auto_now_add=True)
    maxUsers            = models.IntegerField()
    #reportsID           = models.JSONField(models.ForeignKey(Report, null=True, on_delete=models.PROTECT), null=True)                    #do zmiany
    #usersID             = models.CharField(blank=True, null=True, max_length=255)                    #do zmiany
    stats               = models.JSONField(blank=True, null=True)                    #do zmiany

    def __str__(self):
        return self.name

class CircleReports(models.Model):
    name = models.CharField(max_length=255)
    circleID = models.ForeignKey(Circle, on_delete=models.CASCADE)
    reportID = models.ForeignKey(Report, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class CircleUsers(models.Model):
    name = models.CharField(max_length=255)
    circleID = models.ForeignKey(Circle, on_delete=models.CASCADE)
    userID = models.ManyToManyField(CustomUser)

    def __str__(self):
        return self.name

class Message(models.Model):
    sendTime                = models.CharField(max_length=255)         #do zmiany
    senderUserID            = models.CharField(max_length=255)         #do zmiany
    reciverUserID           = models.CharField(max_length=255)         #do zmiany

    def __str__(self):
        return self.sendTime