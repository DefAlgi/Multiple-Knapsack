import numpy as np
from gurobipy import GRB
import time

'''
# Model matematika:
# Mencari maksimum total utility kebutuhan mahasiswa
# selama satu minggu menggunakan Particle Swarm Optimization (PSO).
#
# Strategy: Priority-Based
#
# w = biaya setiap kebutuhan
# v = utility setiap kebutuhan
# u = kapasitas uang saku setiap hari
#
# xij = {0, 1}
#      1 jika kebutuhan i dipilih pada hari j
#      0 jika kebutuhan i tidak dipilih pada hari j
#
# Priority:
# Partikel menghasilkan nilai prioritas untuk setiap kebutuhan.
# Kebutuhan dengan prioritas tertinggi akan dipilih terlebih dahulu
# selama biaya tidak melebihi kapasitas knapsack.
#
# Ketentuan:
# 1. Makan siang wajib setiap hari.
# 2. Makan malam wajib setiap hari.
# 3. Transportasi wajib Senin-Jumat.
# 4. Makan pagi wajib hari Senin.
# 5. Internet wajib minimal 1 kali seminggu.
# 6. Jajan wajib minimal 1 kali seminggu.
# 7. Kapasitas uang saku setiap hari Rp65.000.
#
# Persamaan PSO:
# vij(t) = w * vij(t-1)
#          + c1*r1*(pbest - pij(t-1))
#          + c2*r2*(gbest - pij(t-1))
#
# pij(t) = pij(t-1) + vij(t)
'''

try:
    # Dataset
    w = np.array([10000, 15000, 15000, 17000, 6000, 5000, 15000, 13000])

    v = np.array([4, 10, 7, 10, 3, 8, 5, 4])

    # Capacity setiap hari
    u = np.array([65000, 65000, 65000, 65000, 65000, 65000, 65000])

    n = len(w)
    m = len(u)

    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

    needs = ["Makan Pagi", "Makan Siang", "Makan Malam", "Transportasi", "Akademik", "Internet", "Jajan", "Langganan Aplikasi"]

    # Parameter PSO
    num_particles = 50
    max_iter = 500

    inertia = 0.7
    c1 = 1.5
    c2 = 1.5

    # Random seed
    np.random.seed(42)

    # Initialize particle position and velocity
    position = np.random.uniform(0, 1, (num_particles, n, m))
    velocity = np.random.uniform(-0.1, 0.1, (num_particles, n, m))

    # Priority-based decoding
    def decode_priority(priority):
        x = np.zeros((n, m), dtype=int)

        # Mandatory needs
        for j in range(m):

            # Lunch and dinner every day
            x[1, j] = 1
            x[2, j] = 1

            # Transportation Monday-Friday
            if j < 5:
                x[3, j] = 1

            # Breakfast Monday
            if j == 0:
                x[0, j] = 1

        # Weekly mandatory needs:
        # Internet on Monday
        x[5, 0] = 1

        # Snack on Sunday
        x[6, 6] = 1

        # Fill each daily knapsack based on priority
        for j in range(m):
            current_cost = np.sum(w * x[:, j])
            remaining_items = [i for i in range(n) if x[i, j] == 0]

            # Sort needs from highest to lowest priority
            sorted_items = sorted(remaining_items, key=lambda i: priority[i, j], reverse=True)

            for i in sorted_items:
                if current_cost + w[i] <= u[j]:
                    x[i, j] = 1
                    current_cost += w[i]

        return x

    # Fitness function
    def fitness_function(priority):
        solution = decode_priority(priority)
        total_utility = np.sum(v[:, np.newaxis] * solution)

        return total_utility

    # Initialize personal best
    pbest_position = position.copy()

    pbest_fitness = np.array([
        fitness_function(position[i])
        for i in range(num_particles)
    ])

    # Initialize global best
    best_index = np.argmax(pbest_fitness)

    gbest_position = pbest_position[best_index].copy()
    gbest_fitness = pbest_fitness[best_index]

    # PSO iteration
    start_time = time.time()

    for iteration in range(max_iter):

        for i in range(num_particles):

            r1 = np.random.random((n, m))
            r2 = np.random.random((n, m))

            # Update velocity
            velocity[i] = (inertia * velocity[i] + c1 * r1 * (pbest_position[i] - position[i]) + c2 * r2 * (gbest_position - position[i]))

            # Limit velocity
            velocity[i] = np.clip(velocity[i], -1, 1)

            # Update position
            position[i] = position[i] + velocity[i]

            # Priority value range
            position[i] = np.clip(position[i], 0, 1)

            # Calculate fitness
            current_fitness = fitness_function(position[i])

            # Update personal best
            if current_fitness > pbest_fitness[i]:

                pbest_fitness[i] = current_fitness
                pbest_position[i] = position[i].copy()

            # Update global best
            if current_fitness > gbest_fitness:

                gbest_fitness = current_fitness
                gbest_position = position[i].copy()

        print("Iteration %d | Best Utility: %g" % (iteration + 1, gbest_fitness))

    end_time = time.time()
    execution_time = end_time - start_time

    # Decode final solution
    best_solution = decode_priority(gbest_position)

    # Interpretation of optimization results
    print("\n===== HASIL OPTIMASI PSO PRIORITY =====")

    print("Best Total Utility: %g" % gbest_fitness)

    total_cost = 0

    for j in range(m):

        print("\n--- %s ---" % days[j])

        daily_cost = 0
        daily_utility = 0

        for i in range(n):

            if best_solution[i, j] == 1:

                print("%s | Biaya: Rp%s | Utility: %g" % (needs[i], format(w[i], ",").replace(",", "."), v[i]))

                daily_cost += w[i]
                daily_utility += v[i]

        remaining = u[j] - daily_cost
        total_cost += daily_cost

        print("Total Biaya: Rp%s" % format(daily_cost, ",").replace(",", "."))

        print("Total Utility: %g" % daily_utility)

        print("Sisa Uang Saku: Rp%s" % format(remaining, ",").replace(",", "."))

    print("\n===== RINGKASAN MINGGUAN =====")

    print("Total Pengeluaran: Rp%s" % format(total_cost, ",").replace(",", "."))

    print("Total Kapasitas: Rp%s" % format(np.sum(u), ",").replace(",", "."))

    print("Total Utility: %g" % gbest_fitness)

    print("Execution Time: %.4f seconds" % execution_time)

    print("\nVariabel Keputusan:")

    for j in range(m):
        for i in range(n):
            print("x[%d,%d] = %d" % (i+1, j+1, best_solution[i, j]))

except Exception as e:
    print("Error:", str(e))
