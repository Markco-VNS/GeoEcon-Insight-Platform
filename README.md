# GeoEcon Insight

Dashboard intelijen ekonomi untuk menganalisis pola pengeluaran konsumsi per kapita sebulan antarprovinsi di Indonesia. Aplikasi membandingkan pengeluaran makanan dan bukan makanan, perubahan nominal 2024–2025, serta komposisi konsumsi 2025.

## Fitur

- Ringkasan indikator nasional dan perbandingan 38 provinsi.
- Peta choropleth interaktif untuk melihat sebaran indikator menurut provinsi.
- Perbandingan pengeluaran makanan, bukan makanan, dan total pada 2024–2025.
- Grafik hubungan pengeluaran total dengan porsi makanan sebagai pembacaan deskriptif Hukum Engel.
- Klasifikasi provinsi ke dalam empat kuadran berdasarkan median pengeluaran dan median porsi makanan.
- Simulator skenario aritmetis, pencarian dan penyaringan tabel, serta ekspor data CSV.

## Sumber dan pengolahan data

Backend membaca tiga CSV di `backend/data`:

1. `Rata-rata Pengeluaran ... 2024.csv` — nilai pengeluaran makanan, bukan makanan, dan jumlah.
2. `Rata-rata Pengeluaran ... 2025.csv` — nilai pengeluaran makanan, bukan makanan, dan jumlah.
3. `Persentase Pengeluaran ... 2025.csv` — persentase komposisi makanan dan bukan makanan.

Nama lengkap berkas ditunjukkan langsung di folder `backend/data`. Loader mencocokkan nama berkas berdasarkan jenis dan tahun, lalu menggabungkan tabel berdasarkan nama provinsi. Dataset harus berisi tepat 38 provinsi; baris `Indonesia` digunakan untuk ringkasan nasional. File `indonesia_38_provinces.geojson` hanya menyediakan geometri wilayah peta, bukan sumber indikator ekonomi.

Nilai porsi 2025 mengikuti angka pada CSV persentase. Porsi 2024 dihitung dari nilai pengeluaran makanan dibagi total pengeluaran 2024, karena CSV persentase yang tersedia hanya untuk 2025.

## Rumus indikator

Gunakan notasi berikut untuk suatu provinsi: `M` = pengeluaran makanan, `N` = pengeluaran bukan makanan, dan `T` = pengeluaran total.

| Indikator | Rumus / cara hitung |
|---|---|
| Total pengeluaran | `T = M + N` (nilai total memakai kolom jumlah pada CSV). |
| Porsi makanan 2025 | Mengikuti persentase makanan yang tercatat pada CSV persentase 2025. |
| Porsi bukan makanan 2025 | Mengikuti persentase bukan makanan yang tercatat pada CSV persentase 2025. |
| Porsi makanan 2024 | `(M2024 / T2024) × 100%`. |
| Pertumbuhan nominal 2024–2025 | `((X2025 − X2024) / X2024) × 100%`, dihitung untuk total, makanan, dan bukan makanan. |
| Perubahan porsi makanan | `Porsi makanan 2025 − Porsi makanan 2024`, dalam poin persentase (pp). |
| Median | Nilai tengah indikator dari 38 provinsi; median total dan median porsi makanan menjadi batas kuadran. |
| Disparitas | Rasio `total tertinggi / total terendah`; selisih rupiah `total tertinggi − total terendah`. |
| Korelasi Engel | Korelasi Pearson `r` antara total pengeluaran per provinsi dan porsi makanan 2025. `R² = r²`. |
| Garis regresi Engel | Regresi linear sederhana `porsi makanan = slope × (total / 1.000.000) + intercept`. Total dinyatakan dalam juta rupiah agar skala koefisien lebih mudah dibaca. |

### Kuadran provinsi

Klasifikasi membandingkan nilai provinsi dengan median 38 provinsi:

| Kuadran | Kondisi |
|---|---|
| I — Rentan konsumsi | Total di bawah median dan porsi makanan di atas median. |
| II — Tekanan pangan tinggi | Total sama dengan atau di atas median dan porsi makanan di atas median. |
| III — Transisi konsumsi | Total di bawah median dan porsi makanan sama dengan atau di bawah median. |
| IV — Konsumsi non-pangan besar | Total sama dengan atau di atas median dan porsi makanan sama dengan atau di bawah median. |

