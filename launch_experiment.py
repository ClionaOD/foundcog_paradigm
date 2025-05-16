import os
import random
import warnings

# audio
from ctypes import POINTER, cast
from datetime import datetime

import pandas as pd
from comtypes import CLSCTX_ALL

# psychopy
from psychopy import core, event, gui, sound, visual
from psychopy.constants import FINISHED
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# experiment modules
from pictures import task as pictures_task
from videos import task as videos_task
from sleep import blank as sleep_state
from scan_setup.utils import check_orders, learn_anc

#################################################
### set up scan - participant ID, orders etc. ###
#################################################

# name of subfolder from which to draw stimuli

root_dir = os.path.abspath(".")

# stim_loc = "shortlist_distorted_v2_audio"
# stim_folder = os.path.join(root_dir, stim_loc)

attend_folder = os.path.join(root_dir, "scan_setup", "attention_getters")
use_attention_getters = True
if not os.path.exists(attend_folder) or len(os.listdir(attend_folder)) == 0:
    raise (NotADirectoryError("Attention getters folder not found or empty"))


wait_folder = os.path.join(root_dir, "scan_setup", "calming_vids_distorted")
if not os.path.exists(wait_folder) or len(os.listdir(wait_folder)) == 0:
    raise (NotADirectoryError("Waiting videos folder not found or empty"))

image_folder = os.path.join(root_dir, "pictures", "stimuli")
if not os.path.exists(image_folder) or len(os.listdir(image_folder)) == 0:
    raise (NotADirectoryError("Image folder not found or empty"))


all_vids = [
    "minions_supermarket.mp4",
    "new_orleans.mp4",
    "bathsong.mp4",
    "dog.mp4",
    "moana.mp4",
    "forest.mp4",
]
video_folder = os.path.join(root_dir, "videos", "stimuli")
if not os.path.exists(video_folder) or len(os.listdir(video_folder)) == 0:
    raise (NotADirectoryError("Video folder not found or empty"))

# set paramaters for display
centrepos = [-85, -450]
distort_centrepos = [-85, -450]

stretchy = 1 / 1.46
fixsize = 10

# Get participant and session info
warnDlg = gui.Dlg(title="Caution")
warnDlg.addText("Please Check Participant ID and Run Number Carefully")
warnDlg.addText("If testing code use PID ITT0")
warnDlg.show()
if not warnDlg.OK:
    core.quit()

# Display session information
Session_Info = {"Participant #": "TESTPID", "Session #": 1}

infoDlg = gui.DlgFromDict(
    Session_Info, title="Session Info", order=["Participant #", "Session #"]
)
if not infoDlg.OK:
    core.quit()

# Reenter participant ID
check_pid = {"Participant #": ""}
checkDlg = gui.DlgFromDict(check_pid, title="Please Confirm the PID")
if not checkDlg.OK:
    core.quit()

if (
    Session_Info["Participant #"] != check_pid["Participant #"]
    or "_" in Session_Info["Participant #"]
):
    warnDlg = gui.Dlg(title="MISMATCH PIDS")
    warnDlg.addText("Wrong PID entered")
    warnDlg.addText("Please relaunch program")
    warnDlg.show()
    if not warnDlg.OK:
        core.quit()
    else:
        core.quit()

# reset in case of manual editing in dialogue box
_subj = Session_Info["Participant #"]
sesNum = Session_Info["Session #"]

vid_runs = 0
pic_runs = 0

# events file save location according to BIDS specification
save_dir = os.path.join(root_dir, "experimental_outputs")

ses_save_dir = os.path.join(save_dir, "events", f"sub-{_subj}", f"ses-{sesNum}", "func")
if not os.path.exists(ses_save_dir):
    os.makedirs(ses_save_dir)

