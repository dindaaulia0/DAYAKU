from django.contrib import admin
from django.apps import apps

# Mengambil seluruh model dari aplikasi prediksi
app_config = apps.get_app_config("prediksi")

# Mendaftarkan model agar tampil di Django Admin
for model in app_config.get_models():
    if not admin.site.is_registered(model):
        admin.site.register(model)
