from django.db import models

# Create your models here.


class ManagerInfo(models.Model):
    name = models.CharField(max_length=20)
    pwd = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class QAManager(models.Manager):
    def create(self, qa):
        '''
        新建一个问题
        :param qa:一个字典，里面包含问题和答案
        :return: 一个QA对
        '''
        new_qa = QA()
        new_qa.question = qa['question']
        new_qa.answer = qa['answer']
        return new_qa


class QA(models.Model):
    subject = models.CharField(max_length=100)          # 问题主题
    question = models.CharField(max_length=500)         # 问题字段
    answer = models.CharField(max_length=5000)          # 答案
    answer_link = models.CharField(max_length=100)      # 答案链接
    question_cut = models.CharField(max_length=550)     # 问题分词
    answer_cut = models.CharField(max_length=5500)      # 答案分词
    is_delete = models.BooleanField(default=False)
    manager = QAManager()

    def __str__(self):
        return self.question
