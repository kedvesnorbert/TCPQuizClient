import socket
import threading
import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

FORMAT = "UTF-8"
BUFLEN = 4096
ClientSocket = 0
MYCLIENTNAME = ""
CLIENTS = []
CURRENT_PARTNER = ""
CURRENT_CLIENT = ""
CURRENT_BUTTON_CLICKED = 0
HELP50 = 1
HELP100 = 1
SECONDS = 20

def getNetworkConfigData():
    IP = PORT = ""
    try:
        file = open("network_config.ini", 'r')
    except:
        return False
    while 1:
        temp = file.readline()
        if not temp: break
        if temp[0] == "#": continue
        stemp = temp.split('=')
        if stemp[0].strip() == "IP": 
            IP = stemp[1].strip()
        if stemp[0].strip() == "PORT":
            PORT = stemp[1].strip()
    file.close()
    return IP, PORT


class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        self.lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        self.lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

    def getText(self):
        return self.label.text()

    def addMyWidget(self, w):
        self.lay.addWidget(w)
        self.lay.setAlignment(Qt.AlignTop)

    def removeMyWidget(self):
        while self.lay.count():
            item = self.lay.takeAt(0)
            widget = item.widget()
            widget.deleteLater()


class LoginWindow(QWidget):
    signal_connect = pyqtSignal(bool)

    def openwindow(a):
        loginW.hide()
        waitW.show()
        waitW.setWindowTitle("Waiting room - " + str(MYCLIENTNAME))
        receive_thread = threading.Thread(target=waitW.receive_msg)
        receive_thread.daemon = True
        receive_thread.start()

    def start_connecting(self):
        t = threading.Thread(target=self.connect_to_server)
        t.daemon = True
        t.start()

    def __init__(self):
        super().__init__()
        self.signal_connect.connect(self.openwindow)
        self.setGeometry(50, 50, 900, 950)
        self.setWindowTitle("Login")
        self.setStyleSheet("background-color:#09325D;")

        self.loginlayout = QVBoxLayout()
        self.loginlayout.setAlignment(Qt.AlignCenter)

        self.login_title = QLabel("Log In")
        self.login_title.setFixedWidth(400)
        self.login_title.setAlignment(Qt.AlignHCenter)
        self.login_title.setStyleSheet(
            "color:white; font-weight:bold;font-size:30pt;margin-bottom:80px;")
        self.loginlayout.addWidget(self.login_title)

        self.login_username = QLineEdit()
        self.login_username.setMaxLength(25)
        self.login_username.setFixedWidth(450)
        self.login_username.setPlaceholderText("Enter username")
        self.login_username.setStyleSheet(
            "color:white;font-size:13pt;background-color:transparent;width:100px;height:60px;border:none;border-bottom:3px solid black;")
        self.loginlayout.addWidget(self.login_username)

        self.login_pw = QLineEdit()
        self.login_pw.setMaxLength(25)
        self.login_pw.setFixedWidth(450)
        self.login_pw.setEchoMode(QLineEdit.Password)
        self.login_pw.setPlaceholderText("Enter password")
        self.login_pw.setStyleSheet(
            "color:white;font-size:13pt;background-color:transparent;width:100px;height:60px;border:none;border-bottom:3px solid black;")
        self.login_pw.returnPressed.connect(self.start_connecting)
        self.loginlayout.addWidget(self.login_pw)

        self.login_btn = QPushButton('CONNECT')
        self.login_btn.setFixedWidth(450)
        self.login_btn.setFixedHeight(100)
        self.login_btn.setStyleSheet(
            "font-size:20pt;color:white;margin-top:15px;border:none;background-color:#0D141A")
        self.loginlayout.addWidget(self.login_btn)
        self.login_btn.clicked.connect(self.start_connecting)

        self.login_errmsg = QLabel()
        self.login_errmsg.setFixedWidth(450)
        self.login_errmsg.setWordWrap(True)
        self.login_errmsg.setStyleSheet(
            "color:white;font-size:13pt;margin-top:20px;margin-bottom:20px;text-align:center")

        self.loginlayout.addWidget(self.login_errmsg)
        self.setLayout(self.loginlayout)

    def getLoginBtn(self):
        return self.login_btn

    def getUsernameEntered(self):
        return self.login_username

    def getPasswordEntered(self):
        return self.login_pw

    def getLoginErrorMsg(self):
        return self.login_errmsg

    def connect_to_server(self):
        loginW.getLoginBtn().setEnabled(False)
        loginW.getLoginErrorMsg().setText("LOADING ...\n")
        try:
            usernamepw = loginW.getUsernameEntered().text() + "\t" + loginW.getPasswordEntered().text()
            if(len(loginW.getUsernameEntered().text()) < 3 or len(loginW.getPasswordEntered().text()) < 3):
                loginW.getLoginErrorMsg().setText(
                    "Nem írtál be felhasználónevet vagy jelszót!\nPlease enter username and password!")
            else:
                global MYCLIENTNAME
                MYCLIENTNAME = loginW.getUsernameEntered().text()
                usernamepw = "1\t \t \t" + usernamepw
                usernamepw = usernamepw.encode(FORMAT)
                len_usernamepw = len(usernamepw)
                len_usernamepw_full = len(str(len_usernamepw))
                usernamepw = usernamepw.decode(FORMAT)
                usernamepw = str(len_usernamepw + len_usernamepw_full + 1) + '\t' + usernamepw
                usernamepw = usernamepw.encode(FORMAT)

                global ClientSocket
                ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ClientSocket.connect((str(IP), int(PORT)))
                ClientSocket.send(usernamepw)
                respi = ClientSocket.recv(BUFLEN)
                respi = respi.decode(FORMAT)
                if respi == "E200\0":
                    self.signal_connect.emit(True)
                    print(MYCLIENTNAME)
                else:
                    ClientSocket.close()
                    if respi == "E404\0":
                        loginW.getLoginErrorMsg().setText(
                            "Hibás felhasználónév vagy jelszó!\nWrong username or password!\n")
                    if respi == "E403\0":
                        loginW.getLoginErrorMsg().setText(
                            "Ezzel a fiókkal már bejelentkeztek!\nThis account is currently is use!\n")
        except:
            loginW.getLoginErrorMsg().setText(
                "A szerver visszautasította a kapcsolódást! Server temporary not reachable.\nERR_CONNECTION_REFUSED\n")
            try:
                ClientSocket.close()
            except:
                print("Coulnd't close Clientsocket\n")
        loginW.getLoginBtn().setEnabled(True)

