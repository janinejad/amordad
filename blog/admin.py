from django.contrib import admin
from easy_select2 import select2_modelform
from .models import Tag, PostCategory, Post, Comments,CommentReply

TagForm = select2_modelform(Tag, attrs={'width': '300px'})
PostCategoryForm = select2_modelform(PostCategory, attrs={'width': '100px'})
PostForm = select2_modelform(Post, attrs={'width': '300px'})

class CommentReplyInline(admin.TabularInline):
    model = CommentReply
    extra = 1

class TagAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    form = TagForm

    class Meta:
        model = Tag


class PostAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'image_tag', 'review_reason', 'url_tag']
    list_filter = ['status']
    search_fields = ('title',)
    form = PostForm

    class Meta:
        model = Post

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('user', 'status', 'review_reason', 'active',)
        return super(PostAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser:
            self.exclude = ('user',)
        else:
            self.exclude = ('user', 'status', 'review_reason', 'active',)
        return super(PostAdmin, self).change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        obj.save()
        super().save_model(request, obj, form, change)


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    form = PostCategoryForm

    class Meta:
        model = PostCategory


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    inlines = [CommentReplyInline]

    class Meta:
        model = Comments


admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
