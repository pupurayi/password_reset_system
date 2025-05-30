# reset_system/views.py

from django.shortcuts import render, redirect
from .forms import PasswordResetForm
from .models import PasswordResetRequest
from django.contrib.auth.decorators import login_required

@login_required
def submit_reset_request(request):
    # print("Rendering template: reset_system/submit_request.html")
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            reset_request = form.save(commit=False)
            reset_request.requestor = request.user
            reset_request.save()
            return redirect('request_submitted')  # define this URL
    else:
        form = PasswordResetForm()
    return render(request, 'reset_system/submit_request.html', {'form': form})
