from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Backend API",
      default_version='v1',
      description="Backend API documentation",
      contact=openapi.Contact(email="example.rus1@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

api = [
    path('user/', include('Users.urls')),
    path('content/', include('Content.urls')),
    path('statistics/', include('Statistics.urls')),
    path('games/', include('Games.urls')),
    path('services/', include('Services.urls')),
    # url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api)),
]

admin.site.site_header = 'Backend Administration'
admin.site.site_title = 'Backend Admin'
# admin.site.site_url = '/dashboard'
