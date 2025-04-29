from tkinter.messagebox import QUESTION

from django.db import models

class User(models.Model):
    nickname = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nickname

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, null=False)
    content = models.TextField(max_length=1500, null=False)
    likes = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    answers = models.ManyToManyField('Answer', related_name='question_answers', blank=True)

    def __str__(self):
        return self.title

class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField(max_length=1500, null=False)
    likes = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    created_at = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    reply_to_answer = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='nested_replies')

    def __str__(self):
        return f"Answer by {self.author.nickname} to {self.reply_to.nickname if self.reply_to else 'question'}"
