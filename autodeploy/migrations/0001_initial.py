# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='t_exec_error_log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('error_info', models.TextField(max_length=4000, verbose_name=b'\xe9\x94\x99\xe8\xaf\xaf\xe4\xbf\xa1\xe6\x81\xaf')),
                ('no', models.IntegerField(verbose_name=b'\xe5\x8d\x95\xe5\x8f\xb7')),
                ('task_id', models.CharField(max_length=50, verbose_name=b'\xe4\xbb\xbb\xe5\x8a\xa1\xe5\x8f\xb7')),
            ],
        ),
        migrations.CreateModel(
            name='t_exec_jid_detail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jid', models.CharField(max_length=30, verbose_name=b'\xe4\xbb\xbb\xe5\x8a\xa1ID')),
                ('ip', models.CharField(max_length=15, verbose_name=b'\xe6\x9c\x8d\xe5\x8a\xa1\xe5\x99\xa8IP')),
                ('result', models.CharField(max_length=10, verbose_name=b'\xe6\x89\xa7\xe8\xa1\x8c\xe7\xbb\x93\xe6\x9e\x9c')),
                ('detail', models.TextField(max_length=4000, verbose_name=b'\xe8\xaf\xa6\xe7\xbb\x86')),
                ('donetime', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\xae\x8c\xe6\x88\x90\xe6\x97\xb6\xe9\x97\xb4')),
            ],
        ),
        migrations.CreateModel(
            name='t_exec_log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.CharField(max_length=50, verbose_name=b'\xe4\xbb\xbb\xe5\x8a\xa1\xe5\x8f\xb7')),
            ],
        ),
        migrations.CreateModel(
            name='t_exec_mapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jid', models.CharField(max_length=30, verbose_name=b'\xe4\xbb\xbb\xe5\x8a\xa1ID')),
                ('ip_list', models.TextField(max_length=4000, verbose_name=b'IP\xe5\x88\x97\xe8\xa1\xa8')),
                ('command', models.CharField(max_length=50, verbose_name=b'\xe5\x91\xbd\xe4\xbb\xa4')),
                ('no', models.IntegerField(verbose_name=b'\xe5\x8d\x95\xe5\x8f\xb7')),
                ('task_id', models.CharField(max_length=50, verbose_name=b'\xe4\xbb\xbb\xe5\x8a\xa1\xe5\x8f\xb7')),
            ],
        ),
    ]
