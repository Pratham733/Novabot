from django.db import models
from django.conf import settings


class Document(models.Model):
	# Expanded to align with current frontend generator options
	TYPE_CHOICES = [
		("resume", "Resume"),
		("cover_letter", "Cover Letter"),
		("report", "Report"),
		("proposal", "Proposal"),
		("email", "Email"),
		("summary", "Summary"),
		("presentation", "Presentation"),
		("contract", "Contract"),
		("custom", "Custom"),
	]
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
	doc_type = models.CharField(max_length=32, choices=TYPE_CHOICES)
	title = models.CharField(max_length=200)
	content = models.TextField()
	meta = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.doc_type}: {self.title}"


class ConvertedFile(models.Model):
	"""Stores user-uploaded converted files for up to a retention period (planned 24h)."""
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='converted_files')
	original_name = models.CharField(max_length=255)
	target_format = models.CharField(max_length=16)
	file = models.FileField(upload_to='converted/')
	created_at = models.DateTimeField(auto_now_add=True)
	meta = models.JSONField(default=dict, blank=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Converted {self.original_name} -> {self.target_format}"
