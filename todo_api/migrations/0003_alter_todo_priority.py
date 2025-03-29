# Generated by Django 5.1.6 on 2025-03-29 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_api', '0002_alter_todo_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='priority',
            field=models.CharField(choices=[('Hi', 'high'), ('Md', 'middle'), ('Lo', 'low')], default='Md', max_length=3),
        ),
    ]