class WaitWindow(QWidget):
    signal_recvclientlist = pyqtSignal(str)
    signal_startplaying = pyqtSignal(str)
    signal_getquestion = pyqtSignal(str)
    signal_gameover = pyqtSignal(str)
    signal_helps = pyqtSignal(str)

    def openGameWindow(self, a):
        global MYCLIENTNAME
        global CURRENT_PARTNER
        self.ans = a.split("\t")[4]
        self.boolans = self.ans.split("^")
        if str(self.boolans[0]) == "0":
            self.wait_errmsg.setText("No partner was found to play.\nTry again later!")
            self.play_btn.setEnabled(True)
            self.exit_btn.setEnabled(True)
        else:
            tempclients = self.boolans[1].split("#")
            if tempclients[0] != MYCLIENTNAME:
                CURRENT_PARTNER = tempclients[0]
            else:
                CURRENT_PARTNER = tempclients[1]
            print(CURRENT_PARTNER)
            waitW.hide()
            playW.showFullScreen()
            playW.setMyName("MYSELF")
            playW.setOpponentName(str(CURRENT_PARTNER))
            global HELP50
            global HELP100
            HELP50 = 1
            HELP100 = 1
        print("Done")
    
    def openResultWindow(self, received_answers):
        self.qdata = received_answers.split("#")
        self.myname = self.qdata[0]
        self.myscore_inpersent = self.qdata[1]
        self.myscore_incount = self.qdata[2]
        self.opponentname = self.qdata[3]
        self.opponentscore_inpersent = self.qdata[4]
        self.opponentscore_incount = self.qdata[5]
        playW.clearPlayWindow()
        self.myscore_inpersent = float(self.myscore_inpersent)
        self.opponentscore_inpersent = float(self.opponentscore_inpersent)
        resW.showFullScreen()
        playW.hide()
        if round(float(self.myscore_inpersent), 2) > round(float(self.opponentscore_inpersent), 2):
            resW.show_winning(
                self.myname, self.myscore_inpersent, self.myscore_incount, self.opponentname, self.opponentscore_inpersent, self.opponentscore_incount)
        else:
            if round(float(self.myscore_inpersent), 2) < round(float(self.opponentscore_inpersent), 2):
                resW.show_losing(
                    self.myname, self.myscore_inpersent, self.myscore_incount, self.opponentname, self.opponentscore_inpersent, self.opponentscore_incount)
            else:
                resW.show_draw(
                    self.myname, self.myscore_inpersent, self.myscore_incount, self.opponentname, self.opponentscore_inpersent, self.opponentscore_incount)

    def getresultofhelps(self, received_answers):
        global HELP50
        global HELP100
        self.qdata = received_answers.split("#")
        self.helptype = self.qdata[0]
        if self.helptype == "1":
            HELP50 = HELP50 - 1
            playW.helpfiftybtn.setText("50 : 50\n\nUSED UP")
            playW.helpfiftybtn.setStyleSheet(
                "color:black;font-size:16pt;padding-top:50px;padding-bottom:30px;margin-right:50px;background-color:#5D76A9;")
            self.wrongans1 = self.qdata[1]
            self.wrongans2 = self.qdata[2]
            if self.wrongans1 == "1":
                playW.answer1.setStyleSheet(
                    "color:#7CB9E8;border:none;background-color:#7CB9E8;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;")
                playW.answer1.setEnabled(False)
            if self.wrongans1 == "2":
                playW.answer2.setStyleSheet(
                    "color:#7CB9E8;border:none;background-color:#7CB9E8;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;")
                playW.answer2.setEnabled(False)
            if self.wrongans1 == "3":
                playW.answer3.setStyleSheet(
                    "color:#7CB9E8;border:none;background-color:#7CB9E8;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;")
                playW.answer3.setEnabled(False)
            if self.wrongans1 == "4":
                playW.answer4.setStyleSheet(
                    "color:#7CB9E8;border:none;background-color:#7CB9E8;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;")
                playW.answer4.setEnabled(False)
            if self.wrongans2 == "1":
                playW.answer1.setStyleSheet(
                    "color:#7CB9E8;border:none;background-color:#7CB9E8;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;")
                playW.answer1.setEnabled(False)
            if self.wrongans2 == "2":
                playW.answer2.setStyleSheet(
                    "color:#7CB9E8;border:none;background-color:#7CB9E8;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;")
                playW.answer2.setEnabled(False)
            if self.wrongans2 == "3":
                playW.answer3.setStyleSheet(
                    "color:#7CB9E8;border:none;background-color:#7CB9E8;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;")
                playW.answer3.setEnabled(False)
            if self.wrongans2 == "4":
                playW.answer4.setStyleSheet(
                    "color:#7CB9E8;border:none;background-color:#7CB9E8;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;")
                playW.answer4.setEnabled(False)
        if self.helptype == "2":
            HELP100 = HELP100 - 1
            playW.helphundredbtn.setText("100%\n\nUSED UP")
            playW.helphundredbtn.setStyleSheet(
                "color:black;font-size:16pt;padding-top:50px;padding-bottom:30px;margin-left:50px;background-color:#5D76A9;")
            self.correctans = self.qdata[1]
            if self.correctans == "1":
                playW.answer1.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#00CC00;")
            if self.correctans == "2":
                playW.answer2.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#00CC00;")
            if self.correctans == "3":
                playW.answer3.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#00CC00;")
            if self.correctans == "4":
                playW.answer4.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#00CC00;")

    def start_playing(self):
        tp = threading.Thread(target=self.startplaying_game)
        tp.daemon = True
        tp.start()

    def receive_msg(self):
        while True:
            try:
                print("Receiving data from server ...")
                self.received_data = ClientSocket.recv(BUFLEN)
                self.receiveddata_len = len(self.received_data)
                self.datalength = self.received_data[:7].decode('latin-1')
                self.datatype = self.datalength.split("\t")[1]
                self.datalength = int(self.datalength.split("\t")[0])
                
                #print(self.received_data)
                while self.receiveddata_len < self.datalength:
                    self.received_data = self.received_data + ClientSocket.recv(BUFLEN)
                    self.receiveddata_len = len(self.received_data)
                    #print(self.received_data)

                self.received_data = self.received_data.decode('latin-1')
                self.datatype = int(self.received_data.split("\t")[1])
                if self.datatype == 4:
                    global CLIENTS
                    CLIENTS = self.received_data.split("\t")[4]
                    self.signal_recvclientlist.emit(CLIENTS)
                else:
                    if self.datatype == 2:
                        self.signal_startplaying.emit(str(self.received_data))
                    else:
                        if self.datatype == 5:
                            self.signal_getquestion.emit(str(self.received_data.split("\t")[4]))
                        else:
                            if self.datatype == 7:
                                self.show_answers(str(self.received_data.split("\t")[4]))
                            else:
                                if self.datatype == 8:
                                    self.signal_gameover.emit(str(self.received_data.split("\t")[4]))
                                else:
                                    if self.datatype == 9:
                                        self.signal_helps.emit(str(self.received_data.split("\t")[4]))
                               
            except Exception as e:
                print(str(e))
                if str(e)[0:16] == "[WinError 10053]":
                    e_error = \
                        "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_ABORTED\nThe estabilished connection was aborted by the client."
                else:
                    if str(e)[0:16] == "[WinError 10054]":
                        e_error = \
                            "Megszűnt a kommunikáció a szerverrel.\nA kapcsolat alaphelyzetbe állt.\nERR_CONNECTION_RESET\nThe connection was forcibly closed by the remote host."
                    else:
                        e_error = "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_ABORTED\nThe estabilished connection was aborted by the client."
                resW.hide()
                playW.hide()
                waitW.hide()
                loginW.show()
                loginW.getLoginErrorMsg().setText(e_error)
                waitW.play_btn.setEnabled(True)
                waitW.exit_btn.setEnabled(True)
                waitW.wait_errmsg.setText("Click START button to play!")
                return

    def addClientButtons(self):
        self.clients_label.removeMyWidget()
        global CLIENTS
        global CURRENT_CLIENT
        tempCLIENTS = CLIENTS
        CLIENTS = CLIENTS.split(',')
        if str(MYCLIENTNAME + " 0") in CLIENTS:
            CLIENTS.remove(str(MYCLIENTNAME + " 0"))
        if str(MYCLIENTNAME + " 1") in CLIENTS:
            CLIENTS.remove(str(MYCLIENTNAME + " 1"))
        if str(MYCLIENTNAME + " 2") in CLIENTS:
            CLIENTS.remove(str(MYCLIENTNAME + " 2"))

        for client in CLIENTS:
            self.clientdata = client.split(' ')
            self.clientbutton = QPushButton()
            self.clientbutton.setText(str(self.clientdata[0]))
            self.clientbutton.setObjectName(str(self.clientdata[0]))
            if str(self.clientdata[1]) == "0":
                self.clientbutton.setStyleSheet(
                    "height:50px;font-size:12pt;text-align:center;background-color:lightgray;")
            else:
                self.clientbutton.setStyleSheet("height:50px;font-size:12pt;text-align:center;background-color:pink;")
            self.clients_label.addMyWidget(self.clientbutton)
        CLIENTS = tempCLIENTS
    
    def startplaying_game(self):
        try:
            self.play_btn.setEnabled(False)
            self.exit_btn.setEnabled(False)
            self.wait_errmsg.setText("Searching partner ...")
            self.startplaying_msg = "2\t" + MYCLIENTNAME + "\tServer\tWant a partner"
            self.startplaying_msg = self.startplaying_msg.encode(FORMAT)
            self.len_startplaying_msg = len(self.startplaying_msg)
            self.len_startplaying_msg_full = len(str(self.len_startplaying_msg))
            self.startplaying_msg = self.startplaying_msg.decode(FORMAT)
            self.startplaying_msg = str(
                self.len_startplaying_msg + self.len_startplaying_msg_full + 1) + '\t' + self.startplaying_msg
            self.startplaying_msg = self.startplaying_msg.encode(FORMAT)

            ClientSocket.send(self.startplaying_msg)
        except Exception as e:
            print(str(e))

    def show_question(self, received_question):
        global CURRENT_BUTTON_CLICKED
        CURRENT_BUTTON_CLICKED = 0
        playW.answer1.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        playW.answer2.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        playW.answer3.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        playW.answer4.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        playW.answer1.setEnabled(True)
        playW.answer2.setEnabled(True)
        playW.answer3.setEnabled(True)
        playW.answer4.setEnabled(True)
        global HELP50
        global HELP100
        if HELP50 > 0:
            playW.helpfiftybtn.setEnabled(True)
        if HELP100 > 0:
            playW.helphundredbtn.setEnabled(True)

        self.qdata = received_question.split("#")
        self.tempqid = self.qdata[0]
        self.tempquestion = self.qdata[1]
        self.tempqanswer1 = self.qdata[2]
        self.tempqanswer2 = self.qdata[3]
        self.tempqanswer3 = self.qdata[4]
        self.tempqanswer4 = self.qdata[5]
        self.tempdiff = self.qdata[6]
        self.tempqnumber = self.qdata[7]
        playW.setQuestion(self.tempquestion)
        playW.setAns1(self.tempqanswer1)
        playW.setAns2(self.tempqanswer2)
        playW.setAns3(self.tempqanswer3)
        playW.setAns4(self.tempqanswer4)
        playW.setCurrentquestionnumber(self.tempqnumber)
        playW.myTimer()
    
    def show_answers(self, received_answers):
        global CURRENT_BUTTON_CLICKED
        self.qdata = received_answers.split("#")
        self.opponents_answer = self.qdata[0]
        self.correctanswer = self.qdata[1]
        self.myscore = self.qdata[2]
        self.opponents_score = self.qdata[3]

        if self.opponents_answer == "1":
            if self.opponents_answer == str(CURRENT_BUTTON_CLICKED):
                playW.answer1.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:0.7, y2:0.6, stop:0 rgb(102, 0, 204), stop: 1 rgb(204, 102, 0));")
            else:
                playW.answer1.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color: rgb(204, 102, 0);")

        if self.opponents_answer == "2":
            if self.opponents_answer == str(CURRENT_BUTTON_CLICKED):
                playW.answer2.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:0.7, y2:0.6, stop:0 rgb(102, 0, 204), stop: 1 rgb(204, 102, 0));")
            else:
                playW.answer2.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color: rgb(204, 102, 0);")

        if self.opponents_answer == "3":
            if self.opponents_answer == str(CURRENT_BUTTON_CLICKED):
                playW.answer3.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:0.7, y2:0.6, stop:0 rgb(102, 0, 204), stop: 1 rgb(204, 102, 0));")
            else:
                playW.answer3.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color: rgb(204, 102, 0);")

        if self.opponents_answer == "4":
            if self.opponents_answer == str(CURRENT_BUTTON_CLICKED):
                playW.answer4.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:0.7, y2:0.6, stop:0 rgb(102, 0, 204), stop: 1 rgb(204, 102, 0));")
            else:
                playW.answer4.setStyleSheet(
                    "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color: rgb(204, 102, 0);")

        if str(CURRENT_BUTTON_CLICKED) == str(self.correctanswer):
            self.correction_bordercolor = "border: 10px solid green;"
        else:
            self.correction_bordercolor = "border: 10px solid red;"

        time.sleep(1)
        if self.correctanswer == "1":
            playW.answer1.setStyleSheet(playW.answer1.styleSheet() + self.correction_bordercolor)
        else:
            if self.correctanswer == "2":
                playW.answer2.setStyleSheet(playW.answer2.styleSheet() + self.correction_bordercolor)
            else:
                if self.correctanswer == "3":
                    playW.answer3.setStyleSheet(playW.answer3.styleSheet() + self.correction_bordercolor)
                else:
                    if self.correctanswer == "4":
                        playW.answer4.setStyleSheet(playW.answer4.styleSheet() + self.correction_bordercolor)
        self.myscore = round(float(self.myscore), 2)
        self.opponents_score = round(float(self.opponents_score), 2)
        playW.setMyScore(str(self.myscore))
        playW.setOpponentScore(str(self.opponents_score))
        time.sleep(1)
        playW.getNextQuestion()

    def logout(self):
        try:
            global ClientSocket
            ClientSocket.close()
            waitW.close()
            loginW.show()
            loginW.getLoginErrorMsg().setText(
                "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_RESET\nA kapcsolat alaphelyzetbe állt.")
        except Exception as e:
            waitW.close()
            loginW.show()
            loginW.getLoginErrorMsg().setText(
                "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_RESET\nA kapcsolat alaphelyzetbe állt." + str(e))
    
    def __init__(self):
        super().__init__()
        self.signal_startplaying.connect(self.openGameWindow)
        self.signal_getquestion.connect(self.show_question)
        self.signal_gameover.connect(self.openResultWindow)
        self.signal_helps.connect(self.getresultofhelps)
        self.setGeometry(50, 50, 900, 950)
        self.setFixedSize(900, 950)
        self.setWindowTitle("Waiting room")
        self.setStyleSheet("background-color:lightblue;")

        self.waitlayout = QVBoxLayout()
        self.waitlayout.setAlignment(Qt.AlignCenter)

        self.waittitle = QLabel()
        self.waittitle.setText("Waiting room")
        self.waittitle.setAlignment(Qt.AlignCenter)
        self.waittitle.setStyleSheet("color:black;font-size:18pt;text-align:center;margin-top: 10pt;margin-bottom:10pt")

        self.bodylayout = QHBoxLayout()
        #1.column
        self.clients_label_layout = QVBoxLayout()
        self.clients_label_layout.setAlignment(Qt.AlignTop)

        self.clients_labeltitle = QLabel()
        self.clients_labeltitle.setText("<center>List of connected clients</center><br>")
        self.clients_labeltitle.setAlignment(Qt.AlignTop)
        self.clients_labeltitle.setFixedWidth(400)
        self.clients_labeltitle.setFixedHeight(50)
        self.clients_labeltitle.setStyleSheet(
            "color:black;font-size:15pt;margin-top:5px;")
        self.clients_label_layout.addWidget(self.clients_labeltitle)

        self.clients_label = ScrollLabel()
        self.clients_label.setAlignment(Qt.AlignTop)
        self.clients_label.setFixedWidth(400)
        self.clients_label.setFixedHeight(800)
        self.clients_label.setStyleSheet("color:black;font-size:15pt;height:50px;text-align:left;")
        self.clients_label_layout.addWidget(self.clients_label)

        #2.column
        self.action_layout = QVBoxLayout()
        self.action_layout.setAlignment(Qt.AlignCenter)

        self.play_btn = QPushButton('START')
        self.play_btn.setFixedWidth(400)
        self.play_btn.setFixedHeight(100)
        self.play_btn.setStyleSheet(
            "font-size:20pt;color:white;margin-top:15px;border:none;background-color:#0D141A")
        self.action_layout.addWidget(self.play_btn)
        self.play_btn.clicked.connect(self.start_playing)

        self.wait_errmsg = QLabel()
        self.wait_errmsg.setFixedWidth(400)
        self.wait_errmsg.setWordWrap(True)
        self.wait_errmsg.setStyleSheet(
            "color:black;font-size:13pt;margin-top:20px;margin-bottom:20px;text-align:center")
        self.wait_errmsg.setText("Click START button to play!")
        self.action_layout.addWidget(self.wait_errmsg)

        self.exit_btn = QPushButton('EXIT')
        self.exit_btn.setFixedWidth(400)
        self.exit_btn.setFixedHeight(100)
        self.exit_btn.setStyleSheet(
            "font-size:20pt;color:white;margin-top:15px;border:none;background-color:red")
        self.exit_btn.clicked.connect(self.logout)
        self.action_layout.addWidget(self.exit_btn)

        self.waitlayout.addWidget(self.waittitle)
        self.bodylayout.addLayout(self.clients_label_layout)
        self.bodylayout.addLayout(self.action_layout)
        self.waitlayout.addLayout(self.bodylayout)
        self.setLayout(self.waitlayout)
        self.signal_recvclientlist.connect(self.addClientButtons)


class PlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        global MYCLIENTNAME
        self.setGeometry(50, 50, 1800, 950)
        self.setFixedSize(1800, 950)
        self.setWindowTitle("Playing room")
        self.setStyleSheet("background-color:#7CB9E8;")

        self.playlayout = QVBoxLayout()
        self.playlayout.setAlignment(Qt.AlignTop)

        #1.HEADER
        self.headerlayout = QHBoxLayout()
        self.scorelayout = QHBoxLayout()
        self.headerlayout.setAlignment(Qt.AlignTop)
        self.scorelayout.setAlignment(Qt.AlignTop)

        self.myclientname = QLabel()
        self.myclientname.setText(str(MYCLIENTNAME))
        self.myclientname.setAlignment(Qt.AlignLeft)
        self.myclientname.setStyleSheet(
            "color:black;font-size:18pt;margin-top: 10pt;margin-bottom:10pt")

        self.myscore = QLabel()
        self.myscore.setText("0 points")
        self.myscore.setAlignment(Qt.AlignLeft)
        self.myscore.setStyleSheet(
            "color:black;font-size:18pt;margin-top: 10pt;margin-bottom:10pt;")

        self.headerlayout.addWidget(self.myclientname)
        self.scorelayout.addWidget(self.myscore)

        self.currentquestion_number = QLabel()
        self.currentquestion_number.setText("5 / 10")
        self.currentquestion_number.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.currentquestion_number.setStyleSheet(
            "color:black;font-size:18pt;margin-top: 10pt;margin-bottom:10pt;")

        self.timeleft = QLabel()
        self.timeleft.setText("00:20")
        self.timeleft.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.timeleft.setStyleSheet(
            "color:black;font-size:18pt;margin-top: 10pt;margin-bottom:10pt;")

        self.headerlayout.addWidget(self.currentquestion_number)
        self.scorelayout.addWidget(self.timeleft)

        self.opponentscore = QLabel()
        self.opponentscore.setText("0 points")
        self.opponentscore.setAlignment(Qt.AlignRight)
        self.opponentscore.setStyleSheet(
            "color:black;font-size:18pt;margin-top: 10pt;margin-bottom:10pt;")

        self.opponentname = QLabel()
        #self.opponentname.setText("")
        self.opponentname.setAlignment(Qt.AlignRight)
        self.opponentname.setStyleSheet(
            "color:black;font-size:18pt;margin-top: 10pt;margin-bottom:10pt;")

        self.scorelayout.addWidget(self.opponentscore)
        self.headerlayout.addWidget(self.opponentname)

        #2.QUESTION
        self.question = QLabel()
        self.question.setText("")
        self.question.setWordWrap(True)
        self.question.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.question.setStyleSheet(
            "color:black;font-size:20pt;margin-top:60pt;margin-bottom:20pt;padding-top:100px;padding-bottom:30px;")

        #3.HELPS AND ANSWERS
        self.helpsanslayout = QHBoxLayout()
        self.helpsanslayout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.helpfiftylayout = QVBoxLayout()
        self.helpsanslayout.addLayout(self.helpfiftylayout)
        self.helpfiftybtn = QPushButton()
        self.helpfiftybtn.setFixedWidth(175)
        self.helpfiftybtn.setFixedHeight(175)
        self.helpfiftybtn.setText("50 : 50")
        self.helpfiftybtn.setStyleSheet(
            "color:black;font-size:20pt;padding-top:50px;padding-bottom:30px;margin-right:50px;background-color:#5D76A9;")
        self.helpfiftybtn.clicked.connect(self.getHelp50)
        self.helpfiftylayout.addWidget(self.helpfiftybtn)

        self.answerslayout = QVBoxLayout()
        self.helpsanslayout.addLayout(self.answerslayout)

        self.answer1 = QPushButton()
        self.answer1.setText("")
        self.answer1.setFixedWidth(1300)
        self.answer1.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer1.clicked.connect(self.sendAnswer1)
        self.answerslayout.addWidget(self.answer1)

        self.answer2 = QPushButton()
        self.answer2.setText("")
        self.answer2.setFixedWidth(1300)
        self.answer2.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer2.clicked.connect(self.sendAnswer2)
        self.answerslayout.addWidget(self.answer2)

        self.answer3 = QPushButton()
        self.answer3.setText("")
        self.answer3.setFixedWidth(1300)
        self.answer3.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer3.clicked.connect(self.sendAnswer3)
        self.answerslayout.addWidget(self.answer3)

        self.answer4 = QPushButton()
        self.answer4.setText("")
        self.answer4.setFixedWidth(1300)
        self.answer4.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer4.clicked.connect(self.sendAnswer4)
        self.answerslayout.addWidget(self.answer4)

        self.helphundredlayout = QVBoxLayout()
        self.helpsanslayout.addLayout(self.helphundredlayout)
        self.helphundredbtn = QPushButton()
        self.helphundredbtn.setFixedWidth(175)
        self.helphundredbtn.setFixedHeight(175)
        self.helphundredbtn.setText("100%")
        self.helphundredbtn.setStyleSheet(
            "color:black;font-size:20pt;padding-top:50px;padding-bottom:30px;margin-left:50px;background-color:#5D76A9;")
        self.helphundredbtn.clicked.connect(self.getHelp100)
        self.helphundredlayout.addWidget(self.helphundredbtn)

        self.playlayout.addLayout(self.headerlayout)
        self.playlayout.addLayout(self.scorelayout)
        self.playlayout.addWidget(self.question)
        self.playlayout.addLayout(self.helpsanslayout)
        self.setLayout(self.playlayout)

    def setCurrentquestionnumber(self, value):
        self.currentquestion_number.setText(str(value) + " / 10")
    
    def setQuestion(self, value):
        self.question.setText(str(value))
    
    def setAns1(self, value):
        self.answer1.setText(str(value))
    
    def setAns2(self, value):
        self.answer2.setText(str(value))
    
    def setAns3(self, value):
        self.answer3.setText(str(value))
    
    def setAns4(self, value):
        self.answer4.setText(str(value))
    
    def setMyScore(self, value):
        self.myscore.setText(str(value) + " points")
    
    def setOpponentScore(self, value):
        self.opponentscore.setText(str(value) + " points")
    
    def setOpponentName(self, value):
        self.opponentname.setText(str(value))
    
    def setMyName(self, value):
        self.myclientname.setText(str(value))
    
    def sendAnswer1(self):
        self.pause_action()
        global CURRENT_BUTTON_CLICKED
        CURRENT_BUTTON_CLICKED = 1
        self.answer1.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:rgb(102, 0, 204);")
        self.answer2.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer3.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer4.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer1.setEnabled(False)
        self.answer2.setEnabled(False)
        self.answer3.setEnabled(False)
        self.answer4.setEnabled(False)
        self.helpfiftybtn.setEnabled(False)
        self.helphundredbtn.setEnabled(False)

        sendingans1 = "6\t" + MYCLIENTNAME + "\t \t1"
        sendingans1 = sendingans1.encode(FORMAT)
        len_sendingans1 = len(sendingans1)
        len_sendingans1_full = len(str(len_sendingans1))
        sendingans1 = sendingans1.decode(FORMAT)
        sendingans1 = str(len_sendingans1 + len_sendingans1_full + 1) + '\t' + sendingans1
        sendingans1 = sendingans1.encode(FORMAT)
        ClientSocket.send(sendingans1)
    
    def sendAnswer2(self):
        self.pause_action()
        global CURRENT_BUTTON_CLICKED
        CURRENT_BUTTON_CLICKED = 2
        self.answer2.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:rgb(102, 0, 204);")
        self.answer1.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer3.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer4.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer1.setEnabled(False)
        self.answer2.setEnabled(False)
        self.answer3.setEnabled(False)
        self.answer4.setEnabled(False)
        self.helpfiftybtn.setEnabled(False)
        self.helphundredbtn.setEnabled(False)

        sendingans2 = "6\t" + MYCLIENTNAME + "\t \t2"
        sendingans2 = sendingans2.encode(FORMAT)
        len_sendingans2 = len(sendingans2)
        len_sendingans2_full = len(str(len_sendingans2))
        sendingans2 = sendingans2.decode(FORMAT)
        sendingans2 = str(len_sendingans2 + len_sendingans2_full + 1) + '\t' + sendingans2
        sendingans2 = sendingans2.encode(FORMAT)
        ClientSocket.send(sendingans2)
    
    def sendAnswer3(self):
        self.pause_action()
        global CURRENT_BUTTON_CLICKED
        CURRENT_BUTTON_CLICKED = 3
        self.answer3.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:rgb(102, 0, 204);")
        self.answer1.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer2.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer4.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer1.setEnabled(False)
        self.answer2.setEnabled(False)
        self.answer3.setEnabled(False)
        self.answer4.setEnabled(False)
        self.helpfiftybtn.setEnabled(False)
        self.helphundredbtn.setEnabled(False)

        sendingans3 = "6\t" + MYCLIENTNAME + "\t \t3"
        sendingans3 = sendingans3.encode(FORMAT)
        len_sendingans3 = len(sendingans3)
        len_sendingans3_full = len(str(len_sendingans3))
        sendingans3 = sendingans3.decode(FORMAT)
        sendingans3 = str(len_sendingans3 + len_sendingans3_full + 1) + '\t' + sendingans3
        sendingans3 = sendingans3.encode(FORMAT)
        ClientSocket.send(sendingans3)
    
    def sendAnswer4(self):
        self.pause_action()
        global CURRENT_BUTTON_CLICKED
        CURRENT_BUTTON_CLICKED = 4
        self.answer4.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:rgb(102, 0, 204);")
        self.answer1.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer2.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer3.setStyleSheet(
            "color:black;font-size:15pt;margin-top:30pt;margin-bottom:20pt;padding-top:50px;padding-bottom:30px;background-color:#B9D9EB;")
        self.answer1.setEnabled(False)
        self.answer2.setEnabled(False)
        self.answer3.setEnabled(False)
        self.answer4.setEnabled(False)
        self.helpfiftybtn.setEnabled(False)
        self.helphundredbtn.setEnabled(False)

        sendingans4 = "6\t" + MYCLIENTNAME + "\t \t4"
        sendingans4 = sendingans4.encode(FORMAT)
        len_sendingans4 = len(sendingans4)
        len_sendingans4_full = len(str(len_sendingans4))
        sendingans4 = sendingans4.decode(FORMAT)
        sendingans4 = str(len_sendingans4 + len_sendingans4_full + 1) + '\t' + sendingans4
        sendingans4 = sendingans4.encode(FORMAT)
        ClientSocket.send(sendingans4)
    
    def getNextQuestion(self):
        nextquestion = "3\t" + MYCLIENTNAME + "\t \t"
        nextquestion = nextquestion.encode(FORMAT)
        len_nextquestion = len(nextquestion)
        len_nextquestion_full = len(str(len_nextquestion))
        nextquestion = nextquestion.decode(FORMAT)
        nextquestion = str(len_nextquestion + len_nextquestion_full + 1) + '\t' + nextquestion
        nextquestion = nextquestion.encode(FORMAT)
        ClientSocket.send(nextquestion)
    
    def clearPlayWindow(self):
        self.myscore.setText("0 points")
        self.currentquestion_number.setText("0 / 10")
        self.timeleft.setText("00:20")
        self.opponentscore.setText("0 points")
        self.opponentname.setText("")
        self.question.setText("")
        self.helpfiftybtn.setText("50 : 50")
        self.answer1.setText("")
        self.answer2.setText("")
        self.answer3.setText("")
        self.answer4.setText("")
        self.helphundredbtn.setText("100%")
        self.helpfiftybtn.setEnabled(True)
        self.helphundredbtn.setEnabled(True)
    
    def getHelp50(self):
        global HELP50
        if HELP50 < 1:
            print("Not enough help in HELP50")
            return
        self.helpfiftybtn.setEnabled(False)
        self.helphundredbtn.setEnabled(False)

        gethelp50 = "9\t" + MYCLIENTNAME + "\t \thelp50"
        gethelp50 = gethelp50.encode(FORMAT)
        len_gethelp50 = len(gethelp50)
        len_gethelp50_full = len(str(len_gethelp50))
        gethelp50 = gethelp50.decode(FORMAT)
        gethelp50 = str(len_gethelp50 + len_gethelp50_full + 1) + '\t' + gethelp50
        gethelp50 = gethelp50.encode(FORMAT)
        ClientSocket.send(gethelp50)
    
    def getHelp100(self):
        global HELP100
        if HELP100 < 1:
            print("Not enough help in HELP100")
            return
        self.helphundredbtn.setEnabled(False)
        self.helpfiftybtn.setEnabled(False)

        gethelp100 = "9\t" + MYCLIENTNAME + "\t \thelp100"
        gethelp100 = gethelp100.encode(FORMAT)
        len_gethelp100 = len(gethelp100)
        len_gethelp100_full = len(str(len_gethelp100))
        gethelp100 = gethelp100.decode(FORMAT)
        gethelp100 = str(len_gethelp100 + len_gethelp100_full + 1) + '\t' + gethelp100
        gethelp100 = gethelp100.encode(FORMAT)
        ClientSocket.send(gethelp100)

    def myTimer(self):
        self.countsecs = SECONDS
        self.start = False

        self.countsecs = SECONDS * 10  # changing the value of countsecs

        self.timeleft.setText(str(SECONDS))
        self.start_action()
        try:
            self.timer.deleteLater()
        except Exception as e:
            print(str(e))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.start(100)  # update the timer every tenth second

    # method called by timer
    def showTime(self):
        if self.start:
            self.countsecs -= 1
            if self.countsecs == 0:
                self.start = False
                self.timeleft.setText("Time's UP!")
                print("TIME's UP!!!")
                self.answer1.setEnabled(False)
                self.answer2.setEnabled(False)
                self.answer3.setEnabled(False)
                self.answer4.setEnabled(False)
                self.helpfiftybtn.setEnabled(False)
                self.helphundredbtn.setEnabled(False)

                sendingNoans = "6\t" + MYCLIENTNAME + "\t \t-1"
                sendingNoans = sendingNoans.encode(FORMAT)
                len_sendingNoans = len(sendingNoans)
                len_sendingNoans_full = len(str(len_sendingNoans))
                sendingNoans = sendingNoans.decode(FORMAT)
                sendingNoans = str(len_sendingNoans + len_sendingNoans_full + 1) + '\t' + sendingNoans
                sendingNoans = sendingNoans.encode(FORMAT)
                ClientSocket.send(sendingNoans)

        if self.start:
            text = str(self.countsecs / 10) + " seconds" #getting text from countsecs
            self.timeleft.setText(text)

    def start_action(self):
        self.start = True
        if self.countsecs == 0:
            self.start = False

    def pause_action(self):
        self.start = False
        self.countsecs = SECONDS * 10
        

