from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import write_required
from core.choices import DSARType

from .models import DSARRequest


class DSARForm(forms.ModelForm):
    class Meta:
        model = DSARRequest
        fields = ['subject_name', 'subject_email', 'subject_country', 'request_type', 'notes', 'assigned_to']


@login_required
def dsar_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    qs = DSARRequest.objects.filter(organization=org)
    return render(request, 'dsar/list.html', {'dsars': qs})


@write_required
def dsar_create(request):
    org = request.active_org
    form = DSARForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.save()
        messages.success(request, 'DSAR recorded. Due by ' + obj.due_at.strftime('%Y-%m-%d'))
        return redirect('dsar:list')
    return render(request, 'dsar/form.html', {'form': form})


@login_required
def dsar_detail(request, pk):
    from accounts.permissions import can_write
    from django.core.exceptions import PermissionDenied
    org = request.active_org
    req = get_object_or_404(DSARRequest, pk=pk, organization=org)
    form = DSARForm(request.POST or None, instance=req)
    if request.method == 'POST':
        if not can_write(request):
            raise PermissionDenied('Your role does not permit editing.')
        action = request.POST.get('action')
        if action == 'close':
            req.status = DSARRequest.Status.CLOSED
            req.closed_at = timezone.now()
            req.save()
            messages.success(request, 'DSAR closed.')
            return redirect('dsar:list')
        if form.is_valid():
            form.save()
            messages.success(request, 'DSAR updated.')
            return redirect('dsar:detail', pk=pk)
    return render(request, 'dsar/detail.html', {'req': req, 'form': form})
