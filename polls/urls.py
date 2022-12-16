from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('vote/<int:id>/', views.VotingView.as_view(), name = 'vote'),
    path('result/<int:id>/', views.ResultView.as_view(), name = 'result'),
    path('', views.IndexView.as_view(), name='index'),
    path('create_poll/', views.create_poll, name='create_poll'),
    path('delete_poll/<int:pk>', views.PollDeleteView.as_view(), name='delete_poll'),
    path('edit_poll/<int:id>', views.edit_poll, name='edit_poll')
]

handler403 = 'polls.views.error_pages.error_403'
handler404 = 'polls.views.error_pages.error_404'
handler500 = 'polls.views.error_pages.error_500'