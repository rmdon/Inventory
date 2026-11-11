# PRD — ERP Production Operation

**Status:** Draft untuk review  
**Tanggal:** 11 November 2026  
**Stack target:** Django  
**Sumber data awal:** `Training Web.xlsx`

## 1. Ringkasan

ERP Production Operation membantu tim Sales Planning, Production, dan Warehouse melihat apakah setiap Sales Order dapat dipenuhi dari persediaan dan produksi yang sedang berjalan. Sistem menyediakan dashboard analisis dan Inventory Tracker yang menautkan Sales Order ke empat kelompok data: Finish Good, Not Finish, In Process, dan Raw Material.

Workbook berisi data sintetis untuk periode Oktober 2026–Februari 2027. Jumlah data saat diperiksa: 30 Sales Order, 14 Finish Good, 10 Not Finish, 6 In Process, dan 18 Raw Material. `repeat_no` menjadi kunci relasi utama. Angka dan isi workbook berguna untuk prototipe, belum dianggap data aktual perusahaan.

## 2. Masalah dan tujuan

Saat ini tim perlu menggabungkan beberapa posisi inventory untuk menjawab pertanyaan yang sama: berapa kebutuhan order, berapa yang sudah dikirim, berapa yang tersedia atau sedang diproses, dan berapa kekurangan yang masih harus ditindaklanjuti.

Tujuan produk:

- Menyatukan ringkasan Sales Order dan status empat sumber inventory dalam satu tampilan.
- Menunjukkan pemenuhan order, sisa kebutuhan, potensi material, serta due date dan risiko secara mudah dipindai.
- Memungkinkan pengguna mencari, memfilter, mengurutkan, dan membuka rincian per order.
- Menyediakan dashboard analisis yang konsisten dengan detail Inventory Tracker.
- Mengimpor workbook Excel dengan pemeriksaan kesalahan dan ringkasan hasil impor.

## 3. Pengguna dan kebutuhan

| Pengguna | Kebutuhan utama |
|---|---|
| Planner / Production Controller | Mengidentifikasi order berisiko, memeriksa tahap produksi, dan memprioritaskan tindak lanjut. |
| Warehouse / Inventory | Memastikan coil dan berat yang tercatat per lokasi, status, dan order. |
| Sales / Customer Service | Meninjau status pemenuhan dan jadwal delivery per Sales Order. |
| Supervisor / Manager | Melihat total backlog, pemenuhan, risiko keterlambatan, dan distribusi status. |
| Administrator | Mengelola akses, mengimpor workbook, dan meninjau riwayat impor. |

## 4. Ruang lingkup MVP

### Termasuk

1. Dashboard analisis dengan filter periode due date, customer, dan purchaser.
2. Sales Order list dan detail order.
3. Satu menu sidebar **Sales Order** yang berisi Sales Order dan Inventory Tracker; tracker dapat difilter berdasarkan Finish Good, Not Finish, In Process, Raw Material, atau semua sumber.
4. Pencarian, pengurutan, pagination, filter kategori/status, serta tampilan desktop dan mobile.
5. Impor XLSX untuk sheet utama, validasi format dan kolom, pratinjau hasil, serta laporan baris berhasil/gagal.
6. Login dan peran dasar: Admin, Planner, Viewer.
7. Audit metadata impor dan waktu pembaruan data.

### Di luar ruang lingkup awal

- Perencanaan kapasitas mesin dan penjadwalan produksi otomatis.
- Pembelian, costing, payroll, invoicing, dan akuntansi.
- Integrasi ERP eksternal, supplier, atau mesin produksi.
- Alokasi stok yang mengunci/mengurangi inventory secara transaksional.
- Prediksi probabilitas atau rekomendasi berbasis AI.

## 5. Sumber data dan hubungan

| Sheet | Tujuan | Kolom penting |
|---|---|---|
| `Sales_Order` | Kebutuhan dan pemenuhan order | `repeat_no`, `order_no`, `customer`, `purchaser`, `designation`, `due_date`, `quantity`, `shipped`, `balance`, `allocated`, `req_closed` |
| `Finish_Good` | Produk selesai/siap kirim | `repeat_no`, `jsg_product_no`, `jsg_coil_no`, `weight`, `end_weight`, `order_due_date`, `ship_hold_reason`, `yard_c_r_s` |
| `Not_Finish` | Produk belum selesai | `repeat_no`, `jsg_product_no`, `jsg_coil_no`, `weight`, `finish_hold_reason`, `ship_hold_reason`, `final_line`, `final_line_date`, `count_ng` |
| `In_Process` | Coil dalam proses | `repeat_no`, `jsg_coil_no`, `coil_status`, `leading_process`, `post_process`, `weight`, `status`, `order_due_date` |
| `Raw_Material` | Bahan baku yang terkait order | `repeat_no`, `jsg_coil_no`, `weight`, `end_weight`, `yard`, `raw_material_designation`, `raw_material_thickness`, `raw_material_width` |

