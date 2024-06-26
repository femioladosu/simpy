

import simpy
import random

# Define task states
STATE_READY = "READY"
STATE_RUNNING = "RUNNING"
STATE_WAITING = "WAITING"
STATE_FINISHED = "FINISHED"
STATE_TERMINATED = "TERMINATED"
STATE_MERGE = "MERGE"

# Define the time slice for the new scheduling model
TIME_SLICE = 5

# Global variable to track the number of completed gangs
completed_gangs = 0

class GangScheduler:
    def __init__(self, env, cpu_capacity):
        self.env = env
        self.cpu_capacity = cpu_capacity
        self.cpu = simpy.Resource(env, capacity=cpu_capacity)
        self.ready_queue = simpy.Store(env)  # Queue for ready tasks
        self.gangs = {}  # Track gangs and their tasks
        self.tasks = {}  # Track all tasks and their states
        self.processor_time_slices = [TIME_SLICE] * cpu_capacity  # Track time slices for each processor
        self.merge_state = {}  # Track merge state for preempted tasks

    def task(self, name, bursts, gang_id, processor_id):
        """A task process that performs CPU and I/O operations with state management."""
        global completed_gangs
        state = STATE_READY
        while bursts:
            burst_type, duration = bursts[0]
            if burst_type == 'CPU':
                time_slice = min(self.processor_time_slices[processor_id], duration)
                state = STATE_RUNNING
                print(f'{self.env.now}: {name} state: {state} - requesting CPU for {time_slice} time units on processor {processor_id}')
                with self.cpu.request() as req:
                    yield req
                    print(f'{self.env.now}: {name} state: {state} - got CPU on processor {processor_id}')
                    yield self.env.timeout(time_slice)
                    duration -= time_slice
                    self.processor_time_slices[processor_id] -= time_slice
                    if duration > 0 and len(bursts) > 0:
                        bursts[0] = (burst_type, duration)
                        state = STATE_READY
                        print(f'{self.env.now}: {name} state: {state} - preempted with {duration} time units remaining on processor {processor_id}')
                        self.ready_queue.put((name, bursts, gang_id, processor_id))  # Put back to ready queue if not finished
                    elif len(bursts) > 0:
                        bursts.pop(0)
                        state = STATE_WAITING
                        print(f'{self.env.now}: {name} state: {state} - finished CPU burst on processor {processor_id}')
            else:
                state = STATE_WAITING
                print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units and processor time slice  {self.processor_time_slices[processor_id]}')
                if duration > self.processor_time_slices[processor_id]:
                    state = STATE_MERGE
                    print(f'{self.env.now}: {name} state: {state} - I/O burst longer than remaining time slice, moving to MERGE state')
                    if gang_id not in self.merge_state:
                        self.merge_state[gang_id] = []
                    self.merge_state[gang_id].append((name, bursts, gang_id, processor_id))
                    if len(self.merge_state[gang_id]) == len(self.gangs[gang_id]):
                        print(f'{self.env.now}: All tasks in gang {gang_id} are in MERGE state, moving to READY state')
                        for task in self.merge_state[gang_id]:
                            self.ready_queue.put(task)
                        del self.merge_state[gang_id]
                else:
                    yield self.env.timeout(duration)
                    bursts.pop(0)
                    state = STATE_READY
                    print(f'{self.env.now}: {name} state: {state} - finished I/O burst')

        state = STATE_FINISHED
        print(f'{self.env.now}: {name} state: {state} - task completed')
        if gang_id in self.gangs:
            if name in self.gangs[gang_id]:
                self.gangs[gang_id].remove(name)
                if not self.gangs[gang_id]:  # All tasks in the gang are finished
                    print(f'{self.env.now}: Gang {gang_id} state: {STATE_TERMINATED} - all tasks completed')
                    del self.gangs[gang_id]  # Remove the gang
                    completed_gangs += 1  # Increment the global counter for completed gangs
            else:
                print(f'{self.env.now}: Error - {name} not found in gang {gang_id} tasks')
        else:
            print(f'{self.env.now}: Error - Gang {gang_id} not found')

    def create_gang(self, gang_id, inter_arrival_time, num_tasks, tasks_bursts):
        """Function to create and process a gang of tasks."""
        yield self.env.timeout(inter_arrival_time)  # Simulate the arrival of the gang
        print(f"Gang {gang_id} arrived at {self.env.now}")
        print(f"Gang {gang_id} processes and their bursts:")

        self.gangs[gang_id] = []
        self.merge_state[gang_id] = []  # Initialize merge state for the gang
        for task_id, bursts in enumerate(tasks_bursts, start=1):
            task_name = f"Gang{gang_id}-Task{task_id}"
            self.gangs[gang_id].append(task_name)
            print(f"  {task_name}: {bursts}")
            # Assign a processor ID for the initial placement (e.g., -1 for initial assignment)
            self.ready_queue.put((task_name, bursts, gang_id, -1))  # Add task to ready queue
            self.tasks[task_name] = bursts  # Track task

        print(f"Gang {gang_id}")

