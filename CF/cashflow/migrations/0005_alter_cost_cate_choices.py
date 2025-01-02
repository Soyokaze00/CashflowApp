# Generated by Django 5.1.2 on 2024-12-11 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0004_alter_cost_cate_choices_alter_goals_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost',
            name='cate_choices',
            field=models.CharField(choices=[('needs', 'نیازها'), ('wants', 'خواسته ها'), ('else', 'سایر'), ('parent', 'والدین'), ('part_time_job', 'کار نیمه\u200cوقت'), ('other', 'دیگر')], default='needs', max_length=20),
        ),
    ]
