from django.contrib import admin
from django.urls import path
from core import views  # Views modülünü komple içeri aktarıyoruz

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Ana sayfa rotası
    path('', views.ana_sayfa, name='ana_sayfa'), 
    
    # İmsakiye sayfası rotası
    path('imsakiye/', views.imsakiye_sayfasi, name='imsakiye'),
    
    path('amel-defterim/', views.amel_defterim, name='amel_defterim'),
    path('animasyon/', views.animasyon_sayfasi, name='animasyon'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
