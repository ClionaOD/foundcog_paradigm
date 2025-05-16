from psychopy import event
from psychopy.constants import FINISHED, PLAYING


def sleeping(win, pink_noise):
    sleeping = True
    while sleeping:
        win.flip()
        keys = event.getKeys()
        if pink_noise.status == FINISHED:
            pink_noise.seek(0)
            pink_noise.play()
        if "space" in keys:
            if pink_noise.status == PLAYING:
                pink_noise.pause()
                print("... pink noise stopped")
            else:
                pink_noise.play()
                print("pink noise playing ...")
        if "escape" in keys:
            if pink_noise.status == PLAYING:
                pink_noise.pause()
                pink_noise.seek(0)
                print("... pink noise stopped")
            return
