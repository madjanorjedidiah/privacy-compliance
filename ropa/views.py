from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import write_required
from core.forms import scope_form_to_org

from .models import ProcessingActivity


class ProcessingActivityForm(forms.ModelForm):
    class Meta:
        model = ProcessingActivity
        fields = [
            'name', 'description', 'role',
            'purposes', 'lawful_basis', 'special_category_basis', 'lawful_basis_note',
            'data_categories', 'data_subject_categories',
            'recipients', 'internal_systems',
            'cross_border_transfers', 'transfer_countries', 'transfer_mechanism',
            'retention_schedule', 'retention_note',
            'security_measures', 'dpia_required', 'dpia',
            'owner', 'last_reviewed', 'next_review',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'lawful_basis_note': forms.Textarea(attrs={'rows': 3}),
            'security_measures': forms.Textarea(attrs={'rows': 4}),
            'last_reviewed': forms.DateInput(attrs={'type': 'date'}),
            'next_review': forms.DateInput(attrs={'type': 'date'}),
        }


@login_required
def activity_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    qs = ProcessingActivity.objects.filter(organization=org).select_related('owner', 'retention_schedule')
    return render(request, 'ropa/list.html', {'activities': qs})


@write_required
def activity_create(request):
    org = request.active_org
    form = ProcessingActivityForm(request.POST or None)
    scope_form_to_org(form, org)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.save()
        messages.success(request, f'Processing activity "{obj.name}" added to ROPA.')
        return redirect('ropa:detail', pk=obj.pk)
    return render(request, 'ropa/form.html', {'form': form, 'title': 'Add processing activity'})


@login_required
def activity_detail(request, pk):
    org = request.active_org
    activity = get_object_or_404(ProcessingActivity, pk=pk, organization=org)
    return render(request, 'ropa/detail.html', {'activity': activity})


@write_required
def activity_edit(request, pk):
    org = request.active_org
    activity = get_object_or_404(ProcessingActivity, pk=pk, organization=org)
    form = ProcessingActivityForm(request.POST or None, instance=activity)
    scope_form_to_org(form, org)
    if form.is_valid():
        form.save()
        messages.success(request, 'Activity updated.')
        return redirect('ropa:detail', pk=pk)
    return render(request, 'ropa/form.html', {'form': form, 'title': f'Edit: {activity.name}'})
