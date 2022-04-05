import time
import requests
from requests.exceptions import ChunkedEncodingError
import json

# 서버와 통신하는 클래스
class TankAPI():
    
    def __init__(self):
        self.key = None
        self.ip = None
        self.playername = None
        self.turn = None
        self.dilation = None
    
    def session_resource(self):
        resource = requests.get("http://20.196.214.79:5050/session/resource", params={"ip": self.ip}, timeout=60)
        # print('resource: ', resource.status_code, resource.json()["message"])
        if resource.json()['message'] != 'Opened':
            raise Exception('receiver is closed')
    
    def session_create(self, isWindowMode=True, res_x=1920, res_y=1080):
        params = {
            'ip': self.ip,
            'isWindowMode': isWindowMode,
            'Res_X': res_x,
            'Res_Y': res_y
        }
        print('session create', end='', flush=True)
        while True:
            try:
                print('..', end='', flush=True)
                create = requests.post("http://20.196.214.79:5050/session/create", params, timeout=60)
            except ConnectionRefusedError or ConnectionResetError or ChunkedEncodingError or ConnectionError:
                time.sleep(1)
                continue
            if create.status_code == 200:
                break
        print('done!')
        self.key = json.loads(create.content)['key']
    
    def session_join(self):
        params = {"key": self.key, "playername": self.playername}
        join = requests.post("http://20.196.214.79:5050/session/join", data=params, timeout=60)
        print('join..', end='', flush=True)
        while True:
            if join.status_code == 200:
                print('done!')
                self._game_start()
                break
            else:
                print('..', end='', flush=True)
                join = requests.post("http://20.196.214.79:5050/session/join", data=params, timeout=60)
    
    def _game_start(self):
        startParams = {
            'key': self.key,
            'playername': self.playername,
            'turn': self.turn,
            'dilation': self.dilation
        }
        print('game start..', end='', flush=True)
        join = requests.post("http://20.196.214.79:5050/game/start", data=startParams, timeout=60)
        while True:
            if join.status_code == 200:
                print('done!')
                break
            else:
                print('..', end='', flush=True)
                join = requests.post("http://20.196.214.79:5050/game/start", data=startParams, timeout=60)
    
    def game_status(self):
        print('s', end='', flush=True)
        statusParam = {"key": self.key, "playername": self.playername}
        while True:
            print('.', end='', flush=True)
            try:
                statusResponse = requests.get("http://20.196.214.79:5050/game/status", statusParam, timeout=60)
            except ConnectionRefusedError or ConnectionResetError or ChunkedEncodingError or ConnectionError:
                time.sleep(1)
                continue
            if statusResponse.status_code == 200:
                status = json.loads(statusResponse.content)
                print('!', end='', flush=True)
                
                try:
                    if status['responses']['error']['code'] == 400:
                        # 게임종료
                        self.session_end()
                        return 'gameEnd'
                except KeyError:
                    pass
                return status
    
    def _dirTxt(self, dirInt):
        if dirInt == 0:
            return "Foword"
        elif dirInt == 1:
            return "Left"
        elif dirInt == 2:
            return "Back"
        elif dirInt == 3:
            return "Right"
    
    def agent_move(self, uid, direction):
        moveParam = {'key': self.key, 'uid': uid, 'direction': direction}
        while True:
            try:
                move = requests.post("http://20.196.214.79:5050/agent/move", data=moveParam, timeout=60)
            except ConnectionRefusedError or ConnectionResetError or ChunkedEncodingError or ConnectionError:
                time.sleep(1)
                continue
            if move.status_code == 200:
                break
    
    def agent_attack(self, uid):
        attackParam = {'key':self.key, 'uid': uid}
        while True:
            try:
                attack = requests.post("http://20.196.214.79:5050/agent/attack", data=attackParam, timeout=60)
            except ConnectionRefusedError or ConnectionResetError or ChunkedEncodingError or ConnectionError:
                time.sleep(1)
                continue
            if attack.status_code == 200:
                break
    
    def agent_rotate(self, uid, angle):
        '''
        angle: 45 or -45
        45로 주면 오른쪽으로 돌림
        '''
        rotateParam = {'key': self.key, 'uid': uid, 'angle': angle}
        while True:
            try:
                rotate = requests.post("http://20.196.214.79:5050/agent/rotate", data=rotateParam, timeout=60)
            except ConnectionRefusedError or ConnectionResetError or ChunkedEncodingError or ConnectionError:
                time.sleep(1)
                continue
            if rotate.status_code == 200:
                break
    
    def game_view(self):
        status = self.game_status()
        objects = [] # 탱크 및 장애물들
        agents = status['responses']['data']['message']['agent_info']['agent']
        for agent in agents:
            print('v', end='', flush=True)
            uid = agent['uid']
            while True:
                print('.', end='', flush=True)
                try:
                    view = requests.get(f"http://20.196.214.79:5050/game/view", params={"key": self.key, "uid": uid}, timeout=60)
                except ConnectionRefusedError or ConnectionResetError or ChunkedEncodingError or ConnectionError:
                    time.sleep(1)
                    continue
                if view.status_code == 200:
                    break
        
            # 상대 탱크와 장애물 표시
            try:
                info = json.loads(view.content)["responses"]["data"]["message"]["info"]
            except KeyError:
                if json.loads(view.content)['responses']['error']['message']['reason'] == 'This Agent is not avalilable':
                    continue
            for object in info:
                if object not in objects and object["IsExistObject"] == True:
                    objects.append(object)
            print('!', end='', flush=True)
        
        # # 아군 탱크 표시
        # for agent in agents:
        #     self.gameMap.set_map(agent['location'][0], agent['location'][1], 9)
        return objects
    
    def game_endturn(self):
        endturnParam = {'key': self.key, 'playername': self.playername}
        while True:
            try:
                endturn = requests.post("http://20.196.214.79:5050/game/endturn", data=endturnParam, timeout=60)
            except ConnectionRefusedError or ConnectionResetError or ChunkedEncodingError or ConnectionError:
                time.sleep(1)
                continue
            if endturn.status_code == 200:
                break
    
    def session_reset(self):
        resetParam = {'key':self.key}
        while True:
            try:
                reset = requests.post("http://20.196.214.79:5050/session/reset", data=resetParam, timeout=60)
            except ConnectionRefusedError or ConnectionResetError or ChunkedEncodingError or ConnectionError:
                time.sleep(1)
                continue
            if reset.status_code == 200:
                break
    
    def session_end(self):
        sessionEndParam = {'key': self.key, 'ip': self.ip}
        while True:
            try:
                sessionEnd = requests.post("http://20.196.214.79:5050/session/end", data=sessionEndParam, timeout=60)
            except ConnectionRefusedError or ConnectionResetError or ChunkedEncodingError or ConnectionError:
                time.sleep(1)
                continue
            if sessionEnd.status_code == 200:
                break
