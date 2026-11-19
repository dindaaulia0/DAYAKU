## 1. Deskripsi Aplikasi

DAYAKU merupakan aplikasi yang dirancang untuk membantu pengguna memperkirakan konsumsi energi dan biaya pengisian daya motor listrik. Aplikasi ini memberikan informasi mengenai perkiraan kebutuhan energi berdasarkan karakteristik baterai dan kondisi penggunaan kendaraan.

Pengguna dapat memasukkan beberapa informasi, seperti kapasitas baterai, persentase pengisian baterai awal dan akhir (SOC), jarak perjalanan harian, suhu lingkungan, serta durasi pengisian. Berdasarkan informasi tersebut, aplikasi menghasilkan estimasi konsumsi energi dalam satuan kWh dan perkiraan biaya pengisian dalam rupiah.

DAYAKU menyediakan beberapa fitur utama:

- **Dashboard:** Menampilkan ringkasan dataset, jumlah kendaraan, cakupan provinsi, rata-rata konsumsi energi, rata-rata biaya pengisian, grafik perbandingan nilai aktual dan prediksi, serta evaluasi model.
- **Prediksi:** Menghasilkan estimasi konsumsi energi dan biaya pengisian berdasarkan informasi yang dimasukkan pengguna.
- **Riwayat Prediksi:** Menyimpan dan menampilkan hasil prediksi yang telah dilakukan sehingga pengguna dapat melihat kembali hasil sebelumnya.
- **Dataset:** Menampilkan informasi dan data kendaraan listrik yang digunakan dalam aplikasi.
- **Tentang Aplikasi:** Menyediakan informasi mengenai tujuan, fungsi, dan fitur aplikasi DAYAKU.

Hasil prediksi merupakan estimasi berdasarkan data yang tersedia. Hasil dapat berbeda dari kondisi pengisian sebenarnya dan bukan merupakan tagihan resmi penyedia listrik.

## 2. Sumber dan Lisensi Dataset

Dataset yang digunakan dalam aplikasi DAYAKU terdapat pada file `dataset_ev.csv`.

**Informasi Dataset:**

- Nama file: `dataset_ev.csv`
- Jumlah data: 10.000 baris.
- Jumlah atribut: 26 kolom.
- Format file: CSV (Comma-Separated Values).

Dataset berisi informasi mengenai sesi pengisian kendaraan listrik, termasuk kapasitas baterai, persentase SOC, jarak perjalanan, suhu lingkungan, durasi pengisian, konsumsi energi, dan biaya pengisian.

**Sumber Dataset:**

[Kaggle – Indonesia EV Motor Listrik SPKLU Telemetry 2026](https://www.kaggle.com/datasets/luthfimuthathohirin/indonesia-ev-motor-listrik-spklu-telemetry-2026)

**Lisensi Dataset:**

Informasi lisensi dataset belum tersedia dalam paket proyek. Sumber asli dan ketentuan lisensi perlu dikonfirmasi kepada penyedia dataset sebelum digunakan atau didistribusikan di luar keperluan tugas.

## 3. Persyaratan Menjalankan Aplikasi

Sebelum menjalankan aplikasi, pastikan perangkat telah memiliki:

- Python versi 3.10 atau lebih baru.
- pip (Python Package Installer).
- Browser untuk mengakses aplikasi.
- File `dataset_ev.csv`.
- File `model_ev.joblib`.

## 4. Cara Menjalankan Aplikasi

### A. Ekstrak Proyek

1. Ekstrak file ZIP DAYAKU ke folder yang diinginkan.
2. Buka folder proyek menggunakan Visual Studio Code atau terminal.
3. Pastikan terminal berada pada folder utama proyek yang berisi file `manage.py`.

### B. Membuat Virtual Environment

Jalankan perintah berikut:

```bash
python -m venv venv
```

Aktifkan virtual environment pada Windows:

```bash
venv\Scripts\activate
```

Jika berhasil, terminal akan menampilkan `(venv)` pada bagian awal baris perintah.

### C. Menginstal Dependensi

Jalankan perintah:

```bash
pip install -r requirements.txt
```

Pastikan seluruh dependensi berhasil diinstal sebelum melanjutkan.

### D. Konfigurasi API AI (Opsional)

Apabila ingin menggunakan layanan penjelasan grafik berbasis AI, buat file `.env` pada folder utama proyek yang berisi `manage.py`.

Tambahkan konfigurasi berikut:

```env
GROQ_API_KEY=masukkan_api_key_di_sini
```

Ganti `masukkan_api_key_di_sini` dengan API key yang valid.

Jika API key tidak dikonfigurasi, aplikasi tetap dapat menampilkan penjelasan grafik menggunakan analisis lokal, sesuai dukungan aplikasi.

### E. Menyiapkan Database

Jalankan perintah berikut:

```bash
python manage.py migrate
```

Untuk memeriksa konfigurasi proyek Django, jalankan:

```bash
python manage.py check
```

Jika berhasil, Django akan menampilkan pesan:

```text
System check identified no issues (0 silenced).
```

### F. Menjalankan Aplikasi

Jalankan perintah:

```bash
python manage.py runserver
```

Setelah server berhasil dijalankan, buka browser dan akses:

```text
http://127.0.0.1:8000/
```

Aplikasi DAYAKU siap digunakan.

## 5. Panduan Django Admin

Django Admin digunakan untuk mengelola data aplikasi melalui halaman administrator.

### A. Membuat Akun Administrator

Pastikan virtual environment aktif, kemudian jalankan:

```bash
python manage.py createsuperuser
```

Masukkan informasi akun yang diminta:

- Username: nama pengguna administrator.
- Email address: alamat email (dapat dikosongkan jika konfigurasi mengizinkan).
- Password: kata sandi administrator.
- Password confirmation: masukkan kembali kata sandi.

Catatan: Saat memasukkan password melalui terminal, karakter yang diketik memang tidak akan terlihat. Hal tersebut merupakan perilaku normal Django.

Jika berhasil, akan muncul pesan:

```text
Superuser created successfully.
```

### B. Mengakses Django Admin

Jalankan server:

```bash
python manage.py runserver
```

Kemudian buka alamat:

```text
http://127.0.0.1:8000/admin/
```

Masuk menggunakan username dan password administrator yang telah dibuat.

### C. Mengelola Data

Setelah berhasil masuk, administrator dapat mengelola model aplikasi yang telah didaftarkan pada Django Admin melalui file `prediksi/admin.py`.

Data yang ditampilkan bergantung pada model yang tersedia dan telah didaftarkan dalam aplikasi.

## 6. Menghentikan Aplikasi

Untuk menghentikan server, tekan:

```text
CTRL + C
```

pada terminal yang sedang menjalankan aplikasi.

---

