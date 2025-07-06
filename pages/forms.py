from django import forms
from .models import ContactUs, Emails


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name', 'phone_number', 'title', 'text']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control form-control-lg form-control-light', 'id': 'c-name',
                       'required': 'required'}),
            'title': forms.Select(
                attrs={'class': 'form-select form-select-lg form-select-light', 'id': 'c-subject',
                       'required': 'required'}),
            'phone_number': forms.TextInput(
                attrs={'class': 'form-control form-control-lg form-control-light', 'required': 'required',
                       'id': 'c-phone'}),
            'text': forms.Textarea(
                attrs={'class': 'form-control form-control-lg form-control-light', 'required': 'required',
                       'id': 'c-message', 'rows': "4"}),
        }

    def __init__(self, *args, **kwargs):
        cf = kwargs.pop('cf', None)
        super(ContactUsForm, self).__init__(*args, **kwargs)
        if cf is not None:
            self.fields['title'].queryset = cf.contactsubject_set.all()


class SendEmailForm(forms.ModelForm):
    class Meta:
        model = Emails
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(
                attrs={'class': 'form-control',
                       'required': 'required',
                       'placeholder': 'ایمیل شما'}),
        }
