from django.db import models

class RiwayatPrediksi(models.Model):
    tanggal = models.DateTimeField(auto_now_add=True)

    battery_capacity = models.FloatField()
    initial_soc = models.FloatField()
    final_soc = models.FloatField()
    daily_distance = models.FloatField()
    temperature = models.FloatField()
    charging_duration = models.FloatField()

    predicted_energy = models.FloatField()
    predicted_cost = models.FloatField()

    def __str__(self):
        return f"Prediksi {self.tanggal.strftime('%d-%m-%Y %H:%M')}"

    class Meta:
        ordering = ['-tanggal']
        verbose_name = 'Riwayat Prediksi'
        verbose_name_plural = 'Riwayat Prediksi'
