from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='question_list'),
    path('question/', views.redirect_to_index, name='redirect_question_list'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('question/<int:question_id>/edit', views.question_edit, name='question_edit'),
    path('question/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    path('question/create/', views.question_create, name='question_create'),
    path('answer/<int:answer_id>/', views.answer_edit, name='answer_edit'),
    path('answer/<int:answer_id>/rate/', views.answer_rating, name='answer_rating'),
    path('answer/<int:answer_id>/delete/', views.answer_delete, name='answer_delete'),
    path('answer/<int:answer_id>/select/', views.answer_select, name='answer_select'),
]
