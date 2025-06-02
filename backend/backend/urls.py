from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from recipes.views import IngredientViewSet, RecipesViewSet, follow_short_link
from users.views import UserViewSet

router = routers.DefaultRouter()
router.register("recipes", RecipesViewSet, basename="recipes")
router.register("users", UserViewSet)
router.register("ingredients", IngredientViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
    path("s/<str:code>/", follow_short_link, name="short_link"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