# Configure MRI Settings
MR_settings = {
    "TR": 0.656,  # duration (sec) per whole-brain volume
    "volumes": 455,  # number of whole-brain 3D volumes per scanning run (731 seconds per run, 12.18 mins), might be more if pause or attend needed
    "sync": "s",  # character to use as the sync timing event; assumed to come at start of a volume
    "skip": 5,  # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
    "sound": True,  # in test mode: play a tone as a reminder of scanner noise
}

#######################
### STIMULI IMPORTS ###
#######################

# all Psychopy stimuli need to be loaded onto a window

# try with one win first
win = visual.Window(fullscr=True, screen=0, color=(-1, -1, -1))

### MOVIES ###

# waiting videos
wait_vids = [i for i in os.listdir(wait_folder)]
wait_vids = {
    vid: visual.MovieStim3(
        win,
        filename=os.path.join(wait_folder, vid),
        pos=distort_centrepos,
        size=[640, 360],
        loop=True,
    )
    for vid in wait_vids
}
# stimuli
all_vids = {
    vid: visual.MovieStim3(
        win,
        filename=os.path.join(video_folder, vid),
        pos=distort_centrepos,
        size=[640, 360],
    )
    for vid in all_vids
}
print("movies loaded")

# attention getters
attention = os.listdir(attend_folder)
attention = [
    visual.MovieStim3(
        win, filename=os.path.join(attend_folder, x), pos=centrepos, size=[640, 360]
    )
    for x in attention
    if ".mov" in x
]
print("attention getters loaded")

# video for learning phase of ANC
anc_vid = os.path.join(root_dir, "scan_setup", "misc", "real_cars.mp4")
anc_vid = visual.MovieStim3(
    win,
    filename=os.path.join(root_dir, anc_vid),
    pos=distort_centrepos,
    size=[640, 360],
    loop=True,
)
print("anc video loaded")

### AUDIO ###

# set audio levels - only windows compatible
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# 0 is unmuted
volume.SetMute(0, None)
volume.SetMasterVolumeLevel(-12.0, None)
print("volume.GetMasterVolumeLevel(): %s" % volume.GetMasterVolumeLevel())

# import audio
pic_song = os.path.join(root_dir, "scan_setup", "misc", "pictures_song_2.wav")
imgAudio = sound.Sound(pic_song)
print("song loaded")

pink_noise = os.path.join(root_dir, "scan_setup", "misc", "pink_noise.wav")
pinkNoise = sound.Sound(pink_noise, loops=-1)
print("pink noise loaded")

# play video/audio for waiting and distracting

print(
    """
    --------------------------------
    FOUNDCOG PARADIGM INSTRUCTIONS:
    --------------------------------
    This is the main screen where a video will play to occupy the baby during prep.
    Launch this to pre-load all videos and modules BEFORE the infant enters the scanner.

    FROM HOME - i.e. while waiting video is playing:

    press 'm' to mute the waiting video for L/R calibration of ANC
    
    press 'v' to launch the video experiment and wait for scanner to send first trigger pulse
        if the experiment needs to be relaunched, press 'esc' to return to main waiting screen
        each launch counts as a new run in the events files

    press 'p' to launch the images experiment and wait for scanner
        this will play audio during run
        press 'esc' to return to waiting video
        each launch counts as a new run in the events files
    
    press 'a' to launch a blank screen and no audio
        anatomical/sleeping mode
        while in this state, press 'space' to start/stop pink noise
        'esc' to return to main waiting video
    
    press 'q' to quit the entire experiment.
        all events and logs should have saved within the experiment modules and this should be safe

    """
)

