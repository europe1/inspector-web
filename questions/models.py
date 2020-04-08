from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    text = models.CharField(max_length=255)
    attached_image = models.ImageField(upload_to='userimages/questions',
        blank=True, null=True)
    tags = models.CharField(max_length=100, default='general')
    username = models.CharField(max_length=30)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True)
    selected_answer = models.OneToOneField('Answer', on_delete=models.PROTECT,
        blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.username, self.text)

class Answer(models.Model):
    target_question = models.ForeignKey('Question', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    username = models.CharField(max_length=30)
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True)
    rating = models.IntegerField(default=0)
    def __str__(self):
        return '{} - {}'.format(self.username, self.text)

class QuestionView(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class AnswerRating(models.Model):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    plus = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
