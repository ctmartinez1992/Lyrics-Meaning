import uuid

from django.conf import settings
from django.db import models

from catalog.models import LyricVersion, Song


class AnalysisJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"

    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="analysis_jobs")
    lyric_version = models.ForeignKey(LyricVersion, on_delete=models.CASCADE, related_name="analysis_jobs")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_analysis_jobs",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    idempotency_key = models.CharField(max_length=64, unique=True, db_index=True)
    attempts = models.PositiveIntegerField(default=0)
    error_reason = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def build_idempotency_key(cls, lyric_version_id: int) -> str:
        namespace = uuid.UUID("66b5f31f-a6cf-4632-a5d6-bd8343fb0e0c")
        return uuid.uuid5(namespace, f"lyric-version:{lyric_version_id}").hex

    @classmethod
    def enqueue(cls, *, lyric_version: LyricVersion, requested_by=None) -> tuple["AnalysisJob", bool]:
        key = cls.build_idempotency_key(lyric_version.id)
        return cls.objects.get_or_create(
            idempotency_key=key,
            defaults={
                "song": lyric_version.song,
                "lyric_version": lyric_version,
                "requested_by": requested_by,
                "status": cls.Status.QUEUED,
            },
        )

    def __str__(self):
        return f"AnalysisJob<{self.song_id}:{self.status}>"


class AnalysisResult(models.Model):
    job = models.OneToOneField(AnalysisJob, on_delete=models.CASCADE, related_name="result")
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="analysis_results")
    lyric_version = models.ForeignKey(
        LyricVersion,
        on_delete=models.CASCADE,
        related_name="analysis_results",
    )
    summary = models.TextField()
    key_themes = models.JSONField(default=list)
    detailed_analysis = models.JSONField(default=dict)
    citations = models.JSONField(default=list)
    model_identifier = models.CharField(max_length=255)
    prompt_version = models.CharField(max_length=100)
    provider_metadata = models.JSONField(default=dict)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def latest_published_for_song(cls, song_id: int) -> "AnalysisResult | None":
        return (
            cls.objects.filter(song_id=song_id, is_published=True)
            .order_by("-published_at", "-created_at")
            .first()
        )

    def __str__(self):
        return f"AnalysisResult<{self.song_id}:{self.model_identifier}>"
