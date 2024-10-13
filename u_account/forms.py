from django import forms
from .models import User
from django.core import validators


class RegisterForm(forms.ModelForm):
    password2 = forms.CharField(required=True,
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-control form-control-light', 'minlength': '8'}))
    agree_to_terms = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'password2', 'agree_to_terms', 'mobile']
        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'form-control form-control-light', 'id': 'signup-name', 'required': 'required',
                       'placeholder': 'نام'}),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control form-control-light', 'required': 'required',
                       'placeholder': 'نام خانوادگی'}),
            'mobile': forms.TextInput(
                attrs={'class': 'form-control form-control-light', 'required': 'required',
                       'placeholder': '*********09', 'minlength': '11'}),
            'email': forms.EmailInput(
                attrs={'class': 'form-control form-control-light', 'required': 'required', 'placeholder': 'ایمیل'}),
            'password': forms.PasswordInput(
                attrs={'class': 'form-control form-control-light', 'required': 'required', 'minlength': '8'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user = User.objects.filter(username=email).first()
        if user:
            raise forms.ValidationError('کاربر با این ایمیل از قبل وجود دارد.')
        return email

    def clean_password2(self):
        password2 = self.cleaned_data.get("password2")
        password = self.cleaned_data.get("password")
        if not password == password2:
            raise forms.ValidationError('تایید رمز عبور اشتباه است.')
        return password2

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if len(first_name) == 0:
            raise forms.ValidationError('نام خود را وارد نمایید.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if len(last_name) == 0:
            raise forms.ValidationError('نام خانوادگی خود را وارد نمایید.')
        return last_name

    def clean_agree_to_terms(self):
        agree_to_terms = self.cleaned_data.get("agree_to_terms")
        if not agree_to_terms:
            raise forms.ValidationError('لطفا جهت ثبت نام در سایت قوانین را بپذیرید.')
        return agree_to_terms


class EditInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'tel_no', 'personal_address', 'is_official', 'image',
                  'organization_name', 'firm_no', 'firm_national_id', 'firm_economical_no', 'official_address',
                  'official_postal_code'
            , 'firm_tel_no']
        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'form-control form-control-light mt-3', 'data-bs-binded-element': '#name-value',
                       'data-bs-unset-value': 'مشخص نشده است'}),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control form-control-light mt-3', 'data-bs-binded-element': '#family-value',
                       'data-bs-unset-value': 'مشخص نشده است'}),
            'tel_no': forms.TextInput(
                attrs={'class': 'form-control form-control-light mt-3', 'data-bs-binded-element': '#phone-value',
                       'data-bs-unset-value': 'مشخص نشده است'}),
            'personal_address': forms.Textarea(
                attrs={'class': 'form-control form-control-light mt-3', 'data-bs-binded-element': '#address-value',
                       'data-bs-unset-value': 'مشخص نشده است', 'rows': '5'}),
            'organization_name': forms.TextInput(
                attrs={'class': 'form-control form-control-light mt-3',
                       'data-bs-binded-element': '#organization-name-value',
                       'data-bs-unset-value': 'مشخص نشده است'}),
            'is_official': forms.CheckboxInput(
                attrs={'id': 'isOfficial', 'class': 'form-check-input'}),
            'firm_no': forms.TextInput(
                attrs={'class': 'form-control form-control-light mt-3', 'data-bs-binded-element': '#firm_no-value',
                       'data-bs-unset-value': 'مشخص نشده است'}),
            'firm_national_id': forms.TextInput(
                attrs={'class': 'form-control form-control-light mt-3',
                       'data-bs-binded-element': '#firm_national_id-value',
                       'data-bs-unset-value': 'مشخص نشده است'}),
            'firm_economical_no': forms.TextInput(
                attrs={'class': 'form-control form-control-light mt-3',
                       'data-bs-binded-element': '#firm-economical-no-value',
                       'data-bs-unset-value': 'مشخص نشده است'}),
            'firm_tel_no': forms.TextInput(
                attrs={'class': 'form-control form-control-light mt-3',
                       'data-bs-binded-element': '#firm_tel_no-value',
                       'data-bs-unset-value': 'مشخص نشده است'}),
            'official_postal_code': forms.TextInput(
                attrs={'class': 'form-control form-control-light mt-3',
                       'data-bs-binded-element': '#official_postal_code-value',
                       'data-bs-unset-value': 'مشخص نشده است'}),
            'official_address': forms.Textarea(
                attrs={'class': 'form-control form-control-light mt-3',
                       'data-bs-binded-element': '#official_address-value',
                       'data-bs-unset-value': 'مشخص نشده است', 'rows': '5'}),
            'image': forms.FileInput(
                attrs={'class': 'file-uploader border-light bg-faded-light',
                       'accept': 'image/png, image/jpeg',
                       'data-style-panel-layout': 'compact',
                       'data-image-preview-height': '160',
                       'data-image-crop-aspect-ratio': '1:1',
                       'data-image-resize-target-width': '200',
                       'data-image-resize-target-height': '200',
                       'type': 'file',
                       }),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if len(first_name) == 0:
            raise forms.ValidationError('نام خود را وارد نمایید.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if len(last_name) == 0:
            raise forms.ValidationError('نام خانوادگی خود را وارد نمایید.')
        return last_name

    def clean_personal_address(self):
        personal_address = self.cleaned_data.get("personal_address")
        if not personal_address:
            raise forms.ValidationError('ادرس را وارد نمایید.')
        return personal_address

    def clean_organization_name(self):
        print("clean_organization_name")
        is_official = self.cleaned_data.get("is_official")
        organization_nam = self.cleaned_data.get("organization_name")
        if is_official:
            if not organization_nam:
                print("if not organization_nam")
                raise forms.ValidationError('نام شرکت/سازمان  را وارد نمایید.')
        return organization_nam

    def clean_tel_no(self):
        tel_no = self.cleaned_data.get("tel_no")
        if not tel_no:
            raise forms.ValidationError('شماره تماس را وارد نمایید.')
        return tel_no

    def clean_official_address(self):
        is_official = self.cleaned_data.get("is_official")
        official_address = self.cleaned_data.get("official_address")
        if is_official:
            if not official_address:
                raise forms.ValidationError('آدرس را وارد نمایید.')
        return official_address

    def clean_firm_tel_no(self):
        is_official = self.cleaned_data.get("is_official")
        firm_tel_no = self.cleaned_data.get("firm_tel_no")
        if is_official:
            if not firm_tel_no:
                raise forms.ValidationError('شماره تماس را وارد نمایید.')
        return firm_tel_no

    def clean_firm_national_id(self):
        print("clean_firm_national_id")
        is_official = self.cleaned_data.get("is_official")
        firm_national_id = self.cleaned_data.get("firm_national_id")
        if is_official:
            if not firm_national_id:
                print("if not firm_national_id")
                raise forms.ValidationError('شناسه ملی  را وارد نمایید.')
        return firm_national_id

    def clean_firm_economical_no(self):
        print("clean_firm_economical_no")
        is_official = self.cleaned_data.get("is_official")
        firm_economical_no = self.cleaned_data.get("firm_economical_no")
        if is_official:
            if not firm_economical_no:
                print("f not firm_economical_no")
                raise forms.ValidationError('کد اقتصادی را وارد نمایید.')
        return firm_economical_no

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            if image.file.size > 1024000:
                raise forms.ValidationError('سایز تصویر نباید بیشت از یک مگا بایت باشد.')
        return image


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True, label='پست الکترونیکی',
        widget=forms.EmailInput(
            attrs={'placeholder': 'پست الکترونیکی', 'class': 'form-control form-control-light',
                   'id': 'signin-email'}),
        validators=[
            validators.MaxLengthValidator(100),
            validators.EmailValidator
        ]
    )
    password = forms.CharField(
        required=True, label='رمز عبور',
        widget=forms.PasswordInput(
            attrs={'placeholder': 'رمز عبور', 'class': 'form-control form-control-light', 'id': 'signin-password'}),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True, label='پست الکترونیکی',
        widget=forms.EmailInput(
            attrs={'placeholder': 'پست الکترونیکی', 'class': 'form-control form-control-light',
                   'id': 'signin-email'}),
        validators=[
            validators.MaxLengthValidator(100),
            validators.EmailValidator
        ]
    )


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        required=True, label='رمز عبور',
        widget=forms.PasswordInput(
            attrs={'placeholder': 'رمز عبور', 'class': 'form-control form-control-light', 'id': 'signin-password'}),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    password2 = forms.CharField(
        required=True, label='رمز عبور',
        widget=forms.PasswordInput(
            attrs={'placeholder': 'تایید رمز عبور', 'class': 'form-control form-control-light',
                   'id': 'signin-password'}),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 8:
            raise forms.ValidationError('رمز عبور نباید کمتر از 8 کارکتر باشد.')
        return password

    def clean_password2(self):
        password2 = self.cleaned_data.get("password2")
        password = self.cleaned_data.get("password")
        if not password == password2:
            raise forms.ValidationError('تایید رمز عبور اشتباه است.')
        return password2
