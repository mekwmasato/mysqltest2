# Generated by Django 4.2.4 on 2023-09-21 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_summarized',
            field=models.BooleanField(default=False),
        ),
    ]