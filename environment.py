import numpy as np
import random

import TankAPI

IP = '211.195.1.44'
PLAYERNAME = 'dohyun'
TURN = 100
DILATION = 100

# 강화학습 하기에 편리하도록 인터페이스를 제공하는 클래스
class Environment():
    '''
    ### state
    
    type: list of 38 elements
    
     0) 1번 전차 HP
     1) 1번 전차 AP
     2) 1번 전차 x 위치
     3) 1번 전차 y 위치
     4) 1번 전차 주포 각도
     5) 2번 전차 HP
     6) 2번 전차 AP
     7) 2번 전차 x 위치
     8) 2번 전차 y 위치
     9) 2번 전차 주포 각도
    10) 3번 전차 HP
    11) 3번 전차 AP
    12) 3번 전차 x 위치
    13) 3번 전차 y 위치
    14) 3번 전차 주포 각도
    15) 4번 전차 HP
    16) 4번 전차 AP
    17) 4번 전차 x 위치
    18) 4번 전차 y 위치
    19) 4번 전차 주포 각도
    20) 상대 1번 전차 x 위치
    21) 상대 1번 전차 y 위치
    22) 상대 2번 전차 x 위치
    23) 상대 2번 전차 y 위치
    24) 상대 3번 전차 x 위치
    25) 상대 3번 전차 y 위치
    36) 상대 4번 전차 x 위치
    37) 상대 4번 전차 y 위치
    
    
    ### action
    
    type: single integer
    
    0: attack
    1: rotate +45
    2: rotate -45
    3: move forward
    4: move backward
    5: move left
    6: move right
    7: turn end
    
    
    ### reward
    
    - 적 전차 맞추면 +50
    - 적 전차 잡으면 +10
    - 아군 전차 맞으면 -50
    - 아군 전차 잡히면 -10
    
    '''
    
    def __init__(self):
        self.state = [None] * 38
        self.action_space = [0, 1, 2, 3, 4, 5, 6, 7]
        self.state_size = 38
        self.action_size = 8
        self.tankAPI = TankAPI.TankAPI(IP, PLAYERNAME)
    
    # 처음에 해주는 초기화
    def reset(self, ip=IP, playername=PLAYERNAME, turn=TURN, dilation=DILATION):
        self.tankAPI.session_resource()
        self.tankAPI.session_create()
        self.tankAPI.session_join()
        status = self.tankAPI.game_status()
        agents = status['responses']['data']['message']['agent_info']['agent']
        
        
    
    # 액션을 받아 한 단계 실행하는 함수
    def step(self, action):
        
        
        
        # TODO: next_state, reward, done, info = env.step(action)
        pass
    
    # 지금까지 진행된 상황 뿌려주기
    def render(self):
        pass
    
    pass
