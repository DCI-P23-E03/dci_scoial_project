```python
models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core import validators
# Create your models here.

bad_word = ['cat','dog','fish']

def validate_bad_words(value):
    for word in bad_word:
        if word in value:
            raise ValidationError('No bad words')
        
def validate_age(value):
    if value and (value < 18 or value > 100):
        raise ValidationError('Age should be between 18 and 100')
    
def valide_email(value):
    if value and value.endswith('.what'):
        raise ValidationError("Email address should not end with '.what'.")
    
class User(models.Model):
    username = models.CharField(max_length=50,unique=True,validators=[validate_bad_words,validators.validate_slug])
    email = models.EmailField(unique=True,validators=[valide_email,validators.EmailValidator(message='enter a valid email')])
    bio = models.TextField(blank=True,validators=[validate_bad_words])
    joined_at = models.DateTimeField(default=timezone.now)
    age = models.PositiveIntegerField(null=True,validators=[validate_age])
    
    def clean(self) :
        if not self.joined_at:
            self.joined_at = timezone.now()
            
    def save(self,*args,**kwargs):
        self.full_clean()
        return super().save(*args,**kwargs)
    def __str__(self) :
        return self.username
    
    class Meta:
        ordering = ['-joined_at','username']
        constraints = [models.UniqueConstraint(fields=['username','email'],name='unique email/username')]
        db_table = 'users table'
        verbose_name = 'users from the app'
        
class Post(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    PUBLIC = 'public'
    PRIVATE = 'private'
    VISIBILITY_CHOICES = [
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
    ]
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default=PUBLIC)
    
    def clean(self) :
        if len(self.post) < 10:
            raise ValidationError('POst length must be at least 10')
        
        for word in bad_word:
            if word in self.post:
                raise ValidationError('Post contains inappropriate word')
    
    def save(self,*args,**kwargs):#
        self.full_clean()
        return super().save(*args,**kwargs)
    
    def __str__(self) :
        return self.user.username
    
    class Meta :
        ordering =['created_at']
        verbose_name = 'user post'
```
```python
forms.py
from django import forms
from .models import User,Post

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','bio','age']
        
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post','visibility']
```
```python
views.py
from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView,UpdateView,CreateView,DeleteView
from django.http import HttpResponse
from .models import User, Post
from django.urls import reverse_lazy
from .form_1 import UserForm,PostForm
import logging
logger = logging.getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'social_app/homepage.html'


class UserListView(ListView):
    model = User
    context_object_name = 'users'
    template_name ='social_app/user_list.html'
    
class UserDetailView(DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'social_app/user_detail.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    
class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'social_app/post_list.html'
    

class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'social_app/post_detail.html'
    pk_url_kwarg = 'post_id'
    
    
class UserPostsView(ListView):
    model = Post
    template_name = 'social_app/user_posts.html'
    context_object_name = 'posts'
    
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        print(context)
        print('*'*100)
        username = self.kwargs['username']
        user = get_object_or_404(User,username = username)
        context['user']= user
        print(context)
        return context
    
    def get_queryset(self) :
        username = self.kwargs['username']
        user = get_object_or_404(User , username = username)
        return Post.objects.filter(user=user).order_by('-created_at')
    
    
class CreateUserView(CreateView):
    model = User
    form_class = UserForm
    template_name ='social_app/user_form.html'
    success_url = reverse_lazy('user_list')
    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f'User created {self.object.username}')
        return response
            
class CreatePostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'social_app/post_form.html'
    def form_valid(self,form):
        user = get_object_or_404(User,username=self.kwargs['username'])
        form.instance.user = user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('user_detail',kwargs ={'username':self.object.user.username})
    
    
class UpdateUserView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'social_app/user_form.html'
    
    def get_object(self, queryset=None):
        return get_object_or_404(User,username = self.kwargs['username'])
    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'username': self.object.username})
    def form_valid(self, form):
        response = super().form_valid(form)
        logger.debug(self.request)
        logger.info(f"User updated: {self.object.username}")
        return response
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        logger.warning(f"User update failed: {self.object.username}")
        return response
   
class UpdatePostView(UpdateView):
    model = Post
    template_name = 'social_app/post_form.html'
    form_class = PostForm
    pk_url_kwarg ='post_id'
    slug_url_kwarg = 'username'
    slug_field ='username'
    def get_success_url(self):
        return reverse_lazy('user_posts', kwargs={'username': self.object.user.username})
    def get_object(self, queryset=None):
        return get_object_or_404(Post,id = self.kwargs['post_id'])

 
class DeleteUserView(DeleteView):
    model = User
    template_name = 'social_app/delete_user.html'
    success_url =reverse_lazy('user_list')
    slug_url_kwarg = 'username'
    slug_field ='username'
    
class DeletePostView(DeleteView):
    model = Post
    template_name = 'social_app/delete_post.html'
    pk_url_kwarg ='post_id'
    slug_url_kwarg = 'username'
    slug_field ='username'
    def get_success_url(self):
        return reverse_lazy('user_posts', kwargs={'username': self.object.user.username})
```