from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/results/", views.results, name="results"),
    path("<int:pk>/vote/", views.vote, name="vote"),
    path('create/', views.create_poll, name='create'),
    path('<int:question_id>/update', views.edit_poll, name='update_question'),
    path('filterbytag/', views.get_questions, name='filter'),
    path('tag/', views.TagListView.as_view(), name='tags'),
    path('tags/',views.get_tag,name='get_tags'),
    path('questions/', views.get_questions, name='question-list'),
    path('alldata', views.get_all, name='alldata'),
    # path('<int:pk>/', views.details, name='details'),
    path('<int:pk>/', views.DetailView.as_view(), name='details'),
    path('<int:pk>/alldata/', views.get_allwpk, name='details'),
]