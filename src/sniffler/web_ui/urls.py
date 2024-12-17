from django.urls import path

from .views import HomePageView, ScanView, StatsView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("scan/", ScanView.as_view(), name="scan"),
    path("stats/", StatsView.as_view(), name="stats"),
]
