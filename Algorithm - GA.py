# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 15:51:56 2017

@author: lonsichang
"""

import numpy as np
import random
import math
import matplotlib.pyplot as plt

#length表示每個變數需用幾個binary數字表示
def compute_length(accuracy, xmax, xmin):
    xrange = (abs(xmax)+abs(xmin))*10**accuracy
    for i in range(0,100):
        if xrange>2**i and xrange<=2**(i+1):
            length = i+1
            break
    return  length
#根據精確度建立在-10到10之間的隨機值done
def randvar(accuracy, xmin, xmax):
    randvalue = random.randint(xmin*10**accuracy,xmax*10**accuracy)/(10**accuracy)
    return randvalue
#產生初始解done
def generate_init_population(accuracy, xmin, xmax):
    population = np.zeros((pz,3))
    for i in range(0,pz):
        population[i]=[randvar(accuracy, xmin, xmax), randvar(accuracy, xmin, xmax), 0]
    return population
#計算答案done
def compute_ans(decimal_array):
    for i in range(0,np.shape(decimal_array)[0]):
        ans = (decimal_array[i, 0]**2+decimal_array[i, 1]**2)/40-math.cos(decimal_array[i, 0])*math.cos(decimal_array[i, 1]/(2**0.5))+1
        decimal_array[i,-1] = ans
    return decimal_array
#計算適應值done
def compute_fitness_value(decimal_array):
    for i in range(0,np.shape(decimal_array)[0]):
        decimal_array[i,2] = 1/(decimal_array[i,2]+1)
    return decimal_array
#將十進位轉為二進位done
def encoding(decimal_array, length, accuracy, xmin):
    binary_array = np.zeros((np.shape(decimal_array)[0],(np.shape(decimal_array)[1]-1)*length+1))
    for i in range(0,np.shape(decimal_array)[0]):
        for j in range(0,np.shape(decimal_array)[1]-1):
            for k in range(0, length):
                binary_array[i,(length*(j+1))-k-1] = (decimal_array[i,j]-xmin)*(10**accuracy)//(2**k)%2
        binary_array[i, -1] = decimal_array[i, -1]
    return binary_array
#排序:依最後一行做排序done
def sorting(array):
    fitness = array[:, -1]
    aftersort = np.zeros(np.shape(array))
    for i in range(0, np.shape(array)[0]):
        aftersort[i, :] = array[np.argsort(fitness)[i], :]
    return aftersort
#終止條件
def end_condition(array, objective, allowance, iteration, max_iteration):
    minvalue = array[0,-1]
    position = 0
    end = False
    ans = np.zeros((1, np.shape(array)[1]))
    for i in range(1,np.shape(array)[0]):
       if(array[i, -1]<minvalue):
           minvalue = array[i, -1]
           position = i
    ans = array[position, :]
    if(abs(minvalue-objective)<=allowance or iteration>=max_iteration):
            end = True
            print("answer is :")
            print("x1 =", ans[0])
            print("x2 =", ans[1])
            print("value =", ans[2])
    else:
        print("not end yet")
        print("minvalue =",ans[2])
        
    return ans, end
#複製done
def copymother(array, copy):
    survived = np.zeros(np.shape(array))
    fitness_rate = np.zeros((copy, 1))
    sumfitness = sum(array[-copy:, -1])
    fitness_rate[0, 0] = array[-copy, -1]/sumfitness
    for i in range(0, copy):
        fitness_rate[i, 0] = fitness_rate[i-1, -1]+array[-copy+i, -1]/sumfitness
    for i in range(0, copy):
        dice = random.random()
        if(dice<=fitness_rate[0, 0]):
            survived[i, :] = array[-copy, :]
        else:
            for j in range(1, copy):
                if(dice<=fitness_rate[j, 0] and dice>fitness_rate[j-1,0]):
                    survived[i, :] = array[-copy+j, :]
    return survived

#交配done
def crossover(array,crossover_rate, copy):
    #計算適應值比率
    fitness_rate = np.zeros((copy, 1))
    sumfitness = sum(array[0:copy, -1])
    fitness_rate[0, 0] = array[0, -1]/sumfitness
    for i in range(1, copy):
        fitness_rate[i, 0] = fitness_rate[i-1, -1]+array[i, -1]/sumfitness
    #開始交配
    max_offspring = np.shape(array)[0]-copy
    now_offspring = 0
    while(now_offspring<max_offspring):
        #選擇兩個母體
        parents = np.zeros(2)
        for i in (0, 1):
            dice = random.random()
            if(dice<=fitness_rate[0, 0]):
                parents[i] = 0
            else:
                for j in range(1, copy):
                    if(dice<=fitness_rate[j, 0] and dice>fitness_rate[j-1,0]):
                        parents[i] = j        
        if(parents[0] != parents[1]):
            #判斷交配與否
            dice2 = random.random()
            if(dice2<crossover_rate):
                dice3 = random.randint(0,29)
                if((max_offspring-now_offspring)>=2):
                    array[copy+now_offspring, 0:dice3] = array[int(parents[0]), 0:dice3]
                    array[copy+now_offspring, dice3+1:-1] = array[int(parents[1]), dice3+1:-1]
                    array[copy+now_offspring+1, 0:dice3] = array[int(parents[1]), 0:dice3]
                    array[copy+now_offspring+1, dice3+1:-1] = array[int(parents[0]), dice3+1:-1]
                    now_offspring += 2
                else:
                    array[copy+now_offspring, 0:dice3] = array[int(parents[0]), 0:dice3]
                    array[copy+now_offspring, dice3+1:-1] = array[int(parents[1]), dice3+1:-1]
                    now_offspring += 1
    return array
#突變
def mutation(array, mutation_rate, copy):
    for i in range(copy, np.shape(array)[0]):
        dice = random.random()
        if(dice<mutation_rate):
            dice2 = random.randint(0, np.shape(array)[1]-2)
            array[i, dice2] = abs(array[i, dice2]-1)
    return array
#將二進位轉為十進位
def decoding(array, length, accuracy, xmin):
    population = np.zeros((np.shape(array)[0], int((np.shape(array)[1]-1)/length+1)))
    for i in range(0, np.shape(population)[0]):
        for j in range(0,np.shape(population)[1]-1):
            decimal = 0
            for k in range(0, length):
                decimal = decimal + array[i, (j+1)*length-k-1]*(2**k)
            population[i,j] = decimal/(10**accuracy)-abs(xmin)
    return population


#設定亂數種子
random.seed()
#設定重複次數
max_attempt = 10
#設定變數範圍
xmax = 10
xmin = -10
#accuracy精確度，表示精確制小數點以下第幾位
accuracy = 2
length = compute_length(accuracy, xmax, xmin)
#設定終止條件
objective = 0
allowance = 0.05
max_iteration = 5
#population size
pz = 10
#複製個數
copy = int(pz*0.5)
#交配率，突變率
crossover_rate = 0.8
mutation_rate = 0.4

print("parameter:")          
print("    min objective function : f(x1, x2)=(x1^2+x2^2)/40-cos(x1)*cos(x2/2^0.5)+1")
print("    variable range :", xmin, "<=xi<=", xmax)
print("    accuracy :", accuracy)
print("    length :", length)
print("    population size : ", pz)
print("    copy number :", copy)
print("    crossover rate :", crossover_rate)
print("    mutation rate :", mutation_rate)
print("    end condition is fitness_value-objective<0.001 or iteration>=50")
print()

outcome = np.zeros((max_attempt, 4))
attempt = 0
while(attempt < max_attempt):
    #第一代
    iteration = 1
    population_decimal = generate_init_population(accuracy, xmin, xmax)
    record = np.zeros((max_attempt, max_iteration))
    while(iteration<=max_iteration):
        print("iteration =",iteration)
        #計算答案
        population_decimal = compute_ans(population_decimal)
        #檢驗是否結束
        ans, end = end_condition(population_decimal, objective, allowance, iteration, max_iteration)
        if(end):
            outcome[attempt] = np.array([ans[0], ans[1], ans[2], iteration])
            break
        population_decimal = compute_fitness_value(population_decimal)
        aftersorting = sorting(population_decimal)
        #加密->複製->交配->突變->解密
        population_binary = encoding(aftersorting, length, accuracy, xmin)
        new_population_binary = copymother(population_binary, copy)
        new_population_binary = crossover(new_population_binary, crossover_rate, copy)
        new_population_binary = mutation(new_population_binary, mutation_rate, copy)
        population_decimal = decoding(new_population_binary, length, accuracy, xmin)
        
        average = np.mean(population_decimal[:, 2])
        print(np.mean(population_decimal[:, 2]))
        print(average)
        record[attempt, iteration-1] = np.mean(population_decimal[:, 2])
        iteration += 1
    attempt +=1

record_average = np.apply_along_axis(np.mean, 0, record)
plt.plot(record_average)
plt.ylabel('fitness_value')
plt.show()  
    
print(outcome)
