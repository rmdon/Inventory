# Design — ERP Production Operation

**Status:** Draft untuk review  
**Referensi visual:** Screenshot ERP yang diberikan pengguna  
**Platform:** Django web, desktop dan mobile

## 1. Arah visual

Gunakan karakter visual screenshot: sidebar biru tua, header biru, latar konten biru pucat, panel putih, tabel dengan baris bergantian dan sudut membulat. Pertahankan keterbacaan data produksi yang padat. Gunakan istilah antarmuka Bahasa Indonesia; nama field teknis tetap digunakan pada dokumen dan pemetaan impor.

### Token desain awal

| Elemen | Nilai/aturan |
|---|---|
| Sidebar | Navy `#075084` atau warna senada referensi; teks putih |
| Header | Biru gelap `#075084`; tinggi ringkas |
| Latar konten | Biru pucat `#D9EBF2` |
| Permukaan/kartu | Putih `#FFFFFF`, border abu-biru lembut |
| Baris tabel bergantian | Putih dan biru sangat pucat `#D8EAF1` |
| Teks utama | Navy gelap `#173B5E` |
| Aksen interaktif | Cyan/biru sedang; fokus keyboard terlihat jelas |
| Status | Warna ditambah label teks/icon; jangan hanya mengandalkan warna |
| Radius | 12–18 px pada kartu dan kontrol utama |
| Tipografi | Sans-serif jelas; angka KPI tebal; isi tabel 13–14 px desktop |

Warna final dapat diselaraskan setelah implementasi visual pertama. Pastikan kontras teks dan fokus dapat dibaca.

## 2. Navigasi

Desktop memakai sidebar tetap dengan judul **ERP Production** dan menu:

1. Dashboard
2. Sales Order (mencakup daftar order dan tracker inventory A–D)
3. Data Import (khusus Admin/Planner)

Header memuat judul halaman, pencarian global, notifikasi (opsional MVP), pengguna, dan menu akun. Mobile memakai header ringkas dan navigasi bawah atau drawer; menu dan pencarian tidak menutupi konten.

## 3. Halaman Dashboard

### Susunan desktop

1. Header halaman: “Dashboard Produksi”, tanggal pembaruan, filter rentang due date/customer/purchaser.
2. Baris KPI cards: Sales Order terbuka, total balance, Finish Good siap kirim, In Process, Raw Material terkait, order berisiko.
3. Area grafik dua kolom: status pemenuhan dan balance berdasarkan bulan due date.
4. Area lanjutan: order berisiko/terdekat jatuh tempo dan ringkasan sumber inventory A–D.
5. Tabel “Prioritas tindak lanjut” dengan tombol membuka tracker terfilter.

### KPI dan grafik

- Tiap KPI menampilkan nama, nilai, satuan bila berbobot, dan konteks filter.
- Grafik status memakai kategori yang punya legenda dan angka; klik segmen membuka daftar terfilter.
- Grafik bulanan memakai `due_date`; sumbu/bobot menunjukkan satuan.
- Tampilkan label “Data diperbarui …” dari waktu impor, bukan klaim live.
- Jika sumber tidak cocok atau data kosong, gunakan pesan dan tautan pemeriksaan, bukan grafik nol yang menyesatkan.

## 4. Sales Order dan Inventory Tracker

Halaman ini menjadi satu menu sidebar bernama **Sales Order**. Daftar Sales Order dan tracker inventory berada di halaman yang sama. Pengguna berpindah dengan tab **Daftar Sales Order** dan **Tracker**; filter sumber A–D mengubah data tracker tanpa membuat menu sidebar baru.

### Toolbar Tracker

- Pencarian order, repeat number, customer, atau coil.
- Filter sumber berbentuk tab/chip: **Semua | Finish Good (A) | Not Finish (B) | In Process (C) | Raw Material (D)**.
- Filter tambahan: tanggal jatuh tempo, customer, purchaser, status, sumber risiko, dan designation.
- Aksi: Reset filter dan Ekspor CSV (opsional setelah disepakati).
- Urutan awal: order kritis dan due date terdekat; pilihan sort ditampilkan eksplisit.

### Daftar Sales Order dan tabel tracker

Tampilan default tracker adalah ringkasan A–D per order. Pemilihan A, B, C, atau D menampilkan sumber terpilih dan rincian terkait, dengan Sales Order tetap menjadi konteks baris. Tab Daftar Sales Order menampilkan kolom order, customer, purchaser, designation, due date, quantity, shipped, balance, allocated, dan status.

| Kolom tracker | Isi |
|---|---|
| Sales Order | `order_no`; subteks `repeat_no` |
| Customer / Material | customer, purchaser atau designation |
| Due Date | tanggal dan indikator keterlambatan |
| Order | quantity, shipped, balance |
| A Finish Good | bobot neto eligible dan jumlah coil; indikator hold |
| B Not Finish | bobot/jumlah coil; tahap atau hold utama |
| C In Process | bobot/jumlah coil; proses utama |
| D Raw Material | bobot/jumlah coil; lokasi/grade ringkas |
| Coverage / Gap | cakupan potensial dan kekurangan indikatif |
| Status | Aman / Perhatian / Kritis / Data perlu dicek |
| Detail | tombol/ikon “Lihat” |

Tabel lebar dapat digulir horizontal dengan kolom Sales Order yang mudah dikenali. Pada ponsel, setiap order menjadi kartu berisi identitas dan due date, balance, ringkasan sumber terpilih (atau A–D jika Semua), status, dan tombol detail. Pagination mempertahankan filter.

