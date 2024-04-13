# FL-Studio-APC-mini-mk2
MIDI Controller Script for AKAI APC mini mk2 for FL Studio "Live Performance Mode"

## Features

* Schedule / trigger clips (by pressing the 8x8 grid pads)
* Stop playing clips in track (right buttons labeled "Scene launch")
* Transport controls: Play / Pause (bottom left button labeled "Volume")
* Scroll Playlist Live Area (bottom buttons labeled with arrows)
* Clip colors and status are displayed on the MIDI controller grid
* Beat indicator (lights of bottom left buttons labeled "Fader CTRL")

_(insert demo GIF here)_

## How to use

Create a subfolder `AKAI APC mini mk2` inside your FL Studio Hardware folder<br>
(`C:\Users\<username>\Documents\Image-Line\FL Studio\Settings\Hardware\AKAI APC mini mkii`)<br>
and copy the `device_apcminimkii.py` file from this repository into this newly created folder.<br>

You can now select the controller type `AKAI APC mini MKii (Performance Mode)` for your MIDI controller.

![grafik](https://github.com/dreiekk/FL-Studio-APC-mini-mk2/assets/25348281/b9e793d7-0f78-474d-acc2-f4cec53d1610)

## Docs

Akai APC mini Mk2 - Communication Protocol PDF:<br>
https://cdn.inmusicbrands.com/akai/attachments/APC%20mini%20mk2%20-%20Communication%20Protocol%20-%20v1.0.pdf

(unofficial) FL Studio Python API Reference:<br>
https://miguelguthridge.github.io/FL-Studio-API-Stubs/

(official) FL Studio MIDI Scripting Docs:<br>
https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm

List of Controller Script Events (OnInit, OnNoteOn, ... Functions):<br>
https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm#script_events
