#Biceps

import cv2
import mediapipe as mp
import numpy as np
import datetime
import menu
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:

        print("x = ", x)
        print("y = ", y)

        if 170 < x < 500 and 370 < y < 410:
            print("MENU")
            cv2.destroyWindow("CURLS")
            menu.main()

#Function to calculate angle between a joint.
def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return angle


def main():

    cap = cv2.VideoCapture(0)  # "KneeBend.mp4"


    angle_at_elbow_thresh = 60
    time_thresh = 1
    time_diff = 0
    arm_bent = False
    rep_counted = False
    rep_count = 0
    now = 0
    finished = 0

    shoulder_number = 12
    # right_shoulder =11
    elbow_number = 14
    # right_elbow = 13
    wrist_number = 16
    # right_wrist = 15

    # Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.4, min_tracking_confidence=0.4) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if np.shape(frame) == ():
                break

            # flip image as a mirror
            frame = cv2.flip(frame, 1)

            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Make detection
            results = pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            if finished == 0:
                try:
                    landmarks = results.pose_landmarks.landmark

                    (shoulder, elbow, wrist) = (shoulder_number, elbow_number, wrist_number) if (
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].z < landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].z) else (24, 26, 28)
                    shoulder_coord = [landmarks[shoulder].x, landmarks[shoulder].y]
                    elbow_coord = [landmarks[elbow].x, landmarks[elbow].y]
                    wrist_coord = [landmarks[wrist].x, landmarks[wrist].y]
                    angle_at_elbow = calculate_angle(
                        shoulder_coord, elbow_coord, wrist_coord)
                    image = cv2.putText(image, "Elbow Angle:" + str(angle_at_elbow), (int(landmarks[elbow].x * 640), int(landmarks[elbow].y * 480)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 125, 255), 2, cv2.LINE_AA)

                    if rep_count < 3:
                        image = cv2.putText(image, "LEFT ARM", (20, 70),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 125, 255), 2, cv2.LINE_AA)
                    if rep_count >= 3 and rep_count < 6:
                        image = cv2.putText(image, "RIGHT ARM", (20, 70),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 125, 255), 2, cv2.LINE_AA)

                    if angle_at_elbow > angle_at_elbow_thresh:
                        arm_bent = False

                    if angle_at_elbow < angle_at_elbow_thresh and arm_bent == False:
                        arm_bent = True
                        rep_counted = False
                        now = datetime.datetime.now()

                    if arm_bent:
                        time_diff = (datetime.datetime.now() - now).total_seconds()
                        time_diff = round(time_diff, 1)
                        image = cv2.putText(image, "Time held:" + str(time_diff), (20, 100),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 125, 255), 2, cv2.LINE_AA)

                    if time_diff > time_thresh and rep_counted == False:
                        rep_count += 1
                        rep_counted = True

                    if rep_count == 3:
                        shoulder_number = 11
                        elbow_number = 13
                        wrist_number = 15

                    if rep_count == 6:
                        shoulder_number = -1
                        elbow_number = -1
                        wrist_number = -1
                        finished = 1

                    image = cv2.putText(image, "Rep count:" + str(rep_count), (20, 460),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 125, 255), 3, cv2.LINE_AA)

                except:
                    pass

            if finished == 1:
                image = cv2.putText(image, "FINISHED", (200, 200),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 125, 255), 3, cv2.LINE_AA)
                image = cv2.putText(image, "Return to menu", (200, 400),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 125, 255), 3, cv2.LINE_AA)
                cv2.rectangle(image, pt1=(170, 370), pt2=(500, 410),
                            color=(0, 125, 255), thickness=3)

            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(
                                        color=(245, 117, 66), thickness=2, circle_radius=2),
                                    mp_drawing.DrawingSpec(
                                        color=(245, 66, 230), thickness=2, circle_radius=2)
                                    )

            cv2.imshow('CURLS', image)

            # Définir la fonction de rappel pour le clic de souris
            cv2.setMouseCallback("CURLS", on_click)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyWindow('CURLS')
