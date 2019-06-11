from django.db import models

# Create your models here.
class UserInfoManager(models.Manager):
    def create(self, account):
        user = UserInfo()
        user.name = account['name']
        user.pwd = account['pwd']
        return user

class UserInfo(models.Model):
    name = models.CharField(max_length=20)
    pwd = models.CharField(max_length=20)
    manager = UserInfoManager()

    def __str__(self):
        return self.name
