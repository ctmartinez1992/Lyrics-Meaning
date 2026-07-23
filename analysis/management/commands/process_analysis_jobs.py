from django.core.management.base import BaseCommand

from analysis.services import process_queued_jobs


class Command(BaseCommand):
    help = "Process queued analysis jobs."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=20)

    def handle(self, *args, **options):
        processed = process_queued_jobs(limit=options["limit"])
        self.stdout.write(self.style.SUCCESS(f"Processed {len(processed)} analysis jobs"))

