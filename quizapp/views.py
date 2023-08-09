from django.shortcuts import render,redirect
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth,User
from django.contrib import messages
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin
from .models import Quiz,Question,Student,Choice
from .serializers import *
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status





# home and login
q_id=[]
def home(request):
    user=request.session.get('user')
    authenticated=request.session.get('authenticated')
    context={'user':user,'authenticated':authenticated}
    return render(request,'home.html',context)

def register(request):
    if request.method=="POST":
        your_name=request.POST['yname']
        email=request.POST['email']    
        password=request.POST['pwd']
        cpwd=request.POST['cpwd']
        messages=[]
        if password==cpwd:
            if User.objects.filter(username=your_name).exists():
                messages.append("User Name Taken")
                print('User Name Taken')
                return render(request,'register.html',{'messages':messages})
            elif User.objects.filter(email=email).exists():
                messages.append("Email Already Taken")
                print('Email Already Taken')
                return render(request,'register.html',{'messages':messages})
            else:
                user = User.objects.create_user(username=your_name,password=password,email=email)
                user.save()
                context={'user':None}
                print("User Saved")
                return render(request,'home.html',context)
    # users=User.objects.all()
        else:
            context={'user':None}
            messages.append("Passsword Not Matching")
            print('Passsword Not Matching')
            return render(request,'register.html',{'messages':messages})

    return render(request,'register.html')

def login(request):
    if request.method == 'POST':
        uname=request.POST['uname']
        pwd=request.POST['pwd']
        user=auth.authenticate(username=uname,password=pwd)
        if user is not None:
            auth.login(request,user)
            if user.is_staff:
                context={'user':user}
                return redirect('teacher home page')
            context={'user':user}
            #print(user)
            user=User.objects.filter(username=uname).first()
            request.session['authenticated'] = user.is_authenticated
            request.session['user'] = user.username
            return redirect('home')
        else:
            messages.error(request,"Username or password is wrong")
    return render(request,'login.html')

def logout(request):
    auth.logout(request)
    return render(request,"home.html")

def quiz_create(request):
    return render(request,"quiz_create.html")

#Creating Quiz 
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
        #print(request.data)
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
            return render(request,"teacher_home.html")
        


class QuestionList(generics.ListAPIView):
    permission_classes=[IsAdminUser]
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
    permission_classes=[IsAdminUser]
    queryset=Question.objects.all()
    serializer_class=QuestionSerializer

@permission_classes([IsAuthenticated])
def update(request,pk):
    #print(pk)
    question_text=request.POST.get('question_text')
    try:
        if len(question_text)==0:
            return HttpResponse("Question hasnt been updated")
        #print(question_text)
        question=Question.objects.get(id=pk)
        question.question_text = question_text
        question.save()
        return render(request,"question_updated_sucess.html")
    except:
        error_data = {'error': 'Some error message'}
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

def teacher_home(request):
    return render(request,"teacher_home.html")

def edit(request):
    return render(request,"quiz_id_edit.html")

#Student
quiz_student_id=[]
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def give_quiz(request):
    return render(request,"give_quiz.html")

class QuestionListStudent(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = QuestionSerializer

    #to over ride the query set
    def get_queryset(self):
        # Get the quiz_id from the URL parameter
        quiz_id = self.kwargs.get('quiz_id')
        try:
            quiz=Quiz.objects.get(quiz_id=quiz_id)
        except:
            return None,None
        quiz_id=quiz.id
        quiz_student_id.append(quiz_id)
        
        # Filter the questions based on the quiz_id
        queryset = Question.objects.filter(quiz_id=quiz_id)
        return queryset,quiz_id
    
    def get(self,request,*args,**kwargs):
        query_set,quiz_id=self.get_queryset()
        if query_set is None:
            return render(request,"give_quiz.html")
        if request.user.is_authenticated:
            current_user = request.user

            student =Student.objects.filter()
            for s in student:
                #print(s.user,current_user,s.quiz)
                if current_user==s.user and quiz_id==s.quiz_id:
                    return render(request,"already_given.html")
        choices=[]
        for question in query_set:
            id=question.id
            choice=Choice.objects.filter(question_id=id)
            choices.append(choice)
        #print(query_set)
        if len(choices)==0:
            return render(request,"give_quiz.html")
        #print(choices)
        #print(choices)
        return render(request,"question_view.html",{'questions':query_set,'choices':choices})
    
user_choices={}
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def score(request):
    #print("hi")
    global quiz_student_id
    marks=0
    questions=Question.objects.filter()
    for question in questions:
        choice_id = request.POST.get(f'question{question.id}')
        if choice_id:
            user_choices[question.id]=Choice.objects.get(id=choice_id)
        else:
            user_choices[question.id]=None
    #print(user_choices)
    for id,obj in user_choices.items():
        #if question is unattempted by the student
        if obj is None:
            continue
        if obj.correct:
            print("Correct u scored 4 marks")
            marks+=4
        else:
            print("its incorrect")
    #print(marks)
    #print("hiiiiiiii")
    ctx={'marks':marks}
    if request.user.is_authenticated:
        # Get the current user
        current_user = request.user
        quiz = Quiz.objects.get(id=quiz_student_id[-1])
        student = Student(user=current_user, total_marks=marks, quiz=quiz)
        # Save the new Student instance to the database
        student.save()
    return render(request,"score.html",ctx)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leader_board(request):
    global quiz_student_id
    quiz_id = quiz_student_id[-1]
    #print(quiz_student_id[-1])
    
    students = Student.objects.filter(quiz_id=quiz_id)
    users = []
    
    for student in students:
        user_id = student.user_id
        user = User.objects.get(id=user_id)
        users.append(user)
    
    quiz = Quiz.objects.get(id=quiz_id)
    quiz_id = quiz.quiz_id
    
    combined_list = list(zip(users, students))
    combined_list = sorted(combined_list, key=lambda x: x[1].total_marks, reverse=True)
    
    ranked_list = [(rank+1, user, student) for rank, (user, student) in enumerate(combined_list)]
    
    context = {
        'ranked_list': ranked_list,
        'quiz_id': quiz_id
    }

    return render(request, "leader_board.html", context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quizes(request):
    user=request.user
    id=user.id
    active_quizzes=Quiz.objects.filter(is_active=True)
    attempted_quizzes = Student.objects.filter(student_id=id).values_list('quiz_id', flat=True)
    unattempted_quizzes = active_quizzes.exclude(id__in=attempted_quizzes)
    quizzes = []
    for quiz in unattempted_quizzes:
        quizzes.append({
            'quizId': quiz.quiz_id,
            'marks': quiz.marks
        })

    return JsonResponse(quizzes, safe=False)
    

    



    

