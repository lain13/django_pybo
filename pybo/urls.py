"""pybo URL Configuration
"""
from django.urls import path
from . import views

app_name = 'pybo'

urlpatterns = [
    # base_views.py
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='detail'),

    # question_views.py
    path('question/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('question/modify/<int:pk>/', views.QuestionModifyView.as_view(), name='question_modify'),
    path('question/delete/<int:pk>/', views.QuestionDeleteView.as_view(), name='question_delete'),

    # answer_views.py
    path('answer/create/<int:question_id>/', views.AnswerCreateView.as_view(), name='answer_create'),
    path('answer/modify/<int:pk>/', views.AnswerModifyView.as_view(), name='answer_modify'),
    path('answer/delete/<int:pk>/', views.AnswerDeleteView.as_view(), name='answer_delete'),

    # comment_views.py
    path('comment/create/question/<int:question_id>/', views.CommentCreateQuestionView.as_view(), name='comment_create_question'),
    path('comment/modify/question/<int:pk>/', views.CommentModifyQuestionView.as_view(), name='comment_modify_question'),
    path('comment/delete/question/<int:pk>/', views.CommentDeleteQuestionView.as_view(), name='comment_delete_question'),
    path('comment/create/answer/<int:answer_id>/', views.CommentCreateAnswerView.as_view(), name='comment_create_answer'),
    path('comment/modify/answer/<int:pk>/', views.CommentModifyAnswerView.as_view(), name='comment_modify_answer'),
    path('comment/delete/answer/<int:pk>/', views.CommentDeleteAnswerView.as_view(), name='comment_delete_answer'),

    # vote_views.py
    path('vote/question/<int:question_id>/', views.VoteQuestionView.as_view(), name='vote_question'),
    path('vote/answer/<int:answer_id>/', views.VoteAnswerView.as_view(), name='vote_answer'),
]
