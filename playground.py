# import simpy

# class Task:
#     def __init__(self, name, cpu_bursts, io_bursts):
#         self.name = name
#         self.cpu_bursts = cpu_bursts
#         self.io_bursts = io_bursts
#         self.current_burst_index = 0 # Alternates between index in CPU bursts & IO bursts
#         self.burst_type = 'CPU' # Current burst type: 'CPU' or 'IO'
    
#     def is_completed(self):
#         return self.current_burst_index >= len(self.cpu_bursts) and self.current_burst_index >= len(self.io_bursts)

#     def get_current_burst_duration(self):
#         if self.is_completed():
#             return 0
#         if self.burst_type == 'CPU':
#             return self.cpu_bursts[self.current_burst_index]
#         else:
#             return self.io_bursts[self.current_burst_index]

#     def execute_burst(self, duration):
#         if self.burst_type == 'CPU':
#             self.cpu_bursts[self.current_burst_index] -= duration
#             if self.cpu_bursts[self.current_burst_index] <= 0:
#                 self.burst_type = 'IO'
#         else:
#             self.io_bursts[self.current_burst_index] -= duration
#             if self.io_bursts[self.current_burst_index] <= 0:
#                 self.burst_type = 'CPU'
#                 self.current_burst_index += 1  

# class Gang:
#     def __init__(self, arrival_time, tasks):
#         self.arrival_time = arrival_time
#         self.tasks = tasks
    
#     def is_completed(self):
#         return all(task.is_completed() for task in self.tasks)
    
#     def __str__(self):
#         return f"Gang(arrival_time={self.arrival_time}, tasks={len(self.tasks)})"

# class Scheduler:
#     def __init__(self, env, processors, time_slice):
#         self.env = env
#         self.processors = processors
#         self.time_slice = time_slice
#         self.ready_queue = simpy.Store(env)
#         self.running_queue = []
#         self.time = 0
#         self.time_slice_tracker = 0

#     def add_gang(self, gang):
#         yield self.env.timeout(gang.arrival_time)
#         print(f'Arrival time: {self.env.now}, Gang: {gang}')
#         self.ready_queue.put(gang)

#     def schedule_tasks(self):
#         while True:
#             self.time += 1
#             self.time_slice_tracker += 1

#             # Load as many gangs as possible into running queue
#             while len(self.running_queue) < self.processors and len(self.ready_queue.items) > 0:
#                 gang = yield self.ready_queue.get()
#                 self.running_queue.append(gang)

#             # Execute each task on its processor
#             for gang in list(self.running_queue):
#                 for task in gang.tasks:
#                     burst_duration = min(task.get_current_burst_duration(), self.time_slice)
#                     task.execute_burst(burst_duration)
#                     yield self.env.timeout(burst_duration)

#             # Check if any processes are completed
#             for gang in list(self.running_queue):
#                 if gang.is_completed():
#                     self.running_queue.remove(gang)
#                     print(f'Completion time: {self.env.now}, Gang completed: {gang}')

#             if self.time_slice_tracker >= self.time_slice:
#                 self.time_slice_tracker = 0
#                 # Preempt running gangs back to the end of the ready queue
#                 for gang in list(self.running_queue):
#                     self.running_queue.remove(gang)
#                     self.ready_queue.put(gang)
#                     print(f'Preempted: {gang} at time {self.env.now}')

#             yield self.env.timeout(1)

# # Example usage
# env = simpy.Environment()

# task1 = Task('Task1', [4, 3], [2, 1])
# task2 = Task('Task2', [3, 2], [1, 2])
# gang1 = Gang(0, [task1, task2])

# scheduler = Scheduler(env, processors=4, time_slice=6)
# env.process(scheduler.add_gang(gang1))
# env.process(scheduler.schedule_tasks())

# env.run(until=50)

# class Task:
#     def __init__(self, cpu_bursts, io_bursts):
#         self.cpu_bursts = cpu_bursts
#         self.io_bursts = io_bursts
#         self.current_burst_index = 0 # Alternates between index in CPU bursts & IO bursts
#         self.burst_type = 'CPU' # Current burst type: 'CPU' or 'IO'
    
#     def is_completed(self):
#         return self.current_burst_index >= len(self.cpu_bursts) and self.current_burst_index >= len(self.io_bursts)
    
#     def tick(self):
#         if self.is_completed():
#             return
        
#         if self.burst_type == 'CPU':
#             self.cpu_bursts[self.current_burst_index] -= 1
#             if self.cpu_bursts[self.current_burst_index] == 0:
#                 self.burst_type = 'IO'
#         else:
#             self.io_bursts[self.current_burst_index] -= 1
#             if self.io_bursts[self.current_burst_index] == 0:
#                 self.burst_type = 'CPU'
#                 self.current_burst_index += 1

# class Gang:
#     def __init__(self, arrival_time, tasks):
#         self.arrival_time = arrival_time
#         self.tasks = tasks
    
#     def is_completed(self):
#         return all(task.is_completed() for task in self.tasks)
    
