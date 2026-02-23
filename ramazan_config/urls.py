from django.contrib import admin
from django.urls import path
from core import views  # Views modülünü komple içeri aktarıyoruz

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Ana sayfa rotası
    path('', views.ana_sayfa, name='ana_sayfa'), 
    
    # İmsakiye sayfası rotası
    path('imsakiye/', views.imsakiye_sayfasi, name='imsakiye'),
    
    path('amel-defterim/', views.amel_defterim, name='amel_defterim'),
]