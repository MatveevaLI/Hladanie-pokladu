import random

start_row = 0
start_col = 0

row_map = 0
col_map = 0

treasure_list = []

individual_count = 100
memory_cell_count = 64
generation_count = 1000

best_indivuals = []


class Generation:

    def __init__(self):
        self.individuals = []

    def add_individual(self, indiv):
        self.individuals.append(indiv)


class Individual:
    def __init__(self):
        self.fitness_value = 0
        self.memory_cells = []
        self.path = []
        self.found_treasures = []
        self.path_final = []


def create_first_generation():
    first_generation = Generation()
    for i in range(individual_count):
        indiv = Individual()
        first_generation.add_individual(indiv)

        for j in range(memory_cell_count):
            if j <= 32:
                indiv.memory_cells.append(random.randint(0, 255))
            else:
                indiv.memory_cells.append(0)

    return first_generation


def virtual_machine(generation):
    for individual in generation.individuals:
        copy_memory_cells = individual.memory_cells.copy()

        counter = 0

        # aktualna bunka
        memory_cell_index = 0

        while (memory_cell_index >= 0 and memory_cell_index < 64 and counter < 500):

            operator = (bin(copy_memory_cells[memory_cell_index])[2:].zfill(8)[:2])
            address = int((bin(copy_memory_cells[memory_cell_index])[2:].zfill(8)[2:]), 2)

            memory_cell_index += 1
            counter += 1

            # incrementation
            if operator == "00":
                copy_memory_cells[address] += 1
                if copy_memory_cells[address] == 256:
                    copy_memory_cells[address] = 0

            # decrimentation
            if operator == "01":
                copy_memory_cells[address] -= 1
                if copy_memory_cells[address] == -1:
                    copy_memory_cells[address] = 255

            # jump
            if operator == "10":
                memory_cell_index = address

            # print
            if operator == "11":

                direction = bin(copy_memory_cells[address])[2:].zfill(8)[6:]

                # left
                if direction == "10":
                    individual.path.append("L")

                # right
                if direction == "11":
                    individual.path.append("R")

                # up
                if direction == "00":
                    individual.path.append("U")

                # down
                if direction == "01":
                    individual.path.append("D")

        cur_pos_row = start_row
        cur_pos_col = start_col

        for i in range(len(individual.path)):
            if individual.path[i] == "L":
                cur_pos_col -= 1
            if individual.path[i] == "R":
                cur_pos_col += 1
            if individual.path[i] == "U":
                cur_pos_row -= 1
            if individual.path[i] == "D":
                cur_pos_row += 1

            # kontrola presiahnutia hranic mapy
            if cur_pos_row <= row_map and cur_pos_row > 0 and cur_pos_col <= col_map and cur_pos_col > 0:
                individual.path_final.append(individual.path[i])
            else:
                break

            # kontrola ci je na danej bunke poklad
            for treasure in treasure_list:
                if cur_pos_row == treasure[0] and cur_pos_col == treasure[1]:
                    if treasure not in individual.found_treasures:
                        individual.found_treasures.append(treasure)

            if len(individual.found_treasures) == len(treasure_list):
                break

        fitness(individual)


def fitness(individual):
    if len(individual.path_final) == 0:
        individual.fitness_value = 0
        return

    step_count = len(individual.path_final)

    individual.fitness_value = len(individual.found_treasures) + (1 - (step_count * 0.001))


def ranking_selection(generation):
    count_indiv = 2
    selected = []
    selected_first_group = [[] for i in range(2)]
    selected_second_group = [[] for i in range(2)]

    iteration = int(individual_count * 10 / 100)
    for k in range(int(iteration / 2)):
        for j in range(count_indiv):
            random_indiv_index = random.randint(0, individual_count - 1)
            selected_first_group[j].append(generation.individuals[random_indiv_index])
            selected_first_group[j].append(random_indiv_index)
        for m in range(count_indiv):
            random_indiv_index = random.randint(0, individual_count - 1)
            selected_second_group[m].append(generation.individuals[random_indiv_index])
            selected_second_group[m].append(random_indiv_index)

        if selected_first_group[0][0].fitness_value > selected_first_group[1][0].fitness_value:
            selected.append(selected_first_group[0][1])
        else:
            selected.append(selected_first_group[1][1])

        if selected_second_group[0][0].fitness_value > selected_second_group[1][0].fitness_value:
            selected.append(selected_second_group[0][1])
        else:
            selected.append(selected_second_group[1][1])

        selected_first_group = [[] for i in range(2)]
        selected_second_group = [[] for i in range(2)]

    return selected


