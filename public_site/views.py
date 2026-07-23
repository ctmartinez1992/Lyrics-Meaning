from django.shortcuts import get_object_or_404, render

from analysis.models import AnalysisResult
from catalog.models import Album, Band, Song


def _format_analysis_sections(analysis_result: AnalysisResult | None) -> list[dict]:
    if analysis_result is None or not isinstance(analysis_result.detailed_analysis, dict):
        return []

    sections = []
    for key, value in analysis_result.detailed_analysis.items():
        title = str(key).replace("_", " ").title()
        if isinstance(value, list):
            items = [str(item).strip() for item in value if isinstance(item, (str, int, float)) and str(item).strip()]
            if items:
                sections.append({"title": title, "items": items, "text": ""})
        else:
            text = str(value).strip()
            if text:
                sections.append({"title": title, "items": [], "text": text})
    return sections


def _format_analysis_citations(analysis_result: AnalysisResult | None) -> list[dict]:
    if analysis_result is None or not isinstance(analysis_result.citations, list):
        return []

    citations = []
    for raw in analysis_result.citations:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title", "")).strip()
        url = str(raw.get("url", "")).strip()
        excerpt = str(raw.get("excerpt", "")).strip()
        if title and url:
            citations.append({"title": title, "url": url, "excerpt": excerpt})
    return citations


def band_list(request):
    bands = Band.objects.filter(archived_at__isnull=True).order_by("name")
    return render(request, "public_site/band_list.html", {"bands": bands})


def band_detail(request, slug):
    band = get_object_or_404(
        Band.objects.prefetch_related("albums__songs"),
        slug=slug,
        archived_at__isnull=True,
    )
    albums = band.albums.filter(archived_at__isnull=True).order_by("release_date", "title")
    return render(request, "public_site/band_detail.html", {"band": band, "albums": albums})


def album_detail(request, album_id):
    album = get_object_or_404(
        Album.objects.select_related("band").prefetch_related("songs"),
        pk=album_id,
        archived_at__isnull=True,
        band__archived_at__isnull=True,
    )
    songs = album.songs.filter(archived_at__isnull=True).order_by("track_number", "title")
    return render(request, "public_site/album_detail.html", {"album": album, "songs": songs})


def song_detail(request, song_id):
    song = get_object_or_404(
        Song.objects.select_related("album", "album__band")
        .prefetch_related("lyric_versions__lines")
        .filter(archived_at__isnull=True, album__archived_at__isnull=True, album__band__archived_at__isnull=True),
        pk=song_id,
    )
    current_lyrics = song.lyric_versions.filter(is_current=True).order_by("-created_at").first()
    lines = current_lyrics.lines.order_by("line_number") if current_lyrics else []
    analysis_result = AnalysisResult.latest_published_for_song(song.id)
    analysis_sections = _format_analysis_sections(analysis_result)
    analysis_citations = _format_analysis_citations(analysis_result)
    return render(
        request,
        "public_site/song_detail.html",
        {
            "song": song,
            "current_lyrics": current_lyrics,
            "lines": lines,
            "analysis_result": analysis_result,
            "analysis_sections": analysis_sections,
            "analysis_citations": analysis_citations,
        },
    )
