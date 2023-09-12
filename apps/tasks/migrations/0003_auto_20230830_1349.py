# Generated by Django 3.2.16 on 2023-08-30 11:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20230823_1546'),
        ('tasks', '0002_alter_task_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='assigned_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='users.user'),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('In work', 'In Work'), ('Completed', 'Completed'), ('Assigned', 'Assigned')], default='In work', max_length=30),
        ),
    ]