# ERP Production Operation (Django)

Aplikasi web untuk analisis Sales Order dan pelacakan inventory Finish Good, Not Finish, In Process, serta Raw Material. Tracker A–D berada di dalam satu menu **Sales Order**.

## Menjalankan secara lokal

1. Buat dan aktifkan virtual environment Python.
2. Pada clone baru, salin template: `Copy-Item .env.example .env`, lalu ganti `DJANGO_SECRET_KEY` dengan secret acak milik Anda. File `.env` lokal yang sudah ada tidak perlu ditimpa.
3. Pasang dependensi: `pip install -r requirements.txt`.
4. Buat tabel: `python manage.py migrate`.
5. Buat akun administrator: `python manage.py createsuperuser`.
6. Jalankan aplikasi: `python manage.py runserver`.
7. Buka `http://127.0.0.1:8000/` dan masuk melalui `/admin/login/`.
8. Admin dapat mengimpor workbook `.xlsx` melalui menu Data Import.

Database lokal memakai SQLite. Data contoh dalam `Training Web.xlsx` adalah data sintetis. File `.env` bersifat lokal dan diabaikan Git; gunakan Railway Variables untuk secret production.

## Deploy ke Railway

Aplikasi siap dijalankan sebagai service Railway berbasis Railpack dengan perintah pada `Procfile`. Railway memasang dependency dari `requirements.txt`, kemudian menjalankan migrasi, mengumpulkan static files, dan memulai Gunicorn pada port `$PORT`.

1. Push repository ke GitHub.
2. Buat project Railway dan tambahkan service aplikasi dari repository tersebut.
3. Tambahkan service PostgreSQL pada project yang sama.
4. Pada Variables di service aplikasi, tambahkan:

   | Variable | Nilai |
   |---|---|
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (sesuaikan `Postgres` dengan nama service database) |
   | `DJANGO_SECRET_KEY` | secret acak panjang; buat nilainya sendiri dan simpan di Railway Variables |
   | `DJANGO_DEBUG` | `0` |
   | `CSRF_TRUSTED_ORIGINS` | `https://<domain-railway-anda>` bila domain tidak terdeteksi otomatis |

   Railway menyediakan `RAILWAY_PUBLIC_DOMAIN` untuk service yang memiliki domain. Aplikasi menggunakan domain itu untuk `ALLOWED_HOSTS` dan CSRF. `healthcheck.railway.app` juga diizinkan untuk pemeriksaan deploy.
5. Generate domain publik pada Networking service aplikasi.
6. Atur Healthcheck Path ke `/health/`.
7. Deploy. Perintah startup menjalankan `migrate` dan `collectstatic` sebelum Gunicorn. Jika migrasi gagal, service tidak akan mulai menerima trafik.
8. Setelah deploy, buat akun admin melalui Railway service shell dengan `python manage.py createsuperuser`, lalu masuk dan unggah workbook sampel atau data operasional dari menu Data Import.

Jangan set `DATABASE_URL` ke SQLite di Railway: sistem akan menolak startup bila variabel PostgreSQL tidak tersedia. Database Railway harus berada pada project/environment yang sama dan dihubungkan melalui variable reference agar datanya tetap tersimpan di service PostgreSQL.

Railway saat ini menyarankan Railpack dan service settings, dan dokumentasinya menyatakan Config as Code lama (`railway.json`/`railway.toml`) deprecated untuk service baru. Karena itu repo menggunakan `Procfile` dan konfigurasi yang dijelaskan di atas.

## Deployment readiness

- PostgreSQL melalui `DATABASE_URL` (`dj-database-url` + Psycopg 3).
- Static files memakai WhiteNoise dan compressed manifest storage.
- Gunicorn bind ke `0.0.0.0:$PORT`.
- HTTPS proxy awareness dan secure session/CSRF cookies aktif saat `DJANGO_DEBUG=0`.
- Health endpoint: `/health/`.

Sebelum penggunaan produksi, aktifkan backup PostgreSQL terjadwal dan tetapkan kebijakan pemulihan data.

## Dokumen

- `PRD.md`: kebutuhan produk dan aturan awal tracker.
- `DESIGN.md`: navigasi, visual, dan rancangan halaman.
