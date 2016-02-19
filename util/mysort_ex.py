#!/usr/bin/env python
# coding=utf-8

import random


data = [ random.randint(0,1000) for i in range(2000) ]


def bubble_sort(data):
    num = len(data)
    for i in xrange(num):
        for j in xrange(num-1-i):
            if data[j+1]<data[j]:
                data[j+1],data[j] = data[j],data[j+1]
    return data


def select_sort(data):
    if len(data)<2:
        return data
    num = len(data)
    for i in xrange(num-1):
        minv = i
        for j in xrange(i,num):
            if data[j]<data[minv]:
                minv = j
        if minv!=i:
            data[i],data[minv] = data[minv],data[i]
    return data



def insert_sort(data):
    if len(data)<2:
        return data
    num = len(data)
    for i in xrange(1,num):
        value = data[i]
        j = i-1
        while j>=0 and data[j]>value:
            data[j+1] = data[j]
            j -= 1
        data[j+1] = value
    return data



def partion(data,a,b):
    x = data[b]
    i = a
    for j in xrange(a,b):
        if data[j]<x:
            data[i],data[j] = data[j],data[i]
            i+=1
    data[i],data[b] = data[b],data[i]
    return i


def quick_sort(data,a,b):
    if a>=b:
        return
    i = partion(data,a,b)
    quick_sort(data,a,i-1)
    quick_sort(data,i+1,b)
    return data

def qsort(data):
    if len(data)<2:
        return data
    return qsort([x for x in data[1:] if x<data[0]])+data[0:1]+qsort([x for x in data[1:] if x>=data[0]])

def test():
    print data[:10]
    print 'bubble_sort'
    print  bubble_sort(data)[:10]
    print 'select_sort'
    print select_sort(data)[:10]
    print 'insert_sort'
    print insert_sort(data)[:10]
    print 'quick_sort'
    print quick_sort(data,0,len(data)-1)[:10]
  #  print 'quick_sort2' # easy to reach rescrsion max depth, or   import sys; sys.setrecursionlimit(99999)
  #  print qsort(data)[:10]
    print 'python lib sort'
    print sorted(data)[:10]


test()



