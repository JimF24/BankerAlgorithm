'''
Author: JiaYi FENG
ID: jf3354
Date: 11/21/2018
Banker
'''


import sys
import math
# to-do obj handling inputs
class taskObj:
    def __init__(self, mode, processid, res_type, num):
        self.mode = mode
        self.processid = processid
        self.res_type = res_type
        self.num = num

# process obj records variables
class processObj:
    counter = 0
    blocked = False
    blocked_time = 0
    computing_time = 0
    processid = 0
    aborted = False
    terminated = 0
    def __init__(self, id):
        self.processid = id
        self.owned = [0]
        self.claim = [0]

    def initialize_list(self, resources):
        for i in range (resources):
            self.claim.append(0)
            self.owned.append(0)

#FIFO algo

def Optimize(available, task_matrix, process_list):
    #clock
    time = 0
    #block list
    blocked = []
    #terminate list
    terminated = []
    #delay list
    compute = []
    #while exists process not terminated
    while (len(terminated) != len(process_list)-1):
        release_from_blocked = []
        curr_avail = []
        # maintain a curr_avail list to store resources released in this cycle
        for i in range(len(available)):
            curr_avail.append(0)
        # add blocked time
        for process in blocked:
            process.blocked_time += 1
        #handle blocked list
        for process in blocked:
            working = task_matrix[process.processid]
            requested = working[process.counter]
            if available[requested.res_type] >= requested.num:
                available[requested.res_type] -= requested.num
                release_from_blocked.append(process)
                process.blocked = False
            blocked = [process for process in blocked if process.blocked]
        for p in release_from_blocked:
            p.counter += 1
        #loop through process_list to indirectly loop through tasks list
        for process in process_list:
            if process in blocked or process in terminated or process in release_from_blocked:
                continue

            if process is not None:
                if process.computing_time > 0:
                    process.computing_time -= 1
                    continue
                tasklist = task_matrix[process.processid]
                task = tasklist[process.counter]
            #release
                if task.mode == "release":
                    curr_avail[task.res_type] += task.num
                    process_list[task.processid].owned[task.res_type] -= task.num
                if task.mode == "initiate":
                    process.claim[task.res_type] = task.num
                if task.mode == "request":
                    # if request can be granted
                    if available[task.res_type] >= task.num:
                        available[task.res_type] -= task.num
                        process.owned[task.res_type] += task.num
                    # if not, the process is blocked
                    else:
                        process.blocked = True
                        blocked.append(process)
                if task.mode == "compute":
                    process.computing_time = task.res_type - 1
                    compute.append(process)
                if task.mode == "terminate":
                    process.terminated = time
                    terminated.append(process)
                if process not in blocked:
                    process.counter += 1
        #if deadlock abort processes
        ind = len(blocked)
        while (len(terminated) + ind == len(process_list) - 1) and len(terminated) != len(process_list)-1:
            min_pid = math.inf
            block_ind = 0
            #find process with smallest processid and abort it
            for i in range(len(blocked)):
                if blocked[i].processid < min_pid:
                    min_pid = blocked[i].processid
                    block_ind = i
            aborted = blocked.pop(block_ind)
            ind = ind - 1
            for j in range(1, len(aborted.owned)):
                curr_avail[j] += aborted.owned[j]
            aborted.aborted = True
            aborted.terminated = time
            terminated.append(aborted)
            #check if deadlock still exists
            for cur_process in blocked:
                working = task_matrix[cur_process.processid]
                requested = working[cur_process.counter]
                if available[requested.res_type] + curr_avail[requested.res_type] >= requested.num:
                    ind = len(blocked) - 1

        for i in range(len(available)):
            available[i] += curr_avail[i]

        time += 1
    time -= 1
    totaltime = 0
    totalwait = 0
    print("                                   FIFO")
    for process in process_list:
        if process is not None:
            if process.aborted:
                print("Task: ", process.processid, "    aborted")
            else:
                totaltime += process.terminated
                totalwait += process.blocked_time
                print("Task: ", process.processid, "    Total time: ",process.terminated, "     Total waiting: ", process.blocked_time, "   Percentage of waiting: ", process.blocked_time/process.terminated )
    print("Total: ", "      Total time: ", totaltime, "     Total waiting: ", totalwait, "      Percentage of waiting: ", totalwait/totaltime)
    return time

