from django.urls import path
from . import views


urlpatterns = [
    path('', views.SectionProgressView.as_view(),),
    path('events/', views.EventView.as_view(),),
    path('rating/', views.WeekRatingView.as_view()),
    path('progress/', views.StatisticProgressView.as_view()),
]
