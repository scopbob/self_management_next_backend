# Generated by Django 5.1.6 on 2025-03-29 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='priority',
            field=models.IntegerField(choices=[('Hi', 'high'), ('Md', 'middle'), ('Lo', 'low')], default='Md'),
        ),
    ]
