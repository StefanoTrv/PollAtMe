# Generated by Django 4.1.2 on 2023-03-17 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0014_polloptions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mapping",
            name="poll",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="polls.poll"
            ),
        ),
        migrations.AlterField(
            model_name="polloptions",
            name="poll",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="polls.poll"
            ),
        ),
    ]
