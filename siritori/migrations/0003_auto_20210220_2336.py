# Generated by Django 2.2.18 on 2021-02-20 14:36

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('siritori', '0002_auto_20210220_0203'),
    ]

    operations = [
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kana', models.CharField(max_length=50)),
                ('kanji', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='session',
            name='lastWord',
        ),
        migrations.AddField(
            model_name='link',
            name='dateAdded',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='link',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='siritori.Session'),
        ),
        migrations.AlterField(
            model_name='link',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='siritori.Word'),
        ),
        migrations.AddField(
            model_name='word',
            name='session',
            field=models.ManyToManyField(through='siritori.Link', to='siritori.Session'),
        ),
    ]