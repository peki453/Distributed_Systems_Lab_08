# Distributed Systems Lab 8
# Student: Marko Pezer (BS18-SE-01)

# Import libraries
from time import sleep
from datetime import datetime
from multiprocessing import Process, Pipe
from os import getpid

def local_time(counter):
    return ' (LAMPORT_TIME={}, LOCAL_TIME={})'.format(counter, datetime.now())

def calc_recv_timestamp(recv_time_stamp, counter):
    for id  in range(len(counter)):
        counter[id] = max(recv_time_stamp[id], counter[id])
    return counter

def event(pid, counter):
    counter[pid] = counter[pid] + 1
    print('Something happened in {} !'.format(pid) + local_time(counter))
    return counter

def send_message(pipe, pid, counter):
    counter[pid] = counter[pid] + 1
    pipe.send(('Empty shell', counter))
    print('Message sent from ' + str(pid) + local_time(counter))
    return counter

def recv_message(pipe, pid, counter):
    message, timestamp = pipe.recv()
    counter[pid] = counter[pid] + 1
    counter = calc_recv_timestamp(timestamp, counter)
    print('Message received at ' + str(pid)  + local_time(counter))
    return counter

# Process 1
def process_one(pipe12):
    pid = 0
    counter = [0, 0, 0]
    counter = send_message(pipe12, pid, counter)
    counter = send_message(pipe12, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe12, pid, counter)
    counter = event(pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe12, pid, counter)

# Process 2
def process_two(pipe21, pipe23):
    pid = 1
    counter = [0, 0, 0]
    counter = recv_message(pipe21, pid, counter)
    counter = recv_message(pipe21, pid, counter)
    counter = send_message(pipe21, pid, counter)
    counter = recv_message(pipe23, pid, counter)
    counter = event(pid, counter)
    counter = send_message(pipe21, pid, counter)
    counter = send_message(pipe23, pid, counter)
    counter = send_message(pipe23, pid, counter)

# Process 3
def process_three(pipe32):
    pid = 2
    counter = [0, 0, 0]
    counter = send_message(pipe32, pid, counter)
    counter = recv_message(pipe32, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe32, pid, counter)

# Main part of the code
if __name__ == '__main__':
    oneandtwo, twoandone = Pipe()
    twoandthree, threeandtwo = Pipe()

    process1 = Process(target=process_one, 
            args=(oneandtwo,))
    process2 = Process(target=process_two, 
            args=(twoandone, twoandthree))
    process3 = Process(target=process_three, 
            args=(threeandtwo,))

    # Start all processes
    process1.start()
    process2.start()
    process3.start()
    
    # Join processes
    process1.join()
    process2.join()
    process3.join()

# Reference: https://towardsdatascience.com/understanding-lamport-timestamps-with-pythons-multiprocessing-library-12a6427881c6
