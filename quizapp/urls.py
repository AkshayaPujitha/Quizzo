from django.urls import path,include
from . import views
from django.contrib.auth.views import LogoutView
from quizapp import views


urlpatterns=[
    path('',views.home,name="home"),
    path('login.html',views.login,name="login"),
    path('register.html',views.register,name="register"),
    path('logout', views.logout, name='logout'),
    path('quiz_create',views.quiz_create,name="quiz_create"),
    path('createquiz',views.QuizIdCreate.as_view(),name="create quiz"),
    path('createquestion',views.QuestionCreate.as_view(),name="create question")
    
]
