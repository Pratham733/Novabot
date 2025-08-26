from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from documents.models import ConvertedFile


class Command(BaseCommand):
	help = 'Delete converted files older than 24 hours'

	def handle(self, *args, **options):
		cutoff = timezone.now() - timedelta(hours=24)
		qs = ConvertedFile.objects.filter(created_at__lt=cutoff)
		count = qs.count()
		for obj in qs:
			try:
				storage = obj.file.storage
				name = obj.file.name
				obj.delete()
				if name and storage.exists(name):
					storage.delete(name)
			except Exception:
				# Swallow exceptions to ensure bulk delete continues
				pass
		self.stdout.write(self.style.SUCCESS(f'Purged {count} converted file(s).'))
