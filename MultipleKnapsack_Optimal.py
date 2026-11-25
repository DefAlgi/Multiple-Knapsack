import gurobipy as gp
import numpy as np
from gurobipy import GRB

'''
# Model matematika:
# Mencari maksimum total utility kebutuhan mahasiswa
# selama satu minggu menggunakan Multiple Knapsack Problem.

# Subject to (s.t.)
# w = biaya setiap kebutuhan
# v = utility setiap kebutuhan
# u = kapasitas uang saku setiap hari
# xij = {0, 1}
#      1 jika kebutuhan i dipilih pada hari j
#      0 jika kebutuhan i tidak dipilih pada hari j
#
# Terdapat 8 jenis kebutuhan dan 7 knapsack (Senin-Minggu).
#
# Ketentuan:
# 1. Makan siang wajib setiap hari.
# 2. Makan malam wajib setiap hari.
# 3. Transportasi wajib Senin-Jumat.
# 4. Makan pagi wajib hari Senin.
# 5. Internet wajib minimal 1 kali seminggu.
# 6. Jajan wajib minimal 1 kali seminggu.
# 7. Kapasitas uang saku per hari Rp65.000.
# 8. Untuk sisa uang tidak digunakan keesokan harinya.
'''

try:
    # Create a new model
    model = gp.Model("MultipleKnapsackMahasiswa")

    # Dataset
    w = np.array([10000, 15000, 15000, 17000, 6000, 5000, 15000, 13000])

    v = np.array([4, 10, 7, 10, 3, 8, 5, 4])

    # Capacity setiap hari (Senin-Minggu)
    u = np.array([65000, 65000, 65000, 65000, 65000, 65000, 65000])

    n = len(w)       # Jumlah kebutuhan
    m = len(u)       # Jumlah knapsack / hari

    hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

    kebutuhan = ["Makan Pagi", "Makan Siang", "Makan Malam", "Transportasi", "Akademik", "Internet", "Jajan", "Langganan Aplikasi"]

    # Define binary decision variables
    x = model.addVars(n, m, vtype=GRB.BINARY, name="x")

    # Capacity constraints
    for j in range(m):
        model.addConstr(gp.quicksum(w[i] * x[i, j] for i in range(n)) <= u[j], name=f"Capacity_{hari[j]}")

    # makan siang setiap hari
    for j in range(m):
        model.addConstr(x[1, j] == 1)

    # makan malam setiap hari
    for j in range(m):
        model.addConstr(x[2, j] == 1)

    # Transportasi setiap senin-jumat
    for j in range(5):
        model.addConstr(x[3, j] == 1)

    # makan pagi wajib setiap senin
    model.addConstr(x[0, 0] == 1)

    # Internet harus dipilih minimal sekali dalam 1 minggu
    model.addConstr(gp.quicksum(x[5, j] for j in range(m)) >= 1)

    # Jajan harus dipilih minimal sekali dalam 1 minggu
    model.addConstr(gp.quicksum(x[6, j] for j in range(m)) >= 1)

    # Objective: Maximize total utility
    model.setObjective(gp.quicksum(v[i] * x[i, j] for i in range(n) for j in range(m)), GRB.MAXIMIZE)

    # Solver
    model.optimize()

    # Interpretation of optimization results
    if model.status == GRB.OPTIMAL:

        print("\n===== HASIL OPTIMASI MULTIPLE KNAPSACK =====")
        print("Status: OPTIMAL")
        print("Total Utility Maksimum: %g" % model.ObjVal)

        total_pengeluaran = 0

        for j in range(m):

            print("\n--- %s ---" % hari[j])

            pengeluaran_harian = 0
            utility_harian = 0

            for i in range(n):
                if x[i, j].X > 0.5:
                    print("%s | Biaya: Rp%s | Utility: %g" %(kebutuhan[i], format(w[i], ",").replace(",", "."), v[i]))

                    pengeluaran_harian += w[i]
                    utility_harian += v[i]

            sisa_anggaran = u[j] - pengeluaran_harian
            total_pengeluaran += pengeluaran_harian

            print("Total Biaya: Rp%s" % format(pengeluaran_harian, ",").replace(",", "."))

            print("Total Utility: %g" % utility_harian)

            print("Sisa Uang Saku: Rp%s" % format(sisa_anggaran, ",").replace(",", "."))

        print("\n===== RINGKASAN MINGGUAN =====")
        print("Total Pengeluaran: Rp%s" % format(total_pengeluaran, ",").replace(",", "."))

        print("Total Kapasitas: Rp%s" % format(sum(u), ",").replace(",", "."))

        print("Total Utility Maksimum: %g" % model.ObjVal)

        print("\nVariabel Keputusan:")
        for j in range(m):
            for i in range(n):
                print("x[%d,%d] = %g" % (i+1, j+1, x[i, j].X))

    else:
        print("Optimization ended with status %d" % model.status)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')