Nama sheet pada workbook menjadi sumber kebenaran untuk pemetaan. Kolom historis seperti `purchacer` (ejaan workbook) harus dipetakan ke label aplikasi “Purchaser”. `repeat_no` menyambungkan sheet-sheet utama; referensi order sekunder dipakai untuk pemeriksaan silang, bukan pengganti relasi tanpa aturan bisnis.

## 6. Definisi Inventory Tracker

Inventory Tracker berada di dalam menu **Sales Order**, bukan sebagai menu sidebar terpisah. Halaman ini berawal dari daftar Sales Order dan memiliki filter sumber: Semua, Finish Good (A), Not Finish (B), In Process (C), dan Raw Material (D). Filter menentukan sumber detail yang ditampilkan untuk tiap order; pilihan “Semua” menampilkan ringkasan A–D sekaligus. Setiap baris order menampilkan kebutuhan dan status sumber inventory berikut:

- **A — Finish Good:** total produk selesai yang terkait dengan `repeat_no`, dipisahkan antara bruto, berat akhir (`end_weight`), dan yang memiliki `ship_hold_reason`.
- **B — Not Finish:** total produk belum selesai; tampilkan status/line, hold, dan jumlah coil.
- **C — In Process:** total berat/coil dalam proses; tampilkan `leading_process`, `post_process`, dan `coil_status`.
- **D — Raw Material:** total bahan baku terkait order; tampilkan berat akhir, lokasi, grade, tebal, dan lebar.

Kolom inti tracker: Sales Order, customer, designation, due date, quantity, shipped, balance, A Finish Good, B Not Finish, C In Process, D Raw Material, estimasi total cakupan, estimasi kekurangan, status risiko, dan aksi “Detail”. Baris detail menampilkan coil individual agar angka agregat dapat ditelusuri.

### Prinsip kalkulasi awal

- Kuantitas dan bobot ditampilkan dalam ton, mengikuti skala data workbook; unit harus dikonfirmasi oleh pemilik proses.
- `quantity`, `shipped`, dan `balance` dari Sales Order adalah nilai referensi untuk kebutuhan order. Jangan menjumlahkan `balance` dengan sumber stok.
- Gunakan `end_weight` sebagai kandidat bobot neto untuk cakupan yang dapat dipakai, dan `weight` sebagai bobot bruto/informasi pembanding. Jika `end_weight` kosong, tandai data tidak lengkap; jangan diam-diam mengasumsikan nilainya sama.
- Satu coil tidak boleh dihitung dua kali antar kelompok. Deduplicasi awal menggunakan `jsg_coil_no`; jika identitas coil muncul di lebih dari satu kelompok, tampilkan sebagai anomali dan keluarkan dari agregat gabungan sampai aturan tahap/status disetujui.
- **Total cakupan potensial** = jumlah bobot neto eligible A+B+C+D setelah deduplikasi. Ini angka visibilitas, bukan janji bahwa semua sumber dapat dikirim sekarang.
- **Kekurangan indikatif** = max(0, `balance` − total cakupan potensial). Tandai sebagai estimasi karena raw material dan barang dalam proses perlu konversi, yield, dan waktu produksi.
- Cakupan **siap kirim** dihitung terpisah dari Finish Good yang tidak memiliki ship hold, mengikuti aturan kualitas/hold setelah dikonfirmasi.
- Status “Aman”, “Perlu perhatian”, atau “Kritis” menggunakan due date dan kekurangan indikatif. Ambang jumlah hari dan aturan urutan prioritas perlu disepakati sebelum dipakai operasional.

Angka ringkasan Sales Order (misalnya `finishing_products`, `waiting_finish`, `in_process`, `raw_material_jsg`) dan detail coil berpotensi berbeda karena cakupan data atau waktu snapshot. Sistem perlu menampilkan sumber dan waktu impor, serta pemeriksaan rekonsiliasi; jangan mencampur agregat ringkasan tersebut dengan detail coil tanpa keputusan bisnis.

## 7. Kebutuhan fungsional

### FR-01 Dashboard

- Menampilkan KPI total Sales Order terbuka, total balance, Finish Good siap kirim, bobot dalam produksi, raw material terkait, dan jumlah order berisiko.
- Menyajikan grafik status pemenuhan, balance per bulan due date, dan distribusi order per customer/status.
- Filter dashboard memperbarui seluruh KPI, grafik, dan daftar risiko.
- Setiap grafik memiliki label satuan dan dapat ditelusuri ke daftar order terkait.

### FR-02 Sales Order dan Inventory Tracker

