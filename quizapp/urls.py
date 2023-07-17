from django.urls import path,include
from . import views
from django.contrib.auth.views import LogoutView
from quizapp import views


urlpatterns=[
    path('',views.home,name="home"),
    path('login/',views.login,name="login"),
    path('register/',views.register,name="register"),
    path('logout/', views.logout, name='logout'),
    #Teachers
    path('quiz_create',views.quiz_create,name="quiz_create"),
    path('createquiz',views.QuizIdCreate.as_view(),name="create quiz"),
    path('createquestion',views.QuestionCreate.as_view(),name="create question"),
    #path('view_questions/<int:pk>',views.get_questions,name="get_question_by_quiz_id"),
    path('get/<int:quiz_id>',views.QuestionList.as_view(),name="drf_question_view"),
    path('delete/<int:pk>',views.DeleteQuestion.as_view(),name="delete question"),
    path('update/<int:pk>',views.update,name="update-question"),
    path('teacher_home.html',views.teacher_home,name="teacher home page"),
    path('edit',views.edit,name="edit"),
    #Students
    path('give_quiz/',views.give_quiz,name="give_quiz"),
    path('quiz/<int:quiz_id>',views.QuestionListStudent.as_view(),name="question list for students"),
    path('score',views.score,name="get score"),
    path('leader_board.html',views.leader_board,name="leader board"),
    path('get_quizes',views.get_quizes,name="get_quizes")
    
]