#     def __str__(self):
#         return f"Gang(arrival_time={self.arrival_time}, tasks={len(self.tasks)})"

# class Scheduler:
#     def __init__(self, processors, time_slice):
#         self.processors = processors
#         self.time_slice = time_slice
#         self.ready_queue = []
#         self.running_queue = []
#         self.time = 0
#         self.time_slice_tracker = 0
    
#     def add_gang(self, gang):
#         self.ready_queue.append(gang)
#         self.ready_queue.sort(key=lambda g: g.arrival_time)
    
#     def tick(self):
#         self.time += 1
#         self.time_slice_tracker += 1

#         # Load as many gangs as possible into running queue
#         for gang in list(self.ready_queue):
#             if processes_left() >= len(gang.tasks):
#                 self.ready_queue.remove(gang)
#                 self.running_queue.append(gang)

#         # Execute each process on its processor
#         for gang in self.running_queue:
#             for task in gang.tasks:
#                 task.tick()

#         # Check if any processes are completed
#         for gang in list(self.running_queue):
#             if gang.is_completed():
#                 self.running_queue.remove(gang)
#                 print(f"Gang completed: {gang}")

#         if self.time_slice_tracker >= self.time_slice:
#             self.time_slice_tracker = 0
#             # Preempt running gangs back to the end of the ready queue
#             for gang in list(self.running_queue):
#                 self.running_queue.remove(gang)
#                 self.add_gang(gang)
    
#     def processes_left(self):
#         return self.processors - sum(len(gang.tasks) for gang in self.running_queue)

# # Example Usage:
# task1 = Task([4, 3], [2, 1])
# task2 = Task([3, 2], [1, 2])
# gang1 = Gang(0, [task1, task2])

# scheduler = Scheduler(4, 6)
# scheduler.add_gang(gang1)
# for _ in range(20):  # Run the scheduler for 20 ticks
#     scheduler.tick()





import simpy
import random

# Define task states
STATE_READY = "READY"
STATE_RUNNING = "RUNNING"
STATE_WAITING = "WAITING"
STATE_FINISHED = "FINISHED"
STATE_TERMINATED = "TERMINATED"

# Define the time slice for round-robin scheduling
TIME_SLICE = 5

class GangScheduler:
    def __init__(self, env, cpu_capacity):
        self.env = env
        self.cpu_capacity = cpu_capacity
        self.cpu = simpy.Resource(env, capacity=cpu_capacity)
        self.ready_queue = simpy.Store(env)  # Queue for ready tasks
        self.gangs = {}  # Track gangs and their tasks
        self.tasks = {}  # Track all tasks and their states

    def task(self, name, bursts, gang_id):
        """A task process that performs CPU and I/O operations with state management."""
        state = STATE_READY
        while bursts:
            burst_type, duration = bursts[0]
            if burst_type == 'CPU':
                time_slice = min(TIME_SLICE, duration)
                state = STATE_RUNNING
                print(f'{self.env.now}: {name} state: {state} - requesting CPU for {time_slice} time units')
                with self.cpu.request() as req:
                    yield req
                    print(f'{self.env.now}: {name} state: {state} - got CPU')
                    yield self.env.timeout(time_slice)
                    duration -= time_slice
                    if duration > 0 and len(bursts) > 0:
                        bursts[0] = (burst_type, duration)
                        state = STATE_READY
                        print(f'{self.env.now}: {name} state: {state} - preempted with {duration} time units remaining')
                        self.ready_queue.put((name, bursts, gang_id))  # Put back to ready queue if not finished
                    elif len(bursts) > 0:
                        bursts.pop(0)
                        state = STATE_WAITING
                        print(f'{self.env.now}: {name} state: {state} - finished CPU burst')
            else:
                state = STATE_WAITING
                print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units')
                yield self.env.timeout(duration)
                if len(bursts) > 0:
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
        for task_id, bursts in enumerate(tasks_bursts, start=1):
            task_name = f"Gang{gang_id}-Task{task_id}"
            self.gangs[gang_id].append(task_name)
            print(f"  {task_name}: {bursts}")
            self.ready_queue.put((task_name, bursts, gang_id))  # Add task to ready queue
            self.tasks[task_name] = bursts  # Track task

        print(f"Gang {gang_id}")

def setup_environment(env, num_gangs, cpu_capacity):
    """Setup and run the simulation environment."""
    scheduler = GangScheduler(env, cpu_capacity)
    for i in range(num_gangs):
        num_tasks = random.randint(1, 3)  # Each gang has 1 to 10 tasks
        inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
        # Generate bursts for each task in the gang
        tasks_bursts = []
        for _ in range(num_tasks):
            # Random number of bursts for each task, each burst with a random length from 3 to 20
            bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
            tasks_bursts.append(bursts)
        
        env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts))

    # Start the round-robin scheduling process
    env.process(time_tick_scheduler(env, scheduler))

