# TCPQuizClient written in Python (PyQT5)

## Description:

  The application can be used for playing a REAL-TIME multiple-choice quiz game with another user.
  The TCP Quiz server must be running and must accept the clients.
  
  First of all, a login with username and password is required. After a successful login, the user is redirected to the waiting room
  where a list of connected clients are shown at the left side. Also on the right side is a PLAY button to start a new game and a DISCONNECT button
  to leave the waiting room and disconnect from the server.
  By clicking the PLAY button, the server starts to find you an opponent to play with. This might take a few seconds. If there are no users available to play, 
  a message appears under the Play button to inform you about it, otherwise you'll be redirected to the Playing room and the game will automatically start.
  
  
