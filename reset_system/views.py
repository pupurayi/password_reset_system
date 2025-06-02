from django.shortcuts import get_object_or_404, render, redirect
from .forms import PasswordResetForm
from .models import PasswordResetRequest
from django.utils.timezone import now
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required



@login_required
def submit_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST, user=request.user)
        if form.is_valid():
            reset_request = form.save(commit=False)
            reset_request.requestor = request.user
            reset_request.department = request.user.userprofile.department
            reset_request.save()
            return redirect('request_submitted')
    else:
        form = PasswordResetForm(user=request.user)

    return render(request, 'reset_system/submit_request.html', {'form': form})


@login_required
def director_review_list(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_deputy_director:
        return HttpResponseForbidden("You are not authorized to view this page.")

    department = request.user.userprofile.department
    requests = PasswordResetRequest.objects.filter(department=department, status='pending')

    return render(request, 'reset_system/director_review_list.html', {'requests': requests})


@login_required
def recommend_request(request, request_id):
    reset_request = get_object_or_404(PasswordResetRequest, id=request_id)

    if (
        not hasattr(request.user, 'userprofile')
        or not request.user.userprofile.is_deputy_director
        or request.user.userprofile.department != reset_request.department
    ):
        return HttpResponseForbidden("You are not authorized to act on this request.")

    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments')

        if action == 'recommend':
            reset_request.status = 'recommended'
        elif action == 'deny':
            reset_request.status = 'denied'
        else:
            return HttpResponse("Invalid action.")

        reset_request.deputy_director_comments = comments
        reset_request.updated_at = now()
        reset_request.save()
        return redirect('director_review_list')

    return render(request, 'reset_system/recommend_request.html', {'request_obj': reset_request})


@login_required
def user_request_status(request):
    requests = PasswordResetRequest.objects.filter(requestor=request.user).order_by('-created_at')
    return render(request, 'reset_system/user_requests.html', {'requests': requests})