def time_tick_scheduler(env, scheduler):
    """Scheduler to handle task execution at each time tick."""
    total_gangs = len(scheduler.gangs)  # Assuming initial gangs are stored
    completed_gangs = 0
    while completed_gangs <= total_gangs:
    # Check the state of all gangs and processes
        if scheduler.ready_queue.items:
            task_name, bursts, gang_id = yield scheduler.ready_queue.get()
            print(f'{env.now}: Scheduling {task_name}')
            env.process(scheduler.task(task_name, bursts, gang_id))

        # Check for finished gangs after scheduling (important!)
        if scheduler.ready_queue.items:  
            continue  # Skip checking completed_gangs if there are tasks to schedule

        # Update completed_gangs count after processing tasks (prevents double counting)
        completed_gangs = sum(len(gang) == 0 for gang in scheduler.gangs.values())

        yield env.timeout(1)  # Time tick

# Create a SimPy environment
env = simpy.Environment()
# Setup the environment with 10 gangs and 4 CPU cores
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

# # Define the time slice for round-robin scheduling
# TIME_SLICE = 5

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
#     for i in range(num_gangs):
#         num_tasks = random.randint(1, 10)  # Each gang has 1 to 10 tasks
#         inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
#         # Generate bursts for each task in the gang
#         tasks_bursts = []
#         for _ in range(num_tasks):
#             # Random number of bursts for each task, each burst with a random length from 3 to 20
#             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
#             tasks_bursts.append(bursts)
        
#         env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts))

#     # Start the round-robin scheduling process
#     env.process(time_tick_scheduler(env, scheduler))

# def time_tick_scheduler(env, scheduler):
#     """Scheduler to handle task execution at each time tick."""
#     while True:
#         # Check the state of all gangs and processes
#         if scheduler.ready_queue.items:
#             task_name, bursts, gang_id = yield scheduler.ready_queue.get()
#             print(f'{env.now}: Scheduling {task_name}')
#             env.process(scheduler.task(task_name, bursts, gang_id))
#         yield env.timeout(1)  # Time tick

# # Create a SimPy environment
# env = simpy.Environment()
# # Setup the environment with 10 gangs and 4 CPU cores
# setup_environment(env, 10, 4)
# # Run the simulation
# env.run()








#before this below
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

# class GangScheduler:
#     def __init__(self, env, cpu_capacity):
#         self.env = env
#         self.cpu_capacity = cpu_capacity
#         self.cpu = simpy.Resource(env, capacity=cpu_capacity)
#         self.ready_queue = simpy.Store(env)  # Queue for ready tasks
#         self.gangs = {}  # Track gangs and their tasks

#     def task(self, name, bursts, gang_id):
#         """A task process that performs CPU and I/O operations with state management."""
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
#                     if duration > 0:
#                         bursts[0] = (burst_type, duration)
#                         state = STATE_READY
#                         print(f'{self.env.now}: {name} state: {state} - preempted with {duration} time units remaining')
#                         self.ready_queue.put((name, bursts, gang_id))  # Put back to ready queue if not finished
#                     else:
#                         bursts.pop(0)
#                         state = STATE_WAITING
#                         print(f'{self.env.now}: {name} state: {state} - finished CPU burst')
#             else:
#                 state = STATE_WAITING
#                 print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units')
#                 yield self.env.timeout(duration)
#                 bursts.pop(0)
#                 state = STATE_READY
#                 print(f'{self.env.now}: {name} state: {state} - finished I/O burst')

#         state = STATE_FINISHED
#         print(f'{self.env.now}: {name} state: {state} - task completed')
#         if gang_id in self.gangs:
#             if name in self.gangs[gang_id]:
#                 self.gangs[gang_id].remove(name)
#                 if not self.gangs[gang_id]:  # All tasks in the gang are finished
#                     print(f'{self.env.now}: Gang {gang_id} state: {STATE_TERMINATED} - all tasks completed')
#                     del self.gangs[gang_id]  # Remove the gang
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

# def setup_environment(env, num_gangs, cpu_capacity):
#     """Setup and run the simulation environment."""
#     scheduler = GangScheduler(env, cpu_capacity)
#     for i in range(num_gangs):
#         num_tasks = random.randint(1, 10)  # Each gang has 1 to 10 tasks
#         inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
#         # Generate bursts for each task in the gang
#         tasks_bursts = []
#         for _ in range(num_tasks):
#             # Random number of bursts for each task, each burst with a random length from 3 to 20
#             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
#             tasks_bursts.append(bursts)
        
#         env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts))

#     # Start the round-robin scheduling process
#     env.process(round_robin_scheduler(env, scheduler))

# def round_robin_scheduler(env, scheduler):
#     """Round-robin scheduler to handle task execution with time slicing."""
#     while True:
#         if not scheduler.ready_queue.items:
#             yield env.timeout(1)
#             continue

