"""persoquiz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('new_question/<int:qid>', views.new_question, name='new_question'),
    path('delete_question/<int:quiz_id>/<int:question_id>', views.delete_question, name='delete_question'),
    path('delete_answers/<int:quiz_id>/<int:question_id>', views.delete_answers, name='delete_answers'),
    path('start_question/<int:quiz_id>/<int:question_id>', views.start_question, name='start_question'),
    path('stop_question/<int:quiz_id>/<int:question_id>', views.stop_question, name='stop_question'),
    path('next_question/<int:qid>', views.next_question, name='next_question'),
    path('answers/<int:quiz_id>/<int:question_id>', views.answers, name='answers'),
    path('new_quiz', views.new_quiz, name='new_quiz'),
    path('delete_quiz/<int:quiz_id>', views.delete_quiz, name='delete_quiz'),
    path('quiz/<int:qid>', views.quiz_index, name='quiz_index'),
    re_path('present/(?P<quiz_code>[A-Z]{4})', views.present.as_view(), name='present'),
    re_path('(?P<quiz_code>[A-Z]{4})', views.show.as_view(), name='show'),
    path('', views.index, name='index'),
]
