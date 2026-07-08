# Tutorial IDX Agents — Menggabungkan Dokumen & Data Gold dengan Agent Bricks (Bahasa Indonesia)

Tutorial ini adalah **lanjutan** dari [TUTORIAL_IDX_SIMPLE.md](TUTORIAL_IDX_SIMPLE.md). Setelah Anda membangun gold layer volatilitas saham IDX dan sebuah Genie Space, di sini Anda akan menambahkan **dokumen tak terstruktur** (profil/prospektus sebuah emiten) dan menggabungkannya dengan data tabel gold menggunakan **Agent Bricks** di Databricks.

**Ide utamanya:** kita ingin bisa bertanya **dari dokumen** (mis. "Kapan GOTO IPO dan berapa harga IPO-nya?") **sekaligus** bertanya **dari tabel gold** (mis. "Berapa annualized volatility GOTO?") dalam **satu agen** yang sama. Agen ini otomatis memilih sumber yang tepat untuk tiap pertanyaan.

Emiten yang kita pakai sebagai contoh adalah **PT GoTo Gojek Tokopedia Tbk (GOTO)** — saham teknologi bervolatilitas tinggi dengan cerita publik yang kaya: hasil penggabungan Gojek dan Tokopedia, salah satu IPO terbesar dalam sejarah Bursa Efek Indonesia (2022), dan penurunan harga yang tajam pasca-IPO.

## Konsep: 3 Komponen Agent Bricks

| Komponen | Fungsi | Sumber data |
|----------|--------|-------------|
| **Knowledge Assistant (KA)** | Tanya-jawab dari dokumen (RAG) | File dokumen di UC Volume |
| **Genie Space** | Bahasa alami → SQL | Tabel gold di Unity Catalog |
| **Supervisor Agent (Multi-Agent Supervisor / MAS)** | Mengorkestrasi & memilih agen yang tepat | Menggabungkan KA + Genie Space |

Alur yang kita bangun:

```
Dokumen GOTO (Volume)  ──►  Knowledge Assistant ─┐
                                                 ├──►  Supervisor Agent  ──►  Anda bertanya
Tabel gold volatilitas ──►  Genie Space ─────────┘        (routing)
```

> **Prasyarat khusus tutorial ini:**
> - Anda telah menyelesaikan **[TUTORIAL_IDX_SIMPLE.md](TUTORIAL_IDX_SIMPLE.md)**, sehingga schema `<your_username>_idx_demo` sudah berisi tabel-tabel **gold** (ranking volatilitas, tren volatilitas bulanan, volatilitas saham vs IHSG) dan sudah ada **Genie Space** di atasnya.
> - Fitur **Agent Bricks** aktif di workspace Anda (menu **Agents** di sidebar). Jika tidak terlihat, hubungi admin workspace Anda.

> **Penting:** Ganti `<your_username>` dengan username Anda, dan `<your_catalog>` dengan catalog yang ditugaskan kepada Anda.

---

## Exercise 1: Upload Dokumen Emiten ke Volume

*Tool: Workspace UI (Drag & Drop)*

Knowledge Assistant membaca dokumen dari sebuah Unity Catalog Volume. Kita buat volume khusus dokumen agar terpisah dari data CSV mentah.

### Langkah-langkah

1. Di catalog explorer, buka `<your_catalog>` > `<your_username>_idx_demo`
2. Klik **Create** > **Volume**, beri nama `documents`, tipe **Managed**, lalu **Create**
3. Buka volume `documents`
4. Dari repo lokal, buka folder `data/documents/goto/` — di dalamnya ada file **`GOTO_profil_prospektus.pdf`** (rangkuman profil/prospektus GOTO berbasis informasi publik)
5. **Drag & drop** file tersebut ke volume `documents`

> **Catatan:** File contoh berformat PDF. Knowledge Assistant juga mendukung format teks dan Markdown. Anda bebas menambahkan dokumen lain (mis. laporan tahunan atau prospektus resmi dalam PDF) ke volume yang sama untuk memperkaya jawaban.

### Validasi

- Telusuri volume `documents` dan pastikan `GOTO_profil_prospektus.pdf` sudah ter-upload
- Klik file untuk preview isinya

---

## Exercise 2: Buat Knowledge Assistant atas Dokumen

*Tool: Workspace UI (Agent Bricks)*

Knowledge Assistant (KA) meng-index dokumen dan menjawab pertanyaan berbasis isinya (Retrieval-Augmented Generation).

