# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('salt_path', models.CharField(unique=True, max_length=200, verbose_name=b'git\xe8\xb7\xaf\xe5\xbe\x84')),
                ('target_path', models.CharField(max_length=200, verbose_name=b'\xe6\x9c\xac\xe5\x9c\xb0\xe8\xb7\xaf\xe5\xbe\x84')),
                ('auth', models.CharField(max_length=200, verbose_name=b'\xe6\x9d\x83\xe9\x99\x90')),
                ('user_group', models.CharField(max_length=200, verbose_name=b'\xe5\xb1\x9e\xe7\xbb\x84')),
                ('user', models.CharField(max_length=200, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7')),
                ('md5', models.CharField(max_length=200, verbose_name=b'md5\xe5\x80\xbc')),
                ('update_time', models.CharField(max_length=200, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
            ],
        ),
        migrations.CreateModel(
            name='OperationRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('salt_path', models.CharField(max_length=200, verbose_name=b'\xe6\x9c\xac\xe5\x9c\xb0\xe8\xb7\xaf\xe5\xbe\x84')),
                ('action', models.CharField(max_length=200, verbose_name=b'\xe5\x8a\xa8\xe4\xbd\x9c')),
                ('operate_time', models.CharField(max_length=200, verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe6\x97\xb6\xe9\x97\xb4')),
                ('file_info_id', models.CharField(max_length=200, verbose_name=b'\xe6\x96\x87\xe4\xbb\xb6id')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.CharField(max_length=200, verbose_name=b'\xe4\xba\xa7\xe5\x93\x81\xe7\xba\xbf')),
                ('cluster_name', models.CharField(max_length=200, verbose_name=b'\xe9\x9b\x86\xe7\xbe\xa4\xe5\x90\x8d')),
                ('install_path', models.CharField(max_length=200, verbose_name=b'\xe5\xae\x89\xe8\xa3\x85\xe8\xb7\xaf\xe5\xbe\x84', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='fileinfo',
            name='service_info',
            field=models.ForeignKey(to='filemanage.ServiceInfo'),
        ),
    ]
