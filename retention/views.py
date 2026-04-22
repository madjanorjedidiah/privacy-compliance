from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import write_required
from core.forms import scope_form_to_org

from .models import RetentionPolicy


class RetentionPolicyForm(forms.ModelForm):
    class Meta:
        model = RetentionPolicy
        fields = [
            'name', 'data_category', 'description',
            'retention_months', 'trigger', 'legal_basis',
            'destruction_method', 'owner',
            'last_reviewed', 'next_review', 'legal_hold',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'last_reviewed': forms.DateInput(attrs={'type': 'date'}),
            'next_review': forms.DateInput(attrs={'type': 'date'}),
        }


@login_required
def policy_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    qs = RetentionPolicy.objects.filter(organization=org)
    return render(request, 'retention/list.html', {'policies': qs})


@write_required
def policy_create(request):
    org = request.active_org
    form = RetentionPolicyForm(request.POST or None)
    scope_form_to_org(form, org)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.save()
        messages.success(request, 'Retention policy added.')
        return redirect('retention:list')
    return render(request, 'retention/form.html', {'form': form, 'title': 'Add retention policy'})


@write_required
def policy_edit(request, pk):
    org = request.active_org
    obj = get_object_or_404(RetentionPolicy, pk=pk, organization=org)
    form = RetentionPolicyForm(request.POST or None, instance=obj)
    scope_form_to_org(form, org)
    if form.is_valid():
        form.save()
        messages.success(request, 'Retention policy updated.')
        return redirect('retention:list')
    return render(request, 'retention/form.html', {'form': form, 'title': f'Edit: {obj.name}'})
