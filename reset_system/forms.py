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


class WindowsADResetForm(forms.ModelForm):
    affected_director = forms.ModelChoiceField(
        queryset=User.objects.filter(userprofile__is_deputy_director=True),
        label="Departmental Director",
        required=True
    )

    class Meta:
        model = PasswordResetRequest
        fields = ['affected_name', 'affected_department', 'affected_extension', 'reason', 'affected_director']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].initial = 'forgot_password'
        self.fields['reason'].label = "Reason for Reset"
        self.fields['affected_name'].label = "Full Name of Affected User"
        self.fields['affected_extension'].label = "User's Extension"
        self.fields['affected_department'].label = "User's Department"