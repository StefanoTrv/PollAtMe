# Generated by Django 4.1.2 on 2023-03-01 12:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0007_merge_20230217_1805"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="visibility",
            field=models.IntegerField(
                choices=[(1, "Pubblico"), (2, "Nascosto")], default=2
            ),
        ),
    ]
