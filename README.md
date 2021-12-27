# TCPQuizClient written in Python (PyQT5)

## How to use

1. Download the TCPQuizClient.zip file and extract the files from it. (contains 2 files)
2. Open the network_config.ini file with a text editor and replace the IP address with the address you get from me! :)
![image](https://user-images.githubusercontent.com/93404199/147420079-ea9aea8a-836a-4a7b-922f-491b46c2a69a.png)
3. Save the .ini file, close it and start the TCPQuizClient.exe file

## Description:

  The application can be used for playing a REAL-TIME multiple-choice quiz game with another user.
  
  The TCP Quiz server must be running and must accept the clients. Link to TCP quiz server: https://github.com/kedvesnorbert/TCPQuizServer
  
  
  First of all, a login with username and password is required. After a successful login, the user is redirected to the waiting room
  where a list of connected clients are shown at the left side. Also on the right side is a PLAY button to start a new game and a DISCONNECT button
  to leave the waiting room and disconnect from the server.
  By clicking the PLAY button, the server starts to find you an opponent to play with. This might take a few seconds. If there are no users available to play, 
  a message appears under the Play button to inform you about it, otherwise you'll be redirected to the Playing room and the game will automatically start.
  
  NOTE!! You cannot directly choose the opponent to play with!!!
  
  The Playing room shows your and the opponent's username and both of your current score in points. The question to be answered and the four answers to choose from
  is shown at the center of the window. There's ALWAYS 1 CORRECT ANSWER. Time limit: 20 seconds / question.
  After clicking one of the answers, the server checks if the opponent has already answered. If so, you will see your opponent's answer and of course, the correct answer.
  
  NOTE! Depending on the difficulty of the question it'll be added one or two points if you have answered correctly.
  
  After the game is over, you'll se the result and you can get back to the waiting room.
  
  
  # Screenshots
  <p>
  <img src="https://user-images.githubusercontent.com/93404199/147491771-f5f9075e-530c-4b9a-a382-06ca8da979f6.png" width=45% height=50%>
  <img src="https://user-images.githubusercontent.com/93404199/147492004-b80dcd9a-90c1-42a8-a83e-98d5374d3bf1.png" width=45% height=50%>
  </p>

