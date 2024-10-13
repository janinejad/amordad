from django.urls import path
from .views import blog,blog_sidebar,single_post

app_name = 'blog'
urlpatterns = [
  path('blog/',blog,name='blog'),
  path('blog/category-<slug:cat_slug>/', blog, name='blog'),
  path('blog/tag-<slug:tag_slug>/', blog, name='blog'),
  path('blog/post-<slug:post_slug>/',single_post,name='single_post'),
  path('blog_sidebar/<int:post_id>',blog_sidebar,name='blog_sidebar'),
]
