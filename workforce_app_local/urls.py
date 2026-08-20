from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('postpaid/', include('postpaid.urls', namespace='postpaid')),
    path("prepaid/", include("prepaid.urls", namespace="prepaid")),
    path('user/', include('user.urls')),
    path('lv/', include('lv.urls', namespace='lv')),
    path('mv/', include('mediumv.urls', namespace='mediumv')),
    path("transdist/", include("transdist.urls", namespace="transdist")),
    path("hradmin/", include("hradmin.urls", namespace="hradmin")),
    path("revenue/", include("revenue.urls", namespace="revenue")),
    path("transmission/", include("transmission.urls", namespace="transmission")),

    path("__debug__/", include("debug_toolbar.urls")),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)