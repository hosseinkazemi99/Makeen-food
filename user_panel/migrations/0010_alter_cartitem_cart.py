# Generated by Django 4.1.4 on 2023-04-16 21:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_panel', '0009_alter_cart_created_at_alter_cart_modify_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item', to='user_panel.cart'),
        ),
    ]
