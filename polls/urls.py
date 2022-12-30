from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('vote/<int:id>/', views.VotingView.as_view(), name = 'vote'),
    path('result/<int:id>/', views.ResultView.as_view(), name = 'result'),
    path('new/', views.create_poll, name='create_poll'),
    path('delete/<int:pk>/', views.PollDeleteView.as_view(), name='delete_poll'),
    path('edit/<int:id>/', views.edit_poll, name='edit_poll'),
    path('search/', views.SearchView.as_view(), name='search_poll')
]

handler403 = 'polls.views.error_pages.error_403'
handler404 = 'polls.views.error_pages.error_404'
handler500 = 'polls.views.error_pages.error_500'