from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from assessments.services import run_assessment
from controls.services import sync_controls_from_assessment

from .forms import OrgBasicsForm, OrgProfileForm
from .models import OrgProfile


@login_required
def basics(request):
    org = request.active_org
    if not org:
        messages.error(request, 'No organization on file.')
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = OrgBasicsForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            return redirect('onboarding:profile')
    else:
        form = OrgBasicsForm(instance=org)
    return render(request, 'onboarding/basics.html', {'form': form, 'step': 1, 'total_steps': 3})


@login_required
def profile(request):
    org = request.active_org
    profile_obj, _ = OrgProfile.objects.get_or_create(organization=org)
    if request.method == 'POST':
        form = OrgProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            obj = form.save(commit=False)
            for field in ('sectors', 'data_categories', 'processing_purposes',
                          'data_subject_locations', 'has_establishment_in',
                          'transfer_mechanisms'):
                setattr(obj, field, list(form.cleaned_data.get(field) or []))
            obj.save()
            return redirect('onboarding:review')
    else:
        form = OrgProfileForm(instance=profile_obj)
    return render(request, 'onboarding/profile.html', {'form': form, 'step': 2, 'total_steps': 3})


@login_required
def review(request):
    org = request.active_org
    profile_obj = getattr(org, 'profile', None)

    from jurisdictions.applicability import framework_applies
    from jurisdictions.models import Framework

    preview = []
    if profile_obj:
        for framework in Framework.objects.select_related('jurisdiction').all():
            result = framework_applies(profile_obj, framework.code)
            preview.append({'framework': framework, 'applicable': result.applicable, 'rationale': result.rationale})

    if request.method == 'POST':
        assessment = run_assessment(org, user=request.user, name='Initial applicability assessment')
        result = sync_controls_from_assessment(org, assessment)
        from django.utils import timezone
        org.onboarded_at = timezone.now()
        org.save(update_fields=['onboarded_at'])
        msg = f'Applicable frameworks scoped. {result["created"]} controls ready to action.'
        if result['deprecated'] or result['removed']:
            msg += f' ({result["deprecated"]} deprecated, {result["removed"]} removed.)'
        messages.success(request, msg)
        return redirect('compliance:home')

    return render(request, 'onboarding/review.html', {
        'preview': preview, 'profile': profile_obj,
        'step': 3, 'total_steps': 3,
    })
