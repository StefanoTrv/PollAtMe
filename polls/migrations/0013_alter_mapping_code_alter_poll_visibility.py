# Generated by Django 4.1.2 on 2023-03-14 16:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0012_merge_20230309_1614"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mapping",
            name="code",
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="poll",
            name="visibility",
            field=models.IntegerField(
                choices=[(1, "Pubblico"), (2, "Nascosto")], default=2
            ),
        ),
    ]