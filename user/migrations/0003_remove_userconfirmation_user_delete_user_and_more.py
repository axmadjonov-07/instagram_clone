# Generated by Django 5.0.4 on 2024-05-08 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_id_alter_userconfirmation_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userconfirmation',
            name='user',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.DeleteModel(
            name='UserConfirmation',
        ),
    ]
