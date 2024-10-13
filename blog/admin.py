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
    exclude = ('image_webp',)

    class Meta:
        model = Post

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('user', 'status', 'review_reason', 'active', 'image_webp',)
        return super(PostAdmin, self).add_view(request, form_url, extra_context)

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.status == 4 or obj.status == 3:
                if not (request.user.is_superuser or request.user.is_content_manager):
                    return False
        return True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser or request.user.is_content_manager:
            self.exclude = ('user', 'image_webp',)
        else:
            self.exclude = ('user', 'status', 'review_reason', 'active', 'image_webp',)
        return super(PostAdmin, self).change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        if change and 'image' in form.changed_data:
            post = Post.objects.get(pk=obj.pk)
            old_image = post.image
            old_image.delete()

            old_image_webp = post.image_webp
            old_image_webp.delete()

        if obj.image:
            obj.image.save(
                obj.image.name,
                obj.image.file,
                save=False,
            )
            obj.image_webp.save(
                obj.image.name.replace(".jpg", ".webp"),
                obj.image.file,
                save=False,
            )
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
    exclude = ['image_webp']

    class Meta:
        model = PostCategory

    def save_model(self, request, obj, form, change):
        if change and 'image' in form.changed_data:
            product_cat = PostCategory.objects.get(pk=obj.pk)
            old_image = product_cat.image
            old_image.delete()

            old_image_webp = product_cat.image_webp
            old_image_webp.delete()

        if obj.image:
            obj.image.save(
                obj.image.name,
                obj.image.file,
                save=False,
            )
            obj.image_webp.save(
                obj.image.name.replace(".jpg", ".webp"),
                obj.image.file,
                save=False,
            )

        obj.save()
        super().save_model(request, obj, form, change)


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['__str__']

    class Meta:
        model = Comments


admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
