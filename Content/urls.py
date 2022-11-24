from django.urls import path
from . import views


urlpatterns = [
    # Lessons views
    path('lessons/', views.LessonView.as_view()),
    path('lessons/list/', views.LessonListView.as_view()),
    path('trainers/', views.TrainerProductCreateRetrieveView.as_view()),
    path('questions/check/', views.QuestionCheckView.as_view()),
    path('answers/review/', views.AddUserAnswerForReviewView.as_view()),

    # Classroom views
    path('classroom/', views.ClassroomView.as_view()),
    path('classroom/<str:username>/', views.ClassroomView.as_view()),

    # Access
    path('card/access/', views.CardsAccessView.as_view()),

    # Content update/add/get
    path('video/get/', views.ContentVideoGet.as_view()),
    path('video/access/', views.ContentVideoAccess.as_view()),
    path('content/add/', views.AddContentItems.as_view()),
    path('content/add/search/', views.AddDataToSearchView.as_view()),
    path('indexes/add/', views.UpdateContentRelations.as_view()),
    path('content/get/historyTexts/', views.HistoryTextView.as_view()),

    # WIKI-CONTENT
    path('wiki/item/preview/structure/<slug:table>/',
         views.ContentWikiPreviewViewSet.as_view({'get': 'structure'})),
    path('wiki/item/preview/<slug:table>/<int:index>/', views.ContentWikiPreviewViewSet.as_view({'get': 'retrieve'}), ),
    path('wiki/item/preview/<slug:table>/', views.ContentWikiPreviewViewSet.as_view({'get': 'list'})),

    path('wiki/item/preview/search/names/<slug:table>/', views.ContentFastSearchNamesView.as_view()),
    path('wiki/item/preview/search/<slug:table>/', views.ContentFastSearchFullObjectsView.as_view()),

    path('wiki/item/full/<slug:table>/<int:index>/', views.ContentWikiFullView.as_view({'get': 'retrieve'}), ),

    path('wiki/item/related/structure/<slug:table>/<int:index>/', 
         views.ContentWikiRelatedItemsView.as_view({'get': 'structure'}), ),
    path('wiki/item/related/<slug:table>/<int:index>/', views.ContentWikiRelatedItemsView.as_view({'get': 'list'}), ),

    # Dialogs
    path('dialogs/', views.DialogView.as_view()),
    path('dialogs/save/', views.SaveDialog.as_view()),
    path('dialogs/statistics/answers/', views.DialogStatisticsAnswers.as_view()),
]
