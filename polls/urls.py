from django.urls import path

from . import views
from .views.result_view import displayResult


app_name = 'polls'
urlpatterns = [
    path('vote/<int:id>/', views.VoteView.as_view(), name = "vote"),
    path('result/<int:id>/', displayResult, name = "result")
]
