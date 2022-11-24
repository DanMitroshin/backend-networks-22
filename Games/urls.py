from django.urls import path
from . import views


urlpatterns = [
    path('duels/v1/list/', views.DuelsListView.as_view()),
    path('duels/v1/exit/', views.ExitDuelsRoomView.as_view()),
    path('duels/v1/delete/', views.DeleteDuelView.as_view()),
    path('duels/v1/create/', views.CreateDuelView.as_view()),
    path('duels/v1/accept/', views.AcceptDuelView.as_view()),
    path('duels/v1/answer/', views.AnswerDuelView.as_view()),
    path('duels/v1/update/', views.UpdateDuelView.as_view()),
    path('duels/v1/test/', views.TestDuelView.as_view()),
]
