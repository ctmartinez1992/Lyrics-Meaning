from django.contrib import admin
from django.utils.html import format_html

from analysis.models import AnalysisJob, AnalysisResult


@admin.register(AnalysisJob)
class AnalysisJobAdmin(admin.ModelAdmin):
    list_display = ("id", "song", "lyric_version", "status", "attempts", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("song__title", "lyric_version__version_label", "idempotency_key")
    readonly_fields = ("created_at", "updated_at", "started_at", "completed_at")

    def has_add_permission(self, request):
        return False


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "song",
        "model_identifier",
        "prompt_version",
        "is_published",
        "published_at",
        "citation_count",
        "job_link",
    )
    list_filter = ("is_published", "model_identifier", "prompt_version")
    search_fields = ("song__title", "summary")
    readonly_fields = ("created_at", "job_link")

    @admin.display(description="Citations")
    def citation_count(self, obj):
        return len(obj.citations or [])

    @admin.display(description="Job")
    def job_link(self, obj):
        return format_html('<a href="/admin/analysis/analysisjob/{}/change/">{}</a>', obj.job_id, obj.job_id)
