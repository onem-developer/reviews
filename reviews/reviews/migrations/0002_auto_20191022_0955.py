# Generated by Django 2.2.3 on 2019-10-22 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='comment_owner',
            new_name='comment_owner_id',
        ),
        migrations.RenameField(
            model_name='item',
            old_name='item_owner',
            new_name='item_owner_id',
        ),
    ]