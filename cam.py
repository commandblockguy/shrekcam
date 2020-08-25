import cv2, pyfakewebcam, os, numpy as np, select, sys, importlib
import commands, process_frame

cap = cv2.VideoCapture('/dev/video2')

height, width = 720, 1280

options = commands.defaults(height, width)

# configure camera for 720p @ 60 FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH ,width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
cap.set(cv2.CAP_PROP_FPS, 60)

fake = pyfakewebcam.FakeWebcam('/dev/video20', width, height)

while True:
    try:
        if select.select([sys.stdin,],[],[],0.0)[0]:
            options = commands.process_command(sys.stdin.readline(), options)
            if options['reload']:
                importlib.reload(process_frame)
                importlib.reload(commands)
                print('reloaded modules')
                options['reload'] = False
    except Exception as e:
        print(e)

    _, frame = cap.read()

    try:
        frame = process_frame.get_frame(frame, options)
    except Exception as e:
        print(e)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    fake.schedule_frame(frame)

