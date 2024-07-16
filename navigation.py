#coding=utf-8
#Title: navigation.py
#Author: 李易伦
#Date: 2024-7-14
#Version: 1.0
#Description: 导航算法（Dijkstra,邻接表存图）
#Usage: python navigation.py
#©2024 allenlee
import os,time

class side():
    y=0
    l=0
    def __init__(self,y,l):
        self.y=y
        self.l=l
n=0
ans=[]#邻接表
pre=[]#前驱
d=[]#距离
v=[[False]*(n+2)]#是否访问
s=0#起点
t=0#终点
nameDict={
    0:None,
    1:"T1",
    2:"T2",
    3:"T3",
    4:"T4",
    5:"T5",
    6:"T6",
    7:"T7",
    8:"T8",
    9:"T9",
    10:"T10",
}
def dijkstra():
    global n,ans,pre, d,v,s,t
    #init d
    v=[False]*(n+2)#是否访问
    d=[1e9]*(n+2)#是否访问
    
    pre=[0]*(n+2)
    
    for i in range(1,n+1):
        for j in range(len(ans[i])):
            if i==s:
                d[ans[i][j].y]=ans[i][j].l
            else:
                d[ans[i][j].y]=1e9
                pre[ans[i][j].y]=0
   
    pre[s]=-1
    d[s]=0
    while not v[t]:
        x=0
        lowest=1e9+10
        for j in range(1,n+1):
            if not v[j] and d[j]<lowest:
                lowest=d[j]
                x=j
        v[x]=True
        for i in range(len(ans[x])):
            y=ans[x][i].y
            l=ans[x][i].l
            if d[y]>d[x]+l:
                d[y]=d[x]+l
                pre[y]=x
def test():
    global n,ans,pre,d,v,s,t
    n=4
    ans=[[] for i in range(n+1)]
    s=1
    t=4
    ans[1].append(side(2,10))
    ans[1].append(side(3,2))
    ans[2].append(side(4,1))
    ans[3].append(side(2,1))
    ans[3].append(side(4,10))
    dijkstra()
    print("LEN=",d[t],sep="")
    back=t
    res=[]
    while back>0:
        res.append(nameDict[back])
        back=pre[back]
    res.append(nameDict[s])
    res.reverse()
    print("PATH=",res,sep="")
    return [res,d[t]]
    
if __name__=="__main__":
    os.system("cls")
    stt=time.time()
    test()
    print("TIME=",(time.time()-stt),sep="")