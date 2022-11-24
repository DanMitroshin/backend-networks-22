# Generated by Django 3.0.6 on 2022-11-23 20:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialquestionanswer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='access_groups',
            field=models.ManyToManyField(blank=True, related_name='products', to='Content.AccessGroup'),
        ),
        migrations.AddField(
            model_name='product',
            name='content_theme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentTheme'),
        ),
        migrations.AddField(
            model_name='product',
            name='media_blocks',
            field=models.ManyToManyField(blank=True, related_name='media', to='Content.MediaBlock', verbose_name='Media blocks'),
        ),
        migrations.AddField(
            model_name='product',
            name='trainer_blocks',
            field=models.ManyToManyField(blank=True, related_name='trainers', to='Content.TrainerBlock', verbose_name='Trainer blocks'),
        ),
        migrations.AddField(
            model_name='contentvideo',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddField(
            model_name='contentvideo',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Content.VideoInformation', verbose_name='Video'),
        ),
        migrations.AddField(
            model_name='contenttheme',
            name='video',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentVideo', verbose_name='Video'),
        ),
        migrations.AddField(
            model_name='contentterm',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddField(
            model_name='contentsculpture',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddField(
            model_name='contentpicture',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddField(
            model_name='contentperson',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddField(
            model_name='contentmap',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddField(
            model_name='contentliterature',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddField(
            model_name='contenthistorytext',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddField(
            model_name='contentevent',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddConstraint(
            model_name='contententity',
            constraint=models.UniqueConstraint(fields=('table', 'index'), name='table_index_unique'),
        ),
        migrations.AddField(
            model_name='contentdialoganswer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contentarchitecture',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Content.ContentEntity'),
        ),
        migrations.AddField(
            model_name='associate',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
