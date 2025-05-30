from django import forms
from .models import PasswordResetRequest
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class PasswordResetForm(forms.ModelForm):
    class Meta:
        model = PasswordResetRequest
        fields = ['system', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit Request'))
