from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Quiz(models.Model):
    quiz_title=models.CharField(max_length=300)
    num_questions=models.IntegerField(default=0)
    quiz_id=models.CharField(max_length=100,null=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.quiz_title
    
class Question(models.Model):
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE)
    question_text=models.CharField(max_length=300)

    def __str__(self):
        return self.question_text
    
class Choice(models.Model):    
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    choice_text=models.CharField(max_length=300)
    correct=models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text
    
class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE)
    total_marks=models.IntegerField()


#need to create a model student attempted a question
#class Answers(models.Model):

