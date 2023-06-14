from django.shortcuts import render,redirect
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth,User
from django.contrib import messages
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin
from .models import Quiz
from .serializers import *
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status



# Create your views here.
q_id=[]
def home(request):
    context={'user':None}
    return render(request,'home.html',context)

def register(request):
    if request.method=="POST":
        your_name=request.POST['yname']
        email=request.POST['email']    
        password=request.POST['pwd']
        cpwd=request.POST['cpwd']
        if password==cpwd:
            if User.objects.filter(username=your_name).exists():
                print('User Name Taken')
            elif User.objects.filter(email=email).exists():
                print('Email Already Taken')
            else:
                user = User.objects.create_user(username=your_name,password=password,email=email)
                user.save()
                context={'user':None}
                print("User Saved")
                return render(request,'home.html',context)
    # users=User.objects.all()
        else:
            print('Passsword Not Matching')
            return render(request,'register.html')

    return render(request,'register.html')

def login(request):
    if request.method == 'POST':
        uname=request.POST['uname']
        pwd=request.POST['pwd']
        user=auth.authenticate(username=uname,password=pwd)
        if user is not None:
            auth.login(request,user)
            context={'user':user}
            #print(user)
            user=User.objects.filter(username=uname).first()
            return render(request,'home.html',context)
        else:
            messages.error(request,"Username or password is wrong")
    return render(request,'login.html')

def logout(request):
    auth.logout(request)
    return render(request,"home.html")

def quiz_create(request):
    return render(request,"quiz_create.html")


class QuizIdCreate(CreateModelMixin,GenericAPIView):
    queryset=Quiz.objects.all()
    serializer_class=QuizSerializer
    global q_id
    def post(self,request,*args,**kwargs):
        quiz_id=request.POST.get("quiz_id")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        quiz_id=request.POST.get("quiz_id")
        print(quiz_id)
        q_id.append(quiz_id)
        return render(request,"create_question.html",{'quiz_id':quiz_id})
    
    
class QuestionCreate(generics.CreateAPIView):
    serializer_class = QuestionSerializer

    def create(self, request, *args, **kwargs):
        question_text=request.data.get('question')
        method=request.data.get('add',None)
        print(request.data)
        quiz_id=q_id[-1]
        quiz_store=quiz_id
        quiz=Quiz.objects.get(quiz_id=quiz_id)
        quiz_id=quiz.id
        question_data = {
            'question_text': question_text,
            'quiz': quiz_id
        }
        #print(question_data)
        serializer = self.get_serializer(data=question_data)
        serializer.is_valid(raise_exception=True)
        
        # Save the question
        question = serializer.save()
        choices=[]
        # Create choices
        for i in range(1, 5):
            choice_text = request.data.get(f'option{i}')
            if choice_text:
                is_correct = request.data.get(f'correct_option') == f'option{i}'
                choices.append({'question':question.id,'choice_text': choice_text, 'correct': is_correct})

        
        for choice in choices:
            choice_serializer = ChoiceSerializer(data=choice)
            choice_serializer.is_valid(raise_exception=True)
            choice_serializer.save()

        if method is not None:
            return render(request,"create_question.html",{'quiz_id':quiz_store})
        else:
            return render(request,"home.html")
        
def get_questions(request,pk):
    quiz=Quiz.objects.get(quiz_id=pk)
    quiz_id=quiz.id
    questions=Question.objects.get(quiz_id=quiz_id)
    l=[]

class QuestionList(generics.ListAPIView):
    serializer_class = QuestionSerializer

    #to over ride the query set
    def get_queryset(self):
        # Get the quiz_id from the URL parameter
        quiz_id = self.kwargs.get('quiz_id')
        quiz=Quiz.objects.get(quiz_id=quiz_id)
        quiz_id=quiz.id
        # Filter the questions based on the quiz_id
        queryset = Question.objects.filter(quiz_id=quiz_id)
        return queryset
    
    def get(self,request,*args,**kwargs):
        query_set=self.get_queryset()
        choices=[]
        for question in query_set:
            id=question.id
            choice=Choice.objects.filter(question_id=id)
            choices.append(choice)
        #print(choices)
        return render(request,"delete_question.html",{'questions':query_set,'choices':choices})
    
class DeleteQuestion(generics.DestroyAPIView):
    queryset=Question.objects.all()
    serializer_class=QuestionSerializer

def update(request,pk):
    print(pk)
    question_text=request.POST.get('question_text')
    if len(question_text)==0:
        return HttpResponse("Question hasnt been updated")
    print(question_text)
    question=Question.objects.get(id=pk)
    question.question_text = question_text
    question.save()
    return HttpResponse("Question updated sucessfully")

    

