#!/usr/bin/env python
# coding=utf-8

__author__='jkmiao'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def strQ2B(ustring):
    """
    中文全角转半角
    """
    res = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:
            continue
        elif inside_code >=65281 and inside_code <= 65374:
            inside_code -= 65248

        res += unichr(inside_code)
    return res


def leven_distance(s1,s2):
    """
    动态规划实现编辑距离
    """

    s1 = strQ2B(s1.decode('utf-8')).lower()
    s2 = strQ2B(s2.decode('utf-8')).lower()

    m,n = len(s1),len(s2)
    colsize,v1,v2 = m+1,[],[]

    for i in range((n+1)):
        v1.append(i)
        v2.append(i)

    for i in range(m+1)[1:m+1]:
        for j in range(n+1)[1:n+1]:
            cost = 0
            if s1[i-1]==s2[j-1]:
                cost = 0
            else:
                cost = 1
            minValue = v1[j]+1
            if minValue > v2[j-1]+1:
                minValue = v2[j-1]+1
            if minValue >v1[j-1]+cost:
                minValue = v1[j-1]+cost
            v2[j] = minValue
        for j in range(n+1):
            v1[j] = v2[j]

    return v2[n]


def lcs_string(a,b):
    lena,lenb = len(a),len(b)

    # length table
    c = [[0 for i in b] for j in a]

    # direction table
    flag = [[0 for i in b] for j in a]

    for i in range(lena):
        for j in range(lenb):
            if i==0 or j==0:
                c[i][j] = 0
                continue

            if a[i]==b[j]:
                c[i][j] = c[i-1][j-1]+1
                flag[i][j] = 3

            elif c[i-1][j]<c[i][j-1]:
                c[i][j] = c[i][j-1]
                flag[i][j] = 2
            else:
                c[i][j] = c[i-1][j]
                flag[i][j] = 1


    (p1,p2) = (lena-1,lenb-1)
    s = []
    while 1:
        d = flag[p1][p2]
        if d == 3:
            s.append(a[p1])
            p1 -= 1
            p2 -= 1 
        elif d == 2:
            p2 -= 1
        elif d == 1:
            p1 -= 1
        if p1==0 or p2==0:
            # solve the first element without print problem
            if a[p1]==b[p2]:
                s.append(a[p1])
            break
    s.reverse()
    return ''.join(s)


def lcs_len(a,b):
    c = [[0 for j in b] for i in a]
    for i in range(len(a)):
        for j in range(len(b)):
            if i==0 or j==0:
                continue
            if a[i]==b[j]:
                c[i][j] = c[i-1][j-1]+1
            else:
                c[i][j] = max(c[i-1][j],c[i][j-1])
    return c[i][j]




def lcs_from_list(input,jobnames):
    if input in jobnames:
        return input
    res = [(lcs_len(input,jobname),jobname) for jobname in jobnames]
    res.sort()
    return res[-1][1]




if __name__=="__main__":
    a = "mweiog"
    b = ["ihong","mweihong","miaow"]
    print lcs_from_list(a,b)
