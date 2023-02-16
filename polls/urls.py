from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('vote/<int:id>/', views.VotingView.as_view(), name = 'vote'),
    path('result/<int:id>/', views.ResultView.as_view(), name = 'result'),
    path('new/', views.CreatePollView.as_view(), name='create_poll'),
    path('delete/<int:pk>/', views.PollDeleteView.as_view(), name='delete_poll'),
    path('edit/<int:id>/', views.EditPollView.as_view(), name='edit_poll'),
    path('search/', views.SearchView.as_view(), name='search_poll'),
    path('code/', views.VoteWithCodeView.as_view(), name='vote_code'),
    path('explanation/GM/', views.ExplanationGMView.as_view(), name='explain_gm'),
    path('personal/', views.PersonalPollsView.as_view(), name='personal_polls')
]