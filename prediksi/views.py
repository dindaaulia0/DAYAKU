import os
import json
import math
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv

from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import RiwayatPrediksi


BASE_DIR = Path(settings.BASE_DIR)
load_dotenv(BASE_DIR / '.env')

DATASET_PATH = BASE_DIR / 'dataset_ev.csv'
MODEL_PATH = BASE_DIR / 'model_ev.joblib'

def baca_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            'File dataset_ev.csv tidak ditemukan di folder utama DAYAKU.'
        )

    return pd.read_csv(DATASET_PATH)


def baca_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            'File model_ev.joblib tidak ditemukan. '
            'Jalankan train_model.py terlebih dahulu.'
        )

    return joblib.load(MODEL_PATH)

def pilih_sampel_grafik(aktual, prediksi, jumlah=30):

    pasangan = sorted(
        zip(aktual, prediksi),
        key=lambda item: item[0]
    )

    if not pasangan:
        return {
            'label': [],
            'aktual': [],
            'prediksi': []
        }

    if len(pasangan) > jumlah:
        indeks = [
            round(i * (len(pasangan) - 1) / (jumlah - 1))
            for i in range(jumlah)
        ]

        pasangan = [pasangan[i] for i in indeks]

    return {
        'label': [
            f'Sampel {i + 1}'
            for i in range(len(pasangan))
        ],
        'aktual': [
            round(float(x[0]), 3)
            for x in pasangan
        ],
        'prediksi': [
            round(float(x[1]), 3)
            for x in pasangan
        ]
    }


def penjelasan_lokal(judul, satuan, evaluasi, grafik):

    aktual = grafik['aktual']
    prediksi = grafik['prediksi']

    if not aktual:
        return (
            "RINGKASAN\n"
            "Belum terdapat data pengujian untuk dianalisis.\n\n"
            "KESIMPULAN\n"
            "Grafik belum dapat dijelaskan karena data kosong."
        )

    selisih = [
        a - p
        for a, p in zip(aktual, prediksi)
    ]

    rata_selisih = sum(
        abs(x) for x in selisih
    ) / len(selisih)

    r2 = evaluasi['r2']
    mae = evaluasi['mae']
    rmse = evaluasi['rmse']

    if r2 >= 0.75:
        kualitas = "baik"
    elif r2 >= 0.50:
        kualitas = "cukup"
    else:
        kualitas = "perlu ditingkatkan"

    positif = sum(1 for x in selisih if x > 0)
    negatif = sum(1 for x in selisih if x < 0)

    if positif > negatif:
        pola = "Pada lebih banyak sampel, prediksi berada di bawah nilai aktual."
    elif negatif > positif:
        pola = "Pada lebih banyak sampel, prediksi berada di atas nilai aktual."
    else:
        pola = "Jumlah prediksi yang berada di atas dan di bawah nilai aktual relatif seimbang."

    return (
        f"RINGKASAN\n"
        f"Grafik {judul} memperlihatkan perbandingan antara nilai aktual "
        f"dan nilai prediksi model pada {len(aktual)} sampel data testing. "
        f"Rata-rata selisih absolut pada sampel grafik adalah "
        f"{rata_selisih:,.3f} {satuan}.\n\n"

        f"MEMBACA GRAFIK\n"
        f"• Sumbu horizontal menunjukkan urutan sampel data testing.\n"
        f"• Sumbu vertikal menunjukkan nilai {judul.lower()} dalam satuan {satuan}.\n"
        f"• Garis biru menunjukkan nilai aktual dari dataset.\n"
        f"• Garis hijau menunjukkan nilai prediksi yang dihasilkan model.\n\n"

        f"ANALISIS PERBANDINGAN\n"
        f"Kedekatan garis aktual dan prediksi menunjukkan seberapa dekat "
        f"hasil model terhadap data sebenarnya. Semakin kecil jarak "
        f"kedua garis, semakin kecil selisih prediksinya.\n"
        f"{pola}\n\n"

        f"EVALUASI MODEL\n"
        f"• R² Score: {r2:.4f}. Menunjukkan kemampuan model menjelaskan "
        f"variasi nilai target.\n"
        f"• MAE: {mae:,.3f} {satuan}. Menunjukkan rata-rata kesalahan absolut.\n"
        f"• RMSE: {rmse:,.3f} {satuan}. Mengukur kesalahan dengan penalti "
        f"lebih besar terhadap kesalahan yang besar.\n\n"

        f"KESIMPULAN\n"
        f"Berdasarkan nilai R², performa model untuk target ini tergolong "
        f"{kualitas}. Nilai MAE dan RMSE perlu diperhatikan bersama "
        f"R² untuk memperoleh gambaran performa yang lebih lengkap. "
        f"Hasil grafik merupakan evaluasi pada data testing dan bukan "
        f"jaminan ketepatan untuk seluruh prediksi baru."
    )

