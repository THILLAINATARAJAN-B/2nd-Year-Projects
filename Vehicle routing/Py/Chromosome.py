class Chromosome:
    def _init_(self, pool=None, depot=None, mutation_rate=0, genes=None):
        self.pool = pool or []
        self.depot = depot
        self.genes = genes or []
        self.length = len(genes) if genes else len(pool)
        self.mutation_rate = mutation_rate
        self.fitness = 0
        if not genes:
            self.create_genes()

    def create_genes(self):
        self.genes.append(self.depot)
        for i in range(self.length):
            random_location = self.pool[i]
            existing = next((gene for gene in self.genes if gene['id'] == random_location['id']), None)

            if existing:
                i -= 1
                continue

            self.genes.append(random_location)

        self.genes.append(self.depot)
        self.length = len(self.genes)

    def calc_fitness(self):
        for i in range(1, self.length):
            distance = ((self.genes[i - 1]['x'] - self.genes[i]['x']) ** 2 +
                        (self.genes[i - 1]['y'] - self.genes[i]['y']) * 2) * 0.5
            self.fitness += distance

        self.fitness = 1 / self.fitness
        return self.fitness

    def crossover(self, chromosome):
        pos = randint(1, self.length - 1)
        off_spr2_genes = []
        off_spr1_genes = (
            self.genes[1:pos]
            + chromosome.genes[pos:chromosome.length - 1]
            + self.genes[pos:self.length - 1]
            + chromosome.genes[1:pos]
        )

        for i in range(len(off_spr1_genes) - 1):
            for j in range(i + 1, len(off_spr1_genes)):
                if off_spr1_genes[i]['id'] == off_spr1_genes[j]['id']:
                    off_spr2_genes.append(off_spr1_genes.pop(j))
                    break

            if len(off_spr2_genes) >= len(off_spr1_genes):
                break

        offspring1 = Chromosome(
            None, self.depot, self.mutation_rate, [self.depot, *off_spr1_genes, self.depot]
        )
        offspring2 = Chromosome(
            None, self.depot, self.mutation_rate, [self.depot, *off_spr2_genes, self.depot]
        )

        return {'offspring1': offspring1._dict, 'offspring2': offspring2.dict_}

    def mutate(self):
        for i in range(1, self.length - 1):
            if random() < self.mutation_rate:
                random_idx = randint(1, self.length - 1)
                self.genes[random_idx], self.genes[i] = (
                    self.genes[i],
                    self.genes[random_idx],
                )
        return self._dict_
