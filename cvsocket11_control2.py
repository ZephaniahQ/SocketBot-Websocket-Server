import asyncio
from websockets import serve
import subprocess

# A list to store messages received
received_messages = []
rc_state = True

async def handle_connection(websocket, path):
    global received_messages
    global rc_state
    if path == '/control':
        print(f"Control connection established from {websocket.remote_address}")
        async for message in websocket:
            # Store the message for sending clients
            if message == 'toggle':
                handle_toggle()
            elif rc_state:
                received_messages.append(message)
                print(f"Received message: {message}")
                
    elif path == '/cv':
        print(f"CV connection established from {websocket.remote_address}")
        async for message in websocket:
            if rc_state:
                await websocket.send('kill')
                print("Killing CV script")
            else:
                received_messages.append(message)
                print(f"Received CV message: {message}")
            

    elif path == '/receive':
        print(f"Receive connection established from {websocket.remote_address}")
        while True:
            if received_messages:
                # Send the last received message to the client
                await websocket.send(received_messages[-1])
                print(f"Sent last message to receive client: {received_messages[-1]}")
                # Remove the message from the list after sending it
                received_messages.pop()
            else:
                    print("No message to send to receive client.")
            await asyncio.sleep(0.1)  # Small delay before checking for new messages



def handle_toggle():
    global rc_state

    # Toggle the state
    rc_state = not rc_state
    if rc_state:
        print("Toggling to RC mode")
        print(f"rc_state = {rc_state}")
        subprocess.Popen(["pkill", "-f", "cvchanel_test.py", "release_and_close"])


    else:
        print("Toggling to CV Mode")
        subprocess.Popen(["C:/Users/HP/anaconda3/envs/socketcv/python.exe", "C:/Users/HP/Desktop/Code/opencv_py/processing/cvchanel_test.py"])
        print(f"rc_state = {rc_state}")

async def main():
    print("Starting WebSocket server...")
    try:
        async with serve(handle_connection, "0.0.0.0", 5000):
            print("WebSocket server is running.")
            await asyncio.Future()  # run forever
    except Exception as e:
        print(f"Error starting WebSocket server: {e}")

asyncio.run(main())
