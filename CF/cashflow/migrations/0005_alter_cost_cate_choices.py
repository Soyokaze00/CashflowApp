# Generated by Django 5.1.2 on 2024-11-29 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0004_delete_emailconfirmation_remove_parent_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost',
            name='cate_choices',
            field=models.CharField(default='food', max_length=20),
        ),
    ]