def Banker(available, task_matrix, process_list):
    time = 0
    blocked = []
    terminated = []
    compute = []
    while (len(terminated) != len(process_list)-1):

        release_from_blocked = []
        curr_avail = []
        for i in range(len(available)):
            curr_avail.append(0)
        for process in blocked:
            process.blocked_time += 1
        #handle blocked list
        for process in blocked:
            working = task_matrix[process.processid]
            requested = working[process.counter]
            #do safety check
            safe = True
            if available[requested.res_type] < process.claim[requested.res_type] - process.owned[requested.res_type]:
                safe = False
            if available[requested.res_type] >= requested.num and safe:
                release_from_blocked.append(process)
                process.blocked = False
            blocked = [process for process in blocked if process.blocked]

        for process in release_from_blocked:
            #do request
            tasklist = task_matrix[process.processid]
            task = tasklist[process.counter]
            if task.mode == "request":
                # do safety check
                safe = True
                for i in range(len(available)):
                    if available[i] < process.claim[i] - process.owned[i]:
                        safe = False
                if available[task.res_type] >= task.num and safe:
                    available[task.res_type] -= task.num
                    process.owned[task.res_type] += task.num
                    process.counter += 1
                else:
                    process.blocked = True
                    blocked.append(process)
        for process in process_list:
            if process in blocked or process in terminated or process in release_from_blocked:
                continue
            if process is not None:
                if process.computing_time > 0:
                    process.computing_time -= 1
                    continue
                tasklist = task_matrix[process.processid]
                task = tasklist[process.counter]
            #release
                if task.mode == "release":
                    curr_avail[task.res_type] += task.num
                    process_list[task.processid].owned[task.res_type] -= task.num
                if task.mode == "initiate":
                    if available[task.res_type] < task.num:
                        process.aborted = True
                        for j in range(1, len(process.owned)):
                            curr_avail[j] += process.owned[j]
                        terminated.append(process)
                    else:
                        process.claim[task.res_type] = task.num

                if task.mode == "request":
                    # if exceeds claim, abort
                    if process.owned[task.res_type] + task.num > process.claim[task.res_type]:
                        process.aborted = True
                        for j in range(1, len(process.owned)):
                            curr_avail[j] += process.owned[j]
                        terminated.append(process)
                    #do safety check
                    else:
                        safe = True
                        for i in range(len(available)):
                            if available[i] < process.claim[i] - process.owned[i]:
                                safe = False
                        if available[task.res_type] >= task.num and safe:
                                available[task.res_type] -= task.num
                                process.owned[task.res_type] += task.num
                        else:
                            process.blocked = True
                            blocked.append(process)
                if task.mode == "compute":
                    process.computing_time = task.res_type - 1
                    compute.append(process)
                if task.mode == "terminate":
                    process.terminated = time
                    terminated.append(process)
                if task.mode == "release" and tasklist[process.counter+1].mode == "terminate":
                    process.terminated = time+1
                    terminated.append(process)
                if process not in blocked:
                    process.counter += 1
        for i in range(len(available)):
            available[i] += curr_avail[i]
        time += 1
    time -= 1
    totaltime = 0
    totalwait = 0
    print("                                   Banker")
    for process in process_list:
        if process is not None:
            if process.aborted:
                print("Task: ", process.processid, "    aborted")
            else:
                totaltime += process.terminated
                totalwait += process.blocked_time
                print("Task: ", process.processid, "    Total time: ",process.terminated, "     Total waiting: ", process.blocked_time, "   Percentage of waiting: ", process.blocked_time/process.terminated )
    print("Total: ", "      Total time: ", totaltime, "     Total waiting: ", totalwait, "      Percentage of waiting: ", totalwait/totaltime)
    return time




def main():
    filename = sys.argv[1]
    input = open(filename, "r")
    first_line = input.readline().strip()
    first_line = first_line.split()
    process_num = int(first_line[0])
    res_num = int(first_line[1])
    processlist = []
    available = [0]
    task_list = []
    task_matrix = [None]
    #handle input
    for i in range (process_num):
        task_matrix.append([])
    processlist.append(None)
    for i in range(2,len(first_line)):
        available.append(int(first_line[i]))
    for s in input:
        s = s.strip()
        if len(s) > 1:
            s = s.split()
            temp = taskObj(s[0], int(s[-3]), int(s[-2]), int(s[-1]))
            task_list.append(temp)
    for tasks in task_list:
        task_matrix[tasks.processid].append(tasks)
    for i in range(process_num):
        temp = processObj(i+1)
        processlist.append(temp)
    for process in processlist:
        if process is not None:
            process.initialize_list(res_num)
    Optimize(available, task_matrix, processlist)

    #Reset everything for the next algo
    input.seek(0)
    first_line = input.readline().strip()
    first_line = first_line.split()
    process_num = int(first_line[0])
    res_num = int(first_line[1])
    processlist = []
    available = [0]
    task_list = []
    task_matrix = [None]
    #handle input
    for i in range(process_num):
        task_matrix.append([])
    processlist.append(None)
    for i in range(2, len(first_line)):
        available.append(int(first_line[i]))
    for s in input:
        s = s.strip()
        if len(s) > 1:
            s = s.split()
            temp = taskObj(s[0], int(s[-3]), int(s[-2]), int(s[-1]))
            task_list.append(temp)
    for tasks in task_list:
        task_matrix[tasks.processid].append(tasks)
    for i in range(process_num):
        temp = processObj(i + 1)
        processlist.append(temp)
    for process in processlist:
        if process is not None:
            process.initialize_list(res_num)
    Banker(available, task_matrix, processlist)
main()