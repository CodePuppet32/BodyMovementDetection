button_font = ('Consolas', 13, 'bold')
heading_text_font = ('Consolas', 18)
heading_text_font_bold = ('Ubuntu ', 18, 'bold')
default_text_font = ('Courier ', 10)
default_text_font_bold = ('Courier ', 10, 'bold')
background_color = '#FF9DDA'
background_highlight_color = '#CC704B'

default_button = {'activebackground': 'gray26', 'bg': 'RoyalBlue3', 'relief': 'groove', 'width': '10',
                  'fg': 'gray26', 'font': button_font, 'bd': 2}

# ---- CAUTION ----
# combination of high read_nth_frame_video and low wait_for_n_frames will defy the objective of this project

# how many number of frames of video are to be skipped
# A video usually has 24 to 60 FPS we do not need to read every single frame to be able to detect any movement
# usually remains for 20-40 frames
# minimum 1
read_nth_frame_video = 6

# how many frames should be processed before the detection takes place
# it should not be lower than 20, as we will lose ability to detect change in the video
# grater value means detection will start a little late, but frames will be saved smoother
# minimum 1
wait_for_n_frames = 10

# detection_speed; Acceptable values are "normal", "fast", "faster", "fastest" and "flash"
# flash is the fastest with lower accuracy while normal is the slowest with maximum accuracy
detection_speed = 'flash'

default_slideshow_delay = 600
highest_slideshow_delay = 900
lowest_slideshow_delay = 300


backtrack_frames = 5
skip_frames = 5

# lower is faster
progress_bar_speed = 0.01
