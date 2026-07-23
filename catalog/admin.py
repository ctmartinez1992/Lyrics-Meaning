from django.contrib import admin
from django.utils import timezone

from analysis.models import AnalysisJob
from catalog.models import Album, Band, Genre, LyricLine, LyricVersion, Song


class ArchiveOnlyAdmin(admin.ModelAdmin):
    actions = ["archive_selected"]

    @admin.action(description="Archive selected records")
    def archive_selected(self, request, queryset):
        queryset.update(archived_at=timezone.now())

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Band)
class BandAdmin(ArchiveOnlyAdmin):
    list_display = ("name", "archived_at", "updated_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Album)
class AlbumAdmin(ArchiveOnlyAdmin):
    list_display = ("title", "band", "release_date", "archived_at")
    list_filter = ("band", "genres", "archived_at")
    search_fields = ("title", "band__name")
    filter_horizontal = ("genres",)


@admin.register(Song)
class SongAdmin(ArchiveOnlyAdmin):
    list_display = ("title", "album", "track_number", "is_bonus", "archived_at")
    list_filter = ("album__band", "album", "is_bonus", "genres", "archived_at")
    search_fields = ("title", "album__title", "album__band__name")
    filter_horizontal = ("genres",)


@admin.register(Genre)
class GenreAdmin(ArchiveOnlyAdmin):
    list_display = ("name", "parent_genre", "archived_at", "updated_at")
    list_filter = ("parent_genre", "archived_at")
    search_fields = ("name", "slug", "description", "parent_genre__name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(LyricVersion)
class LyricVersionAdmin(admin.ModelAdmin):
    list_display = ("song", "version_label", "is_current", "created_at")
    list_filter = ("is_current", "song__album__band")
    search_fields = ("song__title", "version_label")
    actions = ["enqueue_analysis_jobs"]

    @admin.action(description="Enqueue analysis jobs")
    def enqueue_analysis_jobs(self, request, queryset):
        for lyric_version in queryset.select_related("song"):
            AnalysisJob.enqueue(lyric_version=lyric_version, requested_by=request.user)


@admin.register(LyricLine)
class LyricLineAdmin(admin.ModelAdmin):
    list_display = ("lyric_version", "line_number", "is_separator", "text")
    list_filter = ("is_separator", "lyric_version__song__album__band")
    search_fields = ("text", "lyric_version__song__title")
