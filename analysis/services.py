import json
import logging
import os
from datetime import UTC, datetime
from urllib import error as url_error
from urllib import parse, request

from django.db import transaction
from django.utils import timezone

from analysis.models import AnalysisJob, AnalysisResult


logger = logging.getLogger("analysis.pipeline")

PROMPT_VERSION = "v2-in-depth"
DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
WIKIPEDIA_SUMMARY_ENDPOINT = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"


def _extract_json_payload(raw_text: str) -> dict:
    payload_text = (raw_text or "").strip()
    if not payload_text:
        raise ValueError("Together AI returned empty content.")

    start = payload_text.find("{")
    end = payload_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Together AI response did not contain a JSON object.")

    try:
        payload = json.loads(payload_text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"Together AI response was not valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("Together AI response JSON must be an object.")
    return payload


def _normalize_payload(payload: dict) -> tuple[str, list[str], dict]:
    summary = payload.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("Together AI response must include a non-empty 'summary' string.")

    key_themes = payload.get("key_themes")
    if not isinstance(key_themes, list):
        raise ValueError("Together AI response must include 'key_themes' as a list of strings.")

    cleaned_themes = [theme.strip() for theme in key_themes if isinstance(theme, str) and theme.strip()]
    if not cleaned_themes:
        raise ValueError("Together AI response 'key_themes' cannot be empty.")

    detailed_analysis = payload.get("detailed_analysis")
    if not isinstance(detailed_analysis, dict) or not detailed_analysis:
        raise ValueError("Together AI response must include 'detailed_analysis' as a non-empty object.")

    return summary.strip(), cleaned_themes[:8], detailed_analysis


def _collect_wikipedia_context(search_queries: list[str], *, max_sources: int = 4) -> list[dict]:
    citations: list[dict] = []
    seen_urls: set[str] = set()
    now = datetime.now(UTC).isoformat()

    for query in search_queries:
        if len(citations) >= max_sources:
            break
        term = query.strip()
        if not term:
            continue

        endpoint = WIKIPEDIA_SUMMARY_ENDPOINT.format(parse.quote(term.replace(" ", "_")))
        req = request.Request(endpoint, headers={"User-Agent": "lyrics-meaning-analyzer/1.0"})
        try:
            with request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (url_error.URLError, TimeoutError, json.JSONDecodeError):
            continue

        url = data.get("content_urls", {}).get("desktop", {}).get("page")
        extract = (data.get("extract") or "").strip()
        title = (data.get("title") or term).strip()
        if not url or not extract or url in seen_urls:
            continue

        seen_urls.add(url)
        citations.append(
            {
                "source": "wikipedia",
                "title": title,
                "url": url,
                "excerpt": extract[:600],
                "retrieved_at": now,
            }
        )

    return citations


def _build_user_prompt(*, song_title: str, album_title: str, band_name: str, lyrics_text: str, citations: list[dict]) -> str:
    citation_lines = [
        f"- {citation.get('title', 'Unknown')}: {citation.get('excerpt', '')} (URL: {citation.get('url', '')})"
        for citation in citations
    ]
    web_context = "\n".join(citation_lines) if citation_lines else "- No external context found."

    return f"""
Analyze the song deeply and return strict JSON only.

Song: {song_title}
Album: {album_title}
Artist/Band: {band_name}

Lyrics (canonical):
{lyrics_text}

Web context:
{web_context}

Return ONLY valid JSON with this shape:
{{
  "summary": "2-4 sentence high-level interpretation",
  "key_themes": ["theme 1", "theme 2", "theme 3"],
  "detailed_analysis": {{
    "narrative_arc": "string",
    "emotional_journey": "string",
    "literary_devices": ["device and evidence", "device and evidence"],
    "cultural_historical_context": "string",
    "line_level_observations": ["observation 1", "observation 2"],
    "alternative_interpretations": ["interpretation 1", "interpretation 2"],
    "overall_meaning": "string"
  }}
}}
""".strip()


def _request_together_chat(*, api_key: str, model_identifier: str, prompt: str) -> dict:
    req_body = {
        "model": model_identifier,
        "max_tokens": 1800,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a literary and music analysis expert. "
                    "Always produce valid JSON and ground contextual claims in the provided web context."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    req = request.Request(
        TOGETHER_API_URL,
        data=json.dumps(req_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _run_together_in_depth_analysis(*, prompt: str) -> tuple[str, list[str], dict, str]:
    api_key = os.getenv("TOGETHER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("TOGETHER_API_KEY is not configured.")

    model_identifier = os.getenv("TOGETHER_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    try:
        response_payload = _request_together_chat(api_key=api_key, model_identifier=model_identifier, prompt=prompt)
    except url_error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Together AI request failed with HTTP {exc.code}: {body}") from exc
    except (url_error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Together AI request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Together AI returned invalid JSON envelope: {exc}") from exc

    choices = response_payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("Together AI response did not include choices.")

    first_choice = choices[0] if isinstance(choices[0], dict) else {}
    message = first_choice.get("message", {}) if isinstance(first_choice, dict) else {}
    raw_text = message.get("content", "") if isinstance(message, dict) else ""

    payload = _extract_json_payload(raw_text)
    summary, key_themes, detailed_analysis = _normalize_payload(payload)
    return summary, key_themes, detailed_analysis, model_identifier


def process_job(job_id: int) -> AnalysisJob:
    with transaction.atomic():
        job = AnalysisJob.objects.select_for_update().select_related("lyric_version", "song__album__band").get(pk=job_id)
        if job.status in {AnalysisJob.Status.SUCCEEDED, AnalysisJob.Status.CANCELED}:
            return job
        if job.status == AnalysisJob.Status.RUNNING:
            return job

        job.status = AnalysisJob.Status.RUNNING
        job.attempts += 1
        job.started_at = timezone.now()
        job.error_reason = ""
        job.save(update_fields=["status", "attempts", "started_at", "error_reason", "updated_at"])

    try:
        song = job.song
        search_queries = [
            f"{song.album.band.name} band",
            f"{song.album.band.name} {song.album.title} album",
            f"{song.album.band.name} {song.title} song",
            song.title,
        ]
        citations = _collect_wikipedia_context(search_queries)
        prompt = _build_user_prompt(
            song_title=song.title,
            album_title=song.album.title,
            band_name=song.album.band.name,
            lyrics_text=job.lyric_version.lyrics_text,
            citations=citations,
        )
        summary, themes, detailed_analysis, model_identifier = _run_together_in_depth_analysis(prompt=prompt)

        with transaction.atomic():
            locked_job = AnalysisJob.objects.select_for_update().get(pk=job.pk)
            if locked_job.status == AnalysisJob.Status.CANCELED:
                return locked_job

            AnalysisResult.objects.update_or_create(
                job=locked_job,
                defaults={
                    "song": locked_job.song,
                    "lyric_version": locked_job.lyric_version,
                    "summary": summary,
                    "key_themes": themes,
                    "detailed_analysis": detailed_analysis,
                    "citations": citations,
                    "model_identifier": model_identifier,
                    "prompt_version": PROMPT_VERSION,
                    "provider_metadata": {
                        "provider": "together",
                        "web_citation_count": len(citations),
                        "citation_sources": sorted(
                            {citation.get("source", "unknown") for citation in citations if isinstance(citation, dict)}
                        ),
                    },
                    "is_published": True,
                    "published_at": timezone.now(),
                },
            )

            locked_job.status = AnalysisJob.Status.SUCCEEDED
            locked_job.completed_at = timezone.now()
            locked_job.save(update_fields=["status", "completed_at", "updated_at"])
            return locked_job
    except Exception as exc:  # explicit persistence of failure state for operator visibility
        logger.exception("analysis_job_failed job_id=%s error=%s", job.pk, exc)
        with transaction.atomic():
            failed_job = AnalysisJob.objects.select_for_update().get(pk=job.pk)
            failed_job.status = AnalysisJob.Status.FAILED
            failed_job.error_reason = str(exc)
            failed_job.completed_at = timezone.now()
            failed_job.save(update_fields=["status", "error_reason", "completed_at", "updated_at"])
            return failed_job


def process_queued_jobs(*, limit: int = 20) -> list[AnalysisJob]:
    queued_ids = list(
        AnalysisJob.objects.filter(status=AnalysisJob.Status.QUEUED).order_by("created_at").values_list("id", flat=True)[:limit]
    )
    processed = []
    for job_id in queued_ids:
        processed.append(process_job(job_id))
    return processed