- Sales Order dan Inventory Tracker diakses dari satu menu sidebar bernama Sales Order.
- Menyediakan tab Daftar Sales Order dan Tracker.
- Pada Tracker, sumber dapat dipilih: Semua, Finish Good (A), Not Finish (B), In Process (C), atau Raw Material (D).
- Mencari berdasarkan order number, repeat number, customer, atau coil.
- Memfilter customer, purchaser, designation, due date, req_closed, allocated, sumber, dan tingkat risiko.
- Menampilkan quantity, shipped, balance, allocated, dan ringkasan sumber inventory yang sedang dipilih.
- Membuka detail order yang menampilkan coil, bobot, lokasi, proses, hold, dan tautan sumber.
- Menandai kekurangan, keterlambatan, hold, nilai kosong, dan anomali identitas secara eksplisit.

### FR-04 Impor data

- Admin/Planner mengunggah XLSX dengan sheet wajib yang dikenali.
- Sistem memvalidasi header, tipe data, kunci kosong/duplikat, format tanggal, dan angka negatif/tidak valid.
- Menampilkan pratinjau serta jumlah create/update/reject sebelum konfirmasi impor.
- Setiap impor menyimpan nama berkas, pengguna, waktu, jumlah baris, dan kesalahan per baris.
- Impor gagal tidak boleh meninggalkan data setengah terbarui. Strategi replace/upsert dan batasan transaksi ditetapkan dalam implementasi.

### FR-05 Akses dan audit

- Login diperlukan untuk melihat data produksi.
- Admin mengelola pengguna dan impor; Planner melihat tracker serta menjalankan impor sesuai izin; Viewer hanya membaca.
- Perubahan data manual di masa depan harus merekam pengguna dan waktu perubahan.

## 8. Kebutuhan non-fungsional

- Django dengan database relasional; SQLite untuk prototipe lokal dan PostgreSQL untuk lingkungan operasional yang disepakati.
- Tampilan responsif; tabel tetap dapat digunakan di layar ponsel melalui kolom prioritas atau mode kartu.
- Semua angka memiliki format satuan konsisten dan tanggal menggunakan zona waktu bisnis yang ditetapkan.
- Validasi dan otorisasi dilakukan di server, bukan hanya di browser.
- Impor berulang bersifat idempotent berdasarkan kunci bisnis yang disetujui.
- Dashboard menampilkan timestamp pembaruan terakhir dan keadaan kosong/error yang jelas.
- Log aplikasi tidak mencatat kata sandi atau rahasia konfigurasi.

## 9. Kriteria penerimaan

1. Workbook sampel dapat dipetakan ke lima dataset utama dan hasil impor memperlihatkan jumlah baris berhasil serta ditolak.
2. Filter sumber di menu Sales Order dapat memilih A, B, C, D, atau Semua; untuk sebuah `repeat_no`, detail hanya menampilkan baris yang cocok dan tidak menambahkan baris dari order lain.
3. Dashboard KPI dan tracker menggunakan aturan agregasi yang sama dan menampilkan satuan.
4. Hold pada Finish Good tampak dan tidak dianggap siap kirim.
5. Coil duplikat antar kategori dan `end_weight` kosong terlihat sebagai masalah data; angka potensial dijelaskan.
6. Search/filter/pagination mempertahankan parameter filter saat berpindah halaman.
7. Viewer tidak dapat mengunggah atau mengubah data.
8. UI mengikuti pola visual referensi dan dapat dioperasikan pada desktop maupun mobile.

## 10. Asumsi, risiko, dan keputusan terbuka

- Workbook README menyebut seluruh data sebagai sintetis/dummy.
- Unit bobot, arti `end_weight`, dan hubungan nilai detail terhadap `balance` harus dikonfirmasi pemilik proses.
- Semantik status `allocated`, `req_closed`, `ship_hold_reason`, `finish_hold_reason`, kategori, dan probabilitas belum menjadi aturan final.
- Aturan pencocokan material berdasarkan grade/dimensi/customer perlu persetujuan teknis produksi.
- Pilihan upsert/replace, frekuensi impor, dan pemilik tiap sheet belum ditetapkan.
- Snapshot data workbook bertanggal 10 November 2026; dashboard tidak boleh menyebutnya real-time.

## 11. Tahapan

1. Review definisi metrik, unit, hold, dan deduplikasi dengan pemilik proses.
2. Rancang model data dan pemetaan workbook, termasuk laporan rekonsiliasi.
3. Bangun dashboard, Sales Order, dan tracker berbasis data sampel.
4. Tambahkan impor tervalidasi, autentikasi, serta audit.
5. Uji penerimaan dengan planner dan warehouse menggunakan workbook representatif.
6. Siapkan PostgreSQL, backup, akses, dan prosedur impor operasional.


