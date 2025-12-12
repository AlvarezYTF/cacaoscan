# Generated migration to improve ActivityLog using ContentType for advanced referential integrity
# Note: ActivityLog does NOT violate normalization - it's a flexible audit table using Django's ContentType pattern
# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


def migrate_resource_type_to_contenttype(apps, schema_editor):
    """
    Migrate existing resource_type and resource_id to content_type and object_id.
    Maps resource_type strings to ContentType objects.
    """
    ActivityLog = apps.get_model('audit', 'ActivityLog')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Map of resource_type strings to app_label.model_name
    resource_type_mapping = {
        'CacaoImage': 'images_app.cacaoimage',
        'CacaoPrediction': 'images_app.cacaoprediction',
        'Finca': 'fincas_app.finca',
        'Lote': 'fincas_app.lote',
        'UserProfile': 'auth_app.userprofile',
        'EmailVerificationToken': 'auth_app.emailverificationtoken',
        'TrainingJob': 'training.trainingjob',
        'ModelMetrics': 'training.modelmetrics',
        'ReporteGenerado': 'reports.reportegenerado',
        'Notification': 'notifications.notification',
        'Persona': 'personas.persona',
    }
    
    logs = ActivityLog.objects.filter(resource_type__isnull=False).exclude(resource_type='')
    migrated = 0
    skipped = 0
    
    for log in logs:
        resource_type = log.resource_type
        resource_id = log.resource_id
        
        if not resource_id:
            skipped += 1
            continue
        
        # Find the mapping
        model_path = resource_type_mapping.get(resource_type)
        if not model_path:
            # Try to find ContentType by app_label and model name
            try:
                app_label, model_name = resource_type.lower(), resource_type.lower()
                # Try common patterns
                if 'cacao' in resource_type.lower():
                    app_label = 'images_app'
                    model_name = 'cacaoimage' if 'image' in resource_type.lower() else 'cacaoprediction'
                elif 'finca' in resource_type.lower():
                    app_label = 'fincas_app'
                    model_name = 'finca'
                elif 'lote' in resource_type.lower():
                    app_label = 'fincas_app'
                    model_name = 'lote'
                elif 'user' in resource_type.lower() or 'profile' in resource_type.lower():
                    app_label = 'auth_app'
                    model_name = 'userprofile'
                elif 'training' in resource_type.lower() or 'job' in resource_type.lower():
                    app_label = 'training'
                    model_name = 'trainingjob'
                elif 'reporte' in resource_type.lower():
                    app_label = 'reports'
                    model_name = 'reportegenerado'
                elif 'notification' in resource_type.lower():
                    app_label = 'notifications'
                    model_name = 'notification'
                elif 'persona' in resource_type.lower():
                    app_label = 'personas'
                    model_name = 'persona'
                
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            except ContentType.DoesNotExist:
                skipped += 1
                continue
        else:
            app_label, model_name = model_path.split('.')
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            except ContentType.DoesNotExist:
                skipped += 1
                continue
        
        # Update the log
        log.content_type = content_type
        log.object_id = resource_id
        log.save(update_fields=['content_type', 'object_id'])
        migrated += 1
    
    print(f"Migrated {migrated} logs, skipped {skipped} logs")


def reverse_migrate_contenttype_to_resource_type(apps, schema_editor):
    """
    Reverse migration: populate resource_type and resource_id from content_type and object_id.
    """
    ActivityLog = apps.get_model('audit', 'ActivityLog')
    
    logs = ActivityLog.objects.filter(content_type__isnull=False)
    
    for log in logs:
        if log.content_type:
            log.resource_type = f"{log.content_type.app_label}.{log.content_type.model}"
            log.resource_id = log.object_id
            log.save(update_fields=['resource_type', 'resource_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0008_alter_loginhistory_failure_reason'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        # Add new ContentType fields for advanced referential integrity
        migrations.AddField(
            model_name='activitylog',
            name='content_type',
            field=models.ForeignKey(
                blank=True,
                help_text='Tipo de recurso afectado (usando ContentType para auditoría flexible)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='contenttypes.contenttype'
            ),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='object_id',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='ID del recurso afectado',
                null=True
            ),
        ),
        # Migrate existing data
        migrations.RunPython(
            migrate_resource_type_to_contenttype,
            reverse_migrate_contenttype_to_resource_type,
        ),
        # Add index for new fields
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['content_type', 'object_id'], name='api_activity_content_idx'),
        ),
    ]