#         # Gather tasks from the ready queue that fit within the available CPU capacity
#         next_tasks = []
#         tasks_to_requeue = []
#         while scheduler.ready_queue.items and len(next_tasks) < scheduler.cpu_capacity:
#             task_name, bursts, gang_id = yield scheduler.ready_queue.get()
#             if len(next_tasks) + len([task for task in next_tasks if task[2] == gang_id]) <= scheduler.cpu_capacity:
#                 next_tasks.append((task_name, bursts, gang_id))
#             else:
#                 tasks_to_requeue.append((task_name, bursts, gang_id))
        
#         # Requeue the tasks that couldn't be scheduled
#         for task in tasks_to_requeue:
#             scheduler.ready_queue.put(task)

#         # Schedule the gathered tasks
#         if next_tasks:
#             for task_name, bursts, gang_id in next_tasks:
#                 print(f'{env.now}: Scheduling {task_name}')
#                 env.process(scheduler.task(task_name, bursts, gang_id))
#             yield env.timeout(TIME_SLICE)  # Time slice for round-robin scheduling
#         else:
#             yield env.timeout(1)

# # Create a SimPy environment
# env = simpy.Environment()
# # Setup the environment with 10 gangs and 4 CPU cores
# setup_environment(env, 10, 4)
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

# class GangScheduler:
#     def __init__(self, env, cpu_capacity):
#         self.env = env
#         self.cpu_capacity = cpu_capacity
#         self.cpu = simpy.Resource(env, capacity=cpu_capacity)
#         self.ready_queue = simpy.Store(env)  # Queue for ready tasks
#         self.gangs = {}  # Track gangs and their tasks

#     def task(self, name, bursts, gang_id):
#         """A task process that performs CPU and I/O operations with state management."""
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
#                     if duration > 0:
#                         bursts[0] = (burst_type, duration)
#                         state = STATE_READY
#                         print(f'{self.env.now}: {name} state: {state} - preempted with {duration} time units remaining')
#                         self.ready_queue.put((name, bursts, gang_id))  # Put back to ready queue if not finished
#                     else:
#                         bursts.pop(0)
#                         state = STATE_WAITING
#                         print(f'{self.env.now}: {name} state: {state} - finished CPU burst')
#             else:
#                 state = STATE_WAITING
#                 print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units')
#                 yield self.env.timeout(duration)
#                 bursts.pop(0)
#                 state = STATE_READY
#                 print(f'{self.env.now}: {name} state: {state} - finished I/O burst')

#         state = STATE_FINISHED
#         print(f'{self.env.now}: {name} state: {state} - task completed')
#         if gang_id in self.gangs:
#             if name in self.gangs[gang_id]:
#                 self.gangs[gang_id].remove(name)
#                 if not self.gangs[gang_id]:  # All tasks in the gang are finished
#                     print(f'{self.env.now}: Gang {gang_id} state: {STATE_TERMINATED} - all tasks completed')
#                     del self.gangs[gang_id]  # Remove the gang
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

# def setup_environment(env, num_gangs, cpu_capacity):
#     """Setup and run the simulation environment."""
#     scheduler = GangScheduler(env, cpu_capacity)
#     for i in range(num_gangs):
#         num_tasks = random.randint(1, 5)  # Each gang has 1 to 10 tasks
#         inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
#         # Generate bursts for each task in the gang
#         tasks_bursts = []
#         for _ in range(num_tasks):
#             # Random number of bursts for each task, each burst with a random length from 3 to 20
#             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
#             tasks_bursts.append(bursts)
        
#         env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts))

#     # Start the round-robin scheduling process
#     env.process(round_robin_scheduler(env, scheduler))

# def round_robin_scheduler(env, scheduler):
#     """Round-robin scheduler to handle task execution with time slicing."""
#     while True:
#         if not scheduler.ready_queue.items:
#             yield env.timeout(1)
#             continue

#         # Gather tasks from the ready queue that fit within the available CPU capacity
#         next_tasks = []
#         tasks_to_requeue = []
#         while scheduler.ready_queue.items and len(next_tasks) < scheduler.cpu_capacity:
#             task_name, bursts, gang_id = yield scheduler.ready_queue.get()
#             if len(next_tasks) + len([task for task in next_tasks if task[2] == gang_id]) <= scheduler.cpu_capacity:
#                 next_tasks.append((task_name, bursts, gang_id))
#             else:
#                 tasks_to_requeue.append((task_name, bursts, gang_id))
        
#         # Requeue the tasks that couldn't be scheduled
#         for task in tasks_to_requeue:
#             scheduler.ready_queue.put(task)

#         # Schedule the gathered tasks
#         if next_tasks:
#             for task_name, bursts, gang_id in next_tasks:
#                 print(f'{env.now}: Scheduling {task_name}')
#                 env.process(scheduler.task(task_name, bursts, gang_id))
#             yield env.timeout(TIME_SLICE)  # Time slice for round-robin scheduling
#         else:
#             yield env.timeout(1)

# # Create a SimPy environment
# env = simpy.Environment()
# # Setup the environment with 10 gangs and 4 CPU cores
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

