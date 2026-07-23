from django.urls import path

from public_site import views


app_name = "public_site"

urlpatterns = [
    path("", views.band_list, name="band-list"),
    path("bands/<slug:slug>/", views.band_detail, name="band-detail"),
    path("albums/<int:album_id>/", views.album_detail, name="album-detail"),
    path("songs/<int:song_id>/", views.song_detail, name="song-detail"),
]

