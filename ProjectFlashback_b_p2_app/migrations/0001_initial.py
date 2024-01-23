# Generated by Django 5.0.1 on 2024-01-23 00:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CookieUser',
            fields=[
                ('cookie', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('requestCount', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('storyId', models.AutoField(primary_key=True, serialize=False)),
                ('storyTitle', models.CharField(max_length=100)),
                ('storyPrompt', models.CharField(max_length=200)),
                ('userCreator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ProjectFlashback_b_p2_app.cookieuser')),
            ],
        ),
        migrations.CreateModel(
            name='StoryStage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stageNumber', models.IntegerField()),
                ('stageStory', models.CharField(max_length=5000)),
                ('illustrationStyle', models.CharField(max_length=100)),
                ('imgPrompt', models.CharField(max_length=1000)),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ProjectFlashback_b_p2_app.story')),
            ],
        ),
    ]