def buat_penjelasan_ai(judul, satuan, evaluasi, grafik):

    fallback = penjelasan_lokal(
        judul,
        satuan,
        evaluasi,
        grafik
    )

    api_key = os.getenv('GROQ_API_KEY')

    if not api_key:
        return (
            fallback +
            "\n\nCATATAN\n"
            "Penjelasan dibuat menggunakan analisis lokal karena "
            "GROQ_API_KEY belum dikonfigurasi."
        )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        prompt = f"""
Analisis grafik DAYAKU berikut menggunakan bahasa Indonesia
yang sederhana, jelas, dan mudah dipahami mahasiswa.

JUDUL: {judul}
SATUAN: {satuan}

NILAI EVALUASI:
R2: {evaluasi['r2']:.4f}
MAE: {evaluasi['mae']:.4f}
RMSE: {evaluasi['rmse']:.4f}

DATA AKTUAL:
{grafik['aktual']}

DATA PREDIKSI:
{grafik['prediksi']}

Buat penjelasan dengan format berikut:

RINGKASAN
Berikan gambaran umum grafik dalam paragraf pendek.

MEMBACA GRAFIK
Jelaskan sumbu X, sumbu Y, garis aktual, dan garis prediksi.
Gunakan bullet point.

ANALISIS PERBANDINGAN
Jelaskan kedekatan garis aktual dan prediksi.
Jelaskan kecenderungan selisih berdasarkan data yang tersedia.

EVALUASI MODEL
Jelaskan R2, MAE, dan RMSE.
Gunakan bullet point dan jangan mengubah angka.

KESIMPULAN
Berikan kesimpulan singkat berdasarkan data.

ATURAN:
- Gunakan judul bagian dengan huruf kapital.
- Pisahkan setiap bagian dengan satu baris kosong.
- Gunakan bullet point dengan simbol •.
- Gunakan paragraf pendek.
- Jangan membuat tabel.
- Jangan mengarang data.
- Jangan menyimpulkan hubungan sebab akibat yang tidak tersedia.
- Jangan mengulang penjelasan yang sama.
- Jangan menggunakan markdown ** atau tanda dekoratif.
"""

        response = client.chat.completions.create(
            model='openai/gpt-oss-20b',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'Kamu adalah analis data aplikasi DAYAKU. '
                        'Berikan penjelasan yang sistematis, akurat, '
                        'dan hanya berdasarkan data yang diberikan.'
                    )
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            temperature=0.3,
            max_completion_tokens=900
        )

        hasil = response.choices[0].message.content

        if not hasil:
            return fallback

        return hasil.strip()

    except Exception as exc:

        print('Groq gagal:', exc)

        return (
            fallback +
            "\n\nCATATAN\n"
            "Layanan AI sedang tidak tersedia. "
            "Penjelasan ditampilkan menggunakan analisis lokal."
        )


def dashboard(request):

    df = baca_dataset()
    model = baca_model()

    evaluasi = model['evaluasi']
    data_uji = model['data_uji']

    grafik_energi = pilih_sampel_grafik(
        data_uji['aktual_energi'],
        data_uji['prediksi_energi']
    )

    grafik_biaya = pilih_sampel_grafik(
        data_uji['aktual_biaya'],
        data_uji['prediksi_biaya']
    )

    context = {
        'jumlah_data': len(df),

        'jumlah_merek': (
            df['vehicle_brand_model'].nunique()
            if 'vehicle_brand_model' in df else 0
        ),

        'jumlah_provinsi': (
            df['province'].nunique()
            if 'province' in df else 0
        ),

        'jumlah_riwayat': RiwayatPrediksi.objects.count(),

        'rata_energi': round(
            float(df['energy_consumed_kwh'].mean()), 2
        ),

        'rata_biaya': round(
            float(df['charging_cost_idr'].mean()), 0
        ),

        'r2_energi': round(
            evaluasi['energi']['r2'] * 100, 2
        ),

        'r2_biaya': round(
            evaluasi['biaya']['r2'] * 100, 2
        ),

        'mae_energi': round(
            evaluasi['energi']['mae'], 3
        ),

        'mae_biaya': round(
            evaluasi['biaya']['mae'], 2
        ),

        'rmse_energi': round(
            evaluasi['energi']['rmse'], 3
        ),

        'rmse_biaya': round(
            evaluasi['biaya']['rmse'], 2
        ),

        'grafik_energi': json.dumps(grafik_energi),
        'grafik_biaya': json.dumps(grafik_biaya),
    }

    return render(
        request,
        'prediksi/dashboard.html',
        context
    )

