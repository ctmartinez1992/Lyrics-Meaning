from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ArchivableModel(models.Model):
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def archive(self):
        if self.archived_at is None:
            self.archived_at = timezone.now()
            self.save(update_fields=["archived_at"])


class Band(TimestampedModel, ArchivableModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Genre(TimestampedModel, ArchivableModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent_genre = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subgenres",
    )

    class Meta:
        ordering = ["name"]

    def clean(self):
        if self.parent_genre_id is None:
            return

        if self.pk and self.parent_genre_id == self.pk:
            raise ValidationError({"parent_genre": "A genre cannot be its own parent."})

        ancestor = self.parent_genre
        while ancestor is not None:
            if self.pk and ancestor.pk == self.pk:
                raise ValidationError({"parent_genre": "A genre cannot be a descendant of itself."})
            ancestor = ancestor.parent_genre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Album(TimestampedModel, ArchivableModel):
    band = models.ForeignKey(Band, on_delete=models.PROTECT, related_name="albums")
    title = models.CharField(max_length=255)
    release_date = models.DateField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True, related_name="albums")

    class Meta:
        ordering = ["title"]
        constraints = [
            models.UniqueConstraint(fields=["band", "title"], name="uniq_album_title_per_band"),
        ]

    def __str__(self):
        return f"{self.band.name} - {self.title}"


class Song(TimestampedModel, ArchivableModel):
    album = models.ForeignKey(Album, on_delete=models.PROTECT, related_name="songs")
    title = models.CharField(max_length=255)
    track_number = models.PositiveIntegerField(null=True, blank=True)
    is_bonus = models.BooleanField(default=False)
    genres = models.ManyToManyField(Genre, blank=True, related_name="songs")

    class Meta:
        ordering = ["title"]
        constraints = [
            models.UniqueConstraint(fields=["album", "title"], name="uniq_song_title_per_album"),
        ]

    def __str__(self):
        return f"{self.album.title} - {self.title}"


class LyricVersion(TimestampedModel):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="lyric_versions")
    version_label = models.CharField(max_length=100, default="original")
    lyrics_text = models.TextField()
    source = models.CharField(max_length=255, blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["song", "version_label"], name="uniq_lyric_version_label"),
            models.UniqueConstraint(
                fields=["song"],
                condition=Q(is_current=True),
                name="uniq_current_lyric_version_per_song",
            ),
        ]

    def clean(self):
        if self.is_current and not self.song_id:
            raise ValidationError("Current lyric versions must belong to a song.")

    def save(self, *args, **kwargs):
        self.clean()
        with transaction.atomic():
            if self.is_current and self.song_id:
                (
                    LyricVersion.objects.filter(song=self.song, is_current=True)
                    .exclude(pk=self.pk)
                    .update(is_current=False)
                )
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.song.title} [{self.version_label}]"


class LyricLine(TimestampedModel):
    lyric_version = models.ForeignKey(LyricVersion, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    is_separator = models.BooleanField(default=False)
    text = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["line_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["lyric_version", "line_number"],
                name="uniq_line_number_per_lyric_version",
            )
        ]

    def clean(self):
        if not self.is_separator and not (self.text or "").strip():
            raise ValidationError({"text": "Text is required when line is not a separator."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lyric_version} line {self.line_number}"
