from django.urls import path

from analysis.views import trigger_analysis


app_name = "analysis"

urlpatterns = [
    path("trigger/<int:lyric_version_id>/", trigger_analysis, name="trigger"),
]

