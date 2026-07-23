from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import RequestFactory, TestCase

from catalog.admin import GenreAdmin
from catalog.models import Album, Band, Genre, LyricLine, LyricVersion, Song


class LyricVersionTests(TestCase):
    def setUp(self):
        self.band = Band.objects.create(name="Massive Attack", slug="massive-attack")
        self.album = Album.objects.create(band=self.band, title="Mezzanine")
        self.song = Song.objects.create(album=self.album, title="Teardrop")

    def test_only_one_current_lyric_version_per_song(self):
        first = LyricVersion.objects.create(
            song=self.song,
            version_label="v1",
            lyrics_text="Love, love is a verb.",
            is_current=True,
        )
        second = LyricVersion.objects.create(
            song=self.song,
            version_label="v2",
            lyrics_text="Love, love is a doing word.",
            is_current=True,
        )
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_current)
        self.assertTrue(second.is_current)

    def test_unique_version_label_per_song(self):
        LyricVersion.objects.create(song=self.song, version_label="original", lyrics_text="x")
        with self.assertRaises(IntegrityError):
            LyricVersion.objects.create(song=self.song, version_label="original", lyrics_text="y")


class LyricLineTests(TestCase):
    def setUp(self):
        band = Band.objects.create(name="Portishead", slug="portishead")
        album = Album.objects.create(band=band, title="Dummy")
        song = Song.objects.create(album=album, title="Roads")
        self.lyric_version = LyricVersion.objects.create(
            song=song,
            version_label="original",
            lyrics_text="How can it feel this wrong?",
            is_current=True,
        )

    def test_rejects_empty_text_for_non_separator_line(self):
        line = LyricLine(lyric_version=self.lyric_version, line_number=1, is_separator=False, text="")
        with self.assertRaisesMessage(ValidationError, "Text is required when line is not a separator."):
            line.save()

    def test_allows_empty_text_for_separator_line(self):
        line = LyricLine.objects.create(lyric_version=self.lyric_version, line_number=1, is_separator=True, text="")
        self.assertTrue(line.is_separator)
        self.assertEqual(line.text, "")


class GenreTests(TestCase):
    def test_rejects_self_parent(self):
        genre = Genre.objects.create(name="Rock")
        genre.parent_genre = genre

        with self.assertRaisesMessage(ValidationError, "A genre cannot be its own parent."):
            genre.save()

    def test_rejects_cycles(self):
        root = Genre.objects.create(name="Rock")
        child = Genre.objects.create(name="Alternative Rock", parent_genre=root)
        root.parent_genre = child

        with self.assertRaisesMessage(ValidationError, "A genre cannot be a descendant of itself."):
            root.save()

    def test_admin_form_surfaces_cycle_validation_error(self):
        root = Genre.objects.create(name="Rock")
        child = Genre.objects.create(name="Alternative Rock", parent_genre=root)
        request = RequestFactory().get("/admin/")
        request.user = AnonymousUser()
        form_class = GenreAdmin(Genre, admin.site).get_form(request, obj=root)
        form = form_class(
            data={
                "name": "Rock",
                "slug": "rock",
                "description": "",
                "parent_genre": child.id,
                "archived_at_0": "",
                "archived_at_1": "",
            },
            instance=root,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("A genre cannot be a descendant of itself.", form.errors["parent_genre"])


class CatalogMetadataTests(TestCase):
    def setUp(self):
        self.band = Band.objects.create(name="Massive Attack", slug="massive-attack")
        self.album = Album.objects.create(band=self.band, title="Mezzanine")
        self.song = Song.objects.create(album=self.album, title="Teardrop")

    def test_album_and_song_allow_independent_multi_genre_assignments(self):
        trip_hop = Genre.objects.create(name="Trip Hop")
        alternative = Genre.objects.create(name="Alternative Rock")
        electronica = Genre.objects.create(name="Electronica")

        self.album.genres.set([trip_hop, alternative])
        self.song.genres.set([electronica])

        self.assertCountEqual(self.album.genres.values_list("name", flat=True), ["Trip Hop", "Alternative Rock"])
        self.assertCountEqual(self.song.genres.values_list("name", flat=True), ["Electronica"])

    def test_song_is_bonus_defaults_to_false(self):
        self.assertFalse(self.song.is_bonus)

    def test_song_is_bonus_persists_true(self):
        self.song.is_bonus = True
        self.song.save(update_fields=["is_bonus"])
        self.song.refresh_from_db()
        self.assertTrue(self.song.is_bonus)

    def test_album_total_tracks_is_derived_not_persisted(self):
        Song.objects.create(album=self.album, title="Angel")
        Song.objects.create(album=self.album, title="Risingson")

        self.assertFalse(hasattr(self.album, "total_tracks"))
        self.assertEqual(self.album.songs.count(), 3)
