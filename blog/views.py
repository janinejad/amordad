
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, reverse, redirect
from blog.forms import CommentForm
from blog.models import Post, PostCategory
import hashlib
# Create your views here.


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


# def blog(request, *args, cat_slug=None, tag_slug=None, **kwargs):
#     posts = cache.get('posts')
#     if not posts:
#         posts = Post.objects.all()
#         cache.set('posts', posts, 60 * 5)
#     qs = request.GET.get("qs")
#     c_slug = request.GET.get("c_slug")
#     sort_by = request.GET.get("sort_by")
#
#     category = cache.get('category')
#     if not category:
#         category = PostCategory.objects.all()
#         cache.set('category', posts, 60 * 5)
#
#     cat = None
#     if c_slug:
#         posts = posts.filter(category__slug=c_slug)
#     if sort_by:
#         if sort_by == "2":
#             posts = posts.order_by("id")
#     if cat_slug:
#         posts = posts.filter(category__slug=cat_slug)
#         cat = PostCategory.objects.filter(slug=cat_slug).first()
#     if tag_slug:
#         posts = posts.filter(tags__slug=tag_slug)
#     if qs:
#         lookup = Q(title__contains=qs) | Q(Description__contains=qs)
#         posts = posts.filter(lookup)
#     paginator = Paginator(posts, 9)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context = {
#         'paginator': paginator,
#         'page_obj': page_obj,
#         'page_number': page_number,
#         'category': category,
#         'page_cat':cat,
#     }
#     return render(request, 'blog.html', context)
def blog(request, *args, cat_slug=None, tag_slug=None, **kwargs):
    qs = request.GET.get("qs")
    c_slug = request.GET.get("c_slug")
    sort_by = request.GET.get("sort_by")
    page_number = request.GET.get("page")

    # ساخت کلید یکتا برای کش ترکیبی
    cache_key_data = f"qs={qs}&c_slug={c_slug}&cat_slug={cat_slug}&tag_slug={tag_slug}&sort_by={sort_by}"
    cache_key = f"posts_cache_{hashlib.md5(cache_key_data.encode()).hexdigest()}"

    posts = cache.get(cache_key)
    if not posts:
        posts = Post.objects.all()

        # فیلتر جستجو
        if qs:
            posts = posts.filter(Q(title__icontains=qs) | Q(Description__icontains=qs))

        # فیلتر دسته‌بندی URL و GET
        if cat_slug:
            posts = posts.filter(category__slug=cat_slug)
        if c_slug:
            posts = posts.filter(category__slug=c_slug)

        # فیلتر تگ
        if tag_slug:
            posts = posts.filter(tags__slug=tag_slug)

        # مرتب‌سازی
        if sort_by == "2":
            posts = posts.order_by("id")

        # ذخیره در کش برای ۳۰ دقیقه
        cache.set(cache_key, posts, 60 * 30)

    # گرفتن دسته‌بندی‌ها از کش
    category = cache.get('categories')
    if not category:
        category = PostCategory.objects.all()
        cache.set('categories', category, 60 * 30)

    # مشخص کردن دسته انتخاب شده
    cat = PostCategory.objects.filter(slug=cat_slug).first() if cat_slug else None

    # صفحه‌بندی
    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(page_number)

    context = {
        'paginator': paginator,
        'page_obj': page_obj,
        'page_number': page_number,
        'category': category,
        'page_cat': cat,
    }
    return render(request, 'blog.html', context)


def single_post(request, *args, post_slug=None, **kwargs):
    post = cache.get(f"post_{post_slug}")
    if not post:
        post = get_object_or_404(Post, slug=post_slug)
        cache.set(f"post_{post_slug}", post, 60 * 5)
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
    other_post = cache.get(f"other_post_{post.id}")
    if not other_post:
        other_post = Post.objects.all().filter(~Q(id=post.id)).order_by('-id')[:4]
        cache.set(f"other_post_{post.id}", other_post, 60 * 5)
    tags = cache.get(f"tags_{post_slug}")
    if not tags:
        tags = post.tags.all()
        cache.set(f"tags_{post_slug}", tags, 60 * 5)

    context = {
        'tags':tags,
        'other_post': other_post,
        'data': {'post': post, 'form': form},
    }
    return render(request, 'post.html', context)


def blog_sidebar(request, post_id=None):
    categories = cache.get('categories')
    if not categories:
        categories = PostCategory.objects.all()
        cache.set('categories', categories, 60 * 5)
    posts = cache.get('posts')
    if not posts:
        posts = Post.objects.all()[:6]
        cache.set('posts', posts, 60 * 5)
    context = {
        'categories': categories,
        'new_posts': posts,
    }
    if post_id:
        post = Post.objects.filter(id=post_id).first()
        if post:
            context["tags"] = post.tags.all()
    return render(request, 'blog_sidebar.html', context)