### Detail order

Buka detail sebagai halaman atau side panel lebar. Bagian atas menunjukkan order number, repeat number, customer, designation, due date, dan badge status. Berikutnya tampilkan progress pemenuhan (quantity, shipped, balance), ringkasan A–D, lalu tab/section coil per kategori. Tiap coil memuat nomor, bobot bruto/neto, lokasi, status/proses, hold, serta timestamp bila tersedia. Panel “Pemeriksaan data” menampilkan coil duplikat, field kosong, dan selisih sumber.

## 5. Filter sumber A–D

Semua sumber inventory berada di halaman Sales Order. Isi tampilan berdasarkan filter:

- **Semua:** ringkasan A–D, status risiko, dan cakupan/gap indikatif.
- **Finish Good (A):** coil/product, berat bruto/neto, yard, due date, dan ship hold.
- **Not Finish (B):** coil/product, berat, final line/tanggal, finish hold, ship hold, dan NG.
- **In Process (C):** coil, berat, coil status, leading/post process, dan status produksi.
- **Raw Material (D):** coil, berat, yard, grade, tebal, lebar, dan tanggal penerimaan.

Klik order/repeat membuka rincian gabungan tanpa meninggalkan konteks Sales Order.

## 6. Data Import

Halaman impor dibatasi peran. Alur layar:

1. Pilih/seret file XLSX dan lihat daftar sheet yang dikenali.
2. Validasi struktur; tampilkan sheet yang kurang, header bermasalah, dan jumlah baris terdeteksi.
3. Pratinjau beberapa baris serta ringkasan create/update/reject.
4. Pengguna mengonfirmasi impor.
5. Tampilkan hasil, error per baris yang dapat diunduh, waktu, pengguna, nama file, serta riwayat impor.

Gunakan gaya tabel dan kartu yang sama. Proses impor tidak dianggap selesai sebelum hasil transaksi berhasil dicatat.

## 7. Interaksi dan keadaan

- Search menerima order number, repeat number, coil number, dan customer.
- Filter aktif ditampilkan sebagai chip yang bisa dihapus.
- Sort, filter, dan halaman aktif terjaga saat detail dibuka lalu kembali.
- Badge status selalu memiliki teks: “Siap”, “Hold”, “Dalam proses”, “Perlu perhatian”, “Kritis”, “Data perlu dicek”.
- Loading memakai placeholder; keadaan kosong menawarkan reset filter; kegagalan memberi pesan dan aksi coba lagi.
- Konfirmasi diperlukan untuk aksi impor yang mengubah data. Kesalahan validasi ditampilkan dekat field dan dalam ringkasan.
- Tanggal ditampilkan dalam format lokal Indonesia; angka memakai pemisah ribuan dan jumlah desimal konsisten.

## 8. Responsif dan aksesibilitas

- Desktop: sidebar terbuka, KPI dalam beberapa kolom, tabel lengkap.
- Tablet: sidebar dapat diciutkan, filter dapat membungkus, tabel dapat digulir.
- Mobile: navigasi ringkas, KPI dua kolom, filter dalam drawer, daftar order berbentuk kartu.
- Semua aksi dapat digunakan dengan keyboard; fokus jelas; tombol ikon memiliki label aksesibel.
- Warna status dilengkapi label, bentuk, atau ikon. Grafik memiliki ringkasan teks/tabel yang dapat dibaca.

## 9. Komponen Django yang disarankan

Gunakan Django templates untuk kerangka halaman dan komponen HTML, dengan CSS terstruktur dan JavaScript ringan untuk filter/panel/grafik sesuai kebutuhan. Pisahkan komponen: `AppSidebar`, `Topbar`, `PageHeader`, `FilterBar`, `KpiCard`, `StatusBadge`, `DataTable`, `Pagination`, `OrderDetail`, `InventoryBreakdown`, dan `ImportSummary`. Data dan kalkulasi berasal dari view/service server-side; template tidak menghitung ulang angka bisnis.

## 10. Wireframe teks

### Dashboard

```text
┌ Sidebar ───────┬ Header: Dashboard Produksi | Search | User ─────────┐
│ Dashboard      │ Filter: Periode | Customer | Purchaser                │
│                │ [SO terbuka] [Balance] [FG siap] [Dalam proses] ...  │
│ Sales Order    │ [Status pemenuhan chart] [Balance per bulan chart]    │
│                │ [Order prioritas / risiko] [Ringkasan A B C D]        │
└────────────────┴──────────────────────────────────────────────────────┘
```

### Sales Order / Tracker

```text
┌ Sidebar ───────┬ Header: Sales Order | Search | User ────────────────┐
│ ...            │ Tab: Daftar SO | Tracker                              │
│                │ Sumber: Semua | A | B | C | D                         │
│                │ Filter: Due date | Customer | Status | Designation    │
│                │ SO | Customer | Due | Qty/Balance | Sumber terpilih   │
│                │ ─ alternating rows; risk badge; action Detail ─       │
│                │ Pagination                              Showing 10    │
└────────────────┴──────────────────────────────────────────────────────┘
```

## 11. Catatan untuk handoff implementasi

Desain mengasumsikan angka A–D dijelaskan sebagai stok fisik/hasil proses dan cakupan potensial, dengan bobot neto, deduplikasi coil, serta hold mengikuti aturan PRD. Dashboard dan tabel harus menampilkan waktu snapshot serta indikator data perlu dicek. Aturan warna status dan ambang risiko baru ditetapkan setelah definisi operasional dikonfirmasi.






