from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import write_required
from core.forms import scope_form_to_org

from .models import DPIA


class DPIAForm(forms.ModelForm):
    class Meta:
        model = DPIA
        fields = [
            'title', 'description', 'status',
            'trigger_automated_decisions', 'trigger_large_scale_special',
            'trigger_systematic_monitoring', 'trigger_sensitive_combined',
            'trigger_new_technology', 'trigger_children',
            'trigger_vulnerable_subjects', 'trigger_data_matching', 'trigger_denies_service',
            'inherent_likelihood', 'inherent_impact',
            'residual_likelihood', 'residual_impact',
            'consultation_summary', 'mitigations', 'outcome', 'decision_note',
            'dpo', 'business_owner', 'approved_at', 'next_review',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'consultation_summary': forms.Textarea(attrs={'rows': 3}),
            'mitigations': forms.Textarea(attrs={'rows': 4}),
            'decision_note': forms.Textarea(attrs={'rows': 3}),
            'approved_at': forms.DateInput(attrs={'type': 'date'}),
            'next_review': forms.DateInput(attrs={'type': 'date'}),
        }


@login_required
def dpia_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    items = DPIA.objects.filter(organization=org).select_related('dpo', 'business_owner')
    return render(request, 'dpia/list.html', {'items': items})


@write_required
def dpia_create(request):
    org = request.active_org
    form = DPIAForm(request.POST or None)
    scope_form_to_org(form, org)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.save()
        messages.success(request, 'DPIA registered.')
        return redirect('dpia:detail', pk=obj.pk)
    return render(request, 'dpia/form.html', {'form': form, 'title': 'New DPIA'})


@login_required
def dpia_detail(request, pk):
    org = request.active_org
    obj = get_object_or_404(DPIA, pk=pk, organization=org)
    return render(request, 'dpia/detail.html', {'dpia': obj})


@write_required
def dpia_edit(request, pk):
    org = request.active_org
    obj = get_object_or_404(DPIA, pk=pk, organization=org)
    form = DPIAForm(request.POST or None, instance=obj)
    scope_form_to_org(form, org)
    if form.is_valid():
        form.save()
        messages.success(request, 'DPIA updated.')
        return redirect('dpia:detail', pk=pk)
    return render(request, 'dpia/form.html', {'form': form, 'title': f'Edit: {obj.title}'})
