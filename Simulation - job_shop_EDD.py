# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 01:00:42 2018

@author: lonsichang
"""

import simpy
import random

#parameter
sim_time = 100

#record
job_list = []

#function
def _arrival(env):
    ID = 0
    while True:
        random_value = random.random()
        if random_value < 0.2:
            interval = 1
        elif random_value < 0.4:
            interval = 2
        elif random_value < 0.7:
            interval = 3
        elif random_value < 0.9:
            interval = 4
        else:
            interval = 5
        yield env.timeout(interval)
        ID += 1
        job_list.append(job(env, ID, MC))

class job:
    def __init__(self, env, ID, MC):
        self.env = env
        self.ID = ID
        self.arrival_time = env.now
        self.type = random.randint(1,6)
        self.finish_time = 0
        if self.type == 1:
            self.due_date = env.now + 7
            self.flow1 = 'A'
            self.time1 = 3
            self.flow2 = 'B'
            self.time2 = 3
        elif self.type == 2:
            self.due_date = env.now + 12
            self.flow1 = 'A'
            self.time1 = 5
            self.flow2 = 'C'
            self.time2 = 2
        elif self.type == 3:
            self.due_date = env.now + 7
            self.flow1 = 'B'
            self.time1 = 4
            self.flow2 = 'A'
            self.time2 = 3
        elif self.type == 4:
            self.due_date = env.now + 10
            self.flow1 = 'B'
            self.time1 = 3
            self.flow2 = 'C'
            self.time2 = 5
        elif self.type == 5:
            self.due_date = env.now + 11
            self.flow1 = 'C'
            self.time1 = 5
            self.flow2 = 'B'
            self.time2 = 4
        else:
            self.due_date = env.now + 6
            self.flow1 = 'C'
            self.time1 = 2
            self.flow2 = 'A'
            self.time2 = 3
        self.ready = env.event()
        self.process = env.process(self.flow(MC))
    
    def flow(self, MC):
        #flow1
        #尚有空機台
        if MC[self.flow1].occupied.count <= 0:
            req = MC[self.flow1].occupied.request()
            yield req
            #排隊等候
        else:
            if len(MC[self.flow1].queue) <= 0:
                MC[self.flow1].queue.append(self)
            else:
                for position in range(len(MC[self.flow1].queue)):
                    #EDD rule
                    if self.due_date < MC[self.flow1].queue[position].due_date:
                        MC[self.flow1].queue.insert(position, self)
                        break   
            yield self.ready
            #離開queue
            MC[self.flow1].queue.pop(0)
            req = MC[self.flow1].occupied.request()
            yield req
        #使用機台
        print('job{} start processing on machine {} at {} min'.format(self.ID,self.flow1, self.env.now))
        yield self.env.timeout(self.time1)
        #離開機台
        MC[self.flow1].occupied.release(req)
        print('job{} finish processing on machine {} at {} min'.format(self.ID,self.flow1, self.env.now))
        #queue有人等候
        if len(MC[self.flow1].queue) > 0:
            MC[self.flow1].queue[0].ready.succeed()
        #----------
        #flow2
        if MC[self.flow2].occupied.count <= 0:
            req = MC[self.flow2].occupied.request()
            yield req
        else:
            if len(MC[self.flow2].queue) <= 0:
                MC[self.flow2].queue.append(self)
            else:
                for position in range(len(MC[self.flow2].queue)):
                    if self.due_date < MC[self.flow2].queue[position].due_date:
                        MC[self.flow2].queue.insert(position, self)
                        break
            self.ready = self.env.event()
            yield self.ready
            MC[self.flow2].queue.pop(0)
            req = MC[self.flow2].occupied.request()
            yield req
        print('job{} start processing on machine {} at {} min'.format(self.ID,self.flow2, self.env.now))
        yield self.env.timeout(self.time2)
        MC[self.flow2].occupied.release(req)
        print('job{} finish processing on machine {} at {} min'.format(self.ID,self.flow2, self.env.now))
        if len(MC[self.flow2].queue) > 0:
            MC[self.flow2].queue[0].ready.succeed()
        #----------
        #所有工序加工完成
        self.finish_time = self.env.now
        print('job{} finish at {}'.format(self.ID, self.finish_time))
        
class Machine:
    def __init__(self, env, _type):
        self.type = _type
        self.queue = []
        self.occupied = simpy.Resource(env)
        #self.working_time = 0

#main
random.seed(1)  
env = simpy.Environment()
MC = {'A' : Machine(env, 'A'),
      'B' : Machine(env, 'B'),
      'C' : Machine(env, 'C')}
env.process(_arrival(env))
env.run(until = sim_time)

#statistic
class _overdue:
    def __init__(self, job_list):
        self.job = []
        self.total_overdue_time = 0
        for job in job_list:
            if job.due_date - job.finish_time < 0 :
                self.job.append(job.ID)
                self.total_overdue_time += job.finish_time - job.due_date

overdue = _overdue(job_list)
