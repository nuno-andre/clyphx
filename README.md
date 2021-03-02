ClyphX
======

**ClyphX** is a _MIDI Remote Script_ for Ableton Live 9.6 - 11 that provides an
extensive list of _Actions_ related to controlling different aspects of Live.

As an example, a simple _Action_ might toggle Overdub on/off:
```
over
```

A more complex _Action List_ might mute tracks 1-2, unmute and arm track 4, turn
the 2nd device on track 4 on, and launch the selected clip on track 4:
```
1-2/mute on; 4/mute off; 4/arm on; 4/dev2 on; 4/play
```

These _Actions_ can be accessed via _X-Triggers_ (Session View Clips, Arrange
View Locators or MIDI Controls). Each _X-Trigger_ can trigger either a single
_Action_ or a list of _Actions_.

**ClyphX** also includes:

- A component called **Macrobat** that adds new functionality to racks in Live
  such as the ability to control track mixer parameters or send MIDI messages
  from Rack Macros.

- Extra preference options for changing some of Live's default behaviors such as
  the ability to choose to have track's automatically Arm upon selection.

> This is a fork of ClyphX 2.6.2, which is licensed under the [GNU LGPL][lic]
> and is [no longer being developed, updated or supported][note].

[lic]: https://spdx.org/licenses/LGPL-2.1-or-later.html "GNU LGPL 2.1 or later"
[note]: https://forum.nativekontrol.com/thread/992/current-version-clyphx-live-9
"nativeKONTROL Forum"

---
Copyright &copy; 2013-2017 Sam "Stray" Hurley <<stray411@hotmail.com>>  
Copyright &copy; 2020-2021 Nuno André Novo <<mail@nunoand.re>>