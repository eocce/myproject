# Generated by Django 3.2.19 on 2023-08-30 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_remotesensingdata_browsejpgpath'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remotesensingdata',
            name='browsejpgpath',
            field=models.CharField(max_length=255),
        ),
    ]
