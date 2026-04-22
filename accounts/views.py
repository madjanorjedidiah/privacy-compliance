from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import SignupForm
from .models import Membership, Organization, OrgProfile


def signup(request):
    if request.method == 'POST':
        from django_ratelimit.core import is_ratelimited
        if is_ratelimited(
            request, group='signup', key='ip',
            rate=settings.RATE_LIMIT_SIGNUP, method='POST', increment=True,
        ):
            return render(request, 'accounts/rate_limited.html', status=429)
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.display_name = form.cleaned_data['display_name']
            user.save()

            org = Organization.objects.create(
                name=form.cleaned_data['organization_name'],
                country=form.cleaned_data['organization_country'][:2],
            )
            OrgProfile.objects.create(organization=org)
            Membership.objects.create(
                user=user, organization=org,
                role=Membership.Role.OWNER, is_primary=True,
            )

            login(request, user)
            messages.success(request, 'Welcome! Let\'s scope your compliance.')
            return redirect('onboarding:basics')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


class LoginView(DjangoLoginView):
    template_name = 'accounts/login.html'

    def post(self, request, *args, **kwargs):
        from django_ratelimit.core import is_ratelimited
        if is_ratelimited(
            request, group='login', key='ip',
            rate=settings.RATE_LIMIT_LOGIN, method='POST', increment=True,
        ):
            return render(request, 'accounts/rate_limited.html', status=429)
        return super().post(request, *args, **kwargs)


class LogoutView(DjangoLogoutView):
    next_page = 'accounts:login'


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {})
