# Generated by Django 5.0.6 on 2024-07-12 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donate_blood', '0007_alter_useraccount_blood_group_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='mobile_no',
            field=models.CharField(max_length=50),
        ),
    ]