### Langkah-langkah

1. Pada sidebar kiri, klik **Agents** (Agent Bricks)
2. Pilih tile **Knowledge Assistant** > **Build**
3. Konfigurasi:
   - **Name:** `<your_username>_goto_docs`
   - **Description:**
     > Menjawab pertanyaan seputar profil dan prospektus PT GoTo Gojek Tokopedia Tbk
     > (GOTO): riwayat pembentukan dan IPO, struktur kepemilikan, kegiatan usaha, aksi
     > strategis (mis. Tokopedia–TikTok), faktor risiko, dan kinerja harga saham.
   - **Knowledge source:** pilih volume `/Volumes/<your_catalog>/<your_username>_idx_demo/documents`
4. (Opsional) Tambahkan **Instructions**, mis.:
   > Jawab dalam Bahasa Indonesia, ringkas dan faktual, mengacu pada isi dokumen. Jika
   > informasi tidak ada di dokumen, katakan tidak tersedia.
5. Klik **Create** / **Build**

### Tunggu Provisioning

Endpoint KA butuh beberapa menit untuk provisioning (status `PROVISIONING` → `ONLINE`). Tunggu hingga **ONLINE** sebelum menguji.

### Uji Knowledge Assistant

Setelah ONLINE, buka playground KA dan coba:

- "Kapan GOTO melakukan IPO dan berapa harga penawaran perdananya?"
- "GOTO adalah hasil penggabungan perusahaan apa saja?"
- "Berapa dana yang dihimpun GOTO dari IPO?"
- "Apa saja faktor risiko utama GOTO?"
- "Apa yang terjadi dengan Tokopedia dan TikTok?"

### Validasi

- Status endpoint KA **ONLINE**
- KA menjawab pertanyaan di atas dengan mengacu pada isi dokumen GOTO

---

## Exercise 3: Pastikan Genie Space atas Data Gold

*Tool: Workspace UI*

Kita akan menggunakan kembali **Genie Space** yang sudah dibuat di [TUTORIAL_IDX_SIMPLE.md](TUTORIAL_IDX_SIMPLE.md) (Exercise 7) — yang terhubung ke tabel-tabel gold volatilitas.

### Langkah-langkah

1. Pada sidebar kiri, klik **Genie**
2. Pastikan Genie Space `<your_username> - Analitik Volatilitas Saham IDX` ada dan berfungsi
3. Jika belum ada, buat sekarang: **New Genie space**, pilih ketiga tabel gold di `<your_catalog>.<your_username>_idx_demo` (ranking volatilitas, tren bulanan, volatilitas vs IHSG), beri nama yang sama
4. Uji cepat: "Berapa annualized volatility GOTO?" dan "Bandingkan volatilitas GOTO dengan IHSG"
5. Catat **Genie Space ID** (terlihat di URL Genie Space, atau via menu **Settings**) — akan dipakai di Exercise 4

### Validasi

- Genie Space menjawab pertanyaan volatilitas terhadap tabel gold
- Anda mengetahui Genie Space ID-nya

---

## Exercise 4: Buat Supervisor Agent (Gabungan Dokumen + Data)

*Tool: Workspace UI (Agent Bricks)*

Supervisor Agent (Multi-Agent Supervisor / MAS) menggabungkan beberapa agen dan **otomatis merutekan** setiap pertanyaan ke agen yang paling tepat — KA untuk pertanyaan dokumen, Genie untuk pertanyaan data.

### Langkah-langkah

1. Pada sidebar kiri, klik **Agents** (Agent Bricks)
2. Pilih tile **Multi-Agent Supervisor** > **Build**
3. Konfigurasi:
   - **Name:** `<your_username>_idx_goto_supervisor`
   - **Description:**
     > Agen gabungan untuk analisis saham GOTO: menjawab pertanyaan dari dokumen
     > profil/prospektus GOTO sekaligus pertanyaan analitik volatilitas dari data gold IDX.
4. Tambahkan **dua agen**:
   - **Agen 1 — Dokumen (Knowledge Assistant):**
     - Pilih KA `<your_username>_goto_docs` yang dibuat di Exercise 2
     - **Description (untuk routing):**
       > Menjawab pertanyaan tentang profil dan prospektus GOTO: riwayat pembentukan dan
       > IPO, harga IPO, dana yang dihimpun, struktur kepemilikan, kegiatan usaha, aksi
       > strategis (Tokopedia–TikTok), dan faktor risiko.
   - **Agen 2 — Data (Genie Space):**
     - Pilih Genie Space `<your_username> - Analitik Volatilitas Saham IDX` (Exercise 3)
     - **Description (untuk routing):**
       > Menjawab pertanyaan kuantitatif volatilitas harga saham IDX dari tabel gold:
       > annualized volatility per saham, ranking saham paling volatil, tren volatilitas
       > bulanan, dan perbandingan volatilitas saham terhadap pasar (IHSG).