def setup_environment(env, num_gangs, cpu_capacity):
    """Setup and run the simulation environment."""
    scheduler = GangScheduler(env, cpu_capacity)
    gang_creation_processes = []
    for i in range(num_gangs):
        num_tasks = random.randint(1, 3)  # Each gang has 1 to 3 tasks
        inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
        # Generate bursts for each task in the gang
        tasks_bursts = []
        for _ in range(num_tasks):
            # Random number of bursts for each task, each burst with a random length from 3 to 20
            bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
            tasks_bursts.append(bursts)
        
        gang_creation_processes.append(env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts)))

    env.process(time_tick_scheduler(env, scheduler, gang_creation_processes))

def time_tick_scheduler(env, scheduler, gang_creation_processes):
    """Scheduler to handle task execution at each time tick."""
    global completed_gangs
    # Wait for all gangs to be created
    yield simpy.events.AllOf(env, gang_creation_processes)
    
    total_gangs = len(scheduler.gangs)
    print(f'Total gangs created: {total_gangs}')
    
    while completed_gangs < total_gangs:  # Loop until all gangs are completed
        if scheduler.ready_queue.items:
            task_name, bursts, gang_id, processor_id = yield scheduler.ready_queue.get()
            # Find an available processor
            for processor_id in range(scheduler.cpu_capacity):
                if scheduler.processor_time_slices[processor_id] > 0:
                    print(f'{env.now}: Scheduling {task_name} on processor {processor_id}')
                    env.process(scheduler.task(task_name, bursts, gang_id, processor_id))
                    scheduler.processor_time_slices[processor_id] = TIME_SLICE  # Reset time slice for the processor
                    break

        print(f'{env.now}: Completed gangs: {completed_gangs}/{total_gangs}')
        yield env.timeout(1)  # Time tick

# Create a SimPy environment
env = simpy.Environment()
# Setup the environment with 4 gangs and 6 CPU cores
setup_environment(env, 4, 6)
# Run the simulation
env.run()






# import simpy
# import random

# # Define task states
# STATE_READY = "READY"
# STATE_RUNNING = "RUNNING"
# STATE_WAITING = "WAITING"
# STATE_FINISHED = "FINISHED"
# STATE_TERMINATED = "TERMINATED"
# STATE_MERGE = "MERGE"

# # Define the time slice for the new scheduling model
# TIME_SLICE = 5

# # Global variable to track the number of completed gangs
# completed_gangs = 0

# class GangScheduler:
#     def __init__(self, env, cpu_capacity):
#         self.env = env
#         self.cpu_capacity = cpu_capacity
#         self.cpu = simpy.Resource(env, capacity=cpu_capacity)
#         self.ready_queue = simpy.Store(env)  # Queue for ready tasks
#         self.gangs = {}  # Track gangs and their tasks
#         self.tasks = {}  # Track all tasks and their states
#         self.processor_time_slices = [TIME_SLICE] * cpu_capacity  # Track time slices for each processor
#         self.merge_state = {}  # Track merge state for preempted tasks

