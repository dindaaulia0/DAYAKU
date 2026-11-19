from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('prediksi/', views.prediksi, name='prediksi'),
    path('riwayat/', views.riwayat, name='riwayat'),
    path('dataset/', views.dataset, name='dataset'),
    path('tentang/', views.tentang, name='tentang'),
    path('analisis-grafik/<str:jenis>/', views.analisis_grafik, name='analisis_grafik'),
]
