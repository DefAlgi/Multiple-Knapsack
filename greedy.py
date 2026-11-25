
import numpy as np

try:

    """
    Objective Function:
    Max Z = Sum(v[i] * x[i,j])

    Subject to:
    Sum(w[i] * x[i,j]) <= u, untuk setiap hari j

    Kebutuhan wajib:
    1. Makan siang dan makan malam setiap hari.
    2. Transportasi hari Senin sampai Jumat.
    3. Makan pagi hari Senin.
    4. Internet minimal satu kali dalam seminggu.
    5. Jajan minimal satu kali dalam seminggu.

    Greedy Strategy 3:
    Memilih kebutuhan berdasarkan rasio utility/weight
    terbesar terlebih dahulu.

    R[i] = v[i] / w[i]

    Variabel Keputusan:
    x[i,j] = 1 jika kebutuhan i dipilih pada hari j.
    x[i,j] = 0 jika kebutuhan i tidak dipilih pada hari j.
    """

    u = 65000

    w = np.array([
        10000,  # Makan pagi
        15000,  # Makan siang
        15000,  # Makan malam
        17000,  # Transportasi
        6000,   # Kebutuhan akademik
        5000,   # Internet
        15000,  # Jajan
        13000   # Berlangganan aplikasi
    ])

    v = np.array([4, 10, 7, 10, 3, 8, 5, 4])

    nama = [
        "Makan pagi",
        "Makan siang",
        "Makan malam",
        "Transportasi",
        "Kebutuhan akademik",
        "Internet",
        "Jajan",
        "Berlangganan aplikasi"
    ]

    hari = [
        "Senin", "Selasa", "Rabu", "Kamis",
        "Jumat", "Sabtu", "Minggu"
    ]

    n = len(v)
    days = 7

    ratio = v / w

    # Mengurutkan kebutuhan dari rasio terbesar
    urutan = np.argsort(-ratio, kind="stable")

    x = np.zeros((n, days), dtype=int)

    for j in range(days):

        # Makan siang dan makan malam wajib setiap hari
        x[1, j] = 1
        x[2, j] = 1

        # Transportasi wajib Senin sampai Jumat
        if j < 5:
            x[3, j] = 1

        # Makan pagi wajib hari Senin
        if j == 0:
            x[0, j] = 1

    # Internet dan jajan minimal satu kali seminggu
    # Dialokasikan terlebih dahulu pada hari Sabtu
    x[5, 5] = 1
    x[6, 5] = 1

    for j in range(days):

        # Menghitung total biaya kebutuhan wajib
        total_harga = np.sum(w * x[:, j])

        # Memilih kebutuhan berdasarkan rasio terbesar
        for i in urutan:

            # Jika kebutuhan sudah dipilih, lanjut
            if x[i, j] == 1:
                continue

            # Memeriksa batas anggaran harian
            if total_harga + w[i] <= u:

                x[i, j] = 1
                total_harga += w[i]

    total_utility = 0
    total_harga_mingguan = 0

    print("HASIL GREEDY STRATEGY 3")
    print("Utility / Weight Ratio Terbesar")
    print("==========================================")

    for j in range(days):

        total_harga = sum(w[i] * x[i, j] for i in range(n))
        utility = sum(v[i] * x[i, j] for i in range(n))
        sisa_uang = u - total_harga

        print("\nHari:", hari[j])
        print("------------------------------------------")

        for i in range(n):
            if x[i, j] == 1:
                print(
                    nama[i],
                    ": Rp%.0f | Utility: %d" % (w[i], v[i])
                )

        print("------------------------------------------")
        print("Total Utility:", utility)
        print("Total Harga: Rp%.0f" % total_harga)
        print("Sisa Uang Saku: Rp%.0f" % sisa_uang)

        total_utility += utility
        total_harga_mingguan += total_harga

    print("\n==========================================")
    print("TOTAL HASIL MINGGUAN")
    print("==========================================")

    print("Total Utility:", total_utility)
    print("Total Harga: Rp%.0f" % total_harga_mingguan)
    print("Total Anggaran: Rp%.0f" % (u * days))
    print(
        "Sisa Uang Saku: Rp%.0f"
        % (u * days - total_harga_mingguan)
    )

    print("\nPemeriksaan Constraint:")
    print("Internet minimal 1 kali:",
          "Terpenuhi" if sum(x[5, :]) >= 1 else "Tidak Terpenuhi")
    print("Jajan minimal 1 kali:",
          "Terpenuhi" if sum(x[6, :]) >= 1 else "Tidak Terpenuhi")
    print("Anggaran setiap hari:",
          "Terpenuhi" if np.all(
              np.sum(w[:, None] * x, axis=0) <= u
          ) else "Tidak Terpenuhi")

    print("\nNilai Variabel Keputusan:")
    for i in range(n):
        for j in range(days):
            print("x[%d,%d] =" % (i+1, j+1), x[i, j])

except AttributeError:
    print("Encountered an attribute error")

