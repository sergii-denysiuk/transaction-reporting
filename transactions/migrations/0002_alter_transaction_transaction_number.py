from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="transaction_number",
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
