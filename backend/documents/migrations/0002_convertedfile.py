from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

	dependencies = [
		('documents', '0001_initial'),
	]

	operations = [
		migrations.CreateModel(
			name='ConvertedFile',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('original_name', models.CharField(max_length=255)),
				('target_format', models.CharField(max_length=16)),
				('file', models.FileField(upload_to='converted/')),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('meta', models.JSONField(blank=True, default=dict)),
				('owner', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='converted_files', to=settings.AUTH_USER_MODEL)),
			],
			options={'ordering': ['-created_at']},
		),
	]
