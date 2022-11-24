from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('vote/<int:id>/', views.VoteView.as_view(), name = 'vote'),
    path('result/<int:id>/', views.SinglePreferenceListView.as_view(), name = 'result'),
    path('', views.IndexView.as_view(), name='index')
]