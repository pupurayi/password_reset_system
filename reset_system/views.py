from django.shortcuts import get_object_or_404, render, redirect
from .forms import PasswordResetForm
from .models import PasswordResetRequest, UserProfile
from django.utils.timezone import now
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
import threading
import socket


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            try:
                profile = user.userprofile
            except UserProfile.DoesNotExist:
                messages.error(request, 'No user profile found.')
                return redirect('custom_login')

            # Redirect all users to dashboard (dashboard handles what they see)
            return redirect('dashboard')

        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'reset_system/login.html')

def custom_logout(request):
    logout(request)
    return redirect('custom_login')

@login_required
def service_desk_dashboard(request):
    if not request.user.userprofile.is_service_desk:
        return HttpResponseForbidden("Only Service Desk users can access this page.")

    requests = PasswordResetRequest.objects.all().order_by('-created_at')
    return render(request, 'reset_system/service_desk_dashboard.html', {'requests': requests})


@login_required
def dashboard(request):
    profile = request.user.userprofile

    if request.method == 'POST':
        form = PasswordResetForm(request.POST, user=request.user)
        if form.is_valid():
            reset_request = form.save(commit=False)
            reset_request.requestor = request.user
            reset_request.department = request.user.userprofile.department
            reset_request.save()

            messages.success(request, "✅ Your password reset request has been submitted successfully.")
            return redirect('dashboard')  # Refresh the page
    else:
        form = PasswordResetForm(user=request.user)

    context = {
        "full_name": request.user.get_full_name(),
        "is_user": not profile.is_deputy_director and not profile.is_ict_head and not profile.is_ict_admin,
        "is_director": profile.is_deputy_director,
        "is_ict_head": profile.is_ict_head,
        "is_ict_admin": profile.is_ict_admin,
        "is_service_desk": getattr(profile, 'is_service_desk', False),
        "form": form,
    }
    return render(request, 'reset_system/dashboard.html', context)


@login_required
def home_redirect(request):
    role = request.user.userprofile.role
    if role == 'User':
        return redirect('user_request_status')
    elif role == 'Director':
        return redirect('director_review_list')
    elif role == 'ICT Head':
        return redirect('ict_review_list')
    else:
        return HttpResponseForbidden("Role not recognized.")

@login_required
def submit_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST, user=request.user)
        if form.is_valid():
            reset_request = form.save(commit=False)
            reset_request.requestor = request.user
            reset_request.department = request.user.userprofile.department
            reset_request.save()

            # ✅ Notify Deputy Director
            dept = reset_request.department
            deputy_director = User.objects.filter(
                userprofile__department=dept,
                userprofile__is_deputy_director=True
            ).first()

            if deputy_director and deputy_director.email:
                subject = f"🔐 Password Reset Approval Needed for {request.user.get_full_name()}"
                message = (
                    f"Good day {deputy_director.get_full_name()},\n\n"
                    f"A password reset request has been submitted by {request.user.get_full_name()} "
                    f"({request.user.username}) for the {reset_request.system} system.\n\n"
                    f"Please review the request in the system.\n"
                    f"- Reason: {reset_request.get_reason_display()}\n"
                    f"- Department: {dept.name}\n\n"
                    f"Regards,\nPassword Reset System"
                )

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[deputy_director.email],
                    fail_silently=True  # Set to False during testing if needed
                )

            messages.success(request, "✅ Your password reset request has been submitted successfully.")
            return redirect('user_request_status')
    else:
        form = PasswordResetForm(user=request.user)

    return render(request, 'reset_system/submit_request.html', {'form': form})

@login_required
def director_review_list(request):
    if not request.user.userprofile.is_deputy_director:
        return HttpResponseForbidden("You are not authorized.")

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        reset_request = get_object_or_404(PasswordResetRequest, id=request_id)

        if reset_request.department == request.user.userprofile.department:
            reset_request.status = 'recommended'
            reset_request.deputy_director_comments = "Auto-approved from list view"
            reset_request.updated_at = now()
            reset_request.save()

            # Email ICT Head
            ict_heads = User.objects.filter(userprofile__is_ict_head=True)
            for head in ict_heads:
                review_url = request.build_absolute_uri(
                    reverse('ict_review_detail', args=[reset_request.id])
                )
                send_mail(
                    subject="🔐 New Request Awaiting Your Approval",
                    message=f"A request from {reset_request.requestor.username} is awaiting your approval.\n\n{review_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[head.email]
                )

        return redirect('director_review_list')

    # For GET
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

    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments')

        if action == 'recommend':
            reset_request.status = 'recommended'
            reset_request.deputy_director_comments = comments
            reset_request.save()

            # Notify ICT Head(s)
            ict_heads = User.objects.filter(userprofile__is_ict_head=True)
            for head in ict_heads:
                review_url = request.build_absolute_uri(
                    reverse('ict_review_detail', args=[reset_request.id])
                )
                send_mail(
                    subject="🔐 Password Reset Request Awaiting Approval",
                    message=f"A request from {reset_request.requestor.username} has been recommended and awaits your approval.\n\nView it here: {review_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[head.email],
                )

            return redirect('director_review_list')

        elif action == 'deny':
            reset_request.status = 'denied'
            reset_request.deputy_director_comments = comments
            reset_request.save()
            return redirect('director_review_list')
    return render(request, 'reset_system/recommend_request.html', {'request_obj': reset_request})