start_vid = "fireworks.mp4"
wait_vid = wait_vids[start_vid]
while wait_vid.status != FINISHED:
    wait_vid.draw()
    win.flip()

    keys = event.getKeys()

    # change to next waiting movie
    if "right" in keys:
        wait_vid.pause()
        wait_vid.reset()
        wait_vid._nextFrameT = 0.0

        if start_vid == "inscapes.mp4":
            start_vid = "sky_celebrate.mp4"
        elif start_vid == "sky_celebrate.mp4":
            start_vid = "fireworks.mp4"
        elif start_vid == "fireworks.mp4":
            start_vid = "inscapes.mp4"

        print(f"waiting video playing is {start_vid}")
        wait_vid = wait_vids[start_vid]
        wait_vid.play()

    # mute audio
    if "m" in keys:
        if volume.GetMute() == 0:
            volume.SetMute(1, None)
            print("audio muted")
        elif volume.GetMute() == 1:
            volume.SetMute(0, None)
            print("audio playing")

    # switch to learning video
    if "l" in keys:
        wait_vid.pause()
        learn_anc(win, anc_vid)
        wait_vid.play()

    # launch images module
    if "p" in keys:
        if volume.GetMute() == 1:
            volume.SetMute(0, None)
            print("audio force play for paradigm")

        pic_runs += 1
        launch = datetime.now().strftime("%H-%M-%S")
        save_loc = os.path.join(
            ses_save_dir,
            f"sub-{_subj}_ses-{sesNum}_task-pictures_dir-AP_run-00{pic_runs}-{launch}_events.tsv",
        )

        wait_vid.pause()
        print("launching pictures run")
        pictures_task.run_imgs(
            win, imgAudio, image_folder, attention, MR_settings, save_loc
        )
        wait_vid.play()
        print("back to home")

    # launch video modules
    if "v" in keys:
        if volume.GetMute() == 1:
            volume.SetMute(0, None)
            print("audio force play for paradigm")

        vid_runs += 1
        launch = datetime.now().strftime("%H-%M-%S")
        save_loc = os.path.join(
            ses_save_dir,
            f"sub-{_subj}_ses-{sesNum}_task-videos_dir-AP_run-00{vid_runs}-{launch}_events.tsv",
        )

        # get the previous orders and choose accordingly
        orders = ["A", "B", "C", "D", "E", "F"]

        if os.path.exists(os.path.join(save_dir, "orders.csv")):
            saved_orders = pd.read_csv(
                os.path.join(save_dir, "orders.csv"), index_col=0
            )
        else:
            saved_orders = pd.DataFrame(columns=["participant", "orders"])
            saved_orders.to_csv(os.path.join(save_dir, "orders.csv"))

        # get least frequent
        ord_counts = check_orders(
            ord_pth=os.path.join(save_dir, "orders.csv"),
            logs_dir=os.path.join(save_dir, "events"),
        )
        least_freq = min(ord_counts, key=ord_counts.get)

        _ord_subj = _subj[:-1] if "A" in _subj else _subj
        if not _ord_subj in list(saved_orders.participant):
            # randomly choose one for first ses/run of this participant
            participant_orders = random.sample(orders, 1)
            # use the least frequent as the other
            participant_orders.append(least_freq)
            # make sure they're not the same
            check_match = True
            while check_match:
                if participant_orders[0] == participant_orders[1]:
                    participant_orders[0] = random.sample(orders, 1)[0]
                else:
                    check_match = False
            # save to log
            saved_orders = saved_orders.append(
                {
                    "participant": _ord_subj,
                    "orders": f"{participant_orders[0]}-{participant_orders[1]}",
                },
                ignore_index=True,
            )
            saved_orders.to_csv(os.path.join(save_dir, "orders.csv"))
        else:
            # if not ses/run the first one, load from our log
            participant_orders = list(
                saved_orders.loc[saved_orders.participant == _ord_subj, "orders"]
            )[0]
            participant_orders = [i for i in list(participant_orders) if not i == "-"]

        wait_vid.pause()
        print("launching videos run")
        videos_task.run_vids(
            win,
            all_vids,
            participant_orders,
            attention,
            attend_folder,
            MR_settings,
            save_loc,
        )
        wait_vid.play()
        print("back to home")

    # launch anatomy module - sleeping baby
    if "a" in keys:
        wait_vid.pause()
        print("sleep mode enabled")
        sleep_state.sleeping(win, pinkNoise)
        wait_vid.play()
        print("back to home")

    if "q" in keys:
        core.quit()
