# Generated by Django 4.2.13 on 2024-06-28 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='news',
            field=models.CharField(choices=[('NW', 'Новость'), ('SE', 'Статья')], default='NW', max_length=2),
        ),
    ]
