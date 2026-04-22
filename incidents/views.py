from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'severity', 'status',
            'detected_at', 'affected_subjects_estimate', 'affected_jurisdictions',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'detected_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


@login_required
def incidents_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    qs = Incident.objects.filter(organization=org)
    return render(request, 'incidents/list.html', {'incidents': qs})


@login_required
def incident_create(request):
    org = request.active_org
    form = IncidentForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.reporter = request.user
        obj.save()
        messages.success(request, 'Incident logged. Regulator notification due by ' + obj.regulator_deadline.strftime('%Y-%m-%d %H:%M UTC'))
        return redirect('incidents:list')
    return render(request, 'incidents/form.html', {'form': form})


@login_required
def incident_detail(request, pk):
    org = request.active_org
    inc = get_object_or_404(Incident, pk=pk, organization=org)
    form = IncidentForm(request.POST or None, instance=inc)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_notified':
            inc.regulator_notified_at = timezone.now()
            inc.status = Incident.Status.NOTIFIED
            inc.save()
            messages.success(request, 'Marked as notified.')
            return redirect('incidents:detail', pk=pk)
        if action == 'resolve':
            inc.resolved_at = timezone.now()
            inc.status = Incident.Status.RESOLVED
            inc.save()
            messages.success(request, 'Incident resolved.')
            return redirect('incidents:list')
        if form.is_valid():
            form.save()
            return redirect('incidents:detail', pk=pk)
    return render(request, 'incidents/detail.html', {'incident': inc, 'form': form})
