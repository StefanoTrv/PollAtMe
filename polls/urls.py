from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('vote/<int:id>/', views.VoteView.as_view(), name = 'vote'),
    path('result/<int:id>/', views.SinglePreferenceListView.as_view(), name = 'result'),
    path('result/gm/<int:id>/', views.MajorityJudgementListView.as_view(), name = 'maj_jud_result'),
    path('', views.IndexView.as_view(), name='index')
]

handler403 = 'polls.views.error_pages.error_403'
handler404 = 'polls.views.error_pages.error_404'
handler500 = 'polls.views.error_pages.error_500'