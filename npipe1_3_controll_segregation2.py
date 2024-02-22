import cv2
import numpy as np
import math
import time
from simple_websocket import Client, ConnectionClosed

signal = 's'

ws = Client.connect('ws://localhost:5000/cv')
try:
    while True:
        ws.send(signal)
        #data = ws.receive()
        #print(f'< {data}')
except (KeyboardInterrupt, EOFError, ConnectionClosed):
    ws.close()

# Initialize last_threshold_check_time
last_threshold_check_time = time.time()

# Function to perform threshold checking and decision-making
def check_thresholds(distance_quarter_y, angle):
    global signal
    if (distance_quarter_y <= 75 and distance_quarter_y >= 38):
        print("Go Forward")
        signal = 'F'
        if (angle > 85):
            print("Turn right")
            signal = "R"
        elif (angle < 60):
            print("Turn Left")
            signal = "L"
    else: print("stop")
    # if angle <= 78 or angle >= 80:
    #     print("Go Forward")
    #     return 'F'
    # elif distance < 38 and angle < 78:
    #     print("Turn left")
    #     return 'L'
    # elif distance > 46 and angle > 82:
    #     print("Turn right")
    #     return 'R'
    # else:
    #     print("Stop")
    #     return 'S'

# Replace with your RTSP stream URL
rtsp_url = "rtsp://192.168.10.10:1935/h264_ulaw.sdp"

# Create a VideoCapture object
cap = cv2.VideoCapture(rtsp_url)

# Check if camera opened successfully
if not cap.isOpened():
    print("Error opening video stream")
else:
    # Read until video is completed
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        # If frame is read correctly ret is True
        if not ret:
            break

        height, width = frame.shape[:2]
        center_x = width // 2
        center_y = height // 2
        quarter_y = 3 * height // 4

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7,  7),  0)
        thresh = cv2.adaptiveThreshold(blurred,  255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,  11,  7)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_contour_area = 300  # Adjust this value based on your requirements
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
        
        if contours:
            # Collecting all contour points
            all_contour_points = np.vstack(contours).squeeze()

            # Fit a line through all the contour points using least squares
            vx, vy, x, y = cv2.fitLine(all_contour_points, cv2.DIST_L2, 0, 0.01, 0.01)
            slope = vy / vx

            if slope >= 0:
                angle = math.atan(slope) * 180 / math.pi
            else:
                angle = 180 + math.atan(slope) * 180 / math.pi

            # Drawing the center-fit line
            point1 = (int(x - 1000 * vx), int(y - 1000 * vy))
            point2 = (int(x + 1000 * vx), int(y + 1000 * vy))

            # Draw the fitline on the frame
            cv2.line(frame, point1, point2, (0, 0, 255), 2)

            # Calculate x-coordinate at the lower quarter y-coordinate of the frame
            x_at_quarter_y = int(x + ((quarter_y - y) / vy) * vx)

            # Calculate the distance between the center x-coordinate and x-coordinate at lower quarter y
            distance_quarter_y = abs(center_x - x_at_quarter_y)

            # Draw the yellow circle at the center x at 3/4 height
            cv2.circle(frame, (center_x, quarter_y), 5, (0, 255, 255), -1)

            # Draw the yellow circle at the x at quarter y height
            cv2.circle(frame, (x_at_quarter_y, quarter_y), 5, (0, 255, 255), -1)

            # Draw the blue line between the two points
            cv2.line(frame, (center_x, quarter_y), (x_at_quarter_y, quarter_y), (255, 0, 0), 2)

            # Check thresholds and make decisions every 500ms
            if time.time() - last_threshold_check_time >= 1:
                check_thresholds(distance_quarter_y, angle)
                last_threshold_check_time = time.time()

            # Draw the angle on the frame
            if angle:
                cv2.putText(frame, "Angle: {:.2f}".format(angle), (10, center_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 2)
            if distance_quarter_y:
                cv2.putText(frame, "distance: {:.2f}".format(distance_quarter_y),(10, center_y + 50), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255,255,255))
                #cv2.putText(frame, "Thresh: {:.2f}".format(distance_quarter_y),(10, center_y + 70), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255,255,255))

        # Display the resulting frame
        cv2.imshow('Tilted Frame', frame)

        # Press Q on keyboard to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
