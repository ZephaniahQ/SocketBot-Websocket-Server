import cv2
import numpy as np
import math
import time

# Initialize last_threshold_check_time
last_threshold_check_time = time.time()

# Function to perform threshold checking and decision-making
def check_thresholds(distance, angle):
    distance_threshold = 8  # Adjust as needed
    angle_threshold = 8  # Adjust as needed

    if (distance < 38 and angle < 78):
        print ("Turn left")
    elif (distance > 46 and angle > 82):
        print ("Turn right")
    else: print("Go Forward")


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

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7,  7),  0)
        thresh = cv2.adaptiveThreshold(blurred,  255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,  11,  7)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_contour_area =   300 # Adjust this value based on your requirements
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
        
        if contours:
            for contour in contours:
                # Separate contours into two groups based on their positions
                left_line_contours = []
                right_line_contours = []

                # Calculate the centroid of the contour
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    if cX < width / 2:
                        left_line_contours.append(contour)
                    else:
                        right_line_contours.append(contour)

            # Draw contours for left line
            cv2.drawContours(frame, left_line_contours, -1, (0, 255, 0), 3)

            # Draw contours for right line
            cv2.drawContours(frame, right_line_contours, -1, (0, 0, 255), 3)


            # Collecting all contour points
            all_contour_points = np.vstack(contours).squeeze()

            # Fit a line through all the contour points using least squares
            vx, vy, x, y = cv2.fitLine(all_contour_points, cv2.DIST_L2, 0, 0.01, 0.01)
            slope = vy / vx

            distance = abs(center_x - int(x))

            if slope >= 0:
                angle = math.atan(slope) * 180 / math.pi
            else:
                angle = 180 + math.atan(slope) * 180 / math.pi

            #drawing the center-fit line
            point1 = (int(x - 1000 * vx), int(y - 1000 * vy))
            point2 = (int(x + 1000 * vx), int(y + 1000 * vy))

            # Draw the fitline on the frame
            cv2.line(frame, point1, point2, (0, 0, 255), 2)

            # Draw the point on the fitline at center y-coordinate of the frame
            cv2.circle(frame, (center_x, center_y), 5, (0, 255, 255), -1)

            # Draw the distance on the frame
            cv2.putText(frame, "D: {:.2f}".format(distance), (10, center_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
           
            # Calculate x-coordinate at the center y-coordinate of the frame
            x_at_center_y = int(x + ((center_y - y) / vy) * vx)

            # Point on the fitline at center y-coordinate of the frame
            point_at_center_y = (x_at_center_y, center_y)

            # Draw the point on the fitline at center y-coordinate of the frame
            cv2.circle(frame, (center_x, center_y),5, (0,255,255), -1)
            cv2.circle(frame, point_at_center_y, 5, (0, 255, 255), -1)

            # Check thresholds and make decisions every 500ms
            if time.time() - last_threshold_check_time >= 0.5:
                check_thresholds(distance, angle)
                last_threshold_check_time = time.time()
            if angle:
                cv2.putText(frame, "Angle: {:.2f}".format(angle), (10, center_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            #cv2.drawContours(frame, contours, -1, (0,  255,  0),  3)
            cv2.line(frame, (center_x, center_y), point_at_center_y, (255,0,0),2)


        # Display the resulting frame
        cv2.imshow('Tilted Frame', frame)
        
        # Press Q on keyboard to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
