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
            cv2.destroyWindow("SQUAT")
            menu.main()

# Function to calculate angle between a joint.


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
        np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return angle


def main():

    cap = cv2.VideoCapture(0)  # 0 for default camera
    angle_at_knee_max = 90
    angle_at_hip_max = 65
    time_max = .5
    time_diff = 0
    knee_bent = False
    rep_counted = False
    rep_count = 0
    now = 0
    finished = 0
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

                    (hip_left, knee_left, ankle_left,
                     shoulder_left) = (23, 25, 27, 11)
                    hip_coord_left = [
                        landmarks[hip_left].x, landmarks[hip_left].y]
                    knee_coord_left = [
                        landmarks[knee_left].x, landmarks[knee_left].y]
                    ankle_coord_left = [
                        landmarks[ankle_left].x, landmarks[ankle_left].y]
                    shoulder_coord_left = [
                        landmarks[shoulder_left].x, landmarks[shoulder_left].y]
                    angle_at_knee_left = calculate_angle(
                        hip_coord_left, knee_coord_left, ankle_coord_left)
                    angle_at_hip_left = calculate_angle(
                        knee_coord_left, hip_coord_left, shoulder_coord_left)

                    (hip_right, knee_right, ankle_right,
                     shoulder_right) = (24, 26, 28, 12)
                    hip_coord_right = [
                        landmarks[hip_right].x, landmarks[hip_right].y]
                    knee_coord_right = [
                        landmarks[knee_right].x, landmarks[knee_right].y]
                    ankle_coord_right = [
                        landmarks[ankle_right].x, landmarks[ankle_right].y]
                    shoulder_coord_right = [
                        landmarks[shoulder_right].x, landmarks[shoulder_right].y]
                    angle_at_knee_right = calculate_angle(
                        hip_coord_right, knee_coord_right, ankle_coord_right)
                    angle_at_hip_right = calculate_angle(
                        knee_coord_right, hip_coord_right, shoulder_coord_right)

                    angle_at_hip = (angle_at_hip_left + angle_at_hip_right)/2

                    # image = cv2.putText(image,"Knee Angle:" + str(angle_at_knee), (int(landmarks[knee].x * 640), int(landmarks[knee].y * 480)),
                    #                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)

                    if angle_at_knee_left > angle_at_knee_max or angle_at_knee_right > angle_at_knee_max or angle_at_hip > angle_at_hip_max:
                        if time_diff < time_max:
                            image = cv2.putText(image, "Keep Your Knee bent", (20, 70),
                                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                        knee_bent = False

                    if angle_at_knee_left <= angle_at_knee_max and angle_at_knee_left <= angle_at_knee_max and angle_at_hip <= angle_at_hip_max and knee_bent == False:
                        knee_bent = True
                        rep_counted = False
                        now = datetime.datetime.now()

                    if knee_bent:
                        time_diff = (datetime.datetime.now() -
                                     now).total_seconds()
                        image = cv2.putText(image, "Time held:" + str(time_diff), (20, 30),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    if time_diff > time_max and rep_counted == False:
                        rep_count += 1
                        rep_counted = True

                    if rep_count == 3:
                        finished = 1

                    image = cv2.putText(image, "Rep count:" + str(rep_count), (20, 460),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 125, 255), 2, cv2.LINE_AA)

                except:
                    pass

            if finished == 1:
                image = cv2.putText(image, "FINISHED", (200, 200),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 125, 255), 3, cv2.LINE_AA)
                image = cv2.putText(image, "Return to menu", (200, 400),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 125, 255), 3, cv2.LINE_AA)
                cv2.rectangle(image, pt1=(170, 370), pt2=(
                    500, 410), color=(0, 125, 255), thickness=3)

            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(
                                          color=(245, 117, 66), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(
                                          color=(245, 66, 230), thickness=2, circle_radius=2)
                                      )

            cv2.imshow('SQUAT', image)

            # Définir la fonction de rappel pour le clic de souris
            cv2.setMouseCallback("SQUAT", on_click)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyWindow("SQUAT")
