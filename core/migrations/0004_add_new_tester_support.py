# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-29 15:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_alter_compiler_add_obsolete'),
    ]

    operations = [
        migrations.AddField(
            model_name='attempt',
            name='checker_comment',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='attempt',
            name='tester_name',
            field=models.CharField(blank=True, default='', max_length=48),
        ),
        migrations.AddField(
            model_name='testinfo',
            name='checker_comment',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='attempt',
            name='result',
            field=models.CharField(blank=True, db_index=True, max_length=36, null=True),
        ),
        migrations.AlterField(
            model_name='attempt',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='compiler',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='notification',
            name='contest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Contest'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='checker',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='problem',
            name='mask_in',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='problem',
            name='mask_out',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AlterField(
            model_name='problem',
            name='name',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='testinfo',
            name='attempt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Attempt'),
        ),
        migrations.AlterField(
            model_name='testinfo',
            name='result',
            field=models.CharField(blank=True, default='', max_length=23),
        ),
    ]
