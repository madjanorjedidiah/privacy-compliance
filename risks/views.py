from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Risk


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = [
            'title', 'description', 'category',
            'likelihood', 'impact',
            'data_sensitivity', 'data_volume_log10', 'regulator_activity',
            'control_effectiveness',
            'treatment', 'treatment_notes', 'owner', 'review_date',
            'linked_requirements',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'treatment_notes': forms.Textarea(attrs={'rows': 2}),
            'review_date': forms.DateInput(attrs={'type': 'date'}),
        }


@login_required
def risks_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    risks = Risk.objects.filter(organization=org)
    heatmap = _build_heatmap(risks)
    heatmap_rows = [
        {'impact_label': f'I{5 - i}', 'cells': row}
        for i, row in enumerate(heatmap)
    ]
    return render(request, 'risks/list.html', {
        'risks': risks, 'heatmap_rows': heatmap_rows,
    })


@login_required
def risk_create(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    form = RiskForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.save()
        form.save_m2m()
        messages.success(request, 'Risk added.')
        return redirect('risks:list')
    return render(request, 'risks/form.html', {'form': form, 'title': 'Add risk'})


@login_required
def risk_edit(request, pk):
    org = request.active_org
    risk = get_object_or_404(Risk, pk=pk, organization=org)
    form = RiskForm(request.POST or None, instance=risk)
    if form.is_valid():
        form.save()
        messages.success(request, 'Risk updated.')
        return redirect('risks:list')
    return render(request, 'risks/form.html', {'form': form, 'title': f'Edit: {risk.title}'})


def _build_heatmap(risks):
    grid = [[[] for _ in range(5)] for _ in range(5)]
    for r in risks:
        x = max(1, min(5, r.likelihood)) - 1
        y = max(1, min(5, r.impact)) - 1
        grid[4 - y][x].append(r)
    return grid
