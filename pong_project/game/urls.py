from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_game, name='create_game'),
    path('<uuid:game_id>/', views.game_page, name='game_page'),
    path('results/', views.list_results, name='list_results'),
]