# # Define the time slice for round-robin scheduling
# TIME_SLICE = 5

# class GangScheduler:
#     def __init__(self, env, cpu_capacity):
#         self.env = env
#         self.cpu = simpy.Resource(env, capacity=cpu_capacity)
#         self.ready_queue = simpy.Store(env)  # Queue for ready tasks

#     def task(self, name, bursts):
#         """A task process that performs CPU and I/O operations with state management."""
#         state = STATE_READY
#         for burst_type, duration in bursts:
#             if burst_type == 'CPU':
#                 while duration > 0:
#                     time_slice = min(TIME_SLICE, duration)
#                     state = STATE_RUNNING
#                     print(f'{self.env.now}: {name} state: {state} - requesting CPU for {time_slice} time units')
#                     with self.cpu.request() as req:
#                         yield req
#                         print(f'{self.env.now}: {name} state: {state} - got CPU')
#                         yield self.env.timeout(time_slice)
#                         duration -= time_slice
#                         print(f'{self.env.now}: {name} state: {state} - finished {time_slice} time units of CPU burst')
#                     state = STATE_READY
#                     self.ready_queue.put((name, bursts))  # Put back to ready queue if not finished
#             else:
#                 state = STATE_WAITING
#                 print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units')
#                 yield self.env.timeout(duration)
#                 state = STATE_READY
#                 print(f'{self.env.now}: {name} state: {state} - finished I/O burst')
        
#         state = STATE_FINISHED
#         print(f'{self.env.now}: {name} state: {state} - task completed')

#     def create_gang(self, gang_id, inter_arrival_time, num_tasks, tasks_bursts):
#         """Function to create and process a gang of tasks."""
#         yield self.env.timeout(inter_arrival_time)  # Simulate the arrival of the gang
#         print(f"Gang {gang_id} arrived at {self.env.now}")
#         print(f"Gang {gang_id} processes and their bursts:")
#         for task_id, bursts in enumerate(tasks_bursts, start=1):
#             task_name = f"Gang{gang_id}-Task{task_id}"
#             print(f"  {task_name}: {bursts}")
#             self.ready_queue.put((task_name, bursts))  # Add task to ready queue

# def setup_environment(env, num_gangs, cpu_capacity):
#     """Setup and run the simulation environment."""
#     scheduler = GangScheduler(env, cpu_capacity)
#     for i in range(num_gangs):
#         num_tasks = random.randint(1, 4)  # Each gang has 1 to 10 tasks
#         inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
#         # Generate bursts for each task in the gang
#         tasks_bursts = []
#         for _ in range(num_tasks):
#             # Random number of bursts for each task, each burst with a random length from 3 to 20
#             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
#             tasks_bursts.append(bursts)
        
#         env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts))

#     # Start the round-robin scheduling process
#     env.process(round_robin_scheduler(env, scheduler))

# def round_robin_scheduler(env, scheduler):
#     """Round-robin scheduler to handle task execution with time slicing."""
#     while True:
#         if not scheduler.ready_queue.items:
#             yield env.timeout(1)
#             continue

#         for _ in range(len(scheduler.ready_queue.items)):
#             task_name, bursts = yield scheduler.ready_queue.get()
#             print(f'{env.now}: Scheduling {task_name}')
#             env.process(scheduler.task(task_name, bursts))
#             yield env.timeout(TIME_SLICE)  # Time slice for round-robin scheduling

# # Create a SimPy environment
# env = simpy.Environment()
# # Setup the environment with 10 gangs and 4 CPU cores
# setup_environment(env, 4, 10)
# # Run the simulation
# env.run(200)







# import simpy
# import random

# # Define task states
# STATE_READY = "READY"
# STATE_RUNNING = "RUNNING"
# STATE_WAITING = "WAITING"
# STATE_FINISHED = "FINISHED"

# class GangScheduler:
#     def __init__(self, env, cpu_capacity):
#         self.env = env
#         self.cpu = simpy.Resource(env, capacity=cpu_capacity)

#     def task(self, name, bursts):
#         """A task process that performs CPU and I/O operations with state management."""
#         state = STATE_READY
#         for burst_type, duration in bursts:
#             if burst_type == 'CPU':
#                 state = STATE_RUNNING
#                 print(f'{self.env.now}: {name} state: {state} - requesting CPU for {duration} time units')
#                 with self.cpu.request() as req:
#                     yield req
#                     state = STATE_RUNNING
#                     print(f'{self.env.now}: {name} state: {state} - got CPU')
#                     yield self.env.timeout(duration)
#                     state = STATE_WAITING
#                     print(f'{self.env.now}: {name} state: {state} - finished CPU burst')
#             else:
#                 state = STATE_WAITING
#                 print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units')
#                 yield self.env.timeout(duration)
#                 state = STATE_READY
#                 print(f'{self.env.now}: {name} state: {state} - finished I/O burst')
        
#         state = STATE_FINISHED
#         print(f'{self.env.now}: {name} state: {state} - task completed')

