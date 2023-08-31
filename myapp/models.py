from django.contrib.auth.models import User
from django.db import models

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # 你的额外字段
#     phone_number = models.CharField(max_length=20)
#     address = models.CharField(max_length=200)

class RemoteSensingData(models.Model):
    zname = models.CharField(max_length=200)
    zpath = models.CharField(max_length=200)
    MSname = models.CharField(max_length=200)
    MSpath = models.CharField(max_length=200)
    PAname = models.CharField(max_length=200)
    PApath = models.CharField(max_length=200)
    CloudPercent = models.FloatField()
    GeodeticInfo = models.JSONField()
    browsejpgpath = models.CharField(max_length=255)
    ProductTime = models.DateTimeField()

    class Meta:
        app_label = 'myapp'

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=200)
    upload_time = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)