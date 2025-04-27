import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, reverse, redirect
from django.http import JsonResponse

from blog.forms import CommentForm
# Create your views here.
from blog.models import Tag, Post, PostCategory


def get_category_children(category):
    all_categories = []
    all_categories.append(category)

    def loop_category(cat):
        if cat.postcategory_set.count() > 0:
            for c in cat.postcategory_set.all():
                all_categories.append(c)
                loop_category(c)

    loop_category(category)
    return all_categories


def blog(request, *args, cat_slug=None, tag_slug=None, **kwargs):
    posts = Post.objects.all()
    qs = request.GET.get("qs")
    c_slug = request.GET.get("c_slug")
    sort_by = request.GET.get("sort_by")
    category = PostCategory.objects.all()
    cat = None
    if c_slug:
        posts = posts.filter(category__slug=c_slug)
    if sort_by:
        if sort_by == "2":
            posts = posts.order_by("id")
    if cat_slug:
        posts = posts.filter(category__slug=cat_slug)
        cat = PostCategory.objects.filter(slug=cat_slug).first()
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    if qs:
        lookup = Q(title__contains=qs) | Q(Description__contains=qs)
        posts = posts.filter(lookup)
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'paginator': paginator,
        'page_obj': page_obj,
        'page_number': page_number,
        'category': category,
        'page_cat':cat,
    }
    return render(request, 'blog.html', context)


def single_post(request, *args, post_slug=None, **kwargs):
    post = get_object_or_404(Post, slug=post_slug)
    if post.http_response_gone:
        return redirect(reverse('handle_410_error'))
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            instance.post_type = 2
            instance.post = post
            if request.user.is_authenticated:
                instance.user = request.user
            instance.save()
            messages.success(request,
                           'نظر شما با موفقیت ثبت گردید!')
        else:
            messages.error(request,
                           form)
    form = CommentForm()
    other_post = Post.objects.filter(~Q(id=post.id)).order_by('-id')[:4]
    context = {
        'tags': post.tags.all(),
        'other_post': other_post,
        'data': {'post': post, 'form': form},
    }
    return render(request, 'post.html', context)


def blog_sidebar(request, post_id=None):
    context = {
        'categories': PostCategory.objects.all(),
        'new_posts': Post.objects.all()[:6]
    }
    if post_id:
        post = Post.objects.filter(id=post_id).first()
        if post:
            context["tags"] = post.tags.all()
    return render(request, 'blog_sidebar.html', context)
