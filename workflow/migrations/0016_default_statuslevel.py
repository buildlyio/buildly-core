from django.db import migrations, models
import django.db.models.deletion
import workflow.models


def fill_empty_wfl_status_with_in_progress(apps, schema_editor):
    """All WFL2 without a status should set to 'in_progress' instead of the default 'project_request'."""
    wfl_status_model = apps.get_model('workflow', 'WorkflowLevelStatus')
    wfl_status, _ = wfl_status_model.objects.get_or_create(
        short_name="in_progress",
        defaults={"name": "In progress", "order": 1}
    )
    wfl2_model = apps.get_model('workflow', 'WorkflowLevel2')
    db_alias = schema_editor.connection.alias
    empty_wfl2s = wfl2_model.objects.using(db_alias).filter(status=None)
    for wfl2 in empty_wfl2s:
        print(f"Set empty status of WFL2 {wfl2} to 'in_progress'.")
        wfl2.status = wfl_status
        wfl2.save()


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0015_auto_20190731_1419'),
    ]

    operations = [

        migrations.RunPython(fill_empty_wfl_status_with_in_progress,
                             migrations.RunPython.noop),

        migrations.AlterField(
            model_name='workflowlevel2',
            name='status',
            field=models.ForeignKey(default=workflow.models._get_default_statuslevel, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='workflowlevel2s', to='workflow.WorkflowLevelStatus'),
        ),
    ]