#     def task(self, name, bursts, gang_id, processor_id):
#         """A task process that performs CPU and I/O operations with state management."""
#         global completed_gangs
#         state = STATE_READY
#         while bursts:
#             burst_type, duration = bursts[0]
#             if burst_type == 'CPU':
#                 time_slice = min(self.processor_time_slices[processor_id], duration)
#                 state = STATE_RUNNING
#                 print(f'{self.env.now}: {name} state: {state} - requesting CPU for {time_slice} time units on processor {processor_id}')
#                 with self.cpu.request() as req:
#                     yield req
#                     print(f'{self.env.now}: {name} state: {state} - got CPU on processor {processor_id}')
#                     yield self.env.timeout(time_slice)
#                     duration -= time_slice
#                     self.processor_time_slices[processor_id] -= time_slice
#                     if duration > 0:
#                         bursts[0] = (burst_type, duration)
#                         state = STATE_READY
#                         print(f'{self.env.now}: {name} state: {state} - preempted with {duration} time units remaining on processor {processor_id}')
#                         self.ready_queue.put((name, bursts, gang_id, processor_id))  # Put back to ready queue if not finished
#                     else:
#                         bursts.pop(0)
#                         state = STATE_WAITING
#                         print(f'{self.env.now}: {name} state: {state} - finished CPU burst on processor {processor_id}')
#             else:
#                 state = STATE_WAITING
#                 print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units')
#                 if duration > self.processor_time_slices[processor_id]:
#                     state = STATE_MERGE
#                     print(f'{self.env.now}: {name} state: {state} - I/O burst longer than remaining time slice, moving to MERGE state')
#                     if gang_id not in self.merge_state:
#                         self.merge_state[gang_id] = []
#                     self.merge_state[gang_id].append((name, bursts, gang_id, processor_id))
#                     if len(self.merge_state[gang_id]) == len(self.gangs[gang_id]):
#                         print(f'{self.env.now}: All tasks in gang {gang_id} are in MERGE state, moving to READY state')
#                         for task in self.merge_state[gang_id]:
#                             self.ready_queue.put(task)
#                         del self.merge_state[gang_id]
#                 else:
#                     yield self.env.timeout(duration)
#                     if len(bursts) > 0:
#                         bursts.pop(0)
#                         state = STATE_READY
#                         print(f'{self.env.now}: {name} state: {state} - finished I/O burst')

#         state = STATE_FINISHED
#         print(f'{self.env.now}: {name} state: {state} - task completed')
#         if gang_id in self.gangs:
#             if name in self.gangs[gang_id]:
#                 self.gangs[gang_id].remove(name)
#                 if not self.gangs[gang_id]:  # All tasks in the gang are finished
#                     print(f'{self.env.now}: Gang {gang_id} state: {STATE_TERMINATED} - all tasks completed')
#                     del self.gangs[gang_id]  # Remove the gang
#                     completed_gangs += 1  # Increment the global counter for completed gangs
#             else:
#                 print(f'{self.env.now}: Error - {name} not found in gang {gang_id} tasks')
#         else:
#             print(f'{self.env.now}: Error - Gang {gang_id} not found')

#     def create_gang(self, gang_id, inter_arrival_time, num_tasks, tasks_bursts):
#         """Function to create and process a gang of tasks."""
#         yield self.env.timeout(inter_arrival_time)  # Simulate the arrival of the gang
#         print(f"Gang {gang_id} arrived at {self.env.now}")
#         print(f"Gang {gang_id} processes and their bursts:")

#         self.gangs[gang_id] = []
#         self.merge_state[gang_id] = []  # Initialize merge state for the gang
#         for task_id, bursts in enumerate(tasks_bursts, start=1):
#             task_name = f"Gang{gang_id}-Task{task_id}"
#             self.gangs[gang_id].append(task_name)
#             print(f"  {task_name}: {bursts}")
#             # Assign a processor ID for the initial placement (e.g., -1 for initial assignment)
#             self.ready_queue.put((task_name, bursts, gang_id, -1))  # Add task to ready queue
#             self.tasks[task_name] = bursts  # Track task

#         print(f"Gang {gang_id}")

# def setup_environment(env, num_gangs, cpu_capacity):
#     """Setup and run the simulation environment."""
#     scheduler = GangScheduler(env, cpu_capacity)
#     gang_creation_processes = []
#     for i in range(num_gangs):
#         num_tasks = random.randint(1, 3)  # Each gang has 1 to 3 tasks
#         inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
#         # Generate bursts for each task in the gang
#         tasks_bursts = []
#         for _ in range(num_tasks):
#             # Random number of bursts for each task, each burst with a random length from 3 to 20
#             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
#             tasks_bursts.append(bursts)
        
#         gang_creation_processes.append(env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts)))

#     env.process(time_tick_scheduler(env, scheduler, gang_creation_processes))

# def time_tick_scheduler(env, scheduler, gang_creation_processes):
#     """Scheduler to handle task execution at each time tick."""
#     global completed_gangs
#     # Wait for all gangs to be created
#     yield simpy.events.AllOf(env, gang_creation_processes)
    
