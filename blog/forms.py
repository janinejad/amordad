from django import forms
from blog.models import Comments


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('comment', 'name',)
        error_messages = {
            'comment': {
                'required': "متن نظر را وارد نمایید!",
            },
        }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update(
            {'class': 'form-control form-control-light form-control-lg mt-2', 'placeholder': 'نظر خود را بنویسید',
             'rows': '5','id':'comment-text'})
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control form-control-light form-control-lg', 'placeholder': 'نام و نام خانوادگی',
             'id': 'comment-name'})
