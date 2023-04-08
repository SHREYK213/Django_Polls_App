from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('create/', views.create_poll, name='create_question'),
    path('<int:question_id>/update/', views.edit_poll, name='update_question'),
    path('<int:question_id>/delete/', views.delete_poll, name='delete'),

]