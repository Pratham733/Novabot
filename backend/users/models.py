from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
	"""Custom user model extending Django's AbstractUser with unique email and optional profile fields."""
	email = models.EmailField('email address', unique=True, blank=True, null=True)
	display_name = models.CharField(max_length=120, blank=True, null=True)
	# avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

	def save(self, *args, **kwargs):
		if self.email:
			self.email = self.email.lower().strip()
		super().save(*args, **kwargs)

	def __str__(self):
		return self.username
