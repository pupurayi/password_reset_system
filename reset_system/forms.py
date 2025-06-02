from django import forms
from .models import PasswordResetRequest, Department
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class PasswordResetForm(forms.ModelForm):
    class Meta:
        model = PasswordResetRequest
        fields = ['system', 'reason', 'department', 'approver']  # 👈 add these fields

    def __init__(self, *args, **kwargs):
        # Expecting the request.user to be passed in from the view
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Crispy helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit Request'))

        # If the user is available and has a department (via profile)
        if user and hasattr(user, 'userprofile'):
            user_dept = user.userprofile.department

            # Pre-fill department
            self.fields['department'].initial = user_dept
            self.fields['department'].disabled = True  # Optional: lock it

            # Filter approver choices
            self.fields['approver'].queryset = User.objects.filter(
                userprofile__department=user_dept,
                userprofile__is_deputy_director=True
            )
        else:
            self.fields['approver'].queryset = User.objects.none()
