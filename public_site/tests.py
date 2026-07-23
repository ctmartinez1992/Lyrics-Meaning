from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from analysis.models import AnalysisJob, AnalysisResult
from catalog.models import Album, Band, LyricLine, LyricVersion, Song


class PublicSiteTests(TestCase):
    def setUp(self):
        self.band = Band.objects.create(name="Radiohead", slug="radiohead")
        self.album = Album.objects.create(band=self.band, title="OK Computer", release_date=timezone.now().date())
        self.song = Song.objects.create(album=self.album, title="Paranoid Android", track_number=2)
        self.lyric_version = LyricVersion.objects.create(
            song=self.song,
            version_label="original",
            lyrics_text="Please could you stop the noise, I'm trying to get some rest",
            is_current=True,
        )
        LyricLine.objects.create(lyric_version=self.lyric_version, line_number=1, text="Please could you stop the noise")
        LyricLine.objects.create(lyric_version=self.lyric_version, line_number=2, is_separator=True, text="")
        LyricLine.objects.create(lyric_version=self.lyric_version, line_number=3, text="I'm trying to get some rest")

    def test_anonymous_can_browse_catalog(self):
        response = self.client.get(reverse("public_site:band-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.band.name)

        response = self.client.get(reverse("public_site:band-detail", args=[self.band.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.album.title)

        response = self.client.get(reverse("public_site:album-detail", args=[self.album.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.song.title)

    def test_song_page_without_analysis_shows_empty_state(self):
        response = self.client.get(reverse("public_site:song-detail", args=[self.song.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analysis not yet available.")

    def test_song_page_with_analysis_shows_summary_and_themes(self):
        job = AnalysisJob.objects.create(
            song=self.song,
            lyric_version=self.lyric_version,
            idempotency_key=AnalysisJob.build_idempotency_key(self.lyric_version.id),
            status=AnalysisJob.Status.SUCCEEDED,
        )
        AnalysisResult.objects.create(
            job=job,
            song=self.song,
            lyric_version=self.lyric_version,
            summary="A meditation on anxiety and noise.",
            key_themes=["anxiety", "alienation"],
            detailed_analysis={
                "overall_meaning": "The narrator is overwhelmed by social and internal noise.",
                "line_level_observations": ["Imperative language amplifies urgency."],
            },
            citations=[
                {
                    "source": "wikipedia",
                    "title": "Paranoid Android",
                    "url": "https://example.test/paranoid-android",
                    "excerpt": "Song background excerpt.",
                }
            ],
            model_identifier="unit-test-model",
            prompt_version="v1",
            provider_metadata={"source": "test"},
            is_published=True,
            published_at=timezone.now(),
        )

        response = self.client.get(reverse("public_site:song-detail", args=[self.song.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A meditation on anxiety and noise.")
        self.assertContains(response, "anxiety")
        self.assertContains(response, "Overall Meaning")
        self.assertContains(response, "Paranoid Android")

    def test_song_page_renders_separator_line_as_spacing(self):
        response = self.client.get(reverse("public_site:song-detail", args=[self.song.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="h-4" aria-hidden="true"></div>', html=True)

    def test_song_page_uses_lyrics_text_fallback_when_no_structured_lines(self):
        song = Song.objects.create(album=self.album, title="No Surprises", track_number=3)
        lyric_version = LyricVersion.objects.create(
            song=song,
            version_label="original",
            lyrics_text="A heart that's full up like a landfill",
            is_current=True,
        )

        response = self.client.get(reverse("public_site:song-detail", args=[song.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A heart that&#x27;s full up like a landfill")
