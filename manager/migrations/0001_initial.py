# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ManagerInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('pwd', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='QA',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('question', models.CharField(max_length=500)),
                ('answer', models.CharField(max_length=5000)),
                ('question_cut', models.CharField(max_length=550)),
                ('answer_cut', models.CharField(max_length=5500)),
                ('subject', models.CharField(max_length=100)),
                ('is_delete', models.BooleanField(default=False)),
            ],
        ),
    ]
