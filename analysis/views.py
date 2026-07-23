from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from analysis.models import AnalysisJob
from catalog.models import LyricVersion


@staff_member_required
@require_POST
def trigger_analysis(request: HttpRequest, lyric_version_id: int) -> HttpResponseRedirect:
    lyric_version = get_object_or_404(LyricVersion, pk=lyric_version_id)
    job, created = AnalysisJob.enqueue(lyric_version=lyric_version, requested_by=request.user)
    if created:
        messages.success(request, f"Analysis job {job.id} queued.")
    else:
        messages.info(request, f"Analysis job {job.id} already exists for this lyric version.")
    return redirect(request.META.get("HTTP_REFERER") or "admin:catalog_lyricversion_changelist")