Nama kuadran adalah label untuk membantu membaca pola relatif antarprovinsi, bukan penilaian resmi tingkat kesejahteraan.

### Simulator skenario

Simulator menerapkan asumsi pada nilai 2025 untuk provinsi terpilih atau seluruh provinsi:

```text
M_simulasi = M × (1 − potongan_pangan_persen / 100)
T_simulasi = (M_simulasi + N) × (1 + stimulus_pendapatan_persen / 100)
Porsi_makanan_simulasi = M_simulasi / (M_simulasi + N) × 100%
```

Kuadran baru dihitung dengan membandingkan total dan porsi makanan simulasi dengan median dasar dashboard. Ini simulasi aritmetis berbasis asumsi, bukan estimasi dampak kausal atau prediksi kebijakan.

## Tech stack

- **Frontend:** React 19, Vite 8, Tailwind CSS 3.
- **Visualisasi:** Leaflet dan React Leaflet untuk peta; Recharts untuk grafik; Lucide React untuk ikon.
- **Backend:** Python, FastAPI, Uvicorn, Pydantic.
- **Pengolahan data:** Pandas dan NumPy.
- **Sumber visual peta:** GeoJSON provinsi lokal; basemap peta dimuat dari penyedia tile yang dikonfigurasi di komponen peta.

## Struktur project

```text
GeoEcon-Insight-Platform/
├── backend/
│   ├── app/
│   │   ├── data_loader.py       # Membaca CSV dan menghitung indikator
│   │   ├── main.py              # API FastAPI
│   │   └── models.py            # Skema respons dan permintaan API
│   ├── data/                    # Tiga CSV dan GeoJSON peta
│   ├── requirements.txt         # Dependensi Python
│   └── run_backend.bat          # Runner backend yang dipanggil run_app.bat
├── frontend/
│   ├── public/                  # Aset publik, termasuk logo
│   ├── src/
│   │   ├── components/          # Peta interaktif
│   │   ├── services/api.js      # Koneksi frontend ke API
│   │   ├── utils/formatters.js  # Format angka dan label
│   │   ├── App.jsx              # Dashboard dan visualisasi
│   │   ├── index.css            # Tailwind dan gaya komponen
│   │   └── main.jsx             # Entry point React
│   ├── package.json
│   └── tailwind.config.js
├── run_app.bat                 # Menjalankan backend dan frontend di Windows
└── README.md
```

## Menjalankan aplikasi di Windows

Persyaratan: Python 3.10 atau lebih baru, Node.js 20.19+ (atau 22.12+) dan npm. Buka PowerShell di folder project, lalu jalankan:

```powershell
.\run_app.bat
```

Skrip akan membuka jendela backend dan frontend, lalu membuka dashboard di `http://localhost:5173`. Jika dependensi frontend atau backend belum tersedia, skrip akan memasangnya saat dijalankan. Backend menyediakan dokumentasi API di `http://127.0.0.1:8000/docs`.

Jika Python belum ditemukan, pasang Python 3.10+ dan aktifkan opsi **Add Python to PATH**, lalu buka ulang PowerShell dan jalankan perintah di atas. Di komputer dengan runtime Codex desktop, runner juga dapat menggunakan Python bawaan Codex sebagai fallback.

## Endpoint API utama

| Endpoint | Kegunaan |
|---|---|
| `GET /api/health` | Status backend dan jumlah provinsi yang terbaca. |
| `GET /api/summary` | Ringkasan indikator nasional dan disparitas. |
| `GET /api/provinces` | Data provinsi dengan pilihan filter dan pengurutan. |
| `GET /api/provinces/{provinsi_id}` | Detail analisis sebuah provinsi. |
| `GET /api/quadrants` | Ringkasan jumlah dan karakteristik kuadran. |
| `GET /api/geojson` | Geometri peta yang sudah diperkaya dengan indikator provinsi. |
| `POST /api/simulate` | Menghitung skenario simulator. |

## Batasan interpretasi

- Perubahan 2024–2025 bersifat nominal dan belum disesuaikan dengan inflasi.
- Data yang tersedia merupakan angka provinsi; aplikasi tidak memisahkan hasil perkotaan dan perdesaan dalam analisis dashboard.
- Korelasi dan regresi antarprovinsi bersifat deskriptif, tidak membuktikan hubungan sebab-akibat.
- Simulator menggunakan perubahan persentase sesuai asumsi pengguna, bukan model dampak kebijakan.
