from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

app_name = 'api'

schema_view = get_schema_view(
    openapi.Info(
        title="Lavocat API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='docs'),
    path('', include('bank.api.core.urls')),
]
