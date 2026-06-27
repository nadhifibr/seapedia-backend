# Seapedia - Marketplace Kelautan & Pantai 🌊

Seapedia adalah platform e-commerce yang didesain khusus untuk memenuhi kebutuhan alat tangkap ikan, perlengkapan selam, hingga peralatan laut lainnya. Platform ini dibangun menggunakan arsitektur monorepo logis yang terpisah antara **Frontend (Next.js)** dan **Backend (Django REST Framework)**.

> 📝 **Catatan untuk Evaluator / Juri COMPFEST Software Engineering Academy**: File `README.md` ini disamakan di repositori Frontend dan Backend agar Anda tidak perlu berpindah-pindah repositori untuk membaca dokumentasi arsitektur, panduan pengujian, dan logika bisnis.

---

## 🚀 1. Demo Accounts (Fast Testing)

Aplikasi telah di-*seed* dengan ratusan data. Untuk memudahkan pengujian End-to-End, silakan gunakan salah satu akun berikut (atau Anda bisa mendaftar akun baru):

| Role | Email | Password | Keterangan |
|------|-------|----------|------------|
| **Admin** | `rakko@gmail.com` | `rakkorakko` | Akses panel admin & statistik platform. |
| **Buyer** | `chiikawa@gmail.com` | `chiikawa` | Akun pembeli dengan saldo dompet besar. |
| **Seller** | `seller_pro_1@example.com`| `password123` | Toko siap pakai dengan banyak produk. |
| **Driver** | `driver_pro_1@example.com`| `password123` | Driver untuk menerima *Delivery Job*. |
| **Multi-Role**| `hachiware@gmail.com` | `hachiware` | Akun hybrid (Buyer sekaligus Seller). |

---

## 📚 2. API Documentation

Dokumentasi API lengkap dengan standar OpenAPI/Swagger telah diimplementasikan menggunakan `drf-spectacular`. 
Anda bisa melakukan testing endpoint secara interaktif melalui:

