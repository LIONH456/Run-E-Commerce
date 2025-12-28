from django.db import migrations, connection


def copy_legacy_products(apps, schema_editor):
    """If a legacy `products` table exists, copy its rows into `store_product`.
    This runs only if `store_product` is empty and `products` exists."""
    with connection.cursor() as cursor:
        # Check if legacy table exists
        cursor.execute("SHOW TABLES LIKE 'products'")
        if cursor.fetchone() is None:
            return
        # Check if store_product already has rows
        cursor.execute("SELECT COUNT(*) FROM store_product")
        count = cursor.fetchone()[0]
        if count > 0:
            return
        # Copy data fields (names must match columns)
        cursor.execute("INSERT INTO store_product (product_id, name, description, price, stock, image_url, status, created_at) SELECT product_id, name, description, price, stock, image_url, status, created_at FROM products")


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_legacy_products, reverse_code=migrations.RunPython.noop),
    ]
