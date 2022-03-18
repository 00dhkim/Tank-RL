import requests
import json

# 서버와 통신하는 클래스
class TankAPI():
    
    def __init__(self):
        self.gameMap = GameMap()
        self.key = None
        self.ip = None
        self.playername = None
        self.turn = None
        self.dilation = None
    
    def session_resource(self):
        resource = requests.get("http://20.196.214.79:5050/session/resource", params={"ip": self.ip})
        # print('resource: ', resource.status_code, resource.json()["message"])
        if resource.json()['message'] != 'Opened':
            raise Exception('receiver is closed')
    
    def session_create(self, isWindowMode=False, res_x=1920, res_y=1080):
        params = {
            'ip': self.ip,
            'isWindowMode': isWindowMode,
            'Res_X': res_x,
            'Res_Y': res_y
        }
        print('session create..', end='', flush=True)
        while True:
            try:
                create = requests.post("http://20.196.214.79:5050/session/create", params)
            except ConnectionRefusedError or ConnectionResetError:
                print('..', end='', flush=True)
                continue
            if create.status_code == 200:
                break
        print('done!')
        self.key = json.loads(create.content)['key']
    
    def session_join(self):
        params = {"key": self.key, "playername": self.playername}
        join = requests.post("http://20.196.214.79:5050/session/join", data=params)
        print('join..', end='', flush=True)
        while True:
            if join.status_code == 200:
                print('done!')
                self._game_start()
                break
            else:
                print('..', end='', flush=True)
                join = requests.post("http://20.196.214.79:5050/session/join", data=params)
    
    def _game_start(self):
        startParams = {
            'key': self.key,
            'playername': self.playername,
            'turn': self.turn,
            'dilation': self.dilation
        }
        print('game start..', end='', flush=True)
        join = requests.post("http://20.196.214.79:5050/game/start", data=startParams)
        while True:
            if join.status_code == 200:
                print('done!')
                break
            else:
                print('..', end='', flush=True)
                join = requests.post("http://20.196.214.79:5050/game/start", data=startParams)
    
    def game_status(self):
        statusParam = {"key": self.key, "playername": self.playername}
        statusResponse = requests.get("http://20.196.214.79:5050/game/status", statusParam)
        while True:
            if statusResponse.status_code == 200:
                status = json.loads(statusResponse.content)
                return status
            else:
                statusResponse = requests.get("http://20.196.214.79:5050/game/status", statusParam)
    
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
                move = requests.post("http://20.196.214.79:5050/agent/move", data=moveParam)
            except ConnectionRefusedError or ConnectionResetError:
                continue
            if move.status_code == 200:
                break
        print(uid, '->', self._dirTxt(direction))
    
    def agent_attack(self, uid):
        attackParam = {'key':self.key, 'uid': uid}
        while True:
            try:
                attack = requests.post("http://20.196.214.79:5050/agent/attack", data=attackParam)
            except ConnectionRefusedError or ConnectionResetError:
                continue
            if attack.status_code == 200:
                break
        print(uid, '-> Attack')
    
    def agent_rotate(self, uid, angle):
        '''
        angle: 45 or -45
        45로 주면 오른쪽으로 돌림
        '''
        rotateParam = {'key': self.key, 'uid': uid, 'angle': angle}
        while True:
            try:
                rotate = requests.post("http://20.196.214.79:5050/agent/rotate", data=rotateParam)
            except ConnectionRefusedError or ConnectionResetError:
                continue
            if rotate.status_code == 200:
                break
        print(uid, '-> Rotate', angle)
    
    def game_view(self):
        status = self.game_status()
        objects = [] # 탱크 및 장애물들
        agents = status['responses']['data']['message']['agent_info']['agent']
        for agent in agents:
            uid = agent['uid']
            while True:
                try:
                    view = requests.get(f"http://20.196.214.79:5050/game/view", params={"key": self.key, "uid": uid})
                except ConnectionRefusedError or ConnectionResetError:
                    continue
                if view.status_code == 200:
                    break
        
            info = json.loads(view.content)["responses"]["data"]["message"]["info"]
            for object in info:
                if object not in objects and object["IsExistObject"] == True:
                    self.gameMap.set_map(object['location'][0], object['location'][1], object['ObjectType'])
                    objects.append(object)
        
        for agent in agents:
            self.gameMap.set_map(agent['location'][0], agent['location'][1], 9)
        return objects, self.gameMap


# 좌표를 칸으로 바꿔서 출력해주기 위한 클래스
class GameMap:
    def __init__(self):
        self.game_map = []
        for _ in range(32):
            self.game_map.append([0]*32)
    
    def __str__(self):
        ret = '-'*60 + '\n'
        for row in self.game_map:
            ret += ' '.join(map(str, row))
            ret += '\n'
        ret = ret.replace('0', ' ')
        ret = ret.replace('1', 'T') # tank
        ret = ret.replace('2', '2')
        ret = ret.replace('3', 'O') # object
        ret = ret.replace('4', '4')
        ret = ret.replace('9', 'M') # my tank
        ret += '-'*60 + '\n'
        return ret
    
    def __repr__(self):
        return self.__str__()
    
    def set_map(self, x, y, objectType):
        x = (x-25200)//1000
        y = (y-147450)//1000
        
        try:
            assert 0 <= x <= 31 and 0 <= y <= 31
            self.game_map[y][x] = objectType
        except:
            print('location excepted', x, y)