#     def create_gang(self, gang_id, inter_arrival_time, num_tasks, tasks_bursts):
#         """Function to create and process a gang of tasks."""
#         yield self.env.timeout(inter_arrival_time)  # Simulate the arrival of the gang
#         print(f"Gang {gang_id} arrived at {self.env.now}")

#         # Create a process for each task in the gang
#         tasks = []
#         for task_id, bursts in enumerate(tasks_bursts, start=1):
#             task_name = f"Gang{gang_id}-Task{task_id}"
#             tasks.append(self.env.process(self.task(task_name, bursts)))

#         # Synchronize all tasks in the gang to start their CPU bursts together
#         yield simpy.events.AllOf(self.env, tasks)
#         print(f"Gang {gang_id} completed at {self.env.now}")

# def setup_environment(env, num_gangs, cpu_capacity):
#     """Setup and run the simulation environment."""
#     scheduler = GangScheduler(env, cpu_capacity)
#     for i in range(num_gangs):
#         num_tasks = random.randint(1, 3)  # Each gang has 1 to 10 tasks
#         inter_arrival_time = random.randint(1, 5)  # Uniform whole number inter-arrival times between 1 and 10
        
#         # Generate bursts for each task in the gang
#         tasks_bursts = []
#         for _ in range(num_tasks):
#             # Random number of bursts for each task, each burst with a random length from 3 to 20
#             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 6)) for _ in range(random.randint(1, 5))]
#             tasks_bursts.append(bursts)
        
#         env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts))

# # Create a SimPy environment
# env = simpy.Environment()
# # Setup the environment with 10 gangs and 4 CPU cores
# setup_environment(env, 4, 5)
# # Run the simulation
# env.run()







# import simpy
# import random

# # Define task states
# STATE_READY = "READY"
# STATE_RUNNING = "RUNNING"
# STATE_WAITING = "WAITING"
# STATE_FINISHED = "FINISHED"

# class GangScheduler:
#     def __init__(self, env, cpu_capacity):
#         self.env = env
#         self.cpu = simpy.Resource(env, capacity=cpu_capacity)

#     def task(self, name, bursts):
#         """A task process that performs CPU and I/O operations with state management."""
#         state = STATE_READY
#         for burst_type, duration in bursts:
#             if burst_type == 'CPU':
#                 state = STATE_RUNNING
#                 print(f'{self.env.now}: {name} state: {state} - requesting CPU for {duration} time units')
#                 with self.cpu.request() as req:
#                     yield req
#                     state = STATE_RUNNING
#                     print(f'{self.env.now}: {name} state: {state} - got CPU')
#                     yield self.env.timeout(duration)
#                     state = STATE_WAITING
#                     print(f'{self.env.now}: {name} state: {state} - finished CPU burst')
#             else:
#                 state = STATE_WAITING
#                 print(f'{self.env.now}: {name} state: {state} - performing I/O for {duration} time units')
#                 yield self.env.timeout(duration)
#                 state = STATE_READY
#                 print(f'{self.env.now}: {name} state: {state} - finished I/O burst')
        
#         state = STATE_FINISHED
#         print(f'{self.env.now}: {name} state: {state} - task completed')

#     def create_gang(self, gang_id, inter_arrival_time, num_tasks, tasks_bursts):
#         """Function to create and process a gang of tasks."""
#         yield self.env.timeout(inter_arrival_time)  # Simulate the arrival of the gang
#         print(f"Gang {gang_id} arrived at {self.env.now}")

#         # Create a process for each task in the gang
#         tasks = []
#         for task_id, bursts in enumerate(tasks_bursts, start=1):
#             task_name = f"Gang{gang_id}-Task{task_id}"
#             tasks.append(self.env.process(self.task(task_name, bursts)))

#         # Synchronize all tasks in the gang to start their CPU bursts together
#         yield simpy.events.AllOf(self.env, tasks)
#         print(f"Gang {gang_id} completed at {self.env.now}")

# def setup_environment(env, num_gangs, cpu_capacity):
#     """Setup and run the simulation environment."""
#     scheduler = GangScheduler(env, cpu_capacity)
#     for i in range(num_gangs):
#         num_tasks = random.randint(1, 10)  # Each gang has 1 to 10 tasks
#         inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
#         # Generate bursts for each task in the gang
#         tasks_bursts = []
#         for _ in range(num_tasks):
#             # Random number of bursts for each task, each burst with a random length from 3 to 20
#             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
#             tasks_bursts.append(bursts)
        
#         env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts))

# # Create a SimPy environment
# env = simpy.Environment()
# # Setup the environment with 10 gangs and 4 CPU cores
# setup_environment(env, 10, 4)
# # Run the simulation
# env.run()








# import simpy
# import random

# class GangScheduler:
#     def __init__(self, env, cpu_capacity):
#         self.env = env
#         self.cpu = simpy.Resource(env, capacity=cpu_capacity)

