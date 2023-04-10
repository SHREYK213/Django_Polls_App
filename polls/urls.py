from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('polls/', views.create_poll, name='create'),
    path('<int:question_id>/update', views.edit_poll, name='update_question'),
    path('<int:question_id>/delete/', views.delete_poll, name='delete'),
    path('?tags=<tags>/', views.IndexView.as_view(), name='filter'),
    path('tags/', views.TagListView.as_view(), name='tags'),

]