def roulette_wheel_selection(generation):
    selected = []
    sum_of_fitness = 0
    previous_probability = 0.0

    for indiv in range(len(generation.individuals)):
        sum_of_fitness += generation.individuals[indiv].fitness_value

    if sum_of_fitness == 0:
        return

    roulette = []

    individual_sorted = {}
    for i in range(len(generation.individuals)):
        individual_sorted[generation.individuals[i].fitness_value] = i

    individual_sorted_invrn = {y: x for x, y in individual_sorted.items()}
    individual_sorted_invrn = sorted(individual_sorted_invrn.items(), key=lambda item: item[1])

    for indiv in range(len(individual_sorted_invrn)):
        roulette.append(previous_probability + (individual_sorted_invrn[indiv][1] / sum_of_fitness))
        previous_probability = previous_probability + (individual_sorted_invrn[indiv][1] / sum_of_fitness)

    iteration = int(len(individual_sorted_invrn) * 10 / 100)

    for i in range(iteration):
        random_number = random.uniform(0, 1)

        counter = 0

        for j in roulette:
            counter += 1
            if random_number < j:
                selected.append(individual_sorted_invrn[counter - 1][0])
                break

            if j == roulette[-1]:
                selected.append(individual_sorted_invrn[counter - 1][0])

    return selected


def load_map():
    global start_row
    global start_col

    global row_map
    global col_map

    file = open("map.txt", "r")
    coord = []
    for line in file:
        coord = line.split()

        if row_map == 0:
            row_map = int(coord[0])
            col_map = int(coord[1])
            coord.clear()
            continue

        if start_row == 0:
            start_row = int(coord[0])
            start_col = int(coord[1])
            coord.clear()
            continue

        else:
            treasure_list.append([int(coord[0]), int(coord[1])])
            coord.clear()


def crossover(parent_one, parent_two):
    crossing_point = random.randint(1, 64)
    memory_cells = []

    for i in range(memory_cell_count):
        if i < crossing_point:
            memory_cells.append(parent_one.memory_cells[i])
        else:
            memory_cells.append(parent_two.memory_cells[i])

    return memory_cells


def mutation(memory_cells):
    chance = random.random()

    if chance < 0.4:
        index_random = random.randint(0, memory_cell_count - 1)
        value_random = random.randint(0, 255)

        memory_cells[index_random] = value_random

    return memory_cells


def create_new_generation(generation):
    new_generation = Generation()

    # ruleta
    selected_individuals = roulette_wheel_selection(generation)

    # turnaj
    # selected_individuals = ranking_selection(generation)

    for m in range(len(selected_individuals)):
        indiv = Individual()
        new_generation.add_individual(indiv)

        for j in range(len(generation.individuals[selected_individuals[m]].memory_cells)):
            indiv.memory_cells.append(generation.individuals[selected_individuals[m]].memory_cells[j])

    individual_fitness = {}

    for r in range(len(generation.individuals)):
        individual_fitness[r] = generation.individuals[r].fitness_value

    count = len(new_generation.individuals)

    while count < individual_count:
        parent_one_index = random.randint(0, len(individual_fitness) - 1)
        parent_two_index = random.randint(0, len(individual_fitness) - 1)

        parent_one = generation.individuals[[parent_one_index][0]]
        parent_two = generation.individuals[[parent_two_index][0]]

        memory_cells = crossover(parent_one, parent_two)
        memory_cells = mutation(memory_cells)

        indiv = Individual()
        new_generation.add_individual(indiv)

        for j in range(len(memory_cells)):
            indiv.memory_cells.append(memory_cells[j])

        count += 1

    return new_generation


def print_data_generation(number_generation, best_indiv, fitness_avr):
    print("\nGeneration ", str(number_generation))
    print("\tFitness: {:.4f}".format(best_indiv[number_generation].fitness_value))
    print("\tFound treasures:", len(best_indiv[number_generation].found_treasures))
    print("\tPath length: ", len(best_indiv[number_generation].path_final))
    print("\n\tFitness average: {:.4f}".format(fitness_avr[number_generation]))


load_map()
generation = create_first_generation()

fitness_value_list = []

for i in range(generation_count):

    virtual_machine(generation)

    fitness_avr = 0
    path_avr = 0

    for f in range(individual_count):
        fitness_avr += generation.individuals[f].fitness_value
    fitness_avr /= individual_count
    fitness_value_list.append(fitness_avr)

    # najdenie najlepsieho
    individual_sorted = {}
    for r in range(len(generation.individuals)):
        individual_sorted[generation.individuals[r].fitness_value] = r

    individual_sorted_invrn = {y: x for x, y in individual_sorted.items()}
    individual_sorted_invrn = sorted(individual_sorted_invrn.items(), reverse=True, key=lambda item: item[1])
    best_one = generation.individuals[individual_sorted_invrn[0][0]]
    best_indivuals.append(best_one)

    # najdene vsetky poklady alebo posledna generacia
    if len(best_indivuals[i].found_treasures) == len(treasure_list) or i == generation_count:
        print_data_generation(i, best_indivuals, fitness_value_list)
        if len(best_indivuals[i].found_treasures):
            print("\n\tFitness: {:.4f}".format(best_indivuals[i].fitness_value))
            print("\tFound treasures: ", best_indivuals[i].found_treasures)
            print("\tPath length: ", len(best_indivuals[i].path_final))
            print("\tPath: ", best_indivuals[i].path_final)
            print("Found all treasures")
        break

    print_data_generation(i, best_indivuals, fitness_value_list)

    # vytvorenie novej generacie
    new_generation = create_new_generation(generation)
    generation = new_generation
