#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 16:09:32 2019

@author: ellie
"""

import pandas as pd
import matplotlib.pyplot as plt
import copy
# -----參數設定-----
# --定義常用料的揀貨頻率（被多少percent訂單需求）
freq = 0.3

# ----匯入資料----
data = pd.read_excel('Geek交易紀錄12-1月.xls')
data.columns = data.loc[0,:]
data = data.drop(0)
data = data.set_index('項次')
data = data.groupby(['料號' , '單據號碼']).sum()['數量'].reset_index()
EIQ = data.groupby(['單據號碼', '料號']).sum().reset_index().pivot(index = '單據號碼', columns = '料號', values = '數量').fillna(0)
EIK = data.groupby(['單據號碼', '料號']).count().reset_index().pivot(index = '單據號碼', columns = '料號', values = '數量').fillna(0)

# 一張訂單需求幾種料
order_QTY = data.groupby(['單據號碼']).count()['料號']
order_QTY.name = 'order_QTY'
order_QTY = order_QTY.sort_values(ascending = False) #大小排序

# 訂單數量
order_amount = order_QTY.shape[0]

# ----IQ, IK analysis----
IQ = data.groupby(['料號']).sum()['數量']
IQ.name = 'IQ'
IK = data.groupby(['料號']).count()['數量']
IK.name = 'IK'

# ---IQK
IQK = pd.concat([IQ,IK], axis = 1)

# ----IQ排序與百分比
Accumulated_IQ = []
copy_IQ = copy.copy(IQK)
copy_IQ = copy_IQ.sort_values(by = ['IQ'] , ascending = False)
IQ_percent = copy_IQ['IQ'].apply(lambda x : x/sum(copy_IQ['IQ']))
for i in range(len(IQ_percent)):
    if i == 0:
        Accumulated_IQ.append(IQ_percent[0])
    else:
        Accumulated_IQ.append(Accumulated_IQ[-1] + IQ_percent[i])
copy_IQ['IQ%'] = Accumulated_IQ

# ----IK排序與百分比
Accumulated_IK = []
copy_IK = copy.copy(IQK)
copy_IK = copy_IK.sort_values(by = ['IK'] , ascending = False)
IK_percent = copy_IK['IK'].apply(lambda x : x/ sum(IQK['IK']))

for i in range(len(IK_percent)):
    if i == 0:
        Accumulated_IK.append(IK_percent[0])
    else:
        Accumulated_IK.append(Accumulated_IK[-1] + IK_percent[i])
copy_IK['IK%'] = Accumulated_IK
copy_IK = copy_IK.reset_index()
plt.plot(IK_percent.cumsum().values)


quantity = len([i for i in copy_IK['IK%'] if i < freq])
freq_SKU = copy_IK.iloc[0:quantity , :]

# ----IQ, IK繪圖----
plt.figure()
IQK['IQ'].sort_values(ascending = False).plot()
plt.xlabel('IQ', size = 20) 
plt.figure()
IQK['IK'].sort_values(ascending = False).plot()
plt.xlabel('IK', size = 20) 

plt.figure()
plt.scatter(IQK['IQ'], IQK['IK'], s = 20, alpha = 0.4)
plt.tick_params(labelsize=13)
plt.xlabel('IQ', size = 20) 
plt.ylabel('IK', size = 20) 

#-------- 匯出資料 ---------
EIQ.to_csv('EIQ.csv')
EIK.to_csv('EIK.csv')
IQK.to_csv('IQK.csv')
freq_SKU.to_csv('常用料資訊.csv')
