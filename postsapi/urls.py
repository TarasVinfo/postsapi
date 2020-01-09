from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from posts import views

schema_view = get_schema_view(
   openapi.Info(
      title="Posts API",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='posts')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.UserCreate.as_view(), name='signup'),
    path('login/', jwt_views.TokenObtainPairView.as_view(),
         name='login'),
    path('token_refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/v1/', include(router.urls)),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
]
