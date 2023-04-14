from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('vote/<int:id>/', views.vote_redirect_view, name='vote'),
    path('vote/<int:id>/<str:token>/', views.vote_redirect_view, name='vote'),
    path('vote/singlepreference/<int:id>/', views.VoteSinglePreferenceView.as_view(), name = 'vote_single_preference'),
    path('vote/singlepreference/<int:id>/<str:token>', views.VoteSinglePreferenceView.as_view(), name = 'vote_single_preference'),
    path('vote/majorityjudgment/<int:id>/', views.VoteMajorityJudgmentView.as_view(), name = 'vote_MJ'),
    path('vote/majorityjudgment/<int:id>/<str:token>', views.VoteMajorityJudgmentView.as_view(), name = 'vote_MJ'),
    path('result/<int:id>/', views.result_redirect_view, name='result'),
    path('result/singlepreference/<int:id>/', views.SinglePreferenceResultView.as_view(), name = 'result_single_preference'),
    path('result/majorityjudgment/<int:id>/', views.MajorityJudgementResultView.as_view(), name = 'result_MJ'),
    path('result/majorityjudgment/<int:id>/<str:include_synthetic>', views.MajorityJudgementResultView.as_view(), name = 'result_MJ_realonly'),
    path('new/', views.CreatePollView.as_view(), name='create_poll'),
    path('success/', views.CreatePollSuccessView.as_view(), name='poll_created_success'),
    path('delete/<int:pk>/', views.PollDeleteView.as_view(), name='delete_poll'),
    path('edit/<int:id>/', views.EditPollView.as_view(), name='edit_poll'),
    path('search/', views.SearchView.as_view(), name='search_poll'),
    path('help/simulated_results/', views.HelpSimulatedResultsView.as_view(), name='help_simulated_results'),
    path('help/majorityjudgment/', views.ExplanationGMView.as_view(), name='explain_gm'),
    path('help/options/', views.ExplanationCreationPollView.as_view(), name='explain_options'),
    path('personal/', views.PersonalPollsView.as_view(), name='personal_polls'),
    path('<str:code>/<str:token>', views.AccessPollView.as_view(), name='access_poll'),
    path('<str:code>', views.AccessPollView.as_view(), name='access_poll'),
    path('tokens/<int:id>/', views.TokensView.as_view(), name='tokens'),
    path('tokens/<int:id>/download/', views.tokens_view.download_tokens, name='download_tokens'),
    path('tokens/<int:id>/success/', views.tokens_view.tokens_success, name='tokens_success'),
    path('tokens/<int:pk>/delete/', views.tokens_view.TokenDeleteView.as_view(), name='tokens_delete')
]