from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    #Risponde agli url "vote/"id_domanda"
    path('vote/<int:id>/', views.VoteView.as_view(), name = "vote"), #il parametro id viene catturato e viene passato alla view,
                                                                    #viene chiamato il metodo get di VoteView
                                                                    #as_view fa un dipatch tra metodo della richiesta e metodo della view:
                                                                    #  1) se ricevo un GET, quindi la prima volta che si chiama la pagina, viene chiamata la funzione get(...)
                                                                    #  2) se ricevo un POST, viene chiamata la funzione post(...)
    path('result/<int:id>/', views.SinglePreferenceListView.as_view(), name = "result"),
    path('', views.IndexView.as_view(), name='index')
]
