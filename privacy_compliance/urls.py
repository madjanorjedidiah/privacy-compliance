from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard:home', permanent=False)),
    path('admin/', admin.site.urls),
    path('ops/', include('ops.urls', namespace='ops')),
    path('', include('core.urls', namespace='public')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('onboarding/', include('accounts.onboarding_urls', namespace='onboarding')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('compliance/', include('controls.compliance_urls', namespace='compliance')),
    path('controls/', include('controls.urls', namespace='controls')),
    path('risks/', include('risks.urls', namespace='risks')),
    path('templates/', include('templates_engine.urls', namespace='templates')),
    path('jurisdictions/', include('jurisdictions.urls', namespace='jurisdictions')),
    path('dsar/', include('dsar.urls', namespace='dsar')),
    path('incidents/', include('incidents.urls', namespace='incidents')),
    path('ropa/', include('ropa.urls', namespace='ropa')),
    path('retention/', include('retention.urls', namespace='retention')),
    path('training/', include('training.urls', namespace='training')),
    path('dpia/', include('dpia.urls', namespace='dpia')),
    path('vendors/', include('vendors.urls', namespace='vendors')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
