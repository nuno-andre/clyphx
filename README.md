ClyphX
======

**ClyphX** is a _MIDI Remote Script_ for Ableton Live 9.6+, 10, and 11 that
provides an extensive list of _Actions_ related to controlling different aspects
of Live.

These _Actions_ can be accessed via _X-Triggers_ (Session View Clips, Arrange
View Locators or MIDI Controls). Each _X-Trigger_ can trigger either a single
_Action_ or a list of _Actions_.

As an example, a simple _Action_ might toggle Overdub on/off:
```
OVER
```

A more complex _Action List_ might mute Tracks 1-2, unmute and arm Track 4, turn
the 2nd Device on Track 4 on, and launch the selected Clip on track 4:
```
1-2/MUTE ON; 4/MUTE OFF; 4/ARM ON; 4/DEV2 ON; 4/PLAY
```

**ClyphX** also includes:

- A component called **Macrobat** that adds new functionality to Racks in Live
  such as the ability to control Track mixer parameters or send MIDI messages
  from Rack Macros.

- Extra preference options for changing some of Live's default behaviors such as
  the ability to choose to have Track's automatically Arm upon selection.

> This is a fork of ClyphX 2.6.2, which is licensed under the [GNU LGPL][lic]
> and is [no longer being developed, updated or supported][note].

[lic]: https://spdx.org/licenses/LGPL-2.1-or-later.html "GNU LGPL 2.1 or later"
[note]: https://forum.nativekontrol.com/thread/992/current-version-clyphx-live-9
"nativeKONTROL Forum"

---
Copyright &copy; 2013-2017 Sam "Stray" Hurley <<stray411@hotmail.com>>  
Copyright &copy; 2020-2021 Nuno André Novo <<mail@nunoand.re>>