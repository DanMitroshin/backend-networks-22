# Generated by Django 3.0.6 on 2022-11-23 20:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.TextField(verbose_name='achievement type')),
                ('value', models.IntegerField(verbose_name='value')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('coins', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(max_length=20, verbose_name='activity type')),
                ('payload', models.TextField(blank=True, null=True, verbose_name='activity payload, if provided')),
                ('timestamp', models.DateField(auto_now_add=True, verbose_name='timestamp')),
            ],
        ),
        migrations.CreateModel(
            name='AnswersProgressState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Day of state')),
                ('total_answers', models.IntegerField(verbose_name='Total amount of answers')),
                ('total_right_answers', models.IntegerField(verbose_name='Total amount of right answers')),
                ('answers_per_day', models.IntegerField(verbose_name='Amount of answers per day')),
                ('right_answers_per_day', models.IntegerField(verbose_name='Amount of right answers per day')),
                ('top_percent', models.IntegerField(blank=True, null=True, verbose_name='Top percent of user among other results this day')),
            ],
        ),
        migrations.CreateModel(
            name='GenerateLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='date')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
                ('amount', models.IntegerField(verbose_name='amount')),
            ],
        ),
        migrations.CreateModel(
            name='InitLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(verbose_name='title')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
                ('version', models.IntegerField(verbose_name='version')),
                ('device', models.CharField(default='a', max_length=10, verbose_name='current_device')),
            ],
        ),
        migrations.CreateModel(
            name='MetricsCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('day', models.DateField()),
                ('average', models.FloatField(blank=True, default=0, null=True)),
                ('metric', models.CharField(blank=True, max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
                ('time_to_complete', models.DurationField(default=datetime.timedelta(0), verbose_name='Product completion time')),
                ('completed', models.IntegerField(default=0, verbose_name='number of completed blocks')),
            ],
        ),
        migrations.CreateModel(
            name='ProductProgress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.IntegerField(default=0, verbose_name='number of completed blocks')),
            ],
        ),
        migrations.CreateModel(
            name='TrainerBlockLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
                ('is_valid', models.BooleanField(default=False, verbose_name='is answer valid')),
                ('answer', models.CharField(blank=True, max_length=100, verbose_name='answer')),
            ],
        ),
        migrations.CreateModel(
            name='TrainerBlockProgress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempts', models.IntegerField(default=0)),
                ('successful_attempts', models.IntegerField(default=0)),
                ('balance', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['balance'],
            },
        ),
        migrations.CreateModel(
            name='UserAnswerForReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')),
                ('problem', models.IntegerField(blank=True, choices=[(3, 'Errors in question'), (2, 'Unsuitable test theme for question'), (1, 'This question repeats in test'), (4, 'Suggestion of new answer'), (100, 'Other problems')], null=True, verbose_name='Problem')),
                ('answer', models.TextField(verbose_name='User answer')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='User comment')),
                ('status', models.IntegerField(choices=[(0, 'Waiting for review'), (1, 'Accepted'), (2, 'Rejected')], default=0, verbose_name='Status of review')),
            ],
        ),
        migrations.CreateModel(
            name='UserMetric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(default='0', verbose_name='value')),
                ('metric', models.TextField(verbose_name='metric')),
            ],
        ),
        migrations.CreateModel(
            name='WeekRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(verbose_name='value')),
                ('status', models.IntegerField(verbose_name='status')),
                ('best_place', models.IntegerField(blank=True, null=True, verbose_name='best_place')),
            ],
            options={
                'ordering': ['-value'],
            },
        ),
    ]
