import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Membaca dataset
BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / 'dataset_ev.csv')

# Menentukan fitur dan target
fitur = [
    'battery_capacity_kwh',
    'initial_soc_pct',
    'final_soc_pct',
    'daily_travel_distance_km',
    'ambient_temperature_celsius',
    'charging_duration_minutes'
]

target_energi = 'energy_consumed_kwh'
target_biaya = 'charging_cost_idr'

# Mengambil data yang diperlukan
data = df[fitur + [target_energi, target_biaya]].copy()

for kolom in data.columns:
    data[kolom] = pd.to_numeric(data[kolom], errors='coerce')

data = data.dropna()

# Memisahkan fitur dan target
X = data[fitur]
y_energi = data[target_energi]
y_biaya = data[target_biaya]

# Membagi data training dan testing
(
    X_train,
    X_test,
    y_energi_train,
    y_energi_test,
    y_biaya_train,
    y_biaya_test
) = train_test_split(
    X,
    y_energi,
    y_biaya,
    test_size=0.2,
    random_state=42
)

# Membuat model
model_energi = LinearRegression()
model_biaya = LinearRegression()

# Melatih model
model_energi.fit(X_train, y_energi_train)
model_biaya.fit(X_train, y_biaya_train)

# Prediksi data testing
prediksi_energi = model_energi.predict(X_test)
prediksi_biaya = model_biaya.predict(X_test)

# Evaluasi model
def evaluasi_model(aktual, prediksi):
    return {
        'r2': float(r2_score(aktual, prediksi)),
        'mae': float(mean_absolute_error(aktual, prediksi)),
        'rmse': float(mean_squared_error(aktual, prediksi) ** 0.5)
    }


hasil_evaluasi = {
    'energi': evaluasi_model(y_energi_test, prediksi_energi),
    'biaya': evaluasi_model(y_biaya_test, prediksi_biaya)
}

# Menyimpan model dan data pengujian
hasil_model = {
    'model_energi': model_energi,
    'model_biaya': model_biaya,
    'fitur': fitur,
    'evaluasi': hasil_evaluasi,

    'data_uji': {
        'aktual_energi': y_energi_test.tolist(),
        'prediksi_energi': prediksi_energi.tolist(),
        'aktual_biaya': y_biaya_test.tolist(),
        'prediksi_biaya': prediksi_biaya.tolist()
    }
}

joblib.dump(hasil_model, BASE_DIR / 'model_ev.joblib')

# Menampilkan hasil
print('PELATIHAN MODEL DAYAKU BERHASIL')
print('Jumlah data:', len(data))
print('Data training:', len(X_train))
print('Data testing:', len(X_test))

print('\nEVALUASI MODEL ENERGI')
print('R2 Score :', hasil_evaluasi['energi']['r2'])
print('MAE      :', hasil_evaluasi['energi']['mae'])
print('RMSE     :', hasil_evaluasi['energi']['rmse'])

print('\nEVALUASI MODEL BIAYA')
print('R2 Score :', hasil_evaluasi['biaya']['r2'])
print('MAE      :', hasil_evaluasi['biaya']['mae'])
print('RMSE     :', hasil_evaluasi['biaya']['rmse'])

print('\nModel tersimpan di model_ev.joblib')
