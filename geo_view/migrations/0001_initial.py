# Generated by Django 5.0.6 on 2024-05-26 13:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField(default='')),
                ('title', models.TextField(default='')),
                ('text', models.TextField(default='')),
                ('topic', models.TextField(db_index=True, default='')),
                ('tags', models.TextField(db_index=True, default='')),
                ('date', models.DateField(db_index=True)),
                ('processed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='GeoPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(db_index=True)),
                ('display_name', models.TextField()),
                ('lat', models.FloatField(null=True)),
                ('lon', models.FloatField(null=True)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='geo_view.geoposition')),
            ],
            options={
                'unique_together': {('parent', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote', models.TextField()),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='geo_view.article')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='geo_view.geoposition')),
            ],
        ),
    ]
