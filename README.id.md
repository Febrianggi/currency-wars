# Currency Wars

[English](README.md) · **Bahasa Indonesia**

Dashboard interaktif untuk memantau pergerakan rupiah (IDR) dan mata uang lainnya terhadap *Special Drawing Rights* (SDR) dari IMF, serta membandingkan posisinya dengan mata uang ASEAN dan dunia memakai peta kendali x-bar. Dashboard dibuka dengan IDR sebagai pilihan awal, mendukung pergantian ke mata uang mana pun di dataset, dan berjalan di browser dari satu file `index.html`.

- **Dashboard langsung:** https://febrianggi.github.io/currency-wars/

## Temuan utama

Berdasarkan cuplikan data bulanan tersimpan di [`data/rates.json`](data/rates.json) (171 mata uang pada 67 titik akhir bulan sejak April 2021 sampai Oktober 2026; diperbarui harian lewat GitHub Actions):

- **IDR berada di sisi lemah pita kendali:** Selama 67 pengamatan bulanan, rata-rata IDR tercatat **21.296,51** per 1 SDR (simpangan baku sampel **1.450,77**, batas kendali bawah **18.394,97**, batas kendali atas **24.198,05**).
- **Enam bulan berturut-turut di luar kendali pada 2026:** IDR bertahan di atas batas kendali atas (lebih lemah dari variasi historis normal) setiap bulan sejak Mei 2026 (**24.453,90**) hingga Oktober 2026 (**24.842,63**), dengan nilai harian *live* terbaru **24.594,29** per SDR.
- **Konteks perbandingan lintas mata uang:** Standardisasi skor-z terhadap riwayat masing-masing mata uang memisahkan pergerakan umum SDR dari pelemahan khusus negara di kelompok ASEAN dan dunia. Buka dashboard langsung untuk angka harian terkini.

## Isi dashboard

| Bagian | Yang ditampilkan |
|---|---|
| **Overview** | Kurs terbaru mata uang pilihan, indikator posisi terhadap batas kendali, kartu angka ringkasan, dan peta kendali x-bar per SDR dengan garis tengah, batas atas/bawah, bulan di luar kendali, pemilih rentang tanggal, serta opsi hitung ulang batas. |
| **vs World** | Peta kendali skor-z untuk seluruh mata uang dalam dataset, menandai batas kendali dan mata uang yang berada di luar batas. |
| **vs ASEAN** | Perbandingan skor-z yang sama untuk sepuluh mata uang ASEAN. Muncul otomatis saat mata uang terpilih adalah anggota ASEAN. |
| **Country view** | Kesimpulan ringkas untuk mata uang terpilih, peta kendali skor-z bulanan, serta perbandingan posisi tahunan terhadap satu mata uang pembanding. |
| **Data tables** | Tabel mata uang terpilih, peringkat dunia, dan perbandingan dua mata uang dengan filter tanggal, pencarian, filter status, pengurutan kolom, dan unduh CSV. |
| **Live data and sources** | Status feed XE, tombol scraper Python di browser, pemuat workbook Excel sendiri, dan catatan metode. |

Dashboard memiliki mode terang dan gelap. Semua grafik, tabel, dan ringkasan ikut diperbarui saat kamu mengganti mata uang atau rentang tanggal di bagian atas halaman.

## Cara membaca grafik

- **Arah kurs:** Kurs dinyatakan dalam satuan mata uang terpilih per 1 SDR. Nilai yang lebih tinggi berarti butuh lebih banyak mata uang lokal untuk memperoleh 1 SDR, artinya mata uang tersebut **lebih lemah**.
- **Batas kendali:** Garis tengah adalah rata-rata sampel pada periode terpilih, sedangkan batas kendali atas dan bawah berada dua simpangan baku sampel (`rata-rata ± 2 SD`) di kedua sisinya. Titik di luar batas ditandai sebagai di luar kendali dibanding variasi historis.
- **Perbandingan skor-z:** Agar mata uang dengan skala berbeda dapat dibandingkan, tiap seri distandardisasi terhadap riwayatnya sendiri. Skor-z positif berarti mata uang lebih lemah daripada rata-rata historisnya; nilai tahunan adalah rata-rata skor-z bulanan pada tahun tersebut.

## Cara menjalankan di lokal

Jalankan server HTTP lokal dari folder utama repositori agar `index.html` bisa memuat `data/rates.json` dengan benar:

```bash
python -m http.server 8000
```

Lalu buka http://localhost:8000 di browser. Hentikan server dengan `Ctrl+C`.

