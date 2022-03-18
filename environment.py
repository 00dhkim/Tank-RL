import numpy as np
import random

import TankAPI

IP = '218.49.147.131'
PLAYERNAME = 'dohyun'
TURN = 100
DILATION = 100

# 강화학습 하기에 편리하도록 인터페이스를 제공하는 클래스
class Environment():
    '''
    ### state
    
    0) 32x32 전체 지도, 0은 모르는 공간, 1~4는 아군 탱크, 5는 적 탱크, 6은 장애물, 7은 빈 공간
    1) 1번 전차 정보, [HP, AP, angle]
    2) 2번 전차 정보, [HP, AP, angle]
    3) 3번 전차 정보, [HP, AP, angle]
    4) 4번 전차 정보, [HP, AP, angle]
    
    # memo: 필요 시 아군탱크, 적탱크, 장애물 리스트를 각각 지정할 수도.
    
    
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
        # state
        self.map = np.zeros((32, 32), dtype=np.int32)
        self.tank_info = np.zeros((4, 3), dtype=np.int32)
        
        # action
        self.action_space = [0, 1, 2, 3, 4, 5, 6, 7]
        self.action_size = 8
        
        self.tankAPI = TankAPI.TankAPI()
        self.turn_tank = 1 # 우리 탱크(1 ~ 4) 중 누구의 턴인지
    
    # 처음에 해주는 초기화
    def reset(self, ip=IP, playername=PLAYERNAME, turn=TURN, dilation=DILATION):
        self.tankAPI.ip, self.tankAPI.playername, self.tankAPI.turn, self.tankAPI.dilation = ip, playername, turn, dilation
        
        self.tankAPI.session_resource()
        self.tankAPI.session_create()
        self.tankAPI.session_join()
        status = self.tankAPI.game_status()
        agents = status['responses']['data']['message']['agent_info']['agent']
                
        for agentIdx in range(len(agents)):
            agent = agents[agentIdx]
            self.tank_info[agentIdx] = [agent['hp'], agent['ap'], 0]
        
        self._set_map()
    
    def _set_map(self):
        status = self.tankAPI.game_status()
        agents = status['responses']['data']['message']['agent_info']['agent']
        
        # 아군탱크 or 적탱크 or 빈공간이었던 부분은 모르는 공간이다.
        # 장애물 위치만 유지 (장애물 파괴안됨)
        for i in range(32):
            for j in range(32):
                if self.map[i][j] == 1 or \
                    self.map[i][j] == 2 or \
                    self.map[i][j] == 3 or \
                    self.map[i][j] == 4 or \
                    self.map[i][j] == 5 or \
                    self.map[i][j] == 7:
                    self.map[i][j] = 0
        
        _, gameMap = self.tankAPI.game_view()
        for i in range(32):
            for j in range(32):
                if gameMap.game_map[i][j] == 1: # 상대 탱크
                    self.map[i][j] = 5
                elif gameMap.game_map[i][j] == 3: # 장애물
                    self.map[i][j] = 6
        
        for agentIdx in range(len(agents)):
            agent = agents[agentIdx]
            
            i, j = self._location2idx(agent['location'])
            self.map[i][j] = agentIdx+1 # 아군 탱크

            # 아군 탱크에서 5만큼 떨어진 공간까지는 빈공간인걸 안다.
            dij = [(i,j) for i in range(-5, 6) for j in range(-5, 6)] # (-5, -5) ~ (5, 5)
            for d in dij:
                ii = d[0] + i
                jj = d[1] + j
                if ii < 0 or ii > 31 or jj < 0 or jj > 31:
                    continue
                if self.map[ii][jj] == 0:
                    self.map[ii][jj] = 7
                    print('', end='')
            
            assert self.tank_info[agentIdx][2]%45 == 0
            # 바라보는 방향으로 빈 공간을 안다.
            angle_directions = [(1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1), (1,1)]
            angleIdx = self.tank_info[agentIdx][2] // 45
            angle = angle_directions[angleIdx] # angle: (a, b) 모양
            ii, jj = i, j # 반복문 내에서만 쓰는 변수
            while True:
                ii += angle[0]
                jj += angle[1]
                if ii < 0 or ii > 31 or jj < 0 or jj > 31:
                    break
                if self.map[ii][jj] == 0:
                    self.map[ii][jj] = 7
                    print('', end='')
    
    
    def _location2idx(self, location):
        x, y = location[0], location[1]
        j = (x-25200)//1000
        i = (y-147450)//1000
        
        assert 0 <= j <= 31 and 0 <= i <= 31
        return i, j # usage: map[i][j]
    
    # 현재 조종할 탱크를 기준으로 수행할 수 있는 액션만 반환
    def legal_actions(self):
        actions = []
        
        status = self.tankAPI.game_status()
        agents = status['responses']['data']['message']['agent_info']['agent']
        agent = agents[self.turn_tank-1]
        
        
        pass
    
    # 액션을 받아 한 단계 실행하는 함수
    def step(self, action):
        
        
        
        # TODO: next_state, reward, done, info = env.step(action)
        pass
    
    # 지금까지 진행된 상황 뿌려주기
    def render(self):
        print('-'*62)
        for i in range(32):
            for j in range(32):
                if self.map[i][j] == 0:
                    print(' ', end=' ') # 모르는공간
                elif self.map[i][j] == 5:
                    print('T', end=' ') # 상대탱크
                elif self.map[i][j] == 6:
                    print('O', end=' ') # 장애물
                elif self.map[i][j] == 7:
                    print('·', end=' ') # 빈공간
                else:
                    print(self.map[i][j], end=' ')
            print()
        print('-'*62)
        print()
    

if __name__ == '__main__':
    env = Environment()
    env.reset()
    print('reset done.')
    env.render()
    