# Generated by Django 5.0.6 on 2024-07-24 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_company_employees_est_num_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="filed",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Date Filed"
            ),
        ),
    ]