import socket, functools, cv2, os, keyboard
from tkinter import *
from threading import Thread
import numpy as np
from plyer import notification
from PIL import ImageTk
from time import sleep

window = Tk()
window.title("Simple PyVNC")
window.geometry("779x702")
window.maxsize(779, 702)
window.minsize(779, 702)
window.iconbitmap("assets/Python.ico")

ahbz = PhotoImage(file='assets/img0.png')
ahbc = PhotoImage(file='assets/img1.png')
backg = PhotoImage(file='assets/background.png')
vncbackg = PhotoImage(file='assets/vncbackground.png')
novnc = PhotoImage(file='assets/novnc.png')

class PyVNC:

    def __init__(self):
        self.selected_client = ''
        self.vncopen = False
        self.islistening = False
        self.activeclcl = 0
        self.CLIENTS = []
        self.CLIENTS_INFO = []
        H = open("data/hosting.txt","r").read()
        self.savedserver = H.split(":")[0]
        self.savedport = H.split(":")[1]
        self.A = open("data/clients.txt","r").read()
        self.main()

    def _vnconclose(self):
        if self.isVNCon:
            pass
        else:
            self.vncopen=False
            self.VNcc.destroy()

    def _onlabel(self, event):
        containing_widget = self.VNCscreen.winfo_containing(event.x_root, event.y_root)
        if containing_widget == self.VNCscreen:
            self.isVNConLABEL = True
        else:
            self.isVNConLABEL = False

    def _receive_data(self,sock, size):
        data = b''
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data

    def _vncdot(self):
        self.THEclient.send("startvnc".encode())
        while self.isVNCon:
            header = self._receive_data(self.THEclient, 6)
            if not header:
                break
            if header[:2] != b'VA':
                continue
            img_size = int.from_bytes(header[2:], byteorder='big')
            img_data = self._receive_data(self.THEclient, img_size)
            if not img_data:
                break
            img_array = np.frombuffer(img_data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is not None:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_pil = __import__("PIL").Image.fromarray(img_rgb)
                img_tk = ImageTk.PhotoImage(img_pil)
            self.VNCscreen.config(image=img_tk)
            self.VNCscreen.image = img_tk

    def _turnoffvnc(self):
        self.THEclient.send("stopvnc".encode())
        sleep(1)
        keyboard.unhook_all()
        self.VNCscreen.config(image=novnc)

    def _b4turnON(self):
        if self.isVNCon:
            self.isVNCon=False
            self.turnvncON.config(image=ahbc)
            Thread(target=self._turnoffvnc).start()
        else:
            self.isVNCon=True
            self.turnvncON.config(image=ahbz)
            Thread(target=self._vncdot).start()
            Thread(target=self._vncpress).start()

    def _vncrightclick(self,event):
        if self.isVNCon:
            x,y=event.x, event.y
            self.THEclient.send(f"vncmouseright|{x}|{y}".encode())
    
    def _vncleftclick(self,event):
        if self.isVNCon:
            x,y=event.x, event.y
            self.THEclient.send(f"vncmouseleft|{x}|{y}".encode())

    def _vnconpress(self,event):
        if self.isVNCon:
            if self.isVNConLABEL:
                self.THEclient.send(f"vnckeyboard|{event.name}".encode())

    def _vncpress(self):
        keyboard.on_press(self._vnconpress)

    def _vncview(self):
        self.isVNConLABEL=False
        self.isVNCon = False
        self.VNcc = Toplevel(window)
        self.VNcc.title("VNC")
        self.VNcc.geometry("1000x663")
        self.VNcc.maxsize(1000, 663)
        self.VNcc.minsize(1000, 663)
        self.VNcc.iconbitmap("assets/Python.ico")
        self.VNcc.protocol("WM_DELETE_WINDOW", self._vnconclose)
        bg = Label(self.VNcc, image=vncbackg,borderwidth=0)
        bg.place(x=0, y=0)
        self.turnvncON = Button(self.VNcc, image=ahbc,bg='#171717',borderwidth=0, activebackground="#171717",command=self._b4turnON)
        self.turnvncON.place(x=150,y=25)
        self.VNCscreen = Label(self.VNcc, image=novnc,borderwidth=0,bg="#171717")
        self.VNCscreen.place(x=40, y=71)
        self.VNCscreen.bind("<Button-1>",self._vncleftclick)
        self.VNCscreen.bind("<Button-3>",self._vncrightclick)
        self.VNCscreen.bind("<Enter>",self._onlabel)

    def _openvnc(self):
        if self.vncopen:
            pass
        else:
            self.vncopen=True
            Thread(target=self._vncview).start()

    def _forvnc(self,event):
        if self.vncopen:
            pass
        else:
            if self.selected_client == '':
                pass
            else:
                last_word = self.selected_client.rstrip().split()[-1]
                for index, user in enumerate(self.CLIENTS_INFO):
                    hh = user.split("|")[3]
                    if hh == last_word:
                        de_index = index
                        break
                self.THEclient = self.CLIENTS[index]
                self.clientsmenu.delete(0, END)
                self.clientsmenu.add_command(label="Open VNC",command=self._openvnc)
                try:
                    self.clientsmenu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.clientsmenu.grab_release()

    def _selectclient(self,event):
        index = self.clientslist.nearest(event.y)
        if index is not None and index >= 0 and index < self.clientslist.size():
            s = self.clientslist.get(index)
            self.selected_client = s

    def _newclient(self,info:str):
        self.activeclcl +=1
        self.activeclients.config(text=f"{self.activeclcl}")
        hwid = info.split("|")[3]
        if os.path.exists(f"clients/{hwid}"):
            pass
        else:
            os.mkdir(f"clients/{hwid}")
            clcl = int(open("data/clients.txt",'r').read())
            clcl +=1;open("data/clients.txt","w+").write(str(clcl))
            self.totalclients.config(text=f"{clcl}")

    def _startserver(self):
        self.port = int(self.port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server, int(self.port)))
        self.server_socket.listen()
        while True:
            client_socket, address = self.server_socket.accept()
            get_client_info = client_socket.recv(1024).decode()
            self.CLIENTS_INFO.append(get_client_info)
            self.CLIENTS.append(client_socket)
            self.clientslist.insert(END,f'{get_client_info.split("|")[0]}       {get_client_info.split("|")[1]}        {get_client_info.split("|")[2]}         {get_client_info.split("|")[3]}')
            Thread(target=self._newclient,args=(get_client_info,)).start()
            Thread(target=self._notifications,args=("New Connection",f"New client connected to your server")).start()

    def _checkserver(self):
        if self.islistening == False:
            if len(self.serverent.get()) > 1:
                if len(self.portent.get()) > 1:
                    self.server = self.serverent.get()
                    self.port = self.portent.get()
                    open("data/hosting.txt","w+").write(f"{self.server}:{self.port}")
                    Thread(target=self._startserver).start()
                    Thread(target=self._notifications,args=("Server is running",f"Listening to {self.server}:{self.port}")).start()
                    self.startlistening.config(image=ahbz)
        else:
            pass

    def main(self):
        bg = Label(window, image=backg,borderwidth=0)
        bg.place(x=0, y=0)
        self.serverent = Entry(window,font=('SeoulHangang',10),bg='#A5A5A5', fg='#171717',width=18,borderwidth=0)
        self.serverent.insert("end",self.savedserver)
        self.serverent.place(x=387,y=38)
        self.portent = Entry(window,font=('SeoulHangang',10),bg='#A5A5A5', fg='#171717',width=18,borderwidth=0)
        self.portent.insert("end",self.savedport)
        self.portent.place(x=594,y=38)
        self.startlistening = Button(window, image=ahbc,bg='#171717',borderwidth=0, activebackground="#171717",command=self._checkserver)
        self.startlistening.place(x=520,y=70)
        self.clientsmenu = Menu(window, tearoff=0, bg="#171717", fg="#FFFFFF")
        self.clientslist = Listbox(window, bg="#0D0D0D", fg="#FFFFFF", width=117, height=31, borderwidth=0)
        self.clientslist.place(x=36,y=165)
        self.activeclients = Label(window, text=f"0",font=("Inter",13),bg="#0D0D0D",fg="#FFFFFF")
        self.activeclients.place(x=165,y=130)
        self.totalclients = Label(window, text=f"0",font=("Inter",13),bg="#0D0D0D",fg="#FFFFFF")
        self.totalclients.place(x=367,y=129)
        self.totalclients.config(text=self.A)
        self.clientslist.bind("<Button-3>", functools.partial(self._forvnc))
        self.clientslist.bind("<Button-1>", self._selectclient)
    
    def _notifications(self,titl3,messag3):
        notification.notify(title=titl3,message=messag3,app_name='PyVNC Notifications',timeout=3)


PyVNC()
window.mainloop()