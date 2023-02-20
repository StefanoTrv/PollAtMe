from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('vote/<int:id>/', views.vote_redirect_view, name='vote'),
    path('vote/singlepreference/<int:id>/', views.VoteSinglePreferenceView.as_view(), name = 'vote_single_preference'),
    path('vote/majorityjudgment/<int:id>/', views.VoteMajorityJudgmentView.as_view(), name = 'vote_MJ'),
    path('result/<int:id>/', views.result_redirect_view, name='result'),
    path('result/singlepreference/<int:id>/', views.SinglePreferenceResultView.as_view(), name = 'result_single_preference'),
    path('result/singlepreference/<int:id>/<str:include_synthetic>', views.SinglePreferenceResultView.as_view(), name = 'result_single_preference_realonly'),
    path('result/majorityjudgment/<int:id>/', views.MajorityJudgementListView.as_view(), name = 'result_MJ'),
    path('result/majorityjudgment/<int:id>/<str:include_synthetic>', views.MajorityJudgementListView.as_view(), name = 'result_MJ_realonly'),
    path('new/', views.CreatePollView.as_view(), name='create_poll'),
    path('delete/<int:pk>/', views.PollDeleteView.as_view(), name='delete_poll'),
    path('edit/<int:id>/', views.EditPollView.as_view(), name='edit_poll'),
    path('search/', views.SearchView.as_view(), name='search_poll'),
    path('code/', views.VoteWithCodeView.as_view(), name='vote_code'),
    path('help/simulated_results/', views.HelpSimulatedResultsView.as_view(), name='help_simulated_results'),
    path('help/majorityjudgment/', views.ExplanationGMView.as_view(), name='explain_gm'),
    path('personal/', views.PersonalPollsView.as_view(), name='personal_polls')
]