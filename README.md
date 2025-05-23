# foundcog_paradigm

## Presentation script for the FOUNDCOG study

There are lots of details in here that are idiosyncratic for our experiment. Please don't hesitate to contact me if you have any questions regarding the FOUNDCOG experiment!

-   We ran this on Windows with now outdated versions of Psychopy and Python. The environment we used is in environment.yaml.
-   Because of our in-bore projection system, all stimuli are distorted so that they appear normal when in the scanner.
-   This also means we only use a small section of the screen. The display size will very likely not apply to your system.

### launch_experiment.py acts as the main hub

-   All videos and audio are pre-loaded.
-   System specific paths are set.
-   This plays a calming video to maintain attention during scan setup. 3 options can by cycled through with right key press.
-   From here, different tasks can be launched.
-   From any task, we can always return here using 'esc'. This most recent calming video will be resumed.
-   To mute audio of the calming video, press 'm'.

### 'a' - sleep state

-   A blank screen will appear.
-   No audio will be played.
-   'spacebar' will start and stop pink noise, useful for transitioning between EPI and quiet T2.

### 'l' - ANC learning

-   This will play a silent video of cars.

### 'v' - Videos task

-   Will launch Psychopy MRI experiment.
-   The program will wait for the first TTL from the scanner.
-   Until then, a blank black screen will appear which is very unsettling for the infant. So it is key to minimise time spent here.
-   An attention getter will start automatically when first TR of the sequence is received.
-   If using MRC Camera software (SphinxGE Viewer), the recording will automatically start and stop.
-   Press 'esc' to end experiment early. Otherwise it will end automatically and return to home screen.
-   Events files are saved in relevant directory.
-   A record of TR timings are also saved, as well as the timing of the Sphinx/MRC camera start/stop.

### 'p' - Pictures task

-   All the same protocols for the videos task, but with the pictures experiment.

### Visualisation of the paradigm for ease of use

![alt text](https://github.com/ClionaOD/foundcog_paradigm/blob/main/scan_setup/misc/paradigm_viz.jpg?raw=true)

### Visualisation of our protocol and priorities

![alt text](https://github.com/ClionaOD/foundcog_paradigm/blob/main/scan_setup/misc/protocol.jpg?raw=true)

## To download stimuli

Stimuli files are not uploaded to this repo because of the large file size. You can find them in the AWS bucket ???

pictures/stimuli - populate with files in [picture_stimuli TODO]()

videos/stimuli - populate with files in [videos_stimuli TODO]()

scan_setup/attention_getters - populate with files in [attention_getters TODO]()

-   Original source: Christina Bergmann Jonathan F. Kominsky Joan Birules Michaela DeBolt Emma K. Ward available at [https://osf.io/wakqf](https://osf.io/wakqf).

scan_setup/calming_vids_distorted - populate with files in [home_screen_vids TODO]()

-   Inscapes video from [Vanderwal, Tamara, et al. "Inscapes: A movie paradigm to improve compliance in functional magnetic resonance imaging." Neuroimage 122 (2015): 222-232.](https://www.sciencedirect.com/science/article/pii/S1053811915006898).

scan_setup/misc - populate with files in [misc_media TODO]()
