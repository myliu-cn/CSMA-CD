# CSMA-CD

## 项目介绍
本项目是计算机网络CSMA/CD协议的仿真程序

## 实验环境  
Python              3.9.16  

## 项目内容  
1. 项目中采用的单位
>   时间单位：0.05us  
    距离单位：0.01km  
    （对应电磁波在1km电缆上的传播时延约为5us）  
    信道带宽：10Mbps    
2. 项目中的类  

**Channel**   
Channel 类实现了信道的传播功能，包括信号在信道上传播和信道的初始化。在 Channel 类中，信号的传播采用的是简单的串行传播方式，即在原信号的左右两侧分别添加正向和反向信号，同时删除原信号。  
> ***self.channel***     
    信道上的信号，长度为500，每个元素代表一个距离单位； 
    每个位置包含的信号用一个list表示，空表表示没有信号，非空表表示有信号；
    1表示正向信号，-1表示反向信号；0表示源点信号，即信号的起点；

> ***self.propagate()***  
    模拟信号在信道上的传输，propagate 方法首先复制一份当前信号列表 self.signal，并遍历每个位置。
    对于非边界位置（即不是第一个或最后一个位置），如果该位置当前信号值为0，则将1值添加到下一个位置的信号列表中，将-1值添加到前一个位置的信号列表中，并从该位置的信号列表中删除0值；如果该位置当前信号值为1，则将1值添加到下一个位置的信号列表中，并从该位置的信号列表中删除1值；如果该位置当前信号值为-1，则将-1值添加到前一个位置的信号列表中，并从该位置的信号列表中删除-1值。
    对于边界位置，如果该位置为第一个位置，则将1值添加到下一个位置的信号列表中（如果该位置当前信号值为0），或从该位置的信号列表中删除-1值（如果该位置当前信号值为-1）；如果该位置为最后一个位置，则将-1值添加到前一个位置的信号列表中（如果该位置当前信号值为0），或从该位置的信号列表中删除1值（如果该位置当前信号值为1）。
    这样就完成了信号在位置之间的传输。

**Node**  
Node 类实现了一个节点的基本功能，包括监听信道状态、发送数据等。每个节点的发送行为包括两个步骤：等待信道空闲、发送数据。当节点监听到信道空闲时，它会等待一段时间（96bits的传输时间），然后再发送数据。如果发送的过程中检测到了冲突信号，节点会停止发送数据，并进行截断二进制指数退避。

初始化参数为:
> ***self.id***  
站点的ID；  
> ***self.pos***  
站点在信道的位置；  
> ***self.channel***  
站点所在的信道；  

调用时：
> ***self.__call__()***  
每经过一个时间单位，就需要调用一次 ***self.__call__()*** 函数，调用时传入参数为所要发送数据长度（单位为字节，且应 >= 64）；若不需要传输数据，则传入参数0.

3. 程序的运行
注意：运行时不需要修改类中的函数和参数。  
(1) 定义信道和站点  
(2) 在每个时间单位下，对每个站点调用一次 ***self.__call__()*** 函数；  
(3) 发送数据只用在数据准备好的那一时刻发送即可，后续时间内均应传入参数0（无数据发送）；  
(4) 每个时刻末尾调用 ***channel.propagate()***

