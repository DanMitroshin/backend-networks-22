from django.urls import path
from Users import views

urlpatterns = [
    path('profile/', views.AccountProfileView.as_view()),
    path('profile/main/', views.UserMainInfoView.as_view()),

    path('auth/', views.AuthView.as_view()),
    path('init/', views.InitView.as_view()),
    path('achievements/', views.AchievementsView.as_view()),
]
