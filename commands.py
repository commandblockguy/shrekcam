import cv2, numpy as np, os.path, time
from os import path
from process_frame import get_next_cc

def defaults(height, width):
    options = {}
    options['height'] = height
    options['width'] = width
    options['mode'] = 'image'
    options['use_watermark'] = False
    options['use_bg'] = False
    options['paused'] = False
    options['text_enabled'] = False
    options['text'] = 'dummy text'
    blank = np.zeros((height,width,3), np.uint8)
    options['bg_frame'] = blank
    options['reload'] = False
    options['captions'] = False
    options['mirror_vert'] = False
    options['mirror_horiz'] = False
    return options

# this is very bad
def process_command(line, options):
    args = line[:-1].split(' ')
    if args[0] == 'video':
        filename = ' '.join(args[1:])
        if path.exists(filename):
            options['video_file'] = cv2.VideoCapture(filename)
            options['mode'] = 'video'
            options['start_time'] = int(time.time() * 1000)
            print("Opening " + filename + " as video")
            captions_filename = path.splitext(filename)[0] + '.srt'
            if path.exists(captions_filename):
                options['captions_file'] = open(captions_filename, 'r')
                options['captions'] = True
                options['current_caption'] = (0, 0, "")
                print('Loaded captions from ' + captions_filename)
        else:
            print('failed to load ' + filename)
    elif args[0] == 'image':
        filename = ' '.join(args[1:])
        if path.exists(filename):
            bg_frame_raw = cv2.imread(filename)
            options['bg_frame'] = cv2.resize(bg_frame_raw, (width, height))
            options['mode'] = 'image'
            print("Opening " + filename + " as image")
        else:
            print('failed to load ' + filename)
    elif args[0] == 'time' and options['mode'] == 'video':
        options['start_time'] = int(time.time() * 1000) - int(args[1])
    elif args[0] == 'get_frame' and options['mode'] == 'video':
        print(options['video_file'].get(cv2.CAP_PROP_POS_FRAMES))
    elif args[0] == 'restart' and options['mode'] == 'video':
        options['video_file'].set(cv2.CAP_PROP_POS_FRAMES, 0)
        options['start_time'] = int(time.time() * 1000)
    elif args[0] == 'watermark':
        if args[1] == 'off':
            options['use_watermark'] = False
        else:
            filename = ' '.join(args[1:])
            if path.exists(filename):
                options['use_watermark'] = True
                options['watermark'] = cv2.imread(' '.join(args[1:]))
            else:
                print('failed to load ' + filename)
    elif args[0] == 'background':
        if args[1] == 'on':
            options['use_bg'] = True
        else:
            options['use_bg'] = False
    elif args[0] == 'captions':
        if args[1] == 'off':
            options['captions'] = False
        else:
            filename = ' '.join(args[1:])
            if path.exists(filename):
                options['captions_file'] = open(filename, 'r')
                options['captions'] = True
                options['current_caption'] = (0, 0, "")
                print('Loaded captions from ' + filename)
    elif args[0] == 'play' and options['mode'] == 'video':
        options['paused'] = False
        options['start_time'] = int(time.time() * 1000) - options['pause_ms']
        options['video_file'].set(cv2.CAP_PROP_POS_MSEC, options['pause_ms'])
    elif args[0] == 'pause' and options['mode'] == 'video':
        options['paused'] = True
        options['pause_ms'] = options['video_file'].get(cv2.CAP_PROP_POS_MSEC)
    elif args[0] == 'text':
        if args[1] == 'off':
            options['text_enabled'] = False
        else:
            options['text'] = ' '.join(args[1:])
            options['text_enabled'] = True
    elif args[0] == 'mirror_vert':
        if args[1] == 'on':
            options['mirror_vert'] = True
        else:
            options['mirror_vert'] = False
    elif args[0] == 'mirror_horiz':
        if args[1] == 'on':
            options['mirror_horiz'] = True
        else:
            options['mirror_horiz'] = False
    elif args[0] == 'reload':
        options['reload'] = True
    elif args[0] == 'ping':
        print('pong')
    elif args[0] == 'test':
        print('starting test')
        with open('./data/shrek.srt') as subs:
            print(get_next_cc(subs))
    elif args[0] == 'stop':
        exit(0)
    else:
        print('unknown command: ' + args[0])
    return options