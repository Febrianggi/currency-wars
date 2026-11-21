# Currency Wars

[English](README.md) · **Bahasa Indonesia**

Currency Wars adalah dashboard interaktif untuk melihat pergerakan rupiah dan mata uang lain terhadap *Special Drawing Rights* (SDR) dari IMF. Kamu bisa membandingkan posisi mata uang pilihanmu dengan mata uang ASEAN dan dunia. Dashboard dibuka dengan rupiah (IDR) sebagai pilihan awal dan berjalan di browser dari satu file `index.html`.

**[Buka dashboard Currency Wars](https://febrianggi.github.io/currency-wars/)**

## Isi dashboard

| Bagian | Yang ditampilkan |
|---|---|
| **Overview** | Kurs terbaru, indikator posisi terhadap batas kendali, angka ringkasan, dan peta kendali x̄ dengan garis tengah, batas atas dan bawah, serta titik bulanan di luar batas. Kamu bisa memilih rentang tanggal dan menghitung ulang batas untuk periode itu. |
| **vs World** | Perbandingan semua mata uang dalam data. Tiap titik adalah skor-z. Grafik menandai batas kendali dan mata uang yang berada di luarnya. |
| **vs ASEAN** | Perbandingan yang sama untuk sepuluh mata uang ASEAN. Bagian ini muncul saat mata uang pilihan termasuk dalam kelompok tersebut. |
| **Country view** | Kesimpulan untuk mata uang pilihan, peta kendali skor-z bulanan, dan perbandingan posisi tahunan dengan satu mata uang lain. |
| **Data tables** | Tabel mata uang pilihan, peringkat dunia, dan perbandingan dua mata uang. Tabel bisa disaring menurut tanggal atau status, dicari, diurutkan, dan diunduh sebagai CSV. |
| **Live data and sources** | Status data XE, tombol untuk menjalankan scraper Python, opsi memakai workbook sendiri, dan catatan metode. |

Dashboard punya mode terang dan gelap. Grafik dan penjelasan ikut berubah saat kamu mengganti mata uang atau periode di bagian atas halaman.

## Cara membaca grafik

Kurs ditampilkan dalam satuan mata uang pilihan per 1 SDR. Untuk rupiah, misalnya, angka yang lebih tinggi berarti perlu lebih banyak rupiah untuk memperoleh 1 SDR. Artinya, rupiah lebih lemah terhadap SDR. Garis tengah menunjukkan rata-rata. Batas kendali atas dan bawah masing-masing berjarak dua simpangan baku sampel dari rata-rata. Titik di luar batas ditandai sebagai di luar kendali menurut aturan grafik ini.

Untuk perbandingan, kurs tiap mata uang diubah menjadi skor-z berdasarkan riwayat mata uang itu sendiri. Skor-z positif berarti mata uang tersebut lebih lemah terhadap SDR dibandingkan rata-rata historisnya. Skor-z tahunan adalah rata-rata skor-z bulanan pada tahun tersebut.

## Data terkini dari XE

Kurs berasal dari [tabel kurs XE](https://www.xe.com/currencytables/?from=XDR) dengan SDR (kode XDR) sebagai basis.

```text
XE → scripts/update_data.py (GitHub Actions, tiap jam) → data/rates.json → index.html
```

- [`scripts/xe_scraper.py`](scripts/xe_scraper.py) membaca tabel XE dengan pustaka standar Python.
- [`scripts/update_data.py`](scripts/update_data.py) mengisi data akhir bulan yang belum tersedia dan menambahkan tabel harian terbaru ke `data/rates.json`. Workflow berjalan tiap jam dan menyimpan perubahan saat ada data baru. XE memperbarui tabelnya sekali sehari.
- Dashboard membaca `data/rates.json` saat dibuka dan tiap 30 menit selama halaman masih terbuka. Kurs harian terbaru muncul sebagai titik **live** setelah titik akhir bulan terakhir. Setelah bulan berakhir, nilainya masuk ke seri akhir bulan.
- Tombol **Run the Python scraper here** memuat Pyodide untuk menjalankan scraper di browser. Karena permintaan langsung ke XE biasanya diblokir oleh aturan CORS, dashboard memberi tahu pengguna dan tetap memakai salinan data dari `data/rates.json`.

Untuk mengisi data pada salinan repo sendiri, buka tab **Actions**, pilih **Update XE rates**, lalu klik **Run workflow**. Workflow mengisi data sejak baris terakhir `data.xlsx` hingga kurs terkini.

Kalau kamu mengubah scraper, jalankan kedua perintah ini dari root repo:

```sh
python scripts/embed_python.py
python -m unittest discover -s tests
```

Perintah pertama memperbarui salinan scraper di `index.html`. Perintah kedua menjalankan tes scraper.

Cek ketentuan penggunaan XE sebelum pengambilan data berskala besar. Workflow memberi jeda antarpemintaan. Jika pembaruan gagal, dashboard tetap memakai data terakhir yang tersedia.

## Pakai workbook Excel sendiri

Di bagian **Live data and sources**, pilih atau seret file `.xlsx` ke area unggah. Dashboard membaca file di browser. Workbook bawaan [`data.xlsx`](data.xlsx) bisa dipakai langsung. Di Chrome dan Edge, klik **Refresh from the same file** untuk membaca ulang file yang baru disimpan di Excel.

Gunakan lembar **Global Data** dengan tanggal di kolom A dan kode mata uang di baris 1. Dashboard mengambil seri IDR dan sepuluh mata uang ASEAN dari lembar ini. Lembar `Data IDR`, `Data ASEAN`, `IDR VS ASEAN`, dan `IDR VS Global` bersifat opsional.

## Notebook

- [`currency_control_chart.ipynb`](currency_control_chart.ipynb) mengulang perhitungan utama di Google Colab, termasuk skor-z, peta kendali mata uang pilihan dan dunia, serta perbandingan tahunan dua mata uang.
- [`fetch_xe_data.ipynb`](fetch_xe_data.ipynb) mengambil data kurs bulanan dari XE dan menyimpannya sebagai workbook Excel.

## Struktur repo

| File | Isi |
|---|---|
| [`index.html`](index.html) | Dashboard |
| [`data/rates.json`](data/rates.json) | Kurs bulanan dan kurs harian terbaru dari workflow |
| [`scripts/xe_scraper.py`](scripts/xe_scraper.py) | Pembaca tabel XE yang juga disalin ke dashboard |
| [`scripts/update_data.py`](scripts/update_data.py) | Pembaru data kurs |
| [`scripts/embed_python.py`](scripts/embed_python.py) | Penyalin scraper ke `index.html` |
| [`tests/test_xe_scraper.py`](tests/test_xe_scraper.py) | Tes scraper |
| [`.github/workflows/update-data.yml`](.github/workflows/update-data.yml) | Jadwal pembaruan data tiap jam |
| [`currency_control_chart.ipynb`](currency_control_chart.ipynb) | Notebook perhitungan |
| [`fetch_xe_data.ipynb`](fetch_xe_data.ipynb) | Notebook pengambilan data |
| [`data.xlsx`](data.xlsx) | Workbook bawaan |

## Catatan teknis

Dashboard memakai HTML, CSS, dan JavaScript dalam satu file dan bisa dijalankan langsung. [Chart.js](https://www.chartjs.org/) 4.4.1 untuk grafik dan [SheetJS](https://sheetjs.com/) 0.18.5 untuk membaca Excel sudah tertanam di halaman. Pyodide 0.26.4 baru diunduh saat tombol scraper Python diklik.
