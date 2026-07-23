from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from analysis.models import AnalysisJob
from analysis.services import process_job
from catalog.models import LyricVersion, Song


class Command(BaseCommand):
    help = "Analyze a song by ID and persist analysis result."

    def add_arguments(self, parser):
        parser.add_argument("--song-id", type=int, required=True)
        parser.add_argument("--lyric-version-id", type=int, required=False)
        parser.add_argument("--refresh", action="store_true")

    def handle(self, *args, **options):
        song_id = options["song_id"]
        lyric_version_id = options.get("lyric_version_id")
        refresh = options["refresh"]

        song = Song.objects.filter(pk=song_id).first()
        if song is None:
            raise CommandError(f"Song {song_id} does not exist.")

        if lyric_version_id is not None:
            lyric_version = LyricVersion.objects.filter(pk=lyric_version_id, song_id=song.id).first()
            if lyric_version is None:
                raise CommandError(f"Lyric version {lyric_version_id} does not exist for song {song_id}.")
        else:
            lyric_version = song.lyric_versions.filter(is_current=True).order_by("-created_at").first()
            if lyric_version is None:
                raise CommandError(f"Song {song_id} has no current lyric version.")

        job, _ = AnalysisJob.enqueue(lyric_version=lyric_version)
        if refresh:
            with transaction.atomic():
                locked_job = AnalysisJob.objects.select_for_update().get(pk=job.pk)
                locked_job.status = AnalysisJob.Status.QUEUED
                locked_job.error_reason = ""
                locked_job.completed_at = None
                locked_job.save(update_fields=["status", "error_reason", "completed_at", "updated_at"])
                job = locked_job

        processed_job = process_job(job.pk)
        self.stdout.write(
            self.style.SUCCESS(
                f"Song {song_id} analyzed with job {processed_job.id} status={processed_job.status} attempts={processed_job.attempts}"
            )
        )
