from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import User


class RegisterUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('0', code='duplicate_email')
        return email


class UserPasswordChangeForm(forms.Form):
    old_password = forms.CharField()
    new_password1 = forms.CharField()
    new_password2 = forms.CharField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError('0', code="password_incorrect")
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError('-1', code="password_mistmatch")
        try:
            password_validation.validate_password(password2, self.user)
        except:
            raise ValidationError('2', code='weak_password')
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class EmailChangeForm(forms.Form):
    """
    A form that lets a user change set their email while checking for a change in the
    e-mail.
    """
    new_email = forms.EmailField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_new_email(self):
        old_email = self.user.email
        new_email = self.cleaned_data.get('new_email')
        if new_email and old_email:
            if new_email == old_email:
                raise forms.ValidationError('0', code='same_email')
        if User.objects.filter(email=new_email).exists():
            raise forms.ValidationError('0', code='already_registered')
        return new_email

    def save(self, commit=True):
        email = self.cleaned_data["new_email"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user