#     total_gangs = len(scheduler.gangs)
#     print(f'Total gangs created: {total_gangs}')
    
#     while completed_gangs < total_gangs:  # Loop until all gangs are completed
#         if scheduler.ready_queue.items:
#             task_name, bursts, gang_id, processor_id = yield scheduler.ready_queue.get()
#             # Find an available processor
#             for processor_id in range(scheduler.cpu_capacity):
#                 if scheduler.processor_time_slices[processor_id] > 0:
#                     print(f'{env.now}: Scheduling {task_name} on processor {processor_id}')
#                     env.process(scheduler.task(task_name, bursts, gang_id, processor_id))
#                     scheduler.processor_time_slices[processor_id] = TIME_SLICE  # Reset time slice for the processor
#                     break

#         print(f'{env.now}: Completed gangs: {completed_gangs}/{total_gangs}')
#         yield env.timeout(1)  # Time tick

# # Create a SimPy environment
# env = simpy.Environment()
# # Setup the environment with 4 gangs and 6 CPU cores
# setup_environment(env, 4, 6)
# # Run the simulation
# env.run()







# import simpy
# import random

# # Define task states
# STATE_READY = "READY"
# STATE_RUNNING = "RUNNING"
# STATE_WAITING = "WAITING"
# STATE_FINISHED = "FINISHED"
# STATE_TERMINATED = "TERMINATED"

# # Define the time slice for round-robin scheduling
# TIME_SLICE = 5

# # Global variable to track the number of completed gangs
# completed_gangs = 0

# class GangScheduler:
#     def __init__(self, env, cpu_capacity):
#         self.env = env
#         self.cpu_capacity = cpu_capacity
#         self.cpu = simpy.Resource(env, capacity=cpu_capacity)
#         self.ready_queue = simpy.Store(env)  # Queue for ready tasks
#         self.gangs = {}  # Track gangs and their tasks
#         self.tasks = {}  # Track all tasks and their states

#     def task(self, name, bursts, gang_id):
#         """A task process that performs CPU and I/O operations with state management."""
#         global completed_gangs
#         state = STATE_READY
#         while bursts:
#             burst_type, duration = bursts[0]
#             if burst_type == 'CPU':
#                 time_slice = min(TIME_SLICE, duration)
#                 state = STATE_RUNNING
#                 print(f'{self.env.now}: {name} state: {state} - requesting CPU for {time_slice} time units')
#                 with self.cpu.request() as req:
#                     yield req
#                     print(f'{self.env.now}: {name} state: {state} - got CPU')
#                     yield self.env.timeout(time_slice)
#                     duration -= time_slice
#                     if duration > 0 and len(bursts) > 0:
#                         bursts[0] = (burst_type, duration)
#                         state = STATE_READY
#                         print(f'{self.env.now}: {name} state: {state} - preempted with {duration} time units remaining')
#                         self.ready_queue.put((name, bursts, gang_id))  # Put back to ready queue if not finished
#                     elif len(bursts) > 0:
#                         bursts.pop(0)
#                         state = STATE_WAITING
#                         print(f'{self.env.now}: {name} state: {state} - finished CPU burst')
#             else:
#                 state = STATE_WAITING
#                 print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units')
#                 yield self.env.timeout(duration)
#                 if len(bursts) > 0:
#                     bursts.pop(0)
#                     state = STATE_READY
#                     print(f'{self.env.now}: {name} state: {state} - finished I/O burst')

#         state = STATE_FINISHED
#         print(f'{self.env.now}: {name} state: {state} - task completed')
#         if gang_id in self.gangs:
#             if name in self.gangs[gang_id]:
#                 self.gangs[gang_id].remove(name)
#                 if not self.gangs[gang_id]:  # All tasks in the gang are finished
#                     print(f'{self.env.now}: Gang {gang_id} state: {STATE_TERMINATED} - all tasks completed')
#                     del self.gangs[gang_id]  # Remove the gang
#                     completed_gangs += 1  # Increment the global counter for completed gangs
#             else:
#                 print(f'{self.env.now}: Error - {name} not found in gang {gang_id} tasks')
#         else:
#             print(f'{self.env.now}: Error - Gang {gang_id} not found')

