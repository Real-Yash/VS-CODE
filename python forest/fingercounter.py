import time
import cv2
import numpy as np
import mediapipe as mp

from metasense import MetaSense

mp_draw = mp.solutions.drawing_utils
mp_draw_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

with mp_hands.Hands(
  model_complexity=1,
  min_detection_confidence=0.5,
  min_tracking_confidence=0.5
 ) as hands:


  COM_PORT = "/dev/cu.usbserial-202206_1CF25B0"
  BASE_BARTRATE = 115200
  MAX_BARTRATE = 3000000

  QUANTIZE = 2 # mm
  # LED_EMIT_DISTANCE = 20


  if __name__ == '__main__':


    # init metasense
    metasense = MetaSense(COM_PORT, BASE_BARTRATE)
    metasense.start()
    metasense.sendCmd("AT+DISP=3\r")
    time.sleep(0.1)
    metasense.sendCmd("AT+UINT={}\r".format(QUANTIZE))
    metasense.sendCmd("AT+FPS=5\r")
    
    is_first_frame = True
    last_frame_id = 0

    try:

        while True:
            frame = metasense.tof_data_queue.get()
            # print(frame['frameID'], frame['res'])
            frame_id = frame['frameID']
            frame_res = frame['res']
            frame_data = frame['frameData']
            frame_data0 = frame['frameData']

            frame_img0 = np.array(frame_data0, np.uint8).reshape(frame_res[0], frame_res[1])
            frame_img0 = cv2.flip(frame_img0, 1)
            frame_img0 = cv2.applyColorMap(frame_img0, cv2.COLORMAP_RAINBOW)
            ##print(frame_id, frame_data[0])

            for idx,data in enumerate(frame_data):
                if(data > 110): frame_data[idx] = 0

            # convert frame data to image
            frame_img = np.array(frame_data, np.uint8).reshape(frame_res[0], frame_res[1])


            #print("Center pixel distance is {} mm".format(frame_img[50][50]))
            # rotate image 180 degree
            frame_img = cv2.flip(frame_img, 1)
            color_img = cv2.applyColorMap(frame_img, cv2.COLORMAP_TWILIGHT_SHIFTED   ) # cv2.COLORMAP_JET
            #color_img = cv2.cvtColor(color_img,cv2.COLOR_BGR2RGB)



            roi = [0,0,100,100]
            roi_w = 100
            roi_h = 100


            #cv2.rectangle(color_img, (int(roi[0]), int(roi[1])), (int(roi[0] + roi[2]), int(roi[1] + roi[3])), (0, 255, 0), 2)
            # crop roi area from frame image
            roi_img = frame_img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
            # rescale roi image to 10x
            roi_img_2 = cv2.resize(roi_img, (roi_w * 10, roi_h * 10))



            roi_img_3 = cv2.resize(color_img, (roi_w * 10, roi_h * 10))

            results = hands.process(roi_img_3)
            print(results.multi_hand_landmarks)






            # convert to binary image
            # roi_img_2_binary = cv2.threshold(roi_img_2, 0, 255, cv2.THpRESH_BINARY | cv2.THRESH_OTSU)[1]
            # draw keyboard on roi image
            keyboard_pixel_width = roi_w * 10 
            keyboard_pixel_height = roi_h * 10

            fingerCount = 0
            if results.multi_hand_landmarks:
                for landmark in results.multi_hand_landmarks:
                    handIndex = results.multi_hand_landmarks.index(landmark)
                    handLabel = results.multi_handedness[handIndex].classification[0].label

                    handLandmarks = []
                    for landmarks in landmark.landmark:
                        handLandmarks.append([landmarks.x, landmarks.y])

                    if handLabel == "Left" and handLandmarks[4][0] > handLandmarks[3][0]:
                        fingerCount = fingerCount + 1
                    elif handLabel == "Right" and handLandmarks[4][0] < handLandmarks[3][0]:
                        fingerCount = fingerCount + 1

                    if handLandmarks[8][1] < handLandmarks[6][1]:
                        fingerCount = fingerCount + 1
                    if handLandmarks[12][1] < handLandmarks[10][1]:
                        fingerCount = fingerCount + 1
                    if handLandmarks[16][1] < handLandmarks[14][1]:
                        fingerCount = fingerCount + 1
                    if handLandmarks[20][1] < handLandmarks[18][1]:
                        fingerCount = fingerCount + 1
                    mp_draw.draw_landmarks(roi_img_3, landmark,mp_hands.HAND_CONNECTIONS,
                                           mp_draw_styles.get_default_hand_landmarks_style(),
                                           mp_draw_styles.get_default_hand_connections_style()
                                           )
            cv2.putText(roi_img_3, str(fingerCount), (50, 450), cv2.FONT_HERSHEY_COMPLEX_SMALL, 10, (255, 0, 0), 10)
            # show images
            #frame_img0 = cv2.resize(frame_img0, (roi_w * 10, roi_h * 10))

            #cv2.imshow("roi_img", roi_img_2)
            #cv2.imshow("frame0", frame_img0)
            cv2.imshow("color", roi_img_3)
            cv2.waitKey(1)


    except KeyboardInterrupt:
        metasense.terminate()

        exit()
    # except Exception as e:
    #     print("error on main",e)
    #     metasense.terminate()
    #     exit()

