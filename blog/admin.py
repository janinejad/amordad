from django.contrib import admin
from easy_select2 import select2_modelform
from .models import Tag, PostCategory, Post, Comments

TagForm = select2_modelform(Tag, attrs={'width': '300px'})
PostCategoryForm = select2_modelform(PostCategory, attrs={'width': '100px'})
PostForm = select2_modelform(Post, attrs={'width': '300px'})


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

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.status == 4 or obj.status == 3:
                if not (request.user.is_superuser or request.user.is_content_manager):
                    return False
        return True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser or request.user.is_content_manager:
            self.exclude = ('user',)
        else:
            self.exclude = ('user', 'status', 'review_reason', 'active',)
        return super(PostAdmin, self).change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        obj.save()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_content_manager:
            return qs
        return qs.filter(user=request.user)


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    form = PostCategoryForm

    class Meta:
        model = PostCategory


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['__str__']

    class Meta:
        model = Comments


admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
