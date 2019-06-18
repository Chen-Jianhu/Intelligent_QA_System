from django.db import models

# Create your models here.
class UserInfoManager(models.Manager):
    def create(self, account):
        user = UserInfo()
        user.name = account['name']
        user.pwd = account['pwd']
        user.sex = account['sex']
        user.age = account['age']
        user.email = account['email']
        user.img_path = account['img_path']
        return user


class UserInfo(models.Model):
    name = models.CharField(max_length=30)
    pwd = models.CharField(max_length=30)
    sex = models.BooleanField(default=True)  # True 男
    age = models.IntegerField(default=18)
    email = models.CharField(max_length=30, null=True, blank=True)
    img_path = models.CharField(max_length=100, default='/static/user/img/user.png')
    manager = UserInfoManager()

    def __str__(self):
        return self.name
