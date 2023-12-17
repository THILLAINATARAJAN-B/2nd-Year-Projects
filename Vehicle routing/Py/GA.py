from random import random, randint

class GA:
    def _init_(
        self,
        pool,
        depot,
        crossover_rate=0,
        mutation_rate=0,
        population_size=1,
        generation_size=0,
        elitism=True
    ):
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.population_size = population_size
        self.generation_size = generation_size
        self.pool = pool
        self.depot = depot
        self.elitism = elitism
        self.current_generation = []
        self.next_generation = []

    def go(self):
        self.create_population()
        self.rank_population()
        for i in range(self.generation_size):
            print(f"{(i / self.generation_size) * 100}%")
            self.create_next_generation()
            self.rank_population()
        return self.current_generation
    def create_population(self):
        for _ in range(self.population_size):
            c = Chromosome(self.pool, self.depot, self.mutation_rate)
            self.current_generation.append(c)

    def rank_population(self):
        self.total_fitness = 0
        for chromosome in self.current_generation:
            self.total_fitness += chromosome.calc_fitness()
        self.current_generation.sort(key=lambda x: x.fitness)

    def create_next_generation(self):
        self.next_generation = []
        if self.elitism:
            self.next_generation.append(self.current_generation[self.population_size - 1])
        for i in range(0, self.population_size - 1, 2):
            child1, child2 = None, None
            parent1 = self.roulette_selection()
            parent2 = self.roulette_selection()
            if random() < self.crossover_rate:
                offspring1, offspring2 = parent1.crossover(parent2)
                child1, child2 = offspring1, offspring2
            else:
                child1, child2 = parent1, parent2
            child1.mutate()
            child2.mutate()

            self.next_generation.extend([child1, child2])
        self.current_generation = self.next_generation.copy()

    def roulette_selection(self):
        random_fitness = random() * self.total_fitness
        increasing_fitness = 0
        for i in range(self.population_size):
            increasing_fitness += self.current_generation[i].fitness
            if increasing_fitness >= random_fitness:
                return self.current_generation[i]
        return self.current_generation[self.population_size - 1]