class ResultWindow(QWidget):
    def __init__(self):
        super().__init__(None, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setGeometry(50, 50, 1800, 950)
        self.setFixedSize(1800, 950)
        self.setWindowTitle("Result")
        self.setWindowModality(Qt.WindowModal)
        self.setStyleSheet("background-color:#7CB9E8;")
    
        self.resultlayout = QVBoxLayout()

        self.resulttext = QLabel()
        self.resulttext.setText("")
        self.resulttext.setAlignment(Qt.AlignHCenter)
        self.resulttext.setFixedWidth(1000)
        self.resulttext.setStyleSheet(
            "color:black;font-size:20pt;margin-top:10pt;margin-bottom:20px;")

        self.resultplayers = QHBoxLayout()

        self.resultplayer1 = QLabel()
        self.resultplayer1.setText("")
        self.resultplayer1.setAlignment(Qt.AlignCenter)
        self.resultplayer1.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;")
        self.resultplayer1.setFixedHeight(300)
        self.resultplayer1.setFixedWidth(500)

        self.resultplayer2 = QLabel()
        self.resultplayer2.setText("")
        self.resultplayer2.setAlignment(Qt.AlignCenter)
        self.resultplayer2.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;")
        self.resultplayer2.setFixedHeight(300)
        self.resultplayer2.setFixedWidth(500)

        self.resultplayers.addWidget(self.resultplayer1)
        self.resultplayers.addWidget(self.resultplayer2)

        self.exitresultlayout = QVBoxLayout()
        self.exitresultlayout.setAlignment(Qt.AlignCenter)
        self.exitresult = QPushButton()
        self.exitresult.setText("BACK TO Waiting Room")
        self.exitresult.setFixedWidth(400)
        self.exitresult.setFixedHeight(125)
        self.exitresult.setStyleSheet(
            "background-color:#0D141A;font-size:28px;text-align:center;color:white;margin-top:20px;")
        self.exitresultlayout.addWidget(self.exitresult)
        self.exitresult.clicked.connect(self.closeResultWindow)

        self.resultlayout.addWidget(self.resulttext)
        self.resultlayout.addLayout(self.resultplayers)
        self.resultlayout.addLayout(self.exitresultlayout)
        self.resultlayout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.resultlayout)
    
    def show_winning(self, myname, myscore_inpersent, myscore_incount, opponentname, opponentscore_inpersent, opponentscore_incount):
        self.resulttext.setText("CONGRATULATIONS! You won!")
        self.resulttext.setStyleSheet(
            "color:green;font-size:20pt;margin-top:10pt;margin-bottom:20px;font-weight:bold;")
        self.resultplayer1.setText(str(myname) + "\n\n" + str(round(float(myscore_inpersent), 2)) + "%\n\n" + \
            str(int(myscore_incount)) + " / 10")
        self.resultplayer1.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;border: 10px solid green;")
        self.resultplayer2.setText(str(opponentname) + "\n\n" + str(round(float(
            opponentscore_inpersent), 2)) + "%\n\n" + str(int(opponentscore_incount)) + " / 10")
        self.resultplayer2.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;border: 10px solid red;")
    
    def show_losing(self, myname, myscore_inpersent, myscore_incount, opponentname, opponentscore_inpersent, opponentscore_incount):
        self.resulttext.setText("You LOST the game!")
        self.resulttext.setStyleSheet(
            "color:red;font-size:20pt;margin-top:10pt;margin-bottom:20px;font-weight:bold;")
        self.resultplayer1.setText(str(myname) + "\n\n" + str(round(float(myscore_inpersent), 2)) + "%\n\n" +
            str(int(myscore_incount)) + " / 10")
        self.resultplayer1.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;border: 10px solid red;")
        self.resultplayer2.setText(str(opponentname) + "\n\n" + str(round(float(
            opponentscore_inpersent), 2)) + "%\n\n" + str(int(opponentscore_incount)) + " / 10")
        self.resultplayer2.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;border: 10px solid green;")
    
    def show_draw(self, myname, myscore_inpersent, myscore_incount, opponentname, opponentscore_inpersent, opponentscore_incount):
        self.resulttext.setText("It's a DRAW!!")
        self.resulttext.setStyleSheet(
            "color:brown;font-size:20pt;margin-top:10pt;margin-bottom:20px;font-weight:bold;")
        self.resultplayer1.setText(str(myname) + "\n\n" + str(round(float(myscore_inpersent), 2)) + "%\n\n" +
            str(int(myscore_incount)) + " / 10")
        self.resultplayer1.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;border: 10px solid brown;")
        self.resultplayer2.setText(str(opponentname) + "\n\n" + str(round(float(
            opponentscore_inpersent), 2)) + "%\n\n" + str(int(opponentscore_incount)) + " / 10")
        self.resultplayer2.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;border: 10px solid brown;")
    
    def closeResultWindow(self):
        resW.close()
        self.resulttext.setText("")
        self.resultplayer1.setText("")
        self.resultplayer2.setText("")
        self.resultplayer1.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;")
        self.resultplayer2.setStyleSheet(
            "color:black;font-size:22pt;margin-top:10pt;margin-bottom:10pt;")
        
        sendingfinish = "8\t" + MYCLIENTNAME + "\t \tFINISH"
        sendingfinish = sendingfinish.encode(FORMAT)
        len_sendingfinish = len(sendingfinish)
        len_sendingfinish_full = len(str(len_sendingfinish))
        sendingfinish = sendingfinish.decode(FORMAT)
        sendingfinish = str(len_sendingfinish + len_sendingfinish_full + 1) + '\t' + sendingfinish
        sendingfinish = sendingfinish.encode(FORMAT)
        ClientSocket.send(sendingfinish)

        waitW.play_btn.setEnabled(True)
        waitW.exit_btn.setEnabled(True)
        waitW.wait_errmsg.setText("Click START button to play!")
        waitW.show()

try:
    IP, PORT = getNetworkConfigData()
except:
    sys.exit()
global app
app = QApplication(sys.argv)
loginW = LoginWindow()
loginW.show()
waitW = WaitWindow()
waitW.hide()
playW = PlayWindow()
playW.hide()
resW = ResultWindow()
resW.hide()
sys.exit(app.exec_())