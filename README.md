# SocketBot-Websocket-Server

This is a python websocket server that communicates between the remote control app and the receiver app and transfers control instructions. There is a main server file and 2 opencv files.
The server uses 3 different channels, one for receiving messages named 'control', one for sending named 'receive', and one experimental on 'cv' for opencv integration and autonomous driving.
Opencv integration failed however as opencv is not behaving well with async websocket code, even tried syncronous websocket package but opencv still stutters. Did not find any other feasible way yet to transfer
control instructions from opencv code to websocket code, moreover opencv implementation is not complete either. As the camera is not centered on the robot a lot of challenges are introduced which surpass my current opencv skills.
In the future I plan to implement a webrtc solution instead of websockets and try different detection methods such as yolov.