@login_required
def user_request_status(request):
    requests = PasswordResetRequest.objects.filter(requestor=request.user).order_by('-created_at')
    return render(request, 'reset_system/user_requests.html', {'requests': requests})


@login_required
def ict_review_detail(request, request_id):
    if not request.user.userprofile.is_ict_head:
        return HttpResponseForbidden("Only the ICT Head can access this page.")
    if not request.user.userprofile.is_ict_head:
        return HttpResponseForbidden("Access denied.")

    reset_request = get_object_or_404(PasswordResetRequest, id=request_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments')

        if action == 'approve':
            reset_request.status = 'approved'
        elif action == 'deny':
            reset_request.status = 'denied'
        else:
            return HttpResponse("Invalid action.")
        reset_request.cto_comments = comments
        reset_request.updated_at = now()
        reset_request.save()
        return redirect('ict_review_list')

    return render(request, 'reset_system/ict_review_detail.html', {'request_obj': reset_request})

@login_required
def ict_admin_dashboard(request):
    if not request.user.userprofile.is_ict_admin:
        return HttpResponseForbidden("Only ICT Admins can access this page.")

    requests = PasswordResetRequest.objects.filter(status='approved')
    return render(request, 'reset_system/ict_admin_dashboard.html', {'requests': requests})

@login_required
def ict_review_list(request):
    if not request.user.userprofile.is_ict_head:
        return HttpResponseForbidden("Only the ICT Head can access this page.")

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')

        reset_request = get_object_or_404(PasswordResetRequest, id=request_id)

        if action == 'approve':
            reset_request.status = 'approved'
        elif action == 'deny':
            reset_request.status = 'denied'
        else:
            return HttpResponse("Invalid action.")

        reset_request.cto_comments = comments
        reset_request.updated_at = now()
        reset_request.save()

        # Optional: email notification to ICT Admins
        try:
            ict_admins = User.objects.filter(userprofile__is_ict_admin=True)
            for admin in ict_admins:
                review_url = request.build_absolute_uri(
                    reverse('finalise_request', args=[reset_request.id])
                )
                send_mail(
                    subject="🔐 ICT Head Approved a Request",
                    message=f"A request from {reset_request.requestor.username} has been approved.\n\nView it here: {review_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.email],
                )
        except socket.error as e:
            print("Email failed:", e)

        messages.success(request, f"✅ Request {action}ed successfully.")

    requests = PasswordResetRequest.objects.filter(status='recommended')
    return render(request, 'reset_system/ict_review_list.html', {'requests': requests})

@login_required
def finalise_request(request, request_id):
    # Only ICT Admins allowed
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_ict_admin:
        return HttpResponseForbidden("Only ICT Admins can access this page.")

    reset_request = get_object_or_404(PasswordResetRequest, id=request_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if not new_password:
            messages.error(request, "Please enter a new password.")
            return redirect('finalise_request', request_id=reset_request.id)

        # Update the request
        reset_request.status = 'completed'
        reset_request.ict_personnel = request.user
        reset_request.completed_at = now()
        reset_request.save()

        # Send email to user
        send_mail(
            subject="🔐 Your password has been reset",
            message=f"Hello {reset_request.requestor.username},\n\nYour password for the {reset_request.system} system has been reset.\n\nYour new password is: {new_password}\n\nPlease log in and change it immediately.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reset_request.requestor.email],
        )

        messages.success(request, "Password reset finalized and user notified.")
        return redirect('ict_admin_dashboard')

    return render(request, 'reset_system/finalise_request.html', {
        'request_obj': reset_request
    })


@login_required
def ict_admin_review_list(request):
    requests = PasswordResetRequest.objects.filter(status='approved')
    return render(request, 'reset_system/ict_admin_review_list.html', {'requests': requests})

