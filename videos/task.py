import random
from datetime import datetime

import pandas as pd

# camera recording
import win32gui
from psychopy import core, event, visual
from psychopy.constants import FINISHED, NOT_STARTED, PAUSED, PLAYING
from psychopy.hardware.emulator import launchScan
from pywinauto.application import Application


def run_vids(
    win, all_vids, participant_orders, attention, attend_folder, MR_settings, save_loc
):
    # path to save frame times
    tr_file = save_loc.replace("_events.tsv", "_trs.csv")
    # path to save camera timestamp
    camera_file = save_loc.replace("_events.tsv", "_camera.csv")

    n_reps = 2

    # launch scanning
    reps = 0
    globalClock = core.Clock()
    key_code = MR_settings["sync"]
    pause_during_delay = MR_settings["TR"] > 0.4
    sync_now = False
    infer_missed_sync = False
    max_slippage = 0.02

    dummy_onsets = []

    centrepos = [0, -450]
    distort_centrepos = [0, -480]

    use_attention_getters = True

    stretchy = 1 / 1.46
    fixsize = 10

    orders = {
        "A": [
            "minions_supermarket.mp4",
            "new_orleans.mp4",
            "bathsong.mp4",
            "dog.mp4",
            "moana.mp4",
            "forest.mp4",
        ],
        "B": [
            "bathsong.mp4",
            "dog.mp4",
            "moana.mp4",
            "forest.mp4",
            "minions_supermarket.mp4",
            "new_orleans.mp4",
        ],
        "C": [
            "new_orleans.mp4",
            "minions_supermarket.mp4",
            "dog.mp4",
            "bathsong.mp4",
            "forest.mp4",
            "moana.mp4",
        ],
        "D": [
            "moana.mp4",
            "forest.mp4",
            "minions_supermarket.mp4",
            "new_orleans.mp4",
            "bathsong.mp4",
            "dog.mp4",
        ],
        "E": [
            "forest.mp4",
            "moana.mp4",
            "new_orleans.mp4",
            "minions_supermarket.mp4",
            "dog.mp4",
            "bathsong.mp4",
        ],
        "F": [
            "dog.mp4",
            "bathsong.mp4",
            "forest.mp4",
            "moana.mp4",
            "new_orleans.mp4",
            "minions_supermarket.mp4",
        ],
    }

    print(
        f"Using orders {participant_orders[0]} and {participant_orders[1]} for this participant"
    )

    vol = launchScan(
        win,
        MR_settings,
        globalClock=globalClock,
        mode="Scan",
        wait_msg="waiting for scanner ...",
    )

    # Setup events
    # include real time column for sanity checking, will be excluded in BIDS
    expt_events = pd.DataFrame(columns=["onset", "duration", "trial_type", "real_time"])

    # Record every trigger by noting time 's' is received
    TRs = []

    def capture(fnc):
        def inner(symbol, modifiers, emulated=False):
            if symbol == 115:  # ASCII code for s
                TRs.append(globalClock.getTime())
            return fnc(symbol, modifiers, emulated=emulated)

        return inner

    event._onPygletKey = capture(event._onPygletKey)

    allKeys = []
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

    if sync_now:  # waits for sync at end each rep
        while reps < n_reps:
            # Get which order (A-F) to play
            # Either x1 or x2 for this participant
            this_order = participant_orders[reps]
            # Get list from our storage dict
            videos = orders[this_order]

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
                ev["real_time"] = datetime.now().strftime("%H:%M:%S:%f")
                onset = globalClock.getTime()
                ev["onset"] = onset
                ev["real_time"] = datetime.now().strftime("%H:%M:%S:%f")

                # play attention getter
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

            # Loop over all stimuli in the chosen order
            for i in range(len(videos)):
                # select filename based on index
                curr_video = videos[i]

                # get the MovieStim object from preloaded dict
                mov = all_vids[curr_video]

                onset = globalClock.getTime()
                realtime = datetime.now().strftime("%H:%M:%S:%f")

                mov.play()
                while mov.status != FINISHED:
                    mov.draw()
                    win.flip()

                    keys = event.getKeys()

                    # functionality to pause the video while scan is still running
                    # this will record how long the stimulus was paused for
                    # note that a paused screen and no audio will be displayed if pressed, which may cause fussing
                    if "p" in keys:
                        ev = {
                            "onset": None,
                            "duration": None,
                            "trial_type": None,
                            "real_time": None,
                        }
                        if mov.status == PLAYING:
                            mov.pause()
                            ev["real_time"] = datetime.now().strftime("%H:%M:%S:%f")
                            pause_onset = globalClock.getTime()

                            ev["onset"] = pause_onset
                            ev["trial_type"] = "pause"

                        elif mov.status == PAUSED:
                            mov.play()
                            pause_end = globalClock.getTime()

                            ev["duration"] = pause_end - pause_onset

                            # update events_df with this trial
                            expt_events = expt_events.append(ev, ignore_index=True)
                            # save out events as tsv each time updated
                            expt_events.to_csv(save_loc, sep="\t", index=False)

                    elif "escape" in keys:
                        ev = {
                            "onset": None,
                            "duration": None,
                            "trial_type": None,
                            "real_time": None,
                        }

                        end = globalClock.getTime()
                        mov.pause()

                        ev["real_time"] = realtime
                        ev["onset"] = onset
                        ev["duration"] = end - onset
                        ev["trial_type"] = curr_video

                        # update events_df with this trial
                        expt_events = expt_events.append(ev, ignore_index=True)
                        # save out events as tsv each time updated
                        expt_events.to_csv(save_loc, sep="\t", index=False)

                        # reset for next repetition
                        mov.reset()
                        mov._nextFrameT = 0.0
                        win.flip()

                        # save out the frame times
                        trdf = pd.DataFrame(TRs, columns=["onset"])
                        trdf.to_csv(tr_file, index=False)

                        try:
                            # stop recording
                            app = Application().connect(
                                title="Sphinx GEV Viewer - V2.1.4-M-B9754"
                            )
                            dialog = app.Dialog
                            # dialog.print_control_identifiers() #
                            dialog.Button6.click()
                            hwnd = win32gui.FindWindow(None, "PsychoPy")
                            win32gui.SetForegroundWindow(
                                hwnd
                            )  # go back to the experiment window to be able to recieve triggers from scanner
                        except:
                            print("automatic recording failed, did the camera crash?")

                        # return to main menu/waiting screen
                        return

                ev = {
                    "onset": None,
                    "duration": None,
                    "trial_type": None,
                    "real_time": None,
                }

                mov.pause()
                end = globalClock.getTime()

                # reset for repetitions
                mov.reset()
                mov._nextFrameT = 0.0
                win.flip()

                ev["real_time"] = realtime
                ev["onset"] = onset
                ev["duration"] = end - onset
                ev["trial_type"] = curr_video

                # update events_df with this trial
                expt_events = expt_events.append(ev, ignore_index=True)
                # save out events as tsv each time updated
                expt_events.to_csv(save_loc, sep="\t", index=False)

            reps += 1
            sync_now = False

    core.wait(3 * 0.656)

    # save out the frame times
    trdf = pd.DataFrame(TRs, columns=["onset"])
    trdf.to_csv(tr_file, index=False)

    try:
        # stop recording
        app = Application().connect(title="Sphinx GEV Viewer - V2.1.4-M-B9754")
        dialog = app.Dialog
        dialog.Button6.click()
        hwnd = win32gui.FindWindow(None, "PsychoPy")
        win32gui.SetForegroundWindow(
            hwnd
        )  # go back to the experiment window to be able to recieve triggers from scanner
    except:
        print("automatic recording failed, did the camera crash?")

    win.flip()
