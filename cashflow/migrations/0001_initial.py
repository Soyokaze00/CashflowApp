# Generated by Django 5.1.2 on 2024-11-27 12:37

import cashflow.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=20)),
                ('date', models.CharField(default=cashflow.models.get_persian_date, max_length=10)),
                ('description', models.CharField(max_length=200)),
                ('cate_choices', models.CharField(choices=[('food', 'خوراکی'), ('needs', 'موارد ضروری'), ('education', 'آموزش'), ('health_cosmetics', 'مواد بهداشتی و آرایشی'), ('clothes', 'لباس'), ('else', 'سایر')], default='food', max_length=20)),
                ('type', models.CharField(choices=[('expense', 'برآمد'), ('income', 'درآمد')], default='expense', max_length=10)),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='costs', to='cashflow.child')),
            ],
        ),
        migrations.AddField(
            model_name='child',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='cashflow.parent'),
        ),
    ]