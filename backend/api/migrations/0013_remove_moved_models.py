# Generated manually - Remove models that were moved to modular apps
# Models moved:
# - LoginHistory → audit app
# - ReporteGenerado → reports app
# - ModelMetrics → training app
# 
# Note: The tables remain in the database with the same names (api_loginhistory, etc.)
# The models are now defined in their respective apps with db_table to maintain compatibility.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_cacaoimage_metadata'),
        ('audit', '0001_add_loginhistory'),  # Ensure audit migration runs first
        ('reports', '0001_add_reportegenerado'),  # Ensure reports migration runs first
        ('training', '0001_add_modelmetrics'),  # Ensure training migration runs first
    ]

    operations = [
        # No operations needed - models are removed from api/models.py
        # The tables remain in the database and are now managed by their respective apps
        # This migration serves as a marker that the models have been moved
    ]