Jika kamu mengubah [`scripts/xe_scraper.py`](scripts/xe_scraper.py), perbarui salinan yang tertanam di halaman lalu jalankan uji unit dari folder utama repositori:

```bash
python scripts/embed_python.py
python -m unittest discover -s tests
```

## Data terkini dari XE

Kurs berasal dari [tabel kurs XE](https://www.xe.com/currencytables/?from=XDR) dengan SDR (`XDR`) sebagai basis:

```text
XE -> scripts/update_data.py (GitHub Actions, tiap jam) -> data/rates.json -> index.html
```

- [`scripts/xe_scraper.py`](scripts/xe_scraper.py) membaca tabel XE hanya dengan pustaka standar Python.
- [`scripts/update_data.py`](scripts/update_data.py) mengisi akhir bulan yang belum tersedia dan menambahkan tabel harian terbaru ke [`data/rates.json`](data/rates.json). Workflow [`.github/workflows/update-data.yml`](.github/workflows/update-data.yml) berjalan tiap jam dan hanya menyimpan commit saat XE menerbitkan data baru (umumnya sekali sehari).
- `index.html` membaca `data/rates.json` saat dibuka dan menyegarkannya tiap 30 menit selama tab terbuka. Kurs harian terbaru tampil sebagai satu titik **live** setelah akhir bulan terakhir hingga bulan berjalan selesai.
- **Run the Python scraper here** (di bagian **Live data and sources**) memuat Pyodide untuk menjalankan scraper di browser. Karena XE tidak mengirim header CORS untuk permintaan langsung dari browser, browser biasanya memblokir permintaan, menampilkan alasannya, dan tetap memakai data dari `data/rates.json`.

Untuk mengisi data di salinan fork baru, buka tab **Actions**, pilih **Update XE rates**, lalu klik **Run workflow**. Cek ketentuan penggunaan XE sebelum pengambilan data berskala besar; bila pembaruan gagal, dashboard tetap menampilkan dataset sebelumnya.

## Pakai workbook Excel sendiri

Di bagian **Live data and sources**, pilih atau seret file `.xlsx` untuk melihat data kurs sendiri secara lokal di browser (tidak ada file yang diunggah). Workbook bawaan [`data.xlsx`](data.xlsx) bisa langsung dipakai. Di Chrome dan Edge, klik **Refresh from the same file** untuk memuat ulang perubahan setelah disimpan di Excel.

Letakkan tanggal di kolom A dan kode mata uang di baris 1 pada lembar bernama **Global Data**. Dashboard mengambil seri IDR dan sepuluh mata uang ASEAN dari lembar tersebut; `Data IDR`, `Data ASEAN`, `IDR VS ASEAN`, dan `IDR VS Global` bersifat opsional.

## Notebook

- [`currency_control_chart.ipynb`](currency_control_chart.ipynb): mengulang perhitungan utama di Python (Google Colab), termasuk skor-z, peta kendali mata uang pilihan dan dunia, serta perbandingan tahunan dua mata uang.
- [`fetch_xe_data.ipynb`](fetch_xe_data.ipynb): mengunduh kurs bulanan dari XE ke dalam workbook Excel.

## Struktur repositori

| File | Isi |
|---|---|
| [`index.html`](index.html) | Dashboard satu halaman mandiri |
| [`data/rates.json`](data/rates.json) | Riwayat bulanan dan nilai harian terbaru dari GitHub Actions |
| [`scripts/xe_scraper.py`](scripts/xe_scraper.py) | Pembaca tabel XE (juga disalin ke dalam `index.html`) |
| [`scripts/update_data.py`](scripts/update_data.py) | Pembaru `data/rates.json` |
| [`scripts/embed_python.py`](scripts/embed_python.py) | Penyalin `xe_scraper.py` ke `index.html` |
| [`tests/test_xe_scraper.py`](tests/test_xe_scraper.py) | Uji unit scraper |
| [`.github/workflows/update-data.yml`](.github/workflows/update-data.yml) | Workflow pembaruan otomatis tiap jam |
| [`currency_control_chart.ipynb`](currency_control_chart.ipynb) | Notebook analisis Colab |
| [`fetch_xe_data.ipynb`](fetch_xe_data.ipynb) | Notebook pengambilan data XE |
| [`data.xlsx`](data.xlsx) | Workbook Excel bawaan |

## Catatan teknis

- HTML, CSS, dan JavaScript polos dalam satu berkas tanpa proses build.
- [Chart.js](https://www.chartjs.org/) 4.4.1 dan [SheetJS](https://sheetjs.com/) 0.18.5 sudah tertanam di halaman. Pyodide 0.26.4 baru diunduh saat tombol scraper Python diklik.
