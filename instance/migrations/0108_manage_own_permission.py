# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-09-27 15:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0107_openedxappserver_terminated'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instancereference',
            options={'ordering': ['-created'], 'permissions': (('manage_own', 'Can manage own instances.'),)},
        ),
    ]