#     def task(self, name, bursts):
#         """A task process that performs CPU and I/O operations."""
#         for burst_type, duration in bursts:
#             if burst_type == 'CPU':
#                 print(f'{self.env.now}: {name} requesting CPU for {duration} time units')
#                 with self.cpu.request() as req:
#                     yield req
#                     print(f'{self.env.now}: {name} got CPU')
#                     yield self.env.timeout(duration)
#                     print(f'{self.env.now}: {name} finished CPU burst')
#             else:
#                 print(f'{self.env.now}: {name} performing I/O for {duration} time units')
#                 yield self.env.timeout(duration)
#                 print(f'{self.env.now}: {name} finished I/O burst')

#     def create_gang(self, gang_id, inter_arrival_time, num_tasks, tasks_bursts):
#         """Function to create and process a gang of tasks."""
#         yield self.env.timeout(inter_arrival_time)  # Simulate the arrival of the gang
#         print(f"Gang {gang_id} arrived at {self.env.now}")

#         # Create a process for each task in the gang
#         tasks = []
#         for task_id, bursts in enumerate(tasks_bursts, start=1):
#             task_name = f"Gang{gang_id}-Task{task_id}"
#             tasks.append(self.env.process(self.task(task_name, bursts)))

#         # Synchronize all tasks in the gang to start their CPU bursts together
#         yield simpy.events.AllOf(self.env, tasks)
#         print(f"Gang {gang_id} completed at {self.env.now}")

# def setup_environment(env, num_gangs, cpu_capacity):
#     """Setup and run the simulation environment."""
#     scheduler = GangScheduler(env, cpu_capacity)
#     for i in range(num_gangs):
#         num_tasks = random.randint(1, 10)  # Each gang has 1 to 10 tasks
#         inter_arrival_time = random.randint(1, 10)  # Uniform whole number inter-arrival times between 1 and 10
        
#         # Generate bursts for each task in the gang
#         tasks_bursts = []
#         for _ in range(num_tasks):
#             # Random number of bursts for each task, each burst with a random length from 3 to 20
#             bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(random.randint(1, 5))]
#             tasks_bursts.append(bursts)
        
#         env.process(scheduler.create_gang(i+1, inter_arrival_time, num_tasks, tasks_bursts))

# # Create a SimPy environment
# env = simpy.Environment()
# # Setup the environment with 10 gangs and 4 CPU cores
# setup_environment(env, 10, 4)
# # Run the simulation
# env.run()








# # import simpy
# # import random
# # from collections import deque

# # class GangScheduler:
# #     def __init__(self, env, num_processors, time_quantum):
# #         self.env = env
# #         self.num_processors = num_processors
# #         self.processors = [simpy.Resource(env, capacity=1) for _ in range(num_processors)]
# #         self.free_processors = list(range(num_processors))
# #         self.queue = deque()
# #         self.time_quantum = time_quantum
# #         self.processor_idle_time = [0] * num_processors
# #         self.processor_busy_time = [0] * num_processors
# #         self.processor_last_free_time = [0] * num_processors

# #     def generate_gangs(self, num_gangs, start_time):
# #         arrival_time = start_time
# #         for gang_id in range(1, num_gangs + 1):
# #             num_tasks = random.randint(1, 5)
# #             inter_arrival_time = random.randint(1, 3)  # Random inter-arrival time between gangs
# #             arrival_time += inter_arrival_time
# #             tasks = [(task_id, [(random.randint(1, 7), random.randint(1, 7)) for _ in range(random.randint(1, 2))])
# #                      for task_id in range(num_tasks)]
# #             self.queue.append((arrival_time, gang_id, tasks))
# #         self.print_gang_details()

# #     def manage_scheduling(self):
# #         while True:
# #             if self.queue and self.free_processors:
# #                 arrival_time, gang_id, tasks = self.queue[0]
# #                 current_time = self.env.now
# #                 if current_time >= arrival_time and len(tasks) <= len(self.free_processors):
# #                     self.queue.popleft()
# #                     self.env.process(self.schedule_gang(gang_id, tasks))
# #             yield self.env.timeout(1)

# #     def schedule_gang(self, gang_id, tasks):
# #         allocated_processors = self.free_processors[:len(tasks)]
# #         self.free_processors = self.free_processors[len(tasks):]
# #         print(f"Scheduling Gang {gang_id} at time {self.env.now} with {len(tasks)} tasks:")
# #         for i, (task_id, bursts) in enumerate(tasks):
# #             processor_id = allocated_processors[i]
# #             print(f"  Task {task_id} of Gang {gang_id} is assigned to Processor {processor_id}.")
# #             busy_time = sum(duration for duration, cycle_type in bursts if cycle_type == 0)
# #             self.processor_busy_time[processor_id] += busy_time
# #             self.update_processor_usage(processor_id, self.env.now)
# #         yield self.env.timeout(self.time_quantum)
# #         print(f"Gang {gang_id} released processors at time {self.env.now}")
# #         for processor_id in allocated_processors:
# #             self.free_processors.append(processor_id)
# #             self.processor_idle_time[processor_id] += self.env.now - self.processor_last_free_time[processor_id]
# #             self.processor_last_free_time[processor_id] = self.env.now
# #         # Re-enqueue the gang if tasks are not completed
# #         self.queue.append((self.env.now, gang_id, tasks))