@require_POST
def analisis_grafik(request, jenis):

    if jenis not in ('energi', 'biaya'):
        return JsonResponse(
            {'error': 'Jenis grafik tidak dikenali.'},
            status=400
        )

    try:

        model = baca_model()
        data_uji = model['data_uji']

        grafik = pilih_sampel_grafik(
            data_uji[f'aktual_{jenis}'],
            data_uji[f'prediksi_{jenis}']
        )

        satuan = (
            'kWh' if jenis == 'energi'
            else 'Rupiah'
        )

        judul = (
            'Konsumsi Energi'
            if jenis == 'energi'
            else 'Biaya Pengisian'
        )

        hasil = buat_penjelasan_ai(
            judul,
            satuan,
            model['evaluasi'][jenis],
            grafik
        )

        return JsonResponse({
            'penjelasan': hasil
        })

    except Exception as exc:

        print('Kesalahan analisis grafik:', exc)

        return JsonResponse(
            {
                'error': (
                    'Penjelasan grafik gagal dibuat. '
                    'Periksa file model dan konfigurasi aplikasi.'
                )
            },
            status=500
        )

def prediksi(request):

    hasil = None
    error = None
    nilai_form = {}

    if request.method == 'POST':

        nama_input = [
            'battery_capacity',
            'initial_soc',
            'final_soc',
            'daily_distance',
            'temperature',
            'charging_duration'
        ]

        try:

            nilai_form = {
                nama: request.POST.get(nama, '').strip()
                for nama in nama_input
            }

            if any(value == '' for value in nilai_form.values()):
                raise ValueError('Semua kolom wajib diisi.')

            angka = {
                nama: float(value)
                for nama, value in nilai_form.items()
            }

            if any(not math.isfinite(v) for v in angka.values()):
                raise ValueError(
                    'Input harus berupa angka yang valid.'
                )

            if any(v < 0 for v in angka.values()):
                raise ValueError(
                    'Input tidak boleh bernilai negatif.'
                )

            if (
                angka['battery_capacity'] <= 0
                or angka['charging_duration'] <= 0
            ):
                raise ValueError(
                    'Kapasitas baterai dan durasi pengisian harus lebih dari 0.'
                )

            if (
                not 0 <= angka['initial_soc'] <= 100
                or not 0 <= angka['final_soc'] <= 100
            ):
                raise ValueError(
                    'SOC awal dan akhir harus berada antara 0 sampai 100%.'
                )

            if angka['final_soc'] <= angka['initial_soc']:
                raise ValueError(
                    'SOC akhir harus lebih besar dari SOC awal.'
                )

            model = baca_model()
            fitur = model['fitur']

            nilai_fitur = {
                'battery_capacity_kwh': angka['battery_capacity'],
                'initial_soc_pct': angka['initial_soc'],
                'final_soc_pct': angka['final_soc'],
                'daily_travel_distance_km': angka['daily_distance'],
                'ambient_temperature_celsius': angka['temperature'],
                'charging_duration_minutes': angka['charging_duration'],
            }

            data_input = pd.DataFrame(
                [[nilai_fitur[nama] for nama in fitur]],
                columns=fitur
            )

            energi = max(
                0.0,
                float(
                    model['model_energi'].predict(data_input)[0]
                )
            )

            biaya = max(
                0.0,
                float(
                    model['model_biaya'].predict(data_input)[0]
                )
            )

            RiwayatPrediksi.objects.create(
                battery_capacity=angka['battery_capacity'],
                initial_soc=angka['initial_soc'],
                final_soc=angka['final_soc'],
                daily_distance=angka['daily_distance'],
                temperature=angka['temperature'],
                charging_duration=angka['charging_duration'],
                predicted_energy=energi,
                predicted_cost=biaya
            )

            hasil = {
                'energi': round(energi, 3),
                'biaya': round(biaya, 0)
            }

        except ValueError as exc:

            error = str(exc)

        except Exception as exc:

            print('Kesalahan prediksi:', exc)
            error = (
                'Prediksi gagal. Periksa data masukan dan file model. '
                f'Detail: {exc}'
            )

    return render(
        request,
        'prediksi/prediksi.html',
        {
            'hasil': hasil,
            'error': error,
            'nilai_form': nilai_form
        }
    )

def riwayat(request):

    daftar = RiwayatPrediksi.objects.all().order_by('-tanggal')

    jumlah_riwayat = daftar.count()

    paginator = Paginator(daftar, 15)

    halaman = paginator.get_page(
        request.GET.get('page')
    )

    context = {
        'halaman': halaman,
        'jumlah_riwayat': jumlah_riwayat
    }

    return render(
        request,
        'prediksi/riwayat.html',
        context
    )

def dataset(request):

    df = baca_dataset()

    kolom = df.columns.tolist()

    records = df.head(1000).to_dict(
        orient='records'
    )

    halaman = Paginator(
        records,
        15
    ).get_page(
        request.GET.get('page')
    )

    return render(
        request,
        'prediksi/dataset.html',
        {
            'jumlah_data': len(df),
            'jumlah_kolom': len(kolom),
            'kolom': kolom,
            'halaman': halaman
        }
    )

def tentang(request):

    return render(
        request,
        'prediksi/tentang.html'
    )