#     def create_gang(self, gang_id, inter_arrival_time, num_tasks, tasks_bursts):
#         """Function to create and process a gang of tasks."""
#         yield self.env.timeout(inter_arrival_time)  # Simulate the arrival of the gang
#         print(f"Gang {gang_id} arrived at {self.env.now}")
#         print(f"Gang {gang_id} processes and their bursts:")

#         self.gangs[gang_id] = []
#         for task_id, bursts in enumerate(tasks_bursts, start=1):
#             task_name = f"Gang{gang_id}-Task{task_id}"
#             self.gangs[gang_id].append(task_name)
#             print(f"  {task_name}: {bursts}")
#             self.ready_queue.put((task_name, bursts, gang_id))  # Add task to ready queue
#             self.tasks[task_name] = bursts  # Track task

#         print(f"Gang {gang_id}")

# def setup_environment(env, num_gangs, cpu_capacity):
#     """Setup and run the simulation environment."""
#     scheduler = GangScheduler(env, cpu_capacity)
#     gang_creation_processes = []
#     for i in range(num_gangs):
#         num_tasks = random.randint(1, 3)  # Each gang has 1 to 3 tasks
#         inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
#         # Generate bursts for each task in the gang
#         tasks_bursts = []
#         for _ in range(num_tasks):
#             # Random number of bursts for each task, each burst with a random length from 3 to 20
#             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
#             tasks_bursts.append(bursts)
        
#         gang_creation_processes.append(env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts)))

#     env.process(time_tick_scheduler(env, scheduler, gang_creation_processes))

# def time_tick_scheduler(env, scheduler, gang_creation_processes):
#     """Scheduler to handle task execution at each time tick."""
#     global completed_gangs
#     # Wait for all gangs to be created
#     yield simpy.events.AllOf(env, gang_creation_processes)
    
#     total_gangs = len(scheduler.gangs)
#     print(f'Total gangs created: {total_gangs}')
    
#     while completed_gangs < total_gangs:  # Loop until all gangs are completed
#         if scheduler.ready_queue.items:
#             task_name, bursts, gang_id = yield scheduler.ready_queue.get()
#             print(f'{env.now}: Scheduling {task_name}')
#             env.process(scheduler.task(task_name, bursts, gang_id))

#         print(f'{env.now}: Completed gangs: {completed_gangs}/{total_gangs}')
#         yield env.timeout(1)  # Time tick

# # Create a SimPy environment
# env = simpy.Environment()
# # Setup the environment with 4 gangs and 6 CPU cores
# setup_environment(env, 4, 6)
# # Run the simulation
# env.run()






# # import simpy
# # import random

# # # Define task states
# # STATE_READY = "READY"
# # STATE_RUNNING = "RUNNING"
# # STATE_WAITING = "WAITING"
# # STATE_FINISHED = "FINISHED"
# # STATE_TERMINATED = "TERMINATED"

# # # Define the time slice for round-robin scheduling
# # TIME_SLICE = 5

# # class GangScheduler:
# #     def __init__(self, env, cpu_capacity):
# #         self.env = env
# #         self.cpu_capacity = cpu_capacity
# #         self.cpu = simpy.Resource(env, capacity=cpu_capacity)
# #         self.ready_queue = simpy.Store(env)  # Queue for ready tasks
# #         self.gangs = {}  # Track gangs and their tasks
# #         self.tasks = {}  # Track all tasks and their states

# #     def task(self, name, bursts, gang_id):
# #         """A task process that performs CPU and I/O operations with state management."""
# #         state = STATE_READY
# #         while bursts:
# #             burst_type, duration = bursts[0]
# #             if burst_type == 'CPU':
# #                 time_slice = min(TIME_SLICE, duration)
# #                 state = STATE_RUNNING
# #                 print(f'{self.env.now}: {name} state: {state} - requesting CPU for {time_slice} time units')
# #                 with self.cpu.request() as req:
# #                     yield req
# #                     print(f'{self.env.now}: {name} state: {state} - got CPU')
# #                     yield self.env.timeout(time_slice)
# #                     duration -= time_slice
# #                     if duration > 0 and len(bursts) > 0:
# #                         bursts[0] = (burst_type, duration)
# #                         state = STATE_READY
# #                         print(f'{self.env.now}: {name} state: {state} - preempted with {duration} time units remaining')
# #                         self.ready_queue.put((name, bursts, gang_id))  # Put back to ready queue if not finished
# #                     elif len(bursts) > 0:
# #                         bursts.pop(0)
# #                         state = STATE_WAITING
# #                         print(f'{self.env.now}: {name} state: {state} - finished CPU burst')
# #             else:
# #                 state = STATE_WAITING
# #                 print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units')
# #                 yield self.env.timeout(duration)
# #                 if len(bursts) > 0:
# #                     bursts.pop(0)
# #                     state = STATE_READY
# #                     print(f'{self.env.now}: {name} state: {state} - finished I/O burst')

