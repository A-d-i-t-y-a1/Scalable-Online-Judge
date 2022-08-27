from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:problem_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:problem_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:problem_id>/leaderboard/', views.leaderboard, name='leaderboard'),
]