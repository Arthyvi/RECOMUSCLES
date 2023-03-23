import cv2
import mediapipe as mp
#import subprocess
import squat
import biceps
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic


def on_mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:

        print("x = ", x)
        print("y = ", y)
        
        if 100 < x < 220 and 65 < y < 115:
            print("SQUAT")
            #subprocess.run(["python", "squat.py"])
            cv2.destroyWindow("MENU")
            squat.main()
        if 420 < x < 440 and 65 < y < 115:
            print("CURLS")
            #subprocess.run(["python", "biceps.py"])
            cv2.destroyWindow("MENU")
            biceps.main()

def calculer_centre(image, text, pos):
    # Calculer les dimensions de l'image
    height, width, channels = image.shape

    # Calculer les coordonnées du centre de l'image
    x = int(width/pos)
    y = int(height/pos)

    # Définir la police et la taille du texte
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (0, 255, 255)  # blanc
    line_type = 2

    # Calculer la taille du texte
    text_size, _ = cv2.getTextSize(text, font, font_scale, line_type)

    # Calculer les coordonnées du coin supérieur gauche du texte pour qu'il soit centré
    text_x = int(x - (text_size[0] / 2))
    text_y = int(y + (text_size[1] / 2))

    return text_x, text_y, font, font_scale, font_color, line_type

def main():
    # For webcam input:
    cap = cv2.VideoCapture(0)
    with mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)

            # Draw landmark annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image,
                results.face_landmarks,
                mp_holistic.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_contours_style())
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles
                .get_default_pose_landmarks_style())

            # inverser l'image
            image = cv2.flip(image, 1)

            # centrer le texte
            text_x, text_y, font, font_scale, font_color, line_type = calculer_centre(image, "MENU", 2)

            # texte
            cv2.putText(image, "MENU", (text_x, 20),
                        font, font_scale, font_color, line_type)	
            
            # bouton squat
            text_x, text_y, font, font_scale, font_color, line_type = calculer_centre(image, "SQUAT", 4)
            cv2.putText(image, "SQUAT", (text_x, 100),
                        font, font_scale, font_color, line_type)
            x1_rect_squat, x2_rect_squat= text_x-10, text_x + 110
            y1_rect, y2_rect= 65, 115
            cv2.rectangle(image, (x1_rect_squat, y1_rect), (x2_rect_squat, y2_rect), (0, 255, 255), 2)
            
            # bouton curls
            text_x, text_y, font, font_scale, font_color, line_type = calculer_centre(image, "CURLS", 4/3)
            cv2.putText(image, "CURLS", (text_x, 100),
                        font, font_scale, font_color, line_type)
            x1_rect_curls, x2_rect_curls= text_x-10, text_x + 110
            cv2.rectangle(image, (x1_rect_curls, y1_rect), (x2_rect_curls, y2_rect), (0, 255, 255), 2)

            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MENU', image)

            # Définir la fonction de rappel pour le clic de souris
            cv2.setMouseCallback("MENU", on_mouse_click)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


main()

