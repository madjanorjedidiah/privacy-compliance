from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import write_required
from core.forms import scope_form_to_org

from .models import TrainingModule, TrainingRecord


class TrainingModuleForm(forms.ModelForm):
    class Meta:
        model = TrainingModule
        fields = ['name', 'description', 'required_months', 'audience_note', 'resource_url', 'mandatory']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class TrainingRecordForm(forms.ModelForm):
    class Meta:
        model = TrainingRecord
        fields = ['module', 'user', 'completed_on', 'evidence_link', 'evidence_file', 'notes']
        widgets = {'completed_on': forms.DateInput(attrs={'type': 'date'})}


@login_required
def module_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    modules = TrainingModule.objects.filter(organization=org)
    records = TrainingRecord.objects.filter(module__organization=org).select_related('module', 'user')
    return render(request, 'training/list.html', {'modules': modules, 'records': records})


@write_required
def module_create(request):
    org = request.active_org
    form = TrainingModuleForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.save()
        messages.success(request, 'Training module added.')
        return redirect('training:list')
    return render(request, 'training/form.html', {'form': form, 'title': 'Add training module'})


@write_required
def record_create(request):
    org = request.active_org
    form = TrainingRecordForm(request.POST or None, request.FILES or None)
    scope_form_to_org(form, org)
    if form.is_valid():
        obj = form.save()
        messages.success(request, f'Recorded training completion for {obj.user.friendly_name}.')
        return redirect('training:list')
    return render(request, 'training/form.html', {'form': form, 'title': 'Record a training completion'})
