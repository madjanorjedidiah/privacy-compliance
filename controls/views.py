from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import write_required
from core.choices import ControlStatus
from core.forms import scope_form_to_org

from .models import Control, ControlStatusChange, Evidence


class ControlForm(forms.ModelForm):
    class Meta:
        model = Control
        fields = ['status', 'owner', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['title', 'description', 'external_link', 'file']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


@login_required
def controls_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    qs = (
        Control.objects
        .filter(organization=org)
        .select_related('requirement__framework__jurisdiction', 'owner')
    )
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    framework = request.GET.get('framework', '')
    if q:
        qs = qs.filter(Q(requirement__title__icontains=q) | Q(requirement__code__icontains=q))
    if status:
        qs = qs.filter(status=status)
    if framework:
        qs = qs.filter(requirement__framework__code=framework)

    from jurisdictions.models import Framework
    frameworks = Framework.objects.select_related('jurisdiction').all()
    return render(request, 'controls/list.html', {
        'controls': qs, 'status_choices': ControlStatus.choices,
        'frameworks': frameworks, 'q': q, 'current_status': status, 'current_framework': framework,
    })


@login_required
def control_detail(request, pk):
    from accounts.permissions import can_write
    org = request.active_org
    control = get_object_or_404(Control, pk=pk, organization=org)
    form = ControlForm(request.POST or None, instance=control)
    scope_form_to_org(form, org)
    evidence_form = EvidenceForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if not can_write(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied('Your role does not permit editing.')
        action = request.POST.get('action')
        if action == 'update_control' and form.is_valid():
            previous_status = control.status
            obj = form.save(commit=False)
            if obj.is_done and not obj.completed_at:
                obj.completed_at = timezone.now()
            obj.save()
            if previous_status != obj.status:
                ControlStatusChange.objects.create(
                    control=obj,
                    from_status=previous_status,
                    to_status=obj.status,
                    changed_by=request.user,
                )
            messages.success(request, 'Control updated.')
            return redirect('controls:detail', pk=pk)
        if action == 'add_evidence' and evidence_form.is_valid():
            ev = evidence_form.save(commit=False)
            ev.control = control
            ev.uploaded_by = request.user
            ev.save()
            messages.success(request, 'Evidence added.')
            return redirect('controls:detail', pk=pk)

    return render(request, 'controls/detail.html', {
        'control': control, 'form': form, 'evidence_form': evidence_form,
        'evidence_list': control.evidence.all(),
    })


@write_required
def control_quick_status(request, pk):
    org = request.active_org
    control = get_object_or_404(Control, pk=pk, organization=org)
    new_status = request.POST.get('status')
    if new_status in [s for s, _ in ControlStatus.choices] and new_status != control.status:
        previous_status = control.status
        control.status = new_status
        if control.is_done and not control.completed_at:
            control.completed_at = timezone.now()
        control.save()
        ControlStatusChange.objects.create(
            control=control,
            from_status=previous_status,
            to_status=control.status,
            changed_by=request.user,
        )
    if request.htmx:
        return render(request, 'controls/_row.html', {'c': control})
    return redirect('controls:list')
