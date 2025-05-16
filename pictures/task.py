import os
import random
import sys
from datetime import datetime

import numpy as np
import pandas as pd

# camera recording
import win32gui
from psychopy import core, event, visual
from psychopy.constants import FINISHED
from psychopy.hardware.emulator import launchScan
from pywinauto.application import Application


def run_imgs(win, audio, img_folder, attention, MR_settings, save_loc):
    # path to save frame times
    tr_file = save_loc.replace("_events.tsv", "_trs.csv")
    # path to save camera timestamp
    camera_file = save_loc.replace("_events.tsv", "_camera.csv")

    # play audio for duration of experiment
    audio.play()

    # path tosave out trigger recordings
    trigger_file = save_loc.replace("_events.tsv", "_triggers.csv")

    # launch scanning
    reps = 0
    n_skips = 0
    globalClock = core.Clock()

    key_code = MR_settings["sync"]
    sync_now = False
    infer_missed_sync = False

    centrepos = [-90, -475]
    distort_centrepos = [-90, -475]

    stretchy = 1 / 1.46
    fixsize = 10
    reducefixdur = 1.0  # Fixation 3.5-4.5 s minus display_time minus this number
    display_time = 2 + reducefixdur  # Seconds for stimulus

    present_stimuli = True  # for testing whole paradigm without waiting for stimuli

    use_attention_getters = True

    # vol = launchScan(win, MR_settings, globalClock=globalClock, mode='Test', wait_msg='waiting for scanner ...') #test mode until scanning
    vol = launchScan(
        win,
        MR_settings,
        globalClock=globalClock,
        mode="Scan",
        wait_msg="waiting for scanner ...",
    )  # test mode until scanning

    fixation = visual.ShapeStim(
        win,
        units="pix",
        vertices=(
            (0, -fixsize * stretchy),
            (0, fixsize * stretchy),
            (0, 0),
            (-fixsize, 0),
            (fixsize, 0),
        ),
        lineWidth=5,
        closeShape=False,
        lineColor="white",
        pos=centrepos,
    )

    # Experiment parameters
    n_types = 2
    n_tokens = 3
    n_reps = 2

    # Setup visuals

    os.chdir(f"{img_folder}")

    types = [
        "crab",
        "seabird",
        "dishware",
        "food",
        "tree_",
        "squirrel",
        "towel",
        "rubberduck",
        "shoppingcart",
        "shelves",
        "cat",
        "fence",
    ]

    expt_events = pd.DataFrame(
        columns=["onset", "duration", "trial_type", "stim_file", "real_time"]
    )

    # Using 4.5 and 5.5 because we will deduct the display time of 3 sec
    # jit = list(np.linspace(4.5,5.5,(n_tokens*len(types))))
    jit = np.array(
        [
            3.5,
            3.51,
            3.53,
            3.54,
            3.56,
            3.57,
            3.58,
            3.6,
            3.61,
            3.63,
            3.64,
            3.65,
            3.67,
            3.68,
            3.7,
            3.71,
            3.73,
            3.74,
            3.75,
            3.77,
            3.78,
            3.8,
            3.81,
            3.82,
            3.84,
            3.85,
            3.87,
            3.88,
            3.89,
            3.91,
            3.92,
            3.94,
            3.95,
            3.96,
            3.98,
            3.99,
            4.01,
            4.02,
            4.04,
            4.05,
            4.06,
            4.08,
            4.09,
            4.11,
            4.12,
            4.13,
            4.15,
            4.16,
            4.18,
            4.19,
            4.2,
            4.22,
            4.23,
            4.25,
            4.26,
            4.27,
            4.29,
            4.3,
            4.32,
            4.33,
            4.35,
            4.36,
            4.37,
            4.39,
            4.4,
            4.42,
            4.43,
            4.44,
            4.46,
            4.47,
            4.49,
            4.5,
        ]
    )

    TRs = []

    def capture(fnc):
        def inner(symbol, modifiers, emulated=False):
            if symbol == 115:  # ASCII code for s
                TRs.append(globalClock.getTime())
            return fnc(symbol, modifiers, emulated=emulated)

        return inner

    event._onPygletKey = capture(event._onPygletKey)

    # Skipping dummies
    dummy_onsets = []
    skip = 0
    while skip < n_skips:  # n_skips set to zero so no dummies being recorded!!
        allKeys = []
        while len(allKeys) == 0:
            allKeys = event.getKeys()
        if MR_settings["sync"] in allKeys:
            sync_now = key_code  # flag

            ev = {
                "onset": None,
                "duration": None,
                "trial_type": None,
                "stim_file": None,
                "real_time": None,
            }

            ev["real_time"] = datetime.now().strftime("%H:%M:%S:%f")
            onset = globalClock.getTime()
            ev["onset"] = onset
            ev["trial_type"] = "dummy"
            ev["stim_file"] = "none"
        if sync_now:
            fixation.draw()
            win.flip()
            skip += 1
        ev["duration"] = globalClock.getTime() - onset
        expt_events = expt_events.append(ev, ignore_index=True)
        sync_now = False

    # save out dummy scans to events
    expt_events.to_csv(save_loc, sep="\t", index=False)

    allKeys = []
    reps = 0

    while len(allKeys) == 0:
        allKeys = event.getKeys()
    if MR_settings["sync"] in allKeys:
        sync_now = key_code  # flag

        before = datetime.now().strftime("%H:%M:%S:%f")
        try:
            # start recording
            app = Application().connect(title="Sphinx GEV Viewer - V2.1.4-M-B9754")
            dialog = app.Dialog
            dialog.Button6.click()
            now = datetime.now().strftime("%H:%M:%S:%f")
            hwnd = win32gui.FindWindow(None, "PsychoPy")
            win32gui.SetForegroundWindow(
                hwnd
            )  # go back to the experiment window to be able to recieve triggers from scanner
            after = datetime.now().strftime("%H:%M:%S:%f")
            pd.DataFrame(
                {"t_before": [before], "onset": [now], "t_after": [after]}
            ).to_csv(camera_file, index=False)
        except:
            print("automatic recording failed, did the camera crash?")

    if sync_now:
        if use_attention_getters:
            # get attention file
            attend = random.choice(attention)

            # reset event dict for this stimulus
            ev = {
                "onset": None,
                "duration": None,
                "trial_type": None,
                "real_time": None,
            }

            # get onsets etc.
            ev["trial_type"] = "attention_getter"
            onset = globalClock.getTime()
            ev["onset"] = onset

            # play attention getter
            ev["real_time"] = datetime.now().strftime("%H:%M:%S:%f")
            while attend.status != FINISHED:
                attend.draw()
                win.flip()

            # get duration
            end = globalClock.getTime()
            ev["duration"] = end - onset

            # reset stimulus to prevent issues with repetitions
            attend.reset()
            attend._nextFrameT = 0.0

            # SAVE
            # update events_df with this trial
            expt_events = expt_events.append(ev, ignore_index=True)
            # save out events as tsv each time updated
            expt_events.to_csv(save_loc, sep="\t", index=False)

        while reps < n_reps:
            stimuli = os.listdir(f"{img_folder}")

            rate = pd.DataFrame(columns=["timesofar", "zoom", "x", "y"])

            presented_images = []
            for i in range(n_tokens):
                random.shuffle(types)
                random.shuffle(jit)

                for idx, condition in enumerate(types):

                    ev = {
                        "onset": None,
                        "duration": None,
                        "trial_type": None,
                        "stim_file": None,
                        "real_time": None,
                    }

                    wait = jit[idx] - display_time

                    img = random.choice([i for i in stimuli if i[:-5] == condition])
                    ev["stim_file"] = img
                    ev["trial_type"] = condition

                    presented_images.append(img)
                    stimuli.remove(img)
                    # Zoom phase

                    onset = globalClock.getTime()
                    ev["real_time"] = datetime.now().strftime("%H:%M:%S:%f")
                    ev["onset"] = onset

                    if present_stimuli:
                        while True:
                            timesofar = globalClock.getTime() - onset
                            if timesofar > display_time:
                                break
                            zoom = 1 - ((1 - timesofar / display_time) ** 3) / 2

                            rate = rate.append(
                                {"timesofar": timesofar, "zoom": zoom, "x": 0, "y": 0},
                                ignore_index=True,
                            )

                            visStim = visual.ImageStim(
                                win,
                                units="pix",
                                image=img,
                                size=[640 * zoom, 360 * zoom],
                                pos=distort_centrepos,
                                interpolate=True,
                            )
                            visStim.draw()
                            win.flip()
                            pass

                        ev["duration"] = globalClock.getTime() - onset
                        expt_events = expt_events.append(ev, ignore_index=True)

                        ev = {
                            "onset": None,
                            "duration": None,
                            "trial_type": None,
                            "stim_file": None,
                            "real_time": None,
                        }
                        fixation.draw()
                        fix_onset = globalClock.getTime()
                        ev["onset"] = fix_onset
                        ev["trial_type"] = "fixation"
                        ev["stim_file"] = "none"
                        ev["real_time"] = datetime.now().strftime("%H:%M:%S:%f")
                        win.flip()
                        core.wait(wait)
                        ev["duration"] = globalClock.getTime() - fix_onset
                        expt_events = expt_events.append(ev, ignore_index=True)

                        expt_events.to_csv(save_loc, sep="\t", index=False)

                        # Check for escape
                        keys = event.getKeys()
                        if "escape" in keys:
                            audio.pause()
                            win.flip()

                            # save out the frame times
                            trdf = pd.DataFrame(TRs, columns=["onset"])
                            trdf.to_csv(tr_file, index=False)

                            # save out the rate
                            rate.to_csv("test_rate_zoom.csv", index=False)

                            try:
                                # stop recording
                                app = Application().connect(
                                    title="Sphinx GEV Viewer - V2.1.4-M-B9754"
                                )
                                dialog = app.Dialog
                                dialog.Button6.click()
                                hwnd = win32gui.FindWindow(None, "PsychoPy")
                                win32gui.SetForegroundWindow(
                                    hwnd
                                )  # go back to the experiment window to be able to recieve triggers from scanner
                            except:
                                print(
                                    "automatic recording failed, did the camera crash?"
                                )
                            return

            reps += 1
            sync_now = False

    core.wait(5 * 0.656)
    audio.pause()

    # save out the frame times
    trdf = pd.DataFrame(TRs, columns=["onset"])
    trdf.to_csv(tr_file, index=False)

    try:
        # stop recording
        app = Application().connect(title="Sphinx GEV Viewer - V2.1.4-M-B9754")
        dialog = app.Dialog
        # dialog.print_control_identifiers() #
        dialog.Button6.click()
        hwnd = win32gui.FindWindow(None, "PsychoPy")
        win32gui.SetForegroundWindow(
            hwnd
        )  # go back to the experiment window to be able to recieve triggers from scanner
    except:
        print("automatic recording failed, did the camera crash?")

    win.flip()
