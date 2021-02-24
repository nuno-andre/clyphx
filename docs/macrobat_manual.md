# Macrobat Manual

[**1. Changes In This Version**](#1.-changes-in-this-version)

[**2. Overview**](#2.-overview)

[**3. Rack Types**](#3.-rack-types)  
[nK Track](#nk-track)  
[nK Receiver](#nk-receiver)  
[nK DR](#nk-dr)  
[nK DR Multi](#nk-dr-multi)  
[nK DR Pad Mix](#nk-dr-pad-mix)  
[nK Chain Maix](#nk-chain-mix)  
[nK CS](#nk-cs)  
[nK Learn](#nk-learn)  
[nK RnR](#nk-rnr)  
[nK Sidechain](#nk-sidechain)  
[nK MIDI](#nk-midi)  
&nbsp; &nbsp; [nK MIDI Rack Routing Options](#nk-midi-rack-routing-options)  
[nK SCL](#nk-scl)

[**4. UserConfig File**](#4.-userconfig-file)

**[5. Simpler/Sampler Parameter Names](#5.-simpler/sampler-parameter-names)**  
[Simpler Parameter Names](#simpler-parameter-names)  
[Sampler Parameter Names](#sampler-parameter-names)  

# 1. Changes In This Version

-  Fixed issue where [DR Multi](#nk-dr-multi) didn't work correctly
   with Macros containing Simpler/Sampler names.
-  [SCL](#nk-scl) now requires Live 9.5 or later.
-  Added new [CS Rack](#nk-cs) for dynamically controlling a Rack's
   Chain Selector.
-  Added new [DR Pad Mix](#nk-dr-pad-mix) for controlling the Mixer
   parameters of the selected Drum Rack Pad.

# 2. Overview

Macrobat adds additional functionality to Racks (any type of Rack that
has Macros on it) in Live while maintaining the default functionality of
the Rack.  Racks that access this additional functional are referred to
as Macrobat Racks.

To access the additional functionality, the Rack's name needs to start
with a particular word/phrase and, in most cases, the names of the
Rack's Macros need to start with particular words/phrases.  Rack/Macro
names shouldn't include special characters (like umlauts).  Also,
naming is not case-sensitive except where noted.

After you've changed the name of a Rack or Macro, you will need to
reselect the Track the Rack is on in order for your changes to take
effect.  You can reselect by selecting another Track and then
reselecting the Track the Rack is on.

Finally, except where noted, Macrobat Racks can exist on any type of
Track and can be nested inside of other Racks.

_**NOTE:**  If the Macro or On/Off switch of a Macrobat Rack is
controlled by another Macro, the Macro or On/Off switch will not be able
to access Macrobat functionality.  Also, ClyphX Actions that operate
upon all Macros at once (such as the Snap Action) cannot be applied to
any of the Macrobat Rack Types except for the [MIDI Rack](#nk-midi)._

# 3. Rack Types

Macrobat provides 12 Rack types:

-  [Track Rack](#nk-track) -- This type can control mixer parameters
   (Volume, Pan and Sends) of the Track it is on.
-  [Receiver Rack](#nk-receiver) -- This type can control the Macros
   of other Racks in your Set.
-  [DR Rack](#nk-dr) -- This type can control the parameters of an
   instance of Simpler/Sampler inside of a Drum Rack on the Track it is
   on.
-  [DR Multi Rack](#nk-dr-multi) -- This type can control the
   parameters of multiple instances of Simpler/Sampler inside of a Drum
   Rack on the Track it is on.
-  [DR Pad Mix Rack](#nk-dr-pad-mix) -- This type can control the mixer
   parameters (Volume, Pan and Sends) of the selected Drum Rack Pad.
-  [Chain Mix Rack](#nk-chain-mix) -- This type can control the mixer
   parameters (Volume, Pan and Mute) of the Chains of a Rack on the
   Track it is on.
-  [CS Rack](#nk-cs) -- This type allows you to use a Macro to
   dynamically control the Rack's Chain Selector.
-  [Learn Rack](#nk-learn) -- This type allows you to use a Macro to
   control the last selected parameter in Live.
-  [RnR Racks](#nk-rnr) -- This type can Reset or Randomize parameters
   of the Devices on the Track it is on.
-  [Sidechain Rack](#nk-sidechain) -- This type allows you to connect
   Macros to the output level of the Track it is on
-  [MIDI Rack](#nk-midi) -- This type allows you to send MIDI messages
   (Control Changes, Program Changes and SysEx).
-  [SCL Rack](#nk-scl) -- This type allows you to use Macros to
   control Push's Root Note and Scale Type for use in Note Mode.

---

## nK Track

The Track Rack can control mixer parameters (Volume, Pan and Sends) of
the Track it is on.  You can have multiple Track Racks on a Track, but
only one Macro should control a parameter.  So you shouldn't have two
Macros that both control a Track's Volume for example.

**RACK NAME:**

The Rack's name needs to start with `NK TRACK`.

**MACRO NAMES:**

Macro Names can be the names of Track mixer parameters to control. 
*VOL* (Track Volume), *PAN* (Track Pan) or *SEND x* (Track Send where x
is the Send letter).

**EXTRA FUNCTIONS:**

The parameters that you've assigned to the Macros can be reset to their
default value by toggling the Track Rack's On/Off switch (turn if off
and then on again).

_**NOTE:** This Rack type has no effect on Tracks with no Audio Output
or on the sub-tracks of a Drum or Instrument Track._

## nK Receiver

The Macros of a Receiver Rack (referred to as Receivers) can control the
Macros of other Racks (referred to as Senders) in your Set.  Each
Receiver should only have one Sender and vice versa.

In order to accomplish this, the name of the Receiver and Sender both
need to contain a unique Identifier.  The format of the Identifier is
*(\*identifier\*).*  For example:  `(*ID*)` or `(*1*)`

**RACK NAME:**

The Rack's name needs to start with `NK RECEIVER`.

**MACRO NAMES:**

Macro Names can include Identifiers.

> _**NOTE:**  The names of Senders and Receivers cannot contain any
other parentheses aside from the ones used in the Identifier._

---

## nK DR

The DR Rack can control the parameters of an instance of Simpler/Sampler
(that is not nested within another Rack) inside of a Drum Rack on the
Track it is on.  The DR Rack will operate on the first Drum Rack (that
is not nested within another Rack) found on the Track.

You can have multiple DR Racks on a Track, but only one Macro should
control a parameter.  So you shouldn't have two Macros that both
control a Simpler's Volume for example.

**RACK NAME:**

The Rack's name needs to start with `NK DR`.  After this name, you will
specify the name or number of the Simpler/Sampler instance to control.

To specify a name, you can see the names of each Simpler/Sampler
instance by looking at the Drum Rack's pads.  You should enter the name
exactly as it appears (the name **is** case-sensitive).  For example: 
*My Drum*

If more than one instance of Simpler/Sampler in the Drum Rack has the
same name, you will only be able to control the last of these.  In this
case, you should specify the Simpler/Sampler number instead.

To specify a number, look at the Chain List of the Drum Rack.  The first
chain listed is 1, second is 2, etc.

**MACRO NAMES:**

Macro names can be the name of a [Simpler/Sampler
parameter](#5.-simpler/sampler-parameter-names) to control.

**EXTRA FUNCTIONS:**

The parameters that you've assigned to the Macros can be reset to their
default value by toggling the DR Rack's On/Off switch (turn if off and
then on again).

---

## nK Dr Multi

The DR Multi Rack is basically the reverse of the [DR Rack](#nk-dr). It
can control the same parameter of multiple instances of  Simpler/Sampler
inside of a Drum Rack on the Track it is on.

**RACK NAME:**

Rack name needs to start with `NK DR MULTI`.  After this name, you
will specify the name of the [Simpler/Sampler
parameter](#5.-simpler/sampler-parameter-names) to control.

**MACRO NAMES:**

Macro names can be the name or number of the Simpler/Sampler instance to
control.  The names you specify **are** case-sensitive.

---

## nK Dr Pad Mix

The DR Pad Mix Rack can control the Mixer parameters (Volume, Pan and
first 6 Sends respectively) of the selected Drum Rack Pad.  The DR Pad
Mix Rack will operate on the first Drum Rack (that is not nested within
another Rack) found on the Track.

**RACK NAME:**

The Rack's name needs to start with `NK DR PAD MIX`.

**MACRO NAMES:**

Doesn't apply.

---

## nK Chain Mix

The Chain Mix Rack can control the mixer parameters (Volume, Pan and
Mute) of a Rack on the Track it is on.  The Chain Mix Rack will operate
on the first Rack (that is not nested within another Rack and is not a
Midi Effects Rack) found on the Track.

You can have multiple Chain Mix Racks on a Track, but only one Macro
should control a parameter.  So you shouldn't have two Macros that both
control a Chain's Volume for example.

**RACK NAME:**

The Rack's name needs to start with `NK CHAIN MIX`.  After this name,
you will specify the Chain mixer parameter to control.  `VOL` (Chain
Volume), `PAN` (Chain Pan) or `MUTE` (Chain Mute).

**MACRO NAMES:**

Macro Names can be the number of the Chain to operate on.  To find the
number of a Chain, look at the Chain List of the Rack.  The first chain
listed is 1, second is 2, etc.

**EXTRA FUNCTIONS:**

The parameters that you've assigned to the Macros can be reset to their
default value by toggling the Chain Mix Rack's On/Off switch (turn if
off and then on again).

---

## nK CS

The CS Rack allows you to use the first Macro of the Rack to dynamically
control the Rack's Chain Selector.  The range of the Macro will change
depending on the number of Chains in the Rack.  Of course, the Macro
will have no functionality unless the Rack contains at least two Chains.

**RACK NAME:**

The Rack's name needs to start with `NK CS`.

**MACRO NAMES:**

Doesn't apply.

---

## nK Learn

The Learn Rack allows you to use the first Macro of the Rack to control
the last parameter that was selected in Live.  You can only have one
Learn Rack in your Set and it can only exist on the Master Track.

You can select a parameter to control by clicking on it with your mouse.

**RACK NAME:**

The Rack's name needs to start with `NK LEARN`.

**MACRO NAMES:**

Doesn't apply.

**EXTRA FUNCTIONS:**

The parameter that is assigned to the first Macro can be reset to its
default value by toggling the Learn Rack's On/Off switch (turn if off
and then on again).

_**NOTE:**  Although all parameters in Live can be clicked on, not all
of them are classified as parameters that can be selected and so cannot
be controlled with the Learn Rack.  As an example, none of the
parameters of a Clip can be controlled.  Also, each time you select a
new parameter, the first Macro on the Learn Rack will update, which will
create an undo point (or multiple undo points)._

---

## nK RnR

RnR Racks can Reset or Randomize parameters of the Devices on the Track
they are on.  RnR Racks don't make use of Macros, they strictly use the
Rack's On/Off Switch.  To access the function of these Racks, just
change the state of the On/Off switch (if it's on, turn if off or vice
versa).

RnR Racks are position-sensitive.  The way they operate depends on where
they are located.
- If the RnR Rack is a top level Rack (not nested inside of another Rack),
  it will apply to other Devices on the Track.
- If the RnR Rack is nested inside of another Rack, it will apply to other
  Devices on the same Device Chain.

RnR Racks will not affect each other or other Macrobat Racks (except for
the [MIDI Rack](#nk-midi)), only other Devices on the Track/Device Chain.

**RACK NAME:**

There are four types of RnR Racks, the names of which need to start with
the following text string:

`NK RST` -- Reset the parameters of the Device to the right of this
Rack.

`NK RST ALL` -- Reset the parameters of all Devices on the Track/Device
Chain.

`NK RND` -- Randomize the parameters of the Device to the right of this
Rack.

`NK RND ALL` -- Randomize the parameters of all Devices on the
Track/Device Chain.

**MACRO NAMES:**

Doesn't apply.

> _**NOTE:**  Chain Selectors, on/off switches and multi-option controls
(such as a filter type chooser) will not be reset/randomized._

---

## nK Sidechain

The Macros on the Sidechain Rack can be connected to the output level of
the Track it is on.

**RACK NAME:**

The Rack's name needs to start with `NK SIDECHAIN`.

**MACRO NAMES:**

To connect a Macro to the output level of the Track, the Macro's name
needs to start with `[SC]`.

**EXTRA FUNCTIONS:**

You can turn the sidechaining on/off with the Rack's On/Off switch.

> _**IMPORTANT NOTE:**  Each movement of a Macro is considered an
> undoable action in Live.  For that reason, when using a Sidechain Rack,
> you will not be able to reliably undo while the sidechaining is in
> effect._

---

## nK MIDI

The MIDI Rack allows you to send MIDI messages (Control Change, Program
Change and SysEx) from the Macros.

**RACK NAME:**

The Rack's name needs to start with `NK MIDI`.

**MACRO NAMES:**

Macro names can start with the following list of words/phrases:

`[CC`_**x**_`]` Control Change message where _**x**_ is the Control Change
number to send.  This number should be in the range of 0 -- 127.

`[PC]` -- Program Change message.

The MIDI Rack can also send SysEx messages.  In order to access this
functionality, you'll first need to create a SysEx List composed of the
SysEx messages you'd like to send.  You'll do this in your [UserConfig
file](#userconfig-file).

To access the SysEx messages from Macros, you'll use the Identifiers
you specified in your SysEx List for the Macro Names

**EXTRA FUNCTIONS:**

By default, the MIDI Rack will send out on MIDI Channel 1.  You can
override this by adding `[CH`_**x**_`]` to the end of the Rack's name where x
is the MIDI Channel number.  This number should be in the range of 1 - 16.
For example: `NK MIDI [CH6]`

### nK MIDI Rack Routing Options

The MIDI data sent by the MIDI Rack can be used in a variety of ways
via several routing options:

- **OPTION A -- Data to external MIDI device.**  
_[ This is the only option useable with SysEx data. ]_

  In order to accomplish this, select the external MIDI device as the
  Output of the ClyphX Control Surface.

> _[ The next two options require a [loopback device such as MIDI Yoke or
IAC](https://help.ableton.com/hc/en-us/articles/209774225-How-to-setup-a-virtual-MIDI-bus) ]_

- **OPTION B -- Data to loopback, re-routed back into Live as Track data.**  
_[ This is the recommended option, but is not compatible with SysEx. 
See [Note](#midi-routing-sysex). ]_

  This option allows the MIDI data to be sent into MIDI Tracks in Live.
From there, the data can be rerouted via the MIDI Track's output routing
and/or recorded.

  In order to accomplish this, select the loopback device as the Output of
the ClyphX Control Surface.  Turn the Track switch on for the loopback
device's input.

  For any MIDI Tracks you wish to use this with, leave the Track's input
set to 'All Ins' or choose the loopback device as the input.  Leave
the Track's input channel set to 'All Channels'.  Arm the Track or
set it's Monitor to 'In'.

>  <a name="midi-routing-sysex">_**NOTE**:  If you'd like to use SysEx and
still maintain the flexibility that Option B provides, you can use an
application such as [Bome's MIDI Translator
Pro](https://www.bome.com/products/miditranslator) to receive the SysEx
from the loopback device and send it to your external MIDI device(s)._</a>

- **OPTION C -- Data to loopback, re-routed back into Live as Remote data.**
 
  This option allows the MIDI data to be sent back into Live as Remote
data (for MIDI mapping parameters).  In order to accomplish this,
select the loopback device as the Output of the ClyphX Control Surface. 
Turn the Remote switch on for the loopback device's input.

  Live's Remote facilities do not support PCs or SysEx, so you should not
set up a Macro to send a PC or SysEx when using Option C.  You should
use CCs only.

  Also, in order to do the actual MIDI mapping, you will need a controller
as you cannot turn the Macros with your mouse while in MIDI mapping
mode.  You can turn them with a controller though.

---

## nK SCL

The first two Macros on the SCL Rack will control Push's Root Note and
Scale Type respectively for use in Note Mode.

**RACK NAME:**

The Rack's name needs to start with `NK SCL`.

**MACRO NAMES:**

Doesn't apply.

**EXTRA FUNCTIONS:**

The Rack's name will show the name of the selected Root Note and Scale
Type.

_**NOTE:** The Macros and Rack name will **not** update if the Root
Note or Scale Type is changed from Push itself or from ClyphX's Push
Actions._

# 4. UserConfig File

If you'd like to send SysEx data with the [MIDI Rack](#nk-midi),
you'll need to create a SysEx List in the file named `user_config.py`,
which you'll find in the `./ClyphX/macrobat` folder.

You can modify this file with any text editor (like Notepad or
TextEdit).  The file itself includes instructions on how to modify it.

_**NOTE:**  You may see two files named user_config in the
ClyphX/macrobat folder.  One of them is a `*.pyc` file (you cannot
modify this) and the other is a `*.py` file.  You should modify the
`*.py` file.*_

# 5. Simpler/Sampler Parameter Names

The following charts show the names of Simpler and Sampler parameters for
use with the [DR Multi Rack](#nk-dr-multi).

## Simpler Parameter Names

|               |             |              |   |
| ------------- | ----------- | ------------ | ----------
| Ve Attack     | Fe Attack   | L Attack     | Pe Attack
| Ve Decay      | Fe Decay    | L Rate       | Pe Decay
| Ve Sustain    | Fe Sustain  | L R \< Key   | Pe Sustain
| Ve Release    | Fe Release  | L Wave       | Pe Release
| S Start       | Filter Freq | Vol \< LFO   | Glide Time
| S Loop Length | Filter Res  | Filt \< LFO  | Spread
| S Length      | Filt \< Vel | Pitch \< LFO | Pan
| S Loop Fade   | Fe \< Env   | Pan \< LFO   | Volume


## Sampler Parameter Names

|                |                |             |   |
| -------------- | -------------- | ----------- | ---------------
| Volume         | Filter Type    | Fe Attack   | L 1 Wave
| Ve Attack      | Filter Morph   | Fe Decay    | L 1 Sync
| Ve Decay       | Filter Freq    | Fe Sustain  | L 1 Sync Rate
| Ve Sustain     | Filter Res     | Fe Release  | L 1 Rate
| Ve Release     | Filt \< Vel    | Fe End      | Vol \< LFO
| Vol \< Vel     | Filt \< Key    | Fe Mode     | Filt \< LFO
| Ve R \< Vel    | Fe \< Env      | Fe Loop     | Pan \< LFO
| Time           | Shaper Amt     | Fe Retrig   | Pitch \< LFO
|                |                |             |  
| L 2 Wave       | L 3 Wave       | O Mode      | Transpose
| L 2 Sync       | L 3 Sync       | O Volume    | Spread
| L 2 Sync Rate  | L 3 Sync Rate  | O Coarse    | Pe \< Env
| L 2 Rate       | L 3 Rate       | O Fine      | Pe Attack
| L 2 R \< Key   | L 3 R \< Key   | Oe Attack   | Pe Peak
| L 2 St Mode    | L 3 St Mode    | Oe Decay    | Pe Decay
| L 2 Spin       | L 3 Spin       | Oe Sustain  | Pe Sustain
| L 2 Phase      | L 3 Phase      | Oe Release  | Pe Release

 

Copyright 2013-2017 [nativeKONTROL](https://nativekontrol.com/).  All rights reserved.

_This document, as well as the software described in it, is provided
under license and may be used or copied only in accordance with the
terms of this license.  The content of this document is furnished for
informational use only, is subject to change without notice, and should
not be construed as a commitment by its authors.  Every effort has been
made to ensure that the information in this document is accurate.  The
authors assume no responsibility or liability for any errors or
inaccuracies that may appear in this document._

_All product and company names mentioned in this document, as well as the
software it describes, are trademarks or registered trademarks of their
respective owners.  This software is solely endorsed and supported by
nativeKONTROL._
