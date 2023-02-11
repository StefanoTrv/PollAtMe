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
    path('code/', views.VoteWithCodeView.as_view(), name='vote_code')
]

handler403 = 'polls.views.error_pages.error_403'
handler404 = 'polls.views.error_pages.error_404'
handler500 = 'polls.views.error_pages.error_500'