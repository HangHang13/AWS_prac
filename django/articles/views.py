from ast import keyword
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from .models import Article, Comment
from .forms import ArticleForm, CommentForm
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.
@require_safe
def index(request):
    articles = Article.objects.order_by('-pk')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'articles': articles,
        'page_obj' : page_obj
    }
    return render(request, 'articles/index.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user
            article.save()
            return redirect('articles:detail', article.pk)
    else:
        form = ArticleForm()
    context = {
        'form': form,
    }
    return render(request, 'articles/create.html', context)


@require_safe
def detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comment_form = CommentForm()
    # 조회한 article의 모든 댓글을 조회(역참조)
    comments = article.comment_set.all()
    context = {
        'article': article,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'articles/detail.html', context)


@require_POST
def delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user.is_authenticated:
        if request.user == article.user:
            article.delete()
            return redirect('articles:index')
    return redirect('articles:index')


@login_required
@require_http_methods(['GET', 'POST'])
def update(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user == article.user:
        if request.method == 'POST':
            form = ArticleForm(request.POST, request.FILES, instance=article)
            if form.is_valid():
                article = form.save()
                return redirect('articles:detail', article.pk)
        else:
            form = ArticleForm(instance=article)
    else:
        return redirect('articles:index')
    context = {
        'article': article,
        'form': form,
    }
    return render(request, 'articles/update.html', context)


@require_POST
def comment_create(request, pk):
    if request.user.is_authenticated:
        article = get_object_or_404(Article, pk=pk)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
        return redirect('articles:detail', article.pk)
    return redirect('accounts:login')


@require_POST
def comment_delete(request, article_pk ,comment_pk):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, pk=comment_pk)
        if request.user == comment.user:
            comment.delete()
    return redirect('articles:detail', article_pk)


@require_POST
def likes(request, article_pk):
    if request.user.is_authenticated:
        article = get_object_or_404(Article, pk=article_pk)
        
        if article.like_users.filter(pk=request.user.pk).exists():
            # if request.user in article.like_users.all()
            article.like_users.remove(request.user)
            liked = False
        else:
            article.like_users.add(request.user)
            liked = True
        context = {
            'liked': liked,
            'liked_cnt' : article.like_users.count(),
            
        }
        return JsonResponse(context)
        # return redirect('articles:index')
    return redirect('accounts:login')

def search(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            searchKeywork = request.GET.get("q","")
            articles = Article.objects.filter(
                Q(title__contains=searchKeywork)|Q(content__contains=searchKeywork)).order_by('-created_at')
            paginator = Paginator(articles, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'articles': articles,
                'page_obj' : page_obj
         }   
        return render(request, 'articles/index.html', context)
    else:
        return render(request,'accounts:login')