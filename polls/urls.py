from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('vote/<int:id>/', views.AnswerView.as_view(), name = "vote")
]