* **Swagger UI (Production)**: [https://seapedia-backend.vercel.app/api/docs/](https://seapedia-backend.vercel.app/api/docs/)
* **Swagger UI (Local)**: `http://localhost:8000/api/docs/`
* **OpenAPI Schema**: `/api/schema/`

---

## 🧪 3. End-to-End Demo Flow

Untuk menguji fungsionalitas utama aplikasi (*happy path*), ikuti langkah berikut:

1. **Buyer Flow**: 
   - Login menggunakan akun Buyer (`chiikawa@gmail.com`).
   - Cari produk di halaman beranda atau *search bar*.
   - Masukkan produk ke keranjang (*Add to Cart*).
   - Masuk ke halaman Cart -> Checkout.
   - Pada halaman Checkout, pilih alamat, metode pengiriman, dan gunakan kode promo (misal: `VOUCHER50`).
   - Klik **Pay Now**.
2. **Seller Flow**:
   - Logout, lalu login sebagai Seller (`seller_pro_1@example.com`), atau gunakan tombol **Ganti Role** di Navbar jika Anda menggunakan akun Multi-Role.
   - Masuk ke Dashboard Seller -> Pesanan.
   - Cari pesanan dengan status `SEDANG_DIKEMAS`.
   - Klik **Proses Pesanan**. Status akan berubah menjadi `MENUNGGU_PENGIRIM` dan sistem otomatis membuat *Delivery Job*.
3. **Driver Flow**:
   - Login menggunakan akun Driver (`driver_pro_1@example.com`).
   - Masuk ke Dashboard Driver -> Cari Job.
   - Ambil pesanan yang berstatus *Available*.
   - Pada menu My Jobs, klik **Selesaikan Pekerjaan** setelah barang diantar. Status pesanan akan menjadi `PESANAN_SELESAI`.
4. **Buyer Review**:
   - Kembali login sebagai Buyer.
   - Masuk ke Dashboard Buyer -> Pesanan -> Riwayat Pesanan.
   - Berikan ulasan (*Rating & Review*) pada produk yang baru saja selesai diantar.

---

## 💼 4. Logika Bisnis (Business Rules)

Berikut adalah implementasi logika bisnis sesuai dengan *requirements* kompetisi:

### A. Single-Store Checkout Behavior
Keranjang belanja (Cart) dirancang untuk beroperasi secara eksklusif pada **satu toko pada satu waktu**. Saat barang pertama dimasukkan, ID keranjang akan "dikunci" pada `store_id` barang tersebut. Ini memastikan seluruh *checkout process* dan perhitungan *Delivery Fee* akurat secara jarak antara 1 titik penjual dan pembeli. Jika pembeli ingin berbelanja di toko lain, mereka harus menyelesaikan *checkout* saat ini atau mengosongkan keranjang.

### B. Discount Combination & PPN 12% Calculation
Sistem harga (*pricing engine*) di API Checkout kami menghitung komponen pesanan dengan hierarki berikut:
1. **Subtotal**: Total dari `(Harga Produk x Kuantitas)`.
2. **Discount**: Dihitung dari tipe Promo (Persentase) atau Voucher (Nominal Fixed). Diskon memotong langsung nilai Subtotal. (Nilai diskon maksimal = Subtotal).
3. **PPN 12%**: Dihitung **setelah** diskon diterapkan. Rumus: `PPN = (Subtotal - Discount) * 12%`.
4. **Total Akhir**: `(Subtotal - Discount) + Delivery Fee + PPN`.

### C. Driver Earning Rule
Pemasukan Driver (`driver_earning`) dipatok setara dengan **Total Ongkos Kirim (Delivery Fee)** yang dibayarkan oleh pembeli. Saat Driver menyelesaikan pekerjaan, saldo dompet Driver akan bertambah sesuai nominal `order.delivery_fee`. Logika ini dapat dilihat di `apps/deliveries/views.py`.

### D. Overdue SLA & Time Simulation
Pesanan yang tidak segera diproses oleh Penjual atau diantar oleh Driver akan **dibatalkan secara otomatis (Auto-Cancel)** jika melewati batas Service Level Agreement (SLA).
- **INSTANT**: 1 Hari.
- **NEXT_DAY**: 2 Hari.
- **REGULAR**: 5 Hari.
- **Time Simulation / Testing**: Aplikasi menggunakan **APScheduler** (*Advanced Python Scheduler*). Secara *default* cron job ini berjalan di *background*. Untuk mensimulasikan waktu tanpa harus menunggu berhari-hari, Anda bisa mengedit nilai `overdue_at` pada tabel Order langsung via Django Admin panel, atau menjalankan *command*: `python manage.py runapscheduler` untuk mengeksekusi inspeksi SLA secara paksa.

---

## 🔒 5. Security Measures

Aplikasi ini di-*harden* dengan beberapa lapis keamanan:

1. **SQL Injection (SQLi)**: Django ORM digunakan untuk seluruh kueri basis data. Data masukan pengguna diikat (*parameterized binding*) secara otomatis sehingga *raw payload* SQL (seperti `' OR 1=1;`) akan dirender sebagai *string* aman, mencegah manipulasi *query*.
2. **Cross-Site Scripting (XSS)**: Seluruh *input* pengguna akan lolos melalui *Input Validator* (DRF Serializers). Di sisi Frontend, Next.js (React) secara *native* melakukan sanitasi DOM dan *auto-escaping* variabel yang di-*render* di antarmuka. Django Security Middleware juga dikonfigurasi untuk perlindungan tambahan.
3. **Session Behavior**: Sistem tidak menggunakan session-cookie klasik, melainkan menggunakan arsitektur *stateless* **JWT (JSON Web Token)** (`djangorestframework-simplejwt`). Access Token memiliki usia pendek (30 menit) dan Refresh Token dirotasi secara otomatis dengan fitur *Blacklist* saat pengguna *logout*.
4. **Role-Based Access Control (RBAC)**: Otorisasi API dilindungi dengan kustom *Permissions Class* (`IsActiveBuyer`, `IsActiveSeller`, `IsActiveDriver`, `IsAdminUser`). Seseorang yang memiliki *token* valid tidak bisa mengakses *endpoint* toko jika perannya di *database* bukan sebagai `SELLER`. Validasi otorisasi berjalan ganda (di Frontend *routing protection* dan di *Backend endpoint API*).

---

## ⚙️ 6. Environment Setup & Run Instructions

### Repositori 1: Backend (Django REST Framework)
Lokasi: `seapedia-backend/`

**Persyaratan**: Python 3.10+, PostgreSQL, Redis.

**Langkah Instalasi:**
1. Buat virtual environment: `python -m venv venv`
2. Aktifkan venv: `source venv/bin/activate` (Mac/Linux) atau `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Buat file `.env` (lihat konfigurasi di bawah).
5. Lakukan migrasi database: `python manage.py migrate`
6. Tanam data *demo*: `python seed_data.py`
7. Jalankan server: `python manage.py runserver` (Berjalan di `localhost:8000`)

**Konfigurasi `.env` Backend:**
```env
DEBUG=True
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/seapedia
REDIS_URL=redis://localhost:6379/1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Repositori 2: Frontend (Next.js 14)
Lokasi: `seapedia-frontend/`

**Persyaratan**: Node.js 18+.

**Langkah Instalasi:**
1. Install dependencies: `npm install`
2. Buat file `.env.local` (lihat konfigurasi di bawah).
3. Jalankan server *development*: `npm run dev` (Berjalan di `localhost:3000`)

**Konfigurasi `.env.local` Frontend:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---
*Dibuat untuk COMPFEST Software Engineering Academy.*
