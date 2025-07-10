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
        self.exclude = ('user','review_reason',)
        return super(PostAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser:
            self.exclude = ('user',)
        else:
            self.exclude = ('user', 'review_reason',)
        return super(PostAdmin, self).change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        from seo.models import JuiceLink
        if obj.Description and obj.create_link_allowed:
            links = JuiceLink.objects.all_sorted_by_prirority().filter(apply_for_posts=True)
            from extensions.seo import create_link_in_content, remove_link
            content = remove_link(obj.Description)
            for link in links:
                if link.title in obj.Description:
                    authorized_tags_list = link.authorized_tags.split(",")
                    content = create_link_in_content(link.title, content, link.link,
                                                     authorized_tags_list)
            obj.Description = content
        obj.save()
        super().save_model(request, obj, form, change)


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    form = PostCategoryForm

    class Meta:
        model = PostCategory


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_filter = ['post_type','is_confirmed']
    list_display = ['__str__']
    inlines = [CommentReplyInline]

    class Meta:
        model = Comments


admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
