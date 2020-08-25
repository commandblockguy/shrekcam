import cv2, numpy as np, requests, time, parse

def get_mask(frame, bodypix_url='http://localhost:9000'):
    _, data = cv2.imencode(".jpg", frame)
    r = requests.post(
        url=bodypix_url,
        data=data.tobytes(),
        headers={'Content-Type': 'application/octet-stream'})
    mask = np.frombuffer(r.content, dtype=np.uint8)
    mask = mask.reshape((frame.shape[0], frame.shape[1]))
    return mask

def post_process_mask(mask):
    mask = cv2.dilate(mask, np.ones((10,10), np.uint8) , iterations=1)
    mask = cv2.erode(mask, np.ones((10,10), np.uint8) , iterations=1)
    return mask

def add_watermark(frame, options):
    num_rows = options['watermark'].shape[0]
    num_frame_rows = frame.shape[0]
    for row in range(num_rows):
        for channel in range(frame.shape[2]):
            frame[num_frame_rows - num_rows + row, :, channel] = options['watermark'][row, :, channel]
    return frame

def get_next_cc(fh):
    fh.readline()
    ts_line = fh.readline()
    ts_res = parse.parse('{}:{}:{},{} --> {}:{}:{},{}\n', ts_line)
    ts_res = list(map(int, list(ts_res)))
    start = tuple(ts_res[:4])
    end = tuple(ts_res[4:])
    start_ms = start[3] + 1000 * start[2] + 60000 * start[1] + 3600000 * start[0]
    end_ms = end[3] + 1000 * end[2] + 60000 * end[1] + 3600000 * end[0]
    lines = []
    while True:
        line = fh.readline()
        if line == '\n':
            break
        lines.append(line)
    return (start_ms, end_ms, lines)

def get_frame(frame, options):
    if options['mode'] == 'video' and not options['paused']:
        # if more than 1 second behind, or ahead, skip directly to the frame
        initial_frame_time = options['video_file'].get(cv2.CAP_PROP_POS_MSEC) + options['start_time']
        if initial_frame_time < int(time.time() * 1000) - 1000 or initial_frame_time > int(time.time() * 1000):
           options['video_file'].set(cv2.CAP_PROP_POS_MSEC, int(time.time() * 1000) - options['start_time'])
        while options['video_file'].get(cv2.CAP_PROP_POS_MSEC) + options['start_time'] < int(time.time() * 1000):
            ret, options['bg_frame'] = options['video_file'].read()
            if not ret:
                options['start_time'] = int(time.time() * 1000)
                options['video_file'].set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, options['bg_frame'] = options['video_file'].read()
    options['bg_frame'] = cv2.resize(options['bg_frame'], (options['width'], options['height']))
    mask = None
    if options['use_bg']:
        while mask is None:
            try:
                mask = get_mask(frame)
            except requests.RequestException as e:
                print(e)
            mask = post_process_mask(mask)
            inv_mask = 1-mask
            for c in range(frame.shape[2]):
                frame[:,:,c] = frame[:,:,c]*mask + options['bg_frame'][:,:,c]*inv_mask
    if options['use_watermark']:
        frame = add_watermark(frame, options)
    if options['captions'] and options['mode'] == 'video':
        curr_time = options['video_file'].get(cv2.CAP_PROP_POS_MSEC)
        curr_cap = options['current_caption']
        while curr_cap[1] < curr_time:
            curr_cap = get_next_cc(options['captions_file'])
            options['current_caption'] = curr_cap
        if curr_cap[0] <= curr_time:
            # todo: wrap text, multi-line
            for i in range(0, len(curr_cap[2])):
                cv2.putText(frame, curr_cap[2][i][:-1], (50, 100 + 40 * i), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    elif options['text_enabled']:
        cv2.putText(frame, options['text'], (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)
    if options['mirror_vert']:
        for c in range(frame.shape[2]):
            frame[:,:,c] = frame[::-1,:,c]
    if options['mirror_horiz']:
        for c in range(frame.shape[2]):
            frame[:,:,c] = frame[:,::-1,c]
    return frame