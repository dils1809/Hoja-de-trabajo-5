import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

RANDOM_SEED = 42
NUM_PROCESSES = [25, 50, 100, 150, 200]
INTERVALS = [10, 5, 1]
MEMORIES = [100, 200]
INSTRUCTION_TIME = 3
CPU_SPEED = 1  
WAITING_IO_PROBABILITY = 1 / 21

class Process:
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.memory_required = random.randint(1, 10)
        self.instructions_remaining = random.randint(1, 10)
        self.waiting_io = False
        self.arrival_time = env.now
        self.waiting_time = 0

    def run(self, cpu):
        while self.instructions_remaining > 0:
            with cpu.request() as req:
                yield req
                yield self.env.timeout(INSTRUCTION_TIME / CPU_SPEED)
                self.instructions_remaining -= min(INSTRUCTION_TIME, self.instructions_remaining)
                if random.random() < WAITING_IO_PROBABILITY:
                    self.waiting_io = True
                    self.waiting_time = self.env.now
                    yield self.env.timeout(random.randint(1, 21))
                    self.waiting_io = False
                    self.waiting_time = self.env.now - self.waiting_time

def process_generator(env, cpu, ram):
    process_id = 0
    while True:
        interval = random.expovariate(1.0 / INTERVALS)
        yield env.timeout(interval)
        process_id += 1
        process = Process(env, process_id)
        env.process(process.run(cpu))

def simulation(env, num_processes, memory_capacity, cpu_speed):
    random.seed(RANDOM_SEED)
    cpu = simpy.Resource(env, capacity=1)
    ram = simpy.Container(env, init=memory_capacity, capacity=memory_capacity)
    env.process(process_generator(env, cpu, ram))
    env.run(until=num_processes)

    waiting_times = [process.waiting_time for process in Process if not process.waiting_io]
    io_waiting_times = [process.waiting_time for process in Process if process.waiting_io]

    average_waiting_time = np.mean(waiting_times)
    io_average_waiting_time = np.mean(io_waiting_times)

    return average_waiting_time, io_average_waiting_time

def main():
    results = {}

    for interval in INTERVALS:
        for memory in MEMORIES:
            for num_processes in NUM_PROCESSES:
                env = simpy.Environment()
                average_waiting_time, io_average_waiting_time = simulation(env, num_processes, memory, CPU_SPEED)
                results[(interval, memory, num_processes)] = (average_waiting_time, io_average_waiting_time)

    # Plotting results
    for interval in INTERVALS:
        for memory in MEMORIES:
            average_waiting_times = [results[(interval, memory, num_processes)][0] for num_processes in NUM_PROCESSES]
            plt.plot(NUM_PROCESSES, average_waiting_times, label=f'Memory: {memory}, Interval: {interval}')

    plt.xlabel('Number of Processes')
    plt.ylabel('Average Waiting Time')
    plt.title('Average Waiting Time vs Number of Processes')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()