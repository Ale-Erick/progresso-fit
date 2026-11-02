from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("metricas", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="metricacorporal",
            old_name="braco",
            new_name="braco_esq",
        ),
        migrations.AddField(
            model_name="metricacorporal",
            name="peitoral",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="metricacorporal",
            name="braco_dir",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="metricacorporal",
            name="abdomen",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="metricacorporal",
            name="coxa_esq",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="metricacorporal",
            name="coxa_dir",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="metricacorporal",
            name="panturrilha_esq",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="metricacorporal",
            name="panturrilha_dir",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
