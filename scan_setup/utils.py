import glob
import os

import pandas as pd

from psychopy import event
from psychopy.constants import FINISHED


def learn_anc(win, vidstim):
    vidstim.play()
    while vidstim.status != FINISHED:
        vidstim.draw()
        win.flip()

        keys = event.getKeys()
        if "escape" in keys:
            # reset for next repetition
            vidstim.reset()
            vidstim._nextFrameT = 0.0
            win.flip()
            # return to main menu/waiting screen
            return
    vidstim.pause()
    # reset for repetitions
    vidstim.reset()
    vidstim._nextFrameT = 0.0
    win.flip()


def check_orders(ord_pth, logs_dir):
    orders = pd.read_csv(ord_pth, index_col=0)

    orders_per_sub = {
        sub: ords.split("-")
        for sub, ords in list(zip(orders.participant, orders.orders))
    }

    subs_per_order = {"A": [], "B": [], "C": [], "D": [], "E": [], "F": []}
    for sub, (order1, order2) in orders_per_sub.items():
        if not sub in subs_per_order[order1]:
            subs_per_order[order1].append(sub)
        if not sub in subs_per_order[order2]:
            subs_per_order[order2].append(sub)

    numruns_per_order = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for order, sublist in subs_per_order.items():
        runs = [
            glob.glob(
                os.path.join(
                    logs_dir,
                    f"sub-{sub}",
                    "ses-?",
                    "func",
                    f"sub-{sub}_ses-?_task-videos_dir-AP_run-00*",
                )
            )
            for sub in sublist
        ]
        runs = [item for sublist in runs for item in sublist]
        numruns_per_order[order] = len(runs)

    return numruns_per_order


if __name__ == "__main__":
    check_orders(
        "/Users/clionaodoherty/Desktop/foundcog_experiment/logs_foundcog/orders.csv",
        "/Users/clionaodoherty/Desktop/foundcog_experiment/logs_foundcog",
    )
