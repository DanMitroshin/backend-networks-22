# Generated by Django 3.0.6 on 2022-11-23 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='QueuePushNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveSmallIntegerField(default=10)),
                ('timestamp', models.DateTimeField()),
                ('status', models.SmallIntegerField()),
                ('tokens', models.TextField()),
                ('title', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('data', models.TextField()),
            ],
            options={
                'ordering': ['priority', 'timestamp'],
            },
        ),
    ]
