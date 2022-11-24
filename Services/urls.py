from django.urls import path
from Services import views

urlpatterns = [
    path('notifications/token/add/', views.NotificationTokenView.as_view()),
    path('notifications/token/delete/', views.NotificationTokenInactiveView.as_view()),
    path('notifications/test/send/', views.NotificationsView.as_view()),
]
