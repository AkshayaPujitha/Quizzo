from rest_framework import serializers
from .models import Quiz,Question,Choice

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Question
        fields=['quiz', 'question_text']
        
    
class QuizSerializer(serializers.ModelSerializer):

    class Meta:
        model=Quiz
        fields="__all__"

    def validate_quiz_id(self, value):
        if Quiz.objects.filter(quiz_id=value).exists():
            raise serializers.ValidationError('Quiz ID must be unique.')
        return value
