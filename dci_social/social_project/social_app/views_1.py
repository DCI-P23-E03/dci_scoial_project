from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.http import HttpResponse
from .models import User, Post

# class HomePageView(View):
#     def get(self,request):
#         return HttpResponse('<h1>finally weekend !</h1>')
    
    
# class UserListView(View):
#     def get(self, request):
#         users = User.objects.all()
#         return render(request, 'social_app/user_list.html', {'users': users})

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
        
    
    
    
    
    
    