5. (Opsional) Tambahkan **Instructions** routing, mis.:
   > Untuk pertanyaan tentang profil, sejarah, kepemilikan, aksi korporasi, atau risiko
   > GOTO, gunakan agen Dokumen. Untuk pertanyaan angka volatilitas, ranking, tren, atau
   > perbandingan terhadap IHSG, gunakan agen Data. Jika pertanyaan mencakup keduanya,
   > ambil informasi dari kedua agen lalu gabungkan jawabannya.
6. Klik **Create** / **Build** dan tunggu status endpoint **ONLINE**

### Validasi

- Supervisor Agent terdaftar di **Agents** dengan dua agen (Dokumen + Data)
- Status endpoint **ONLINE**

---

## Exercise 5: Uji Pertanyaan Gabungan (Dokumen + Tabel)

*Tool: Playground Agent Bricks*

Inilah tujuan utama tutorial: bertanya **dari dokumen** dan **dari data gold** dalam satu percakapan. Buka playground Supervisor Agent dan coba pertanyaan berikut.

**Pertanyaan dokumen (dijawab agen KA):**
- "Kapan GOTO IPO dan berapa harga IPO-nya?"
- "GOTO adalah gabungan perusahaan apa, dan siapa investor besarnya?"
- "Apa yang terjadi antara Tokopedia dan TikTok pada 2023?"

**Pertanyaan data (dijawab agen Genie):**
- "Berapa annualized volatility GOTO?"
- "Apakah GOTO termasuk saham paling volatil? Tunjukkan rankingnya."
- "Bandingkan volatilitas GOTO dengan pasar (IHSG)."

**Pertanyaan gabungan (menggunakan kedua agen):**
- "Jelaskan tiga lini usaha GOTO, lalu tunjukkan seberapa volatil sahamnya dibanding IHSG."
- "Menurut dokumen, apa faktor risiko utama GOTO — dan apakah tercermin pada tingkat volatilitas harganya di data?"
- "Berapa harga IPO GOTO menurut dokumen, dan bagaimana tren volatilitas bulanannya belakangan ini?"

### Validasi

- Pertanyaan dokumen dijawab dari isi `GOTO_profil_prospektus.pdf`
- Pertanyaan data dijawab dengan query ke tabel gold (via Genie)
- Pertanyaan gabungan menunjukkan agen mengambil dari **kedua** sumber dan merangkumnya

---

## Penutup

Selamat! Anda telah membangun **agen gabungan (structured + unstructured)** untuk analisis saham IDX:

| Step | Apa yang Anda Bangun | Tool |
|------|----------------------|------|
| Exercise 1 | Volume `documents` + upload dokumen GOTO | Workspace UI |
| Exercise 2 | Knowledge Assistant atas dokumen GOTO | Agent Bricks |
| Exercise 3 | Genie Space atas tabel gold volatilitas | Workspace UI |
| Exercise 4 | Supervisor Agent yang menggabungkan KA + Genie | Agent Bricks |
| Exercise 5 | Tanya-jawab gabungan dokumen + data | Playground |

**Apa Selanjutnya?**
- Tambahkan dokumen lain (laporan tahunan, prospektus resmi PDF, keterbukaan informasi) ke volume `documents` untuk memperkaya jawaban KA.
- Tambahkan emiten lain (mis. BREN, ARTO, BUMI) dengan dokumen masing-masing, lalu perluas Supervisor Agent.
- Sematkan Supervisor Agent ke aplikasi atau dashboard, atau panggil melalui API untuk integrasi lebih lanjut.
- Tambahkan **certified queries** dan **instructions** di Genie Space agar jawaban data makin akurat.

> **Catatan:** Dokumen GOTO pada tutorial ini adalah rangkuman ilustratif dari informasi
> publik untuk keperluan latihan — bukan dokumen resmi emiten. Untuk dokumen resmi,
> rujuk [idx.co.id](https://www.idx.co.id) serta situs resmi perusahaan.
