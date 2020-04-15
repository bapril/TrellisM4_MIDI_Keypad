#TrellisM4_MIDI_Keypad

## Introduction

This project is a Circuit Python replacement for the Arduono based: https://github.com/bapril/MIDI_Macro_Launcher

The NeoTrellisM4 keypad from Adafruit(https://www.adafruit.com/product/4020) is appears via USB as a MIDI kepyad offering 31 pages of color-coded buttons. The 32nd button is the page switch key. Each page emits on a dedicated midi channel. Pages 1-16 emit on channels 1-16 notes 1-31, Pages 17-31 emit on channels 1-16 notes 33-63. The data.csv file allows the user to specify the color of each button in each page. I use Keyboard Mastero (https://www.keyboardmaestro.com/main/) to trigger macros based on MIDI input, this reduces the need to remember funky key comnbinations, and allows macros to be triggered even while keys are being pressed. 