# #         state = STATE_FINISHED
# #         print(f'{self.env.now}: {name} state: {state} - task completed')
# #         if gang_id in self.gangs:
# #             if name in self.gangs[gang_id]:
# #                 self.gangs[gang_id].remove(name)
# #                 if not self.gangs[gang_id]:  # All tasks in the gang are finished
# #                     print(f'{self.env.now}: Gang {gang_id} state: {STATE_TERMINATED} - all tasks completed')
# #                     del self.gangs[gang_id]  # Remove the gang
# #             else:
# #                 print(f'{self.env.now}: Error - {name} not found in gang {gang_id} tasks')
# #         else:
# #             print(f'{self.env.now}: Error - Gang {gang_id} not found')

# #     def create_gang(self, gang_id, inter_arrival_time, num_tasks, tasks_bursts):
# #         """Function to create and process a gang of tasks."""
# #         yield self.env.timeout(inter_arrival_time)  # Simulate the arrival of the gang
# #         print(f"Gang {gang_id} arrived at {self.env.now}")
# #         print(f"Gang {gang_id} processes and their bursts:")

# #         self.gangs[gang_id] = []
# #         for task_id, bursts in enumerate(tasks_bursts, start=1):
# #             task_name = f"Gang{gang_id}-Task{task_id}"
# #             self.gangs[gang_id].append(task_name)
# #             print(f"  {task_name}: {bursts}")
# #             self.ready_queue.put((task_name, bursts, gang_id))  # Add task to ready queue
# #             self.tasks[task_name] = bursts  # Track task

# #         print(f"Gang {gang_id}")

# # def setup_environment(env, num_gangs, cpu_capacity):
# #     """Setup and run the simulation environment."""
# #     scheduler = GangScheduler(env, cpu_capacity)
# #     gang_creation_processes = []
# #     for i in range(num_gangs):
# #         num_tasks = random.randint(1, 3)  # Each gang has 1 to 3 tasks
# #         inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
# #         # Generate bursts for each task in the gang
# #         tasks_bursts = []
# #         for _ in range(num_tasks):
# #             # Random number of bursts for each task, each burst with a random length from 3 to 20
# #             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
# #             tasks_bursts.append(bursts)
        
# #         gang_creation_processes.append(env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts)))

# #     env.process(time_tick_scheduler(env, scheduler, gang_creation_processes))

# # def time_tick_scheduler(env, scheduler, gang_creation_processes):
# #     """Scheduler to handle task execution at each time tick."""
# #     # Wait for all gangs to be created
# #     yield simpy.events.AllOf(env, gang_creation_processes)
    
# #     total_gangs = len(scheduler.gangs)
# #     print(f'Total gangs created in line 108: {total_gangs}')
# #     completed_gangs = 0
    
# #     while completed_gangs < total_gangs:  # Loop until all gangs are completed
# #         print(f'Total gangs created in time tick: {total_gangs}')
# #         print(f'Completed gangs created in time tick: {completed_gangs}')
# #         if scheduler.ready_queue.items:
# #             task_name, bursts, gang_id = yield scheduler.ready_queue.get()
# #             print(f'{env.now}: Scheduling {task_name}')
# #             env.process(scheduler.task(task_name, bursts, gang_id))

# #         # Check for finished gangs after scheduling (important!)
# #         if not scheduler.ready_queue.items:
# #             completed_gangs = sum(len(gang) == 2 for gang in scheduler.gangs.values())
# #             print(f'{env.now}: line 123 Completed gangs: {completed_gangs}/{total_gangs}')

# #         yield env.timeout(1)  # Time tick

# # # Create a SimPy environment
# # env = simpy.Environment()
# # # Setup the environment with 4 gangs and 6 CPU cores
# # setup_environment(env, 4, 6)
# # # Run the simulation
# # env.run()
