# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 22:32:51 2020

@author: cimlab
"""


from gurobipy import *
import pandas as pd
import numpy as np
import os
import csv

#EXP_RESULT = []

sheet_ = ['Order','Pod', 'Distance']

path = 'C:\\Users\\cimlab\\Desktop\\潘\\ver_2.0'
files = os.listdir(path)
files = [f for f in files if f[:4] == 'exp1']
fileGroup = list(set([f.split('_')[1] for f in files]))
fileGroup.sort()

for group in fileGroup:
    files_xlsx = [f for f in files if f.split('_')[1] == group]  

    # Model
    for file_name in files_xlsx:
        demand = pd.read_excel('{}\\{}'.format(path,file_name), sheet_name = sheet_[0])
        demand = demand.iloc[:, 1:]
        storage = pd.read_excel('{}\\{}'.format(path,file_name), sheet_name = sheet_[1])
        storage = storage.iloc[:, 1:]
        layout = pd.read_excel('{}\\{}'.format(path,file_name), sheet_name = sheet_[2])
        layout = layout.iloc[:, 1:]
        '''Index'''
        S = demand.shape[1] 
        N = demand.shape[0] 
        R = storage.shape[0] 
        print('--items--:', S,'--pods--',R)
         # T slot param
        C = 2
        T = R * N #int(R * math.ceil(N/C)) #int(R * math.ceil(N/C))#int(approximation * 2 *N)
           
        #-----------------------------------------            
        
        '''Model'''
        #decision var
        yit = [[] for t in range(T)] #訂單與slot
        xjt = [[] for t in range(T)] #pod and slot
        asijt = pd.DataFrame(np.zeros((N, T)))
        alpha_jt = [[] for t in range(T)] #num of pod visit
        
        
        # creat PPS model
        pps = Model("SEQ_PPS_model_new")
        
        #creat var
        pps.setParam("PreSOS1BigM",  1000000)
        BIG_M = pps.Params.PreSOS1BigM #bigM
        
        #decision variable
        for t in range(T):
            for i in range(N):
                yit[t].append(pps.addVar(vtype = GRB.BINARY)) #訂單出現
        print('var1 done')
        for t in range(T):
            for j in range(R):
                xjt[t].append(pps.addVar(vtype = GRB.BINARY)) #貨架出現
        print('var2 done')
        for t in range(T):
            asijt.iloc[:,t] = [asijt.iloc[:,t].apply(lambda x: ([[pps.addVar(vtype = GRB.CONTINUOUS, lb = 0) for s in range(S)] for p in range(R)]), 1)] #是否揀
        print('var3 done')
        for t in range(T):
            for j in range(R):
                alpha_jt[t].append(pps.addVar(vtype = GRB.CONTINUOUS, lb=0))
        print('var4 done')
        
        pps.update()
        print('var ALL done')
        
        '''constraint'''
        #2
        for t in range(T):
            pps.addConstr(quicksum( xjt[t][j] for j in range(R) ) <= 1)
        print('cons 2 done')
        
        #3
        for t in range(T):
            pps.addConstr(quicksum( yit[t][i] for i in range(N) ) <= C)
        print('cons 3 done')
        
        #4
        for i in range(N):
            for t in range(2,T):
                for j in range(1,t):
                    for k in range(1,j+1):
                        pps.addConstr(yit[t-j-1][i] + yit[t][i] <= yit[t-k][i] + 1)
        print('cons 4 done')
        
        #5
        for i in range(N):
            for s in range(S):
                pps.addConstr(quicksum(quicksum(asijt.iloc[i,t][j][s] for j in range(R)) for t in range(T)) == demand.iloc[i,s], "pickqty_demand" )
        print('cons 5 done')
        
        #6
        for j in range(R):
            for s in range(S):
                pps.addConstr(quicksum(quicksum(asijt.iloc[i,t][j][s] for i in range(N)) for t in range(T)) <= storage.iloc[j,s], "pickqty_storage")
        print('cons 6 done')
            
        #7
        for t in range(T):
            for j in range(R):
                for i in range(N):
                    for s in range(S):
                        pps.addConstr( asijt.iloc[i,t][j][s] <= BIG_M * xjt[t][j] , "storage related asijt constraint " )
        print('cons 7 done')
        
        #8          
        for t in range(T):
            for i in range(N):
                for j in range(R):
                    for s in range(S):
                        pps.addConstr( asijt.iloc[i,t][j][s] <= BIG_M * yit[t][i] , "order demand related asijt constraint " )
        print('cons 8 done')
        
        #9
        for j in range(R):
            for t in range(1,T):
                pps.addConstr(alpha_jt[t][j] >= xjt[t][j]- xjt[t-1][j])
        print('cons 9 done')
            
        print('cons done')
        
        '''OBJ'''
        obj =  quicksum(xjt[0][j] * layout.iloc[j,0] for j in range(R)) + quicksum(layout.iloc[j,0] * alpha_jt[t][j] for j in range(R) for t in range(1,T)) 
        pps.setObjective(obj,GRB.MINIMIZE)
        pps.setParam('TimeLimit', 60*60*2)
        
        #optimize
        pps.optimize()
        print('optimize start')
        
        #print best
        print('---Result----')        
        print("RunTime:", pps.RunTime)
        print('Total Distance:', pps.objVal)
        print('------------------------------------------')
        with open('C:\\Users\\cimlab\\Desktop\\潘\\ver_2.0\\EXP1\\Output\\EXP1_MIP_{}p{}.csv'.format(group, R), 'a', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([file_name,pps.RunTime,pps.NodeCount, pps.objVal])

'''
#----------------print_result------------------------------
RESULT_DATA = []
for n in range(nSolutions):
    pps.setParam(GRB.Param.SolutionNumber, n)
    #print('solnum:', pps.Params.SolutionNumber)
    
    
    
    results = pd.DataFrame(columns=('pod', 'order'))
    asijt_data = pd.DataFrame(np.zeros((1,N)))    
    
    for t in range(T):
        #print("In slot {}".format(t))
        order_temp = []
        
        for j in range(R):
            if xjt[t][j].Xn == 1:
                pod_temp = j
                #print("pod {} is here".format(j))
        for i in range(N):
            if yit[t][i].Xn == 1:
                #print("order {} is picking".format(i))
                order_temp.append(i)
                
        results.loc[t] = [pod_temp,order_temp]
    
    #---計算asijt揀貨量
    for t in range(T):
        list_ = []
        for i in range(N):
            list_.append([k for k in [[asijt.iloc[i,t][j][s].Xn for s in range(S)] for j in range(R)]])
        
        asijt_data.loc[t+1] = list_
    asijt_data = asijt_data.drop(asijt_data.index[0]).reset_index(drop = True)

    
    pick_list = []
    for t in range(T):
        temp=[]
        for i in results.loc[t,'order']:
            temp.append(asijt_data.iloc[t,i])
        pick_list.append(temp)
    results['picking_detail'] = pick_list
    
    RESULT_DATA.append(results)
EXP_RESULT.append(RESULT_DATA)
    
#order.save()     
    #pps.setParam("OutputFlag", 0) # 不顯示求解過程

dist = 0
for t in range(T):
    for j in range(R):
        dist += alpha_jt[t][j].Xn
print(dist)
'''        
                