# #     def update_processor_usage(self, processor_id, start_time):
# #         if self.processor_last_free_time[processor_id] < start_time:
# #             self.processor_idle_time[processor_id] += start_time - self.processor_last_free_time[processor_id]
# #         self.processor_last_free_time[processor_id] = start_time + self.time_quantum

# #     def print_gang_details(self):
# #         print("Gangs and Tasks at time:", self.env.now)
# #         for arrival_time, gang_id, tasks in self.queue:
# #             print(f"Gang {gang_id} arrives at {arrival_time}:")
# #             for task_id, bursts in tasks:
# #                 print(f"  Task {task_id}: Bursts -> {bursts}")

# #     def print_processor_times(self):
# #         for i, (idle_time, busy_time) in enumerate(zip(self.processor_idle_time, self.processor_busy_time)):
# #             print(f"Processor {i}: Idle time: {idle_time}, Busy time: {busy_time}")

# # # Setup
# # env = simpy.Environment()
# # num_processors = 5  # Total number of processors
# # scheduler = GangScheduler(env, num_processors, time_quantum=5)

# # # Generate gangs with random tasks, starting from time 0
# # scheduler.generate_gangs(5, start_time=0)

# # # Start the scheduling management process
# # env.process(scheduler.manage_scheduling())

# # # Run the simulation
# # env.run(until=50)

# # # Print processor times and final state of gangs
# # scheduler.print_processor_times()
# # scheduler.print_gang_details()

# import simpy
# import random

# class GangScheduler:
#     def __init__(self, env, num_cpus, time_slice):
#         self.env = env
#         self.num_cpus = num_cpus
#         self.time_slice = time_slice
#         self.cpu_resources = simpy.Resource(env, capacity=num_cpus)
#         self.queue = []
#         self.metrics = {
#             "total_completion_time": 0,
#             "total_waiting_time": 0,
#             "total_gangs_processed": 0
#         }

#     def create_gang(self, gang_id, inter_arrival_time, num_tasks, task_bursts):
#         """Create and manage a gang of tasks."""
#         yield self.env.timeout(inter_arrival_time)
#         arrival_time = self.env.now
#         print(f"Gang {gang_id} arrived at {arrival_time}")

#         # Manage resource allocation
#         if self.cpu_resources.count + num_tasks <= self.num_cpus:
#             requests = [self.cpu_resources.request() for _ in range(num_tasks)]
#             results = yield simpy.AllOf(self.env, requests)
            
#             # Process all tasks in the gang simultaneously
#             tasks = [self.env.process(self.process_task(gang_id, i + 1, task_bursts[i])) for i in range(num_tasks)]
#             yield simpy.AllOf(self.env, tasks)

#             # Release resources
#             for req in requests:
#                 self.cpu_resources.release(req)

#             completion_time = self.env.now - arrival_time
#             self.metrics["total_completion_time"] += completion_time
#             self.metrics["total_gangs_processed"] += 1
#             print(f"Gang {gang_id} completed in {completion_time} seconds.")
#         else:
#             # Requeue if not enough resources
#             self.env.process(self.create_gang(gang_id, self.time_slice, num_tasks, task_bursts))

#     def process_task(self, gang_id, task_id, burst):
#         """Process individual tasks with preemptive time slices."""
#         burst_type, burst_duration = burst
#         start_time = self.env.now
#         print(f"  Task {task_id} of Gang {gang_id}: {burst_type} Burst for {burst_duration}s at {start_time}")
#         yield self.env.timeout(burst_duration)
#         end_time = self.env.now
#         waiting_time = end_time - start_time - burst_duration
#         self.metrics["total_waiting_time"] += waiting_time

#     def setup_environment(self, num_gangs):
#         for i in range(num_gangs):
#             num_tasks = random.randint(1, 10)
#             inter_arrival_time = random.randint(1, 10)
#             task_bursts = [(random.choice(['CPU', 'IO']), random.randint(3, 20)) for _ in range(num_tasks)]
#             self.env.process(self.create_gang(i + 1, inter_arrival_time, num_tasks, task_bursts))

#     def report_metrics(self):
#         if self.metrics["total_gangs_processed"] > 0:
#             avg_completion_time = self.metrics["total_completion_time"] / self.metrics["total_gangs_processed"]
#             avg_waiting_time = self.metrics["total_waiting_time"] / self.metrics["total_gangs_processed"]
#             print(f"Average Completion Time: {avg_completion_time}, Average Waiting Time: {avg_waiting_time}")

# # Create a SimPy environment
# env = simpy.Environment()
# scheduler = GangScheduler(env, num_cpus=4, time_slice=10)
# scheduler.setup_environment(10)
# env.run(until=100)
# scheduler.report_metrics()
