from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('vote/<int:id>/', views.VoteView.as_view(), name = 'vote'),
    path('result/<int:id>/', views.SinglePreferenceListView.as_view(), name = 'result'),
    path('', views.IndexView.as_view(), name='index'),
    path('create_poll/step1/', views.create_poll_step1, name='create_poll_step_1'),
    path('create_poll/step2/', views.create_poll_step2, name='create_poll_step_2'),
    path('create_poll/step3/', views.create_poll_step3, name='create_poll_step_3')
]

handler403 = 'polls.views.error_pages.error_403'
handler404 = 'polls.views.error_pages.error_404'
handler500 = 'polls.views.error_pages.error_500'