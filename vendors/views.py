from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import write_required
from core.forms import scope_form_to_org

from .models import Vendor


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'name', 'role', 'country', 'website', 'contact_email',
            'data_categories', 'purposes', 'sub_processor_countries',
            'dpa_on_file', 'dpa_signed_on', 'dpa_expires_on', 'dpa_document_url',
            'transfer_mechanism', 'tia_completed',
            'risk_tier', 'last_security_audit', 'next_security_audit',
            'certifications', 'owner', 'notes',
        ]
        widgets = {
            'dpa_signed_on': forms.DateInput(attrs={'type': 'date'}),
            'dpa_expires_on': forms.DateInput(attrs={'type': 'date'}),
            'last_security_audit': forms.DateInput(attrs={'type': 'date'}),
            'next_security_audit': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


@login_required
def vendor_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    qs = Vendor.objects.filter(organization=org).select_related('owner')
    return render(request, 'vendors/list.html', {'vendors': qs})


@write_required
def vendor_create(request):
    org = request.active_org
    form = VendorForm(request.POST or None)
    scope_form_to_org(form, org)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.save()
        messages.success(request, f'Vendor "{obj.name}" added.')
        return redirect('vendors:list')
    return render(request, 'vendors/form.html', {'form': form, 'title': 'Add vendor'})


@write_required
def vendor_edit(request, pk):
    org = request.active_org
    obj = get_object_or_404(Vendor, pk=pk, organization=org)
    form = VendorForm(request.POST or None, instance=obj)
    scope_form_to_org(form, org)
    if form.is_valid():
        form.save()
        messages.success(request, 'Vendor updated.')
        return redirect('vendors:list')
    return render(request, 'vendors/form.html', {'form': form, 'title': f'Edit: {obj.name}'})
