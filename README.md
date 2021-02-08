ClyphX
======

**ClyphX** is a _MIDI Remote Script_ for Ableton Live 9.6+ or 10.x that provides
an extensive list of Actions related to controlling different aspects of Live.
These Actions can be accessed via X-Triggers (Session View Clips, Arrange View
Locators or MIDI Controls). Each X-Trigger can trigger either a single Action
or a list of Actions.

As an example, a simple Action might be `OVER`, which will toggle _Overdub_
on/off. A more complex Action List might mute _Tracks 1 - 2_, unmute and arm
_Track 4_, turn the 2nd Device on _Track 4_ on and launch the selected Clip on
_Track 4_: `1/MUTE ON; 2/MUTE ON; 4/MUTE OFF; 4/ARM ON; 4/DEV2 ON; 4/PLAY`

**ClyphX** also includes a component called **Macrobat** that adds new
functionality to Racks in Live such as the ability to control Track mixer
parameters or send MIDI messages from Rack Macros.

**ClyphX** also includes extra preference options for changing some of Live's
default behaviors such as the ability to choose to have Track's automatically
Arm upon selection.

> This is a fork of ClyphX 2.6.2, which is licensed under the [GNU LGPL][lic]
> and is [no longer being developed, updated or supported][note].

[lic]: https://spdx.org/licenses/LGPL-2.1-or-later.html "GNU LGPL 2.1 or later"
[note]: https://forum.nativekontrol.com/thread/992/current-version-clyphx-live-9
"nativeKONTROL Forum"

---
Copyright &copy; 2013-2017 Sam "Stray" Hurley <<stray411@hotmail.com>>  
Copyright &copy; 2020-2021 Nuno André Novo <<mail@nunoand.re>>