from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from analysis.models import AnalysisJob, AnalysisResult
from analysis.services import process_queued_jobs
from catalog.models import Album, Band, LyricVersion, Song


class AnalysisPipelineTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin",
            password="password123!",
            is_staff=True,
            is_superuser=True,
        )
        band = Band.objects.create(name="Portishead", slug="portishead")
        album = Album.objects.create(band=band, title="Dummy")
        self.song = Song.objects.create(album=album, title="Roads")
        self.lyric = LyricVersion.objects.create(
            song=self.song,
            version_label="original",
            lyrics_text="How can it feel, this wrong?",
            is_current=True,
        )

    def test_staff_trigger_queues_job_once(self):
        self.client.force_login(self.user)
        url = reverse("analysis:trigger", args=[self.lyric.id])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(AnalysisJob.objects.count(), 1)
        self.assertEqual(AnalysisJob.objects.first().status, AnalysisJob.Status.QUEUED)

    def test_worker_processes_queued_job(self):
        AnalysisJob.enqueue(lyric_version=self.lyric, requested_by=self.user)
        with patch("analysis.services._collect_wikipedia_context") as context_mock, patch(
            "analysis.services._run_together_in_depth_analysis"
        ) as model_mock:
            context_mock.return_value = [
                {
                    "source": "wikipedia",
                    "title": "Roads (song)",
                    "url": "https://example.test/roads",
                    "excerpt": "Song context",
                    "retrieved_at": "2026-07-23T00:00:00+00:00",
                }
            ]
            model_mock.return_value = (
                "A claustrophobic meditation on emotional distance.",
                ["isolation", "fear"],
                {
                    "narrative_arc": "The voice drifts from confusion to fragile clarity.",
                    "line_level_observations": ["Repetition signals anxiety."],
                    "overall_meaning": "It explores loneliness and dependence.",
                },
                "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            )
            processed = process_queued_jobs(limit=5)
        self.assertEqual(len(processed), 1)
        job = AnalysisJob.objects.select_related("result").get()
        self.assertEqual(job.status, AnalysisJob.Status.SUCCEEDED)
        self.assertTrue(job.result.summary)
        self.assertTrue(job.result.key_themes)
        self.assertEqual(job.result.provider_metadata.get("provider"), "together")
        self.assertIn("overall_meaning", job.result.detailed_analysis)
        self.assertEqual(len(job.result.citations), 1)

    def test_worker_marks_failed_on_malformed_output(self):
        AnalysisJob.enqueue(lyric_version=self.lyric, requested_by=self.user)
        with patch("analysis.services._collect_wikipedia_context", return_value=[]), patch(
            "analysis.services._run_together_in_depth_analysis",
            side_effect=ValueError("Together AI response did not contain a JSON object."),
        ):
            process_queued_jobs(limit=5)

        job = AnalysisJob.objects.get()
        self.assertEqual(job.status, AnalysisJob.Status.FAILED)
        self.assertIn("JSON object", job.error_reason)

    def test_worker_continues_when_context_fetch_fails(self):
        AnalysisJob.enqueue(lyric_version=self.lyric, requested_by=self.user)
        with patch("analysis.services._collect_wikipedia_context", return_value=[]), patch(
            "analysis.services._run_together_in_depth_analysis",
            return_value=(
                "Summary",
                ["theme"],
                {"overall_meaning": "Meaning"},
                "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            ),
        ):
            process_queued_jobs(limit=5)

        result = AnalysisResult.objects.get(song=self.song)
        self.assertEqual(result.summary, "Summary")
        self.assertEqual(result.citations, [])

    def test_analyze_song_command_uses_song_id(self):
        with patch("analysis.services._collect_wikipedia_context", return_value=[]), patch(
            "analysis.services._run_together_in_depth_analysis",
            return_value=(
                "Summary",
                ["theme"],
                {"overall_meaning": "Meaning"},
                "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            ),
        ):
            call_command("analyze_song", song_id=self.song.id)
        result = AnalysisResult.objects.get(song=self.song)
        self.assertEqual(result.summary, "Summary")
        self.assertEqual(result.detailed_analysis["overall_meaning"], "Meaning")

    def test_analyze_song_command_errors_when_song_missing(self):
        with self.assertRaises(CommandError):
            call_command("analyze_song", song_id=99999)

    def test_cross_cli_skill_definitions_are_in_sync(self):
        root = Path(settings.BASE_DIR)
        github_skill = root / ".github/skills/song-in-depth-analysis/SKILL.md"
        cursor_skill = root / ".cursor/skills/song-in-depth-analysis/SKILL.md"
        claude_skill = root / ".claude/skills/song-in-depth-analysis/SKILL.md"

        github_text = github_skill.read_text(encoding="utf-8")
        self.assertEqual(github_text, cursor_skill.read_text(encoding="utf-8"))
        self.assertEqual(github_text, claude_skill.read_text(encoding="utf-8"))
