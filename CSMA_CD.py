import random
import copy
import time
'''
时间单位：0.05us
距离单位：0.01km，因此两站点的最大距离为500单位
（对应电磁波在1km电缆上的传播时延约为5us）
信道带宽：10Mbps
'''
class Channel():
    '''定义信道类'''
    def __init__(self):
        '''
        下面定义信道上的信号，长度为500，每个元素代表一个距离单位；
        每个位置包含的信号用一个list表示，空表表示没有信号，非空表表示有信号；
        1表示正向信号，-1表示反向信号；0表示源点信号，即信号的起点；
        '''
        self.signal = [[] for _ in range(500)]


    def propagate(self):
        '''信号在信道上传播，参数为信号的起点的站点'''
        signal_copy = copy.deepcopy(self.signal)
        for i in range(500):
            if len(signal_copy[i]) > 0:
                for j in range(len(signal_copy[i])):
                    if i != 0 and i != 499:
                        if signal_copy[i][j] == 0:
                            self.signal[i+1].append(1)
                            self.signal[i-1].append(-1)
                            self.signal[i].remove(0)
                        elif signal_copy[i][j] == 1:
                            self.signal[i+1].append(1)
                            self.signal[i].remove(1)
                        elif signal_copy[i][j] == -1:
                            self.signal[i-1].append(-1)
                            self.signal[i].remove(-1)
                    elif i == 0:
                        if signal_copy[i][j] == 0:
                            self.signal[i+1].append(1)
                            self.signal[i].remove(0)
                        elif signal_copy[i][j] == -1:
                            self.signal[i].remove(-1)
                    elif i == 499:
                        if signal_copy[i][j] == 0:
                            self.signal[i-1].append(-1)
                            self.signal[i].remove(0)
                        elif signal_copy[i][j] == 1:
                            self.signal[i].remove(1)
                    
        
        

class Node():
    '''定义站点类，初始化参数为站点的ID和位置'''
    def __init__(self, id: int, pos: int, channel: Channel):
        self.id = id            # 站点的ID
        self.pos = pos          # 站点的位置
        self.channel = channel  # 站点所在的信道
        self.data = False       # 当前站点是否有数据要发送
        self.busy = False       # 当前信道是否正忙
        self.collision = False  # 当前站点是否检测到冲突信号
        self.data_length = 0    # 当前站点要发送的数据长度
        self.backoff_time = 0   # 当前站点退避的时间
        self.channel_free = 192 # 当前站点信道空闲的时间
        self.sending_time = 0   # 当前站点发送数据的时间
        self.failed_times = 0   # 当前站点发送数据失败的次数
        if self.pos >= 500 or self.pos < 0:
            raise ValueError('站点位置超出范围')
    
    def __call__(self, data_length: int):
        '''
        站点完成单位时间内的全部工作，参数为数据长度；
        data_length长度应大于64，输入单位为字节；  
        不发送数据时，data_length应为0；
        1. 监听信道上是否正忙，是否有冲突信号；
        2. 如果信道上没有冲突信号，且当前站点有数据要发送，则发送数据；
        3. 如果信道上有冲突信号，且当前站点正在发送数据，则停止发送数据；
        4. 如果信道上有冲突信号，且当前站点没有发送数据，则等待下一次发送机会；
        '''
        if self.data_length*16 - self.sending_time != 0 and data_length != 0:
            print('当前站点还有数据未发送，无法重新设置数据长度')
        elif data_length != 0:
            self.data_length = data_length

        if data_length > 0 and data_length < 64:
            raise ValueError('数据长度应大于64字节')
        
        if self.data_length > 0:
            self.data = True
        else:
            self.data = False

        self.listen()
        if self.backoff_time == 0: # 退避时间到
            if self.data == True: # 当前站点有数据要发送
                if self.busy == False and self.channel_free == 192: # 信道空闲
                    self.send()
                    print('站点{}发送数据...({}/{} Byte)'.format(self.id, self.sending_time//16, self.data_length))
                    if self.sending_time == self.data_length * 8 * 2:
                        self.stop()
                        self.data = False
                        self.failed_times = 0
                        self.data_length = 0
                        print('站点{}发送数据成功'.format(self.id))
                elif self.collision == True: # 信道冲突
                    self.stop()
                    self.failed_times += 1
                    self.backoff()
                    print('站点{}发送数据失败'.format(self.id))
                else:
                    print('站点{}等待下一次发送机会'.format(self.id))
            else: # 当前站点没有数据要发送
                print('站点{}没有数据要发送'.format(self.id))
        else: # 退避时间未到
            self.backoff_time -= 1
            print('站点{}退避时间未到，剩余{}'.format(self.id, self.backoff_time))


    def listen(self):
        '''监听信道上是否正忙（并统计空闲时间），是否有冲突信号'''
        if self.sending_time == 0:
            if self.channel.signal[self.pos] == []:        
                self.busy = False
                self.collision = False
                if self.channel_free < 192:
                    self.channel_free += 1
            else:
                self.busy = True
                self.collision = False
                self.channel_free = 0
        else:
            if len(self.channel.signal[self.pos]) > 0:
                self.busy = True
                self.collision = True

    def send(self):
        '''发送数据'''
        self.channel.signal[self.pos] = [0]  # 在信道上放置信号
        self.sending_time += 1  # 发送时间加1

    def stop(self):
        '''停止发送数据'''
        self.sending_time = 0

    def backoff(self):
        '''截断二进制指数退避算法'''
        if self.failed_times >= 16:
            pass
        else:
            k = min(self.failed_times, 10)
            self.backoff_time = random.randint(0, 2**k-1)*1024
        
if __name__ == '__main__':
    channel = Channel()
    node1 = Node(1, 0, channel)
    node2 = Node(2, 29, channel)
    node3 = Node(3, 49, channel)
    print('t = 1')
    node1(64)
    node2(64)
    node3(64)
    channel.propagate()
    for t in range(1,1500):
        print('t =', t+1)
        node1(0)
        node2(0)
        node3(0)
        channel.propagate()


