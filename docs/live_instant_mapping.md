Live Instant Mapping Info for Ableton Live v10.1.30
===================================================

The following document covers the parameter banks accessible via Ableton Live's
_Instant Mapping_ feature for each built in device. This info also applies to
controlling device parameters via **ClyphX**'s _Device Actions_.

> **NOTE:** The order of parameter banks is sometimes changed by Ableton. If you
find the information in this document to be incorrect, you can recreate it with
**ClyphX** by triggering an action named `MAKE_DEV_DOC`. That will create a new
version of this file in your user/home directory.

* * *

Device Index
------------
[Amp](#amp)  
[Analog](#analog)  
[Arpeggiator](#arpeggiator)  
[AutoFilter](#autofilter)  
[AutoPan](#autopan)  
[Beat Repeat](#beat-repeat)  
[Cabinet](#cabinet)  
[Chord](#chord)  
[Chorus](#chorus)  
[Collision](#collision)  
[Compressor](#compressor)  
[Corpus](#corpus)  
[DrumBuss](#drumbuss)  
[Dynamic Tube](#dynamic-tube)  
[EQ Eight](#eq-eight)  
[EQ Three](#eq-three)  
[Echo](#echo)  
[Electric](#electric)  
[Erosion](#erosion)  
[Filter Delay](#filter-delay)  
[Flanger](#flanger)  
[Frequency Shifter](#frequency-shifter)  
[Gate](#gate)  
[Glue Compressor](#glue-compressor)  
[Grain Delay](#grain-delay)  
[Impulse](#impulse)  
[InstrumentVector](#instrumentvector)  
[Looper](#looper)  
[Multiband Dynamics](#multiband-dynamics)  
[Note Length](#note-length)  
[Operator](#operator)  
[Overdrive](#overdrive)  
[Pedal](#pedal)  
[Phaser](#phaser)  
[Pitch](#pitch)  
[Random](#random)  
[Redux](#redux)  
[Resonator](#resonator)  
[Reverb](#reverb)  
[Sampler](#sampler)  
[Saturator](#saturator)  
[Scale](#scale)  
[Simpler](#simpler)  
[Tension](#tension)  
[Utility](#utility)  
[Velocity](#velocity)  
[Vinyl Distortion](#vinyl-distortion)  
[Vocoder](#vocoder)  

* * *

## Amp

| `B0`: Best of Banks | `B1`: Global   | `B2`: Dual Mono |
| :------------------ | :------------- | :-------------- |
| `P1`: Amp Type      | `P1`: Amp Type | `P1`: Dual Mono |
| `P2`: Bass          | `P2`: Bass     | `P2`:           |
| `P3`: Middle        | `P3`: Middle   | `P3`:           |
| `P4`: Treble        | `P4`: Treble   | `P4`:           |
| `P5`: Presence      | `P5`: Presence | `P5`:           |
| `P6`: Gain          | `P6`: Gain     | `P6`:           |
| `P7`: Volume        | `P7`: Volume   | `P7`:           |
| `P8`: Dry/Wet       | `P8`: Dry/Wet  | `P8`:           |

[Back to Device Index](#device-index)

* * *

## Analog

| `B0`: Best of Banks | `B1`: Oscillators | `B2`: Filters      | `B3`: Filter Envelopes | `B4`: Filter Modulation | `B5`: Volume Envelopes | `B6`: Mix        | `B7`: Output        |
| :------------------ | :---------------- | :----------------- | :--------------------- | :---------------------- | :--------------------- | :--------------- | :------------------ |
| `P1`: F1 Freq       | `P1`: OSC1 Level  | `P1`: OSC1 Balance | `P1`: FEG1 Attack      | `P1`: F1 On/Off         | `P1`: AEG1 Attack      | `P1`: AMP1 Level | `P1`: Volume        |
| `P2`: F1 Resonance  | `P2`: OSC1 Octave | `P2`: F1 Freq      | `P2`: FEG1 Decay       | `P2`: F1 Freq < LFO     | `P2`: AEG1 Decay       | `P2`: AMP1 Pan   | `P2`: Noise On/Off  |
| `P3`: OSC1 Shape    | `P3`: OSC1 Semi   | `P3`: F1 Resonance | `P3`: FEG1 Sustain     | `P3`: F1 Freq < Env     | `P3`: AEG1 Sustain     | `P3`: LFO1 Shape | `P3`: Noise Level   |
| `P4`: OSC1 Octave   | `P4`: OSC1 Shape  | `P4`: F1 Type      | `P4`: FEG1 Rel         | `P4`: F1 Res < LFO      | `P4`: AEG1 Rel         | `P4`: LFO1 Speed | `P4`: Noise Color   |
| `P5`: OSC2 Shape    | `P5`: OSC2 Level  | `P5`: OSC2 Balance | `P5`: FEG2 Attack      | `P5`: F2 On/Off         | `P5`: AEG2 Attack      | `P5`: AMP2 Level | `P5`: Unison On/Off |
| `P6`: OSC2 Octave   | `P6`: OSC2 Octave | `P6`: F2 Freq      | `P6`: FEG2 Decay       | `P6`: F2 Freq < LFO     | `P6`: AEG2 Decay       | `P6`: AMP2 Pan   | `P6`: Unison Detune |
| `P7`: OSC2 Detune   | `P7`: OSC2 Semi   | `P7`: F2 Resonance | `P7`: FEG2 Sustain     | `P7`: F2 Freq < Env     | `P7`: AEG2 Sustain     | `P7`: LFO2 Shape | `P7`: Vib On/Off    |
| `P8`: Volume        | `P8`: OSC2 Shape  | `P8`: F2 Type      | `P8`: FEG2 Rel         | `P8`: F2 Res < LFO      | `P8`: AEG2 Rel         | `P8`: LFO2 Speed | `P8`: Vib Amount    |

[Back to Device Index](#device-index)

* * *

## Arpeggiator

| `B0`: Best of Banks   | `B1`: Style          | `B2`: Pitch/Velocity  |
| :-------------------- | :------------------- | :-------------------- |
| `P1`: Synced Rate     | `P1`: Style          | `P1`: Tranpose Mode   |
| `P2`: Free Rate       | `P2`: Groove         | `P2`: Tranpose Key    |
| `P3`: Transp. Steps   | `P3`: Offset         | `P3`: Transp. Steps   |
| `P4`: Transp. Dist.   | `P4`: Synced Rate    | `P4`: Transp. Dist.   |
| `P5`: Gate            | `P5`: Retrigger Mode | `P5`: Velocity Decay  |
| `P6`: Tranpose Key    | `P6`: Ret. Interval  | `P6`: Velocity Target |
| `P7`: Velocity Decay  | `P7`: Repeats        | `P7`: Velocity On     |
| `P8`: Velocity Target | `P8`: Gate           | `P8`: Vel. Retrigger  |

[Back to Device Index](#device-index)

* * *

## AutoFilter

| `B0`: Best of Banks   | `B1`: Filter          | `B2`: Filter Extra      | `B3`: Side Chain |
| :-------------------- | :-------------------- | :---------------------- | :--------------- |
| `P1`: Frequency       | `P1`: Frequency       | `P1`: Filter Type       | `P1`:            |
| `P2`: Resonance       | `P2`: Resonance       | `P2`: LFO Quantize On   | `P2`:            |
| `P3`: Filter Type     | `P3`: Env. Attack     | `P3`: LFO Quantize Rate | `P3`:            |
| `P4`: Env. Modulation | `P4`: Env. Release    | `P4`: LFO Stereo Mode   | `P4`:            |
| `P5`: LFO Amount      | `P5`: Env. Modulation | `P5`: LFO Spin          | `P5`:            |
| `P6`: LFO Waveform    | `P6`: LFO Amount      | `P6`: LFO Sync          | `P6`: S/C On     |
| `P7`: LFO Frequency   | `P7`: LFO Frequency   | `P7`: LFO Sync Rate     | `P7`: S/C Mix    |
| `P8`: LFO Phase       | `P8`: LFO Phase       | `P8`: LFO Offset        | `P8`: S/C Gain   |

[Back to Device Index](#device-index)

* * *

## AutoPan

| `B0`: Best of Banks  | `B1`:                |
| :------------------- | :------------------- |
| `P1`: Frequency      | `P1`: Frequency      |
| `P2`: Phase          | `P2`: Phase          |
| `P3`: Shape          | `P3`: Shape          |
| `P4`: Waveform       | `P4`: Waveform       |
| `P5`: Sync Rate      | `P5`: Sync Rate      |
| `P6`: Offset         | `P6`: Offset         |
| `P7`: Width (Random) | `P7`: Width (Random) |
| `P8`: Amount         | `P8`: Amount         |

[Back to Device Index](#device-index)

* * *

## Beat Repeat

| `B0`: Best of Banks | `B1`: Repeat Rate  | `B2`: Gate/Pitch   |
| :------------------ | :----------------- | :----------------- |
| `P1`: Grid          | `P1`: Interval     | `P1`: Chance       |
| `P2`: Interval      | `P2`: Offset       | `P2`: Gate         |
| `P3`: Offset        | `P3`: Grid         | `P3`: Pitch        |
| `P4`: Gate          | `P4`: Variation    | `P4`: Pitch Decay  |
| `P5`: Pitch         | `P5`: Filter Freq  | `P5`: Filter Freq  |
| `P6`: Pitch Decay   | `P6`: Filter Width | `P6`: Filter Width |
| `P7`: Variation     | `P7`: Volume       | `P7`: Volume       |
| `P8`: Chance        | `P8`: Decay        | `P8`: Decay        |

[Back to Device Index](#device-index)

* * *

## Cabinet

| `B0`: Best of Banks       | `B1`:                     |
| :------------------------ | :------------------------ |
| `P1`: Cabinet Type        | `P1`: Cabinet Type        |
| `P2`: Microphone Position | `P2`: Microphone Position |
| `P3`: Microphone Type     | `P3`: Microphone Type     |
| `P4`: Dual Mono           | `P4`: Dual Mono           |
| `P5`:                     | `P5`:                     |
| `P6`:                     | `P6`:                     |
| `P7`:                     | `P7`:                     |
| `P8`: Dry/Wet             | `P8`: Dry/Wet             |

[Back to Device Index](#device-index)

* * *

## Chord

| `B0`: Best of Banks | `B1`: Shift  | `B2`: Shift %   |
| :------------------ | :----------- | :-------------- |
| `P1`: Shift1        | `P1`: Shift1 | `P1`: Velocity1 |
| `P2`: Shift2        | `P2`: Shift2 | `P2`: Velocity2 |
| `P3`: Shift3        | `P3`: Shift3 | `P3`: Velocity3 |
| `P4`: Shift4        | `P4`: Shift4 | `P4`: Velocity4 |
| `P5`: Shift5        | `P5`: Shift5 | `P5`: Velocity5 |
| `P6`: Velocity5     | `P6`: Shift6 | `P6`: Velocity6 |
| `P7`: Shift6        | `P7`:        | `P7`:           |
| `P8`: Velocity6     | `P8`:        | `P8`:           |

[Back to Device Index](#device-index)

* * *

## Chorus

| `B0`: Best of Banks  | `B1`:                |
| :------------------- | :------------------- |
| `P1`: LFO Amount     | `P1`: LFO Amount     |
| `P2`: LFO Rate       | `P2`: LFO Rate       |
| `P3`: Delay 1 Time   | `P3`: Delay 1 Time   |
| `P4`: Delay 1 HiPass | `P4`: Delay 1 HiPass |
| `P5`: Delay 2 Time   | `P5`: Delay 2 Time   |
| `P6`: Delay 2 Mode   | `P6`: Delay 2 Mode   |
| `P7`: Feedback       | `P7`: Feedback       |
| `P8`: Dry/Wet        | `P8`: Dry/Wet        |

[Back to Device Index](#device-index)

* * *

## Collision

| `B0`: Best of Banks       | `B1`: Mallet              | `B2`: Noise             | `B3`: Resonator 1, Set A    | `B4`: Resonator 1, Set B | `B5`: Resonator 2, Set A    | `B6`: Resonator 2, Set B |
| :------------------------ | :------------------------ | :---------------------- | :-------------------------- | :----------------------- | :-------------------------- | :----------------------- |
| `P1`: Res 1 Brightness    | `P1`: Mallet On/Off       | `P1`: Noise Volume      | `P1`: Res 1 Decay           | `P1`: Res 1 Listening L  | `P1`: Res 2 Decay           | `P1`: Res 2 Listening L  |
| `P2`: Res 1 Type          | `P2`: Mallet Volume       | `P2`: Noise Filter Type | `P2`: Res 1 Material        | `P2`: Res 1 Listening R  | `P2`: Res 2 Material        | `P2`: Res 2 Listening R  |
| `P3`: Mallet Stiffness    | `P3`: Mallet Noise Amount | `P3`: Noise Filter Freq | `P3`: Res 1 Type            | `P3`: Res 1 Hit          | `P3`: Res 2 Type            | `P3`: Res 2 Hit          |
| `P4`: Mallet Noise Amount | `P4`: Mallet Stiffness    | `P4`: Noise Filter Q    | `P4`: Res 1 Quality         | `P4`: Res 1 Brightness   | `P4`: Res 2 Quality         | `P4`: Res 2 Brightness   |
| `P5`: Res 1 Inharmonics   | `P5`: Mallet Noise Color  | `P5`: Noise Attack      | `P5`: Res 1 Tune            | `P5`: Res 1 Inharmonics  | `P5`: Res 2 Tune            | `P5`: Res 2 Inharmonics  |
| `P6`: Res 1 Decay         | `P6`:                     | `P6`: Noise Decay       | `P6`: Res 1 Fine Tune       | `P6`: Res 1 Radius       | `P6`: Res 2 Fine Tune       | `P6`: Res 2 Radius       |
| `P7`: Res 1 Tune          | `P7`:                     | `P7`: Noise Sustain     | `P7`: Res 1 Pitch Env.      | `P7`: Res 1 Opening      | `P7`: Res 2 Pitch Env.      | `P7`: Res 2 Opening      |
| `P8`: Volume              | `P8`:                     | `P8`: Noise Release     | `P8`: Res 1 Pitch Env. Time | `P8`: Res 1 Ratio        | `P8`: Res 2 Pitch Env. Time | `P8`: Res 2 Ratio        |

[Back to Device Index](#device-index)

* * *

## Compressor

| `B0`: Best of Banks | `B1`: Compression         | `B2`: Output          | `B3`: Side Chain  |
| :------------------ | :------------------------ | :-------------------- | :---------------- |
| `P1`: Threshold     | `P1`: Threshold           | `P1`: Threshold       | `P1`: S/C EQ On   |
| `P2`: Ratio         | `P2`: Ratio               | `P2`: Expansion Ratio | `P2`: S/C EQ Type |
| `P3`: Attack        | `P3`: Attack              | `P3`: LookAhead       | `P3`: S/C EQ Freq |
| `P4`: Release       | `P4`: Release             | `P4`: S/C Listen      | `P4`: S/C EQ Q    |
| `P5`: Model         | `P5`: Auto Release On/Off | `P5`: S/C Gain        | `P5`: S/C EQ Gain |
| `P6`: Knee          | `P6`: Env Mode            | `P6`: Makeup          | `P6`: S/C On      |
| `P7`: Dry/Wet       | `P7`: Knee                | `P7`: Dry/Wet         | `P7`: S/C Mix     |
| `P8`: Output Gain   | `P8`: Model               | `P8`: Output Gain     | `P8`: S/C Gain    |

[Back to Device Index](#device-index)

* * *

## Corpus

| `B0`: Best of Banks  | `B1`: Amount         | `B2`: Body        | `B3`: Tune              |
| :------------------- | :------------------- | :---------------- | :---------------------- |
| `P1`: Brightness     | `P1`: Decay          | `P1`: Listening L | `P1`: Resonance Type    |
| `P2`: Resonance Type | `P2`: Material       | `P2`: Listening R | `P2`: Tune              |
| `P3`: Material       | `P3`: Mid Freq       | `P3`: Hit         | `P3`: Transpose         |
| `P4`: Inharmonics    | `P4`: Width          | `P4`: Brightness  | `P4`: Fine              |
| `P5`: Decay          | `P5`: Bleed          | `P5`: Inharmonics | `P5`: Spread            |
| `P6`: Ratio          | `P6`: Resonance Type | `P6`: Radius      | `P6`: Resonator Quality |
| `P7`: Tune           | `P7`: Gain           | `P7`: Opening     | `P7`: Note Off          |
| `P8`: Dry Wet        | `P8`: Dry Wet        | `P8`: Ratio       | `P8`: Off Decay         |

[Back to Device Index](#device-index)

* * *

## DrumBuss

| `B0`: Best of Banks | `B1`: Drive         | `B2`: Gain          |
| :------------------ | :------------------ | :------------------ |
| `P1`: Drive         | `P1`: Drive         | `P1`: Trim          |
| `P2`: Drive Type    | `P2`: Drive Type    | `P2`: Output Gain   |
| `P3`: Crunch        | `P3`: Transients    | `P3`: Dry/Wet       |
| `P4`: Boom Amt      | `P4`: Crunch        | `P4`: Compressor On |
| `P5`: Trim          | `P5`: Boom Freq     | `P5`: Damping Freq  |
| `P6`: Damping Freq  | `P6`: Boom Amt      | `P6`:               |
| `P7`: Output Gain   | `P7`: Boom Decay    | `P7`:               |
| `P8`: Dry/Wet       | `P8`: Boom Audition | `P8`:               |

[Back to Device Index](#device-index)

* * *

## Dynamic Tube

| `B0`: Best of Banks | `B1`:          |
| :------------------ | :------------- |
| `P1`: Drive         | `P1`: Drive    |
| `P2`: Bias          | `P2`: Bias     |
| `P3`: Envelope      | `P3`: Envelope |
| `P4`: Tone          | `P4`: Tone     |
| `P5`: Attack        | `P5`: Attack   |
| `P6`: Release       | `P6`: Release  |
| `P7`: Output        | `P7`: Output   |
| `P8`: Dry/Wet       | `P8`: Dry/Wet  |

[Back to Device Index](#device-index)

* * *

## EQ Eight

| `B0`: Best of Banks | `B1`: Band On/Off   | `B2`: Frequency     | `B3`: Gain     | `B4`: Resonance     | `B5`: Filter Type     | `B6`: Output      | `B7`: EQs 3-5       |
| :------------------ | :------------------ | :------------------ | :------------- | :------------------ | :-------------------- | :---------------- | :------------------ |
| `P1`: 1 Frequency A | `P1`: 1 Filter On A | `P1`: 1 Frequency A | `P1`: 1 Gain A | `P1`: 1 Resonance A | `P1`: 1 Filter Type A | `P1`: Adaptive Q  | `P1`: 3 Gain A      |
| `P2`: 1 Gain A      | `P2`: 2 Filter On A | `P2`: 2 Frequency A | `P2`: 2 Gain A | `P2`: 2 Resonance A | `P2`: 2 Filter Type A | `P2`:             | `P2`: 3 Frequency A |
| `P3`: 2 Frequency A | `P3`: 3 Filter On A | `P3`: 3 Frequency A | `P3`: 3 Gain A | `P3`: 3 Resonance A | `P3`: 3 Filter Type A | `P3`:             | `P3`: 3 Resonance A |
| `P4`: 2 Gain A      | `P4`: 4 Filter On A | `P4`: 4 Frequency A | `P4`: 4 Gain A | `P4`: 4 Resonance A | `P4`: 4 Filter Type A | `P4`:             | `P4`: 4 Gain A      |
| `P5`: 3 Frequency A | `P5`: 5 Filter On A | `P5`: 5 Frequency A | `P5`: 5 Gain A | `P5`: 5 Resonance A | `P5`: 5 Filter Type A | `P5`:             | `P5`: 4 Frequency A |
| `P6`: 3 Gain A      | `P6`: 6 Filter On A | `P6`: 6 Frequency A | `P6`: 6 Gain A | `P6`: 6 Resonance A | `P6`: 6 Filter Type A | `P6`:             | `P6`: 4 Resonance A |
| `P7`: 4 Frequency A | `P7`: 7 Filter On A | `P7`: 7 Frequency A | `P7`: 7 Gain A | `P7`: 7 Resonance A | `P7`: 7 Filter Type A | `P7`: Scale       | `P7`: 5 Gain A      |
| `P8`: 4 Gain A      | `P8`: 8 Filter On A | `P8`: 8 Frequency A | `P8`: 8 Gain A | `P8`: 8 Resonance A | `P8`: 8 Filter Type A | `P8`: Output Gain | `P8`: 5 Frequency A |

[Back to Device Index](#device-index)

* * *

## EQ Three

| `B0`: Best of Banks | `B1`:         |
| :------------------ | :------------ |
| `P1`: GainLo        | `P1`: GainLo  |
| `P2`: GainMid       | `P2`: GainMid |
| `P3`: GainHi        | `P3`: GainHi  |
| `P4`: FreqLo        | `P4`: FreqLo  |
| `P5`: LowOn         | `P5`: LowOn   |
| `P6`: MidOn         | `P6`: MidOn   |
| `P7`: HighOn        | `P7`: HighOn  |
| `P8`: FreqHi        | `P8`: FreqHi  |

[Back to Device Index](#device-index)

* * *

## Echo

| `B0`: Best of Banks | `B1`: Sync        | `B2`: Time         | `B3`: Gate/Ducking | `B4`: Noise/Wobble | `B5`: Gain         | `B6`: Filter    | `B7`: Reverb       | `B8`: Modulation |
| :------------------ | :---------------- | :----------------- | :----------------- | :----------------- | :----------------- | :-------------- | :----------------- | :--------------- |
| `P1`: L Division    | `P1`: L Division  | `P1`: L Time       | `P1`: Gate On      | `P1`: Noise On     | `P1`: Feedback     | `P1`: Filter On | `P1`: Reverb Level | `P1`: Mod Wave   |
| `P2`: R Division    | `P2`: R Division  | `P2`: R Time       | `P2`: Gate Thr     | `P2`: Noise Amt    | `P2`: Feedback Inv | `P2`: HP Freq   | `P2`: Reverb Decay | `P2`: Mod Sync   |
| `P3`: L Time        | `P3`: L Sync Mode | `P3`: L Offset     | `P3`: Gate Release | `P3`: Noise Mrph   | `P3`: Input Gain   | `P3`: HP Res    | `P3`: Reverb Loc   | `P3`: Mod Rate   |
| `P4`: R Time        | `P4`: R Sync Mode | `P4`: R Offset     | `P4`: Duck On      | `P4`: Wobble On    | `P4`: Output Gain  | `P4`: LP Freq   | `P4`: Stereo Width | `P4`: Mod Freq   |
| `P5`: Input Gain    | `P5`: L 16th      | `P5`: Link         | `P5`: Duck Thr     | `P5`: Wobble Amt   | `P5`: Clip Dry     | `P5`: LP Res    | `P5`: Mod Phase  |
| `P6`: Feedback      | `P6`: R 16th      | `P6`: Channel Mode | `P6`: Duck Release | `P6`: Wobble Mrph  | `P6`: Dry Wet      | `P6`: Dly < Mod  |
| `P7`: Stereo Width  | `P7`: L Sync      | `P7`: Env Mix      | `P7`: Repitch      | `P7`: Flt < Mod  |
| `P8`: Dry Wet       | `P8`: R Sync      | `P8`: Mod 4x     |

[Back to Device Index](#device-index)

* * *

## Electric

| `B0`: Best of Banks | `B1`: Mallet and Tine | `B2`: Tone and Damper | `B3`: Pickup       | `B4`: Modulation    | `B5`: Global     |
| :------------------ | :-------------------- | :-------------------- | :----------------- | :------------------ | :--------------- |
| `P1`: M Stiffness   | `P1`: M Stiffness     | `P1`: F Tone Decay    | `P1`: P Symmetry   | `P1`: M Stiff < Vel | `P1`: Volume     |
| `P2`: M Force       | `P2`: M Force         | `P2`: F Tone Vol      | `P2`: P Distance   | `P2`: M Stiff < Key | `P2`: Voices     |
| `P3`: Noise Amount  | `P3`: Noise Pitch     | `P3`: F Release       | `P3`: P Amp In     | `P3`: M Force < Vel | `P3`: Semitone   |
| `P4`: F Tine Vol    | `P4`: Noise Decay     | `P4`: Damp Tone       | `P4`: P Amp Out    | `P4`: M Force < Key | `P4`: Detune     |
| `P5`: F Tone Vol    | `P5`: Noise Amount    | `P5`: Damp Balance    | `P5`: Pickup Model | `P5`: Noise < Key   | `P5`: KB Stretch |
| `P6`: F Release     | `P6`: F Tine Color    | `P6`: Damp Amount     | `P6`:              | `P6`: F Tine < Key  | `P6`: PB Range   |
| `P7`: P Symmetry    | `P7`: F Tine Decay    | `P7`:                 | `P7`:              | `P7`: P Amp < Key   | `P7`:            |
| `P8`: Volume        | `P8`: F Tine Vol      | `P8`:                 | `P8`:              | `P8`:               | `P8`:            |

[Back to Device Index](#device-index)

* * *

## Erosion

| `B0`: Best of Banks | `B1`:           |
| :------------------ | :-------------- |
| `P1`: Frequency     | `P1`: Frequency |
| `P2`: Width         | `P2`: Width     |
| `P3`: Mode          | `P3`: Mode      |
| `P4`: Amount        | `P4`: Amount    |
| `P5`:               | `P5`:           |
| `P6`:               | `P6`:           |
| `P7`:               | `P7`:           |
| `P8`:               | `P8`:           |

[Back to Device Index](#device-index)

* * *

## Filter Delay

| `B0`: Best of Banks  | `B1`: Input L Filter | `B2`: Input L+R Filter | `B3`: Input R Filter |
| :------------------- | :------------------- | :--------------------- | :------------------- |
| `P1`: 2 Filter Freq  | `P1`: 1 Filter Freq  | `P1`: 2 Filter Freq    | `P1`: 3 Filter Freq  |
| `P2`: 2 Filter Width | `P2`: 1 Filter Width | `P2`: 2 Filter Width   | `P2`: 3 Filter Width |
| `P3`: 2 Beat Delay   | `P3`: 1 Beat Delay   | `P3`: 2 Beat Delay     | `P3`: 3 Beat Delay   |
| `P4`: 2 Feedback     | `P4`: 1 Beat Swing   | `P4`: 2 Beat Swing     | `P4`: 3 Beat Swing   |
| `P5`: 1 Volume       | `P5`: 1 Feedback     | `P5`: 2 Feedback       | `P5`: 3 Feedback     |
| `P6`: 3 Volume       | `P6`: 1 Pan          | `P6`: 2 Pan            | `P6`: 3 Pan          |
| `P7`: 2 Volume       | `P7`: 1 Volume       | `P7`: 2 Volume         | `P7`: 3 Volume       |
| `P8`: Dry            | `P8`: Dry            | `P8`: Dry              | `P8`: Dry            |

[Back to Device Index](#device-index)

* * *

## Flanger

| `B0`: Best of Banks   | `B1`: Frequency Controls | `B2`: LFO / S&H          |
| :-------------------- | :----------------------- | :----------------------- |
| `P1`: Hi Pass         | `P1`: Hi Pass            | `P1`: LFO Amount         |
| `P2`: Delay Time      | `P2`: Dry/Wet            | `P2`: Frequency          |
| `P3`: Frequency       | `P3`: Delay Time         | `P3`: LFO Phase          |
| `P4`: Sync Rate       | `P4`: Feedback           | `P4`: Sync               |
| `P5`: LFO Amount      | `P5`: Env. Modulation    | `P5`: LFO Offset         |
| `P6`: Env. Modulation | `P6`: Env. Attack        | `P6`: Sync Rate          |
| `P7`: Feedback        | `P7`: Env. Release       | `P7`: LFO Width (Random) |
| `P8`: Dry/Wet         | `P8`:                    | `P8`: LFO Waveform       |

[Back to Device Index](#device-index)

* * *

## Frequency Shifter

| `B0`: Best of Banks      | `B1`:                    |
| :----------------------- | :----------------------- |
| `P1`: Coarse             | `P1`: Coarse             |
| `P2`: Fine               | `P2`: Fine               |
| `P3`: Mode               | `P3`: Mode               |
| `P4`: Ring Mod Frequency | `P4`: Ring Mod Frequency |
| `P5`: Drive On/Off       | `P5`: Drive On/Off       |
| `P6`: Drive              | `P6`: Drive              |
| `P7`: Wide               | `P7`: Wide               |
| `P8`: Dry/Wet            | `P8`: Dry/Wet            |

[Back to Device Index](#device-index)

* * *

## Gate

| `B0`: Best of Banks | `B1`: Gate      | `B2`: Side Chain  |
| :------------------ | :-------------- | :---------------- |
| `P1`: Threshold     | `P1`: Threshold | `P1`: S/C EQ On   |
| `P2`: Return        | `P2`: Return    | `P2`: S/C EQ Type |
| `P3`: FlipMode      | `P3`: FlipMode  | `P3`: S/C EQ Freq |
| `P4`: LookAhead     | `P4`: LookAhead | `P4`: S/C EQ Q    |
| `P5`: Attack        | `P5`: Attack    | `P5`: S/C EQ Gain |
| `P6`: Hold          | `P6`: Hold      | `P6`: S/C On      |
| `P7`: Release       | `P7`: Release   | `P7`: S/C Mix     |
| `P8`: Floor         | `P8`: Floor     | `P8`: S/C Gain    |

[Back to Device Index](#device-index)

* * *

## Glue Compressor

| `B0`: Best of Banks | `B1`: Compression  | `B2`: Side Chain  |
| :------------------ | :----------------- | :---------------- |
| `P1`: Threshold     | `P1`: Threshold    | `P1`: S/C EQ On   |
| `P2`: Ratio         | `P2`: Ratio        | `P2`: S/C EQ Type |
| `P3`: Attack        | `P3`: Attack       | `P3`: S/C EQ Freq |
| `P4`: Release       | `P4`: Release      | `P4`: S/C EQ Q    |
| `P5`: Peak Clip In  | `P5`: Peak Clip In | `P5`: S/C EQ Gain |
| `P6`: Range         | `P6`: Range        | `P6`: S/C On      |
| `P7`: Makeup        | `P7`: Dry/Wet      | `P7`: S/C Mix     |
| `P8`: Dry/Wet       | `P8`: Makeup       | `P8`: S/C Gain    |

[Back to Device Index](#device-index)

* * *

## Grain Delay

| `B0`: Best of Banks | `B1`:            |
| :------------------ | :--------------- |
| `P1`: Frequency     | `P1`: Frequency  |
| `P2`: Pitch         | `P2`: Pitch      |
| `P3`: Time Delay    | `P3`: Time Delay |
| `P4`: Beat Swing    | `P4`: Beat Swing |
| `P5`: Random        | `P5`: Random     |
| `P6`: Spray         | `P6`: Spray      |
| `P7`: Feedback      | `P7`: Feedback   |
| `P8`: DryWet        | `P8`: DryWet     |

[Back to Device Index](#device-index)

* * *

## Impulse

| `B0`: Best of Banks    | `B1`: Pad 1             | `B2`: Pad 2             | `B3`: Pad 3             | `B4`: Pad 4             | `B5`: Pad 5             | `B6`: Pad 6             | `B7`: Pad 7             | `B8`: Pad 8             |
| :--------------------- | :---------------------- | :---------------------- | :---------------------- | :---------------------- | :---------------------- | :---------------------- | :---------------------- | :---------------------- |
| `P1`: Global Time      | `P1`: 1 Start           | `P1`: 2 Start           | `P1`: 3 Start           | `P1`: 4 Start           | `P1`: 5 Start           | `P1`: 6 Start           | `P1`: 7 Start           | `P1`: 8 Start           |
| `P2`: Global Transpose | `P2`: 1 Transpose       | `P2`: 2 Transpose       | `P2`: 3 Transpose       | `P2`: 4 Transpose       | `P2`: 5 Transpose       | `P2`: 6 Transpose       | `P2`: 7 Transpose       | `P2`: 8 Transpose       |
| `P3`: 1 Transpose      | `P3`: 1 Stretch Factor  | `P3`: 2 Stretch Factor  | `P3`: 3 Stretch Factor  | `P3`: 4 Stretch Factor  | `P3`: 5 Stretch Factor  | `P3`: 6 Stretch Factor  | `P3`: 7 Stretch Factor  | `P3`: 8 Stretch Factor  |
| `P4`: 2 Transpose      | `P4`: 1 Saturator Drive | `P4`: 2 Saturator Drive | `P4`: 3 Saturator Drive | `P4`: 4 Saturator Drive | `P4`: 5 Saturator Drive | `P4`: 6 Saturator Drive | `P4`: 7 Saturator Drive | `P4`: 8 Saturator Drive |
| `P5`: 3 Transpose      | `P5`: 1 Filter Freq     | `P5`: 2 Filter Freq     | `P5`: 3 Filter Freq     | `P5`: 4 Filter Freq     | `P5`: 5 Filter Freq     | `P5`: 6 Filter Freq     | `P5`: 7 Filter Freq     | `P5`: 8 Filter Freq     |
| `P6`: 4 Transpose      | `P6`: 1 Filter Res      | `P6`: 2 Filter Res      | `P6`: 3 Filter Res      | `P6`: 4 Filter Res      | `P6`: 5 Filter Res      | `P6`: 6 Filter Res      | `P6`: 7 Filter Res      | `P6`: 8 Filter Res      |
| `P7`: 5 Transpose      | `P7`: 1 Pan             | `P7`: 2 Pan             | `P7`: 3 Pan             | `P7`: 4 Pan             | `P7`: 5 Pan             | `P7`: 6 Pan             | `P7`: 7 Pan             | `P7`: 8 Pan             |
| `P8`: 6 Transpose      | `P8`: 1 Volume          | `P8`: 2 Volume          | `P8`: 3 Volume          | `P8`: 4 Volume          | `P8`: 5 Volume          | `P8`: 6 Volume          | `P8`: 7 Volume          | `P8`: 8 Volume          |

[Back to Device Index](#device-index)

* * *

## InstrumentVector

| `B0`: Best of Banks     | `B1`: Oscillator 1   | `B2`: Oscillator 2   | `B3`: Filter 1             | `B4`: Filter 2             | `B5`: Amp Envelope  | `B6`: Envelope 2/3  | `B7`: LFO 1/2       | `B8`: Global            |
| :---------------------- | :------------------- | :------------------- | :------------------------- | :------------------------- | :------------------ | :------------------ | :------------------ | :---------------------- |
| `P1`: Osc 1 Pos         | `P1`: Osc 1 Transp   | `P1`: Osc 2 Transp   | `P1`: Filter 1 On          | `P1`: Filter 2 On          | `P1`: Amp Attack    | `P1`: Env 2 Attack  | `P1`: LFO 1 Amount  | `P1`: Time              |
| `P2`: Osc 1 Transp      | `P2`: Osc 1 Detune   | `P2`: Osc 2 Detune   | `P2`: Filter 1 Freq        | `P2`: Filter 2 Freq        | `P2`: Amp Decay     | `P2`: Env 2 Decay   | `P2`: LFO 1 Rate    | `P2`: Global Mod Amount |
| `P3`: Osc 2 Pos         | `P3`: Osc 1 Pos      | `P3`: Osc 2 Pos      | `P3`: Filter 1 Res         | `P3`: Filter 2 Res         | `P3`: Amp Sustain   | `P3`: Env 2 Sustain | `P3`: LFO 1 S. Rate | `P3`: Unison Amount     |
| `P4`: Osc 2 Transp      | `P4`: Osc 1 Effect 1 | `P4`: Osc 2 Effect 1 | `P4`: Filter 1 Drive       | `P4`: Filter 2 Drive       | `P4`: Amp Release   | `P4`: Env 2 Release | `P4`: LFO 1 Sync    | `P4`: Transpose         |
| `P5`: Filter 1 Freq     | `P5`: Osc 1 Effect 2 | `P5`: Osc 2 Effect 2 | `P5`: Filter 1 Type        | `P5`: Filter 2 Type        | `P5`: Amp A Slope   | `P5`: Env 3 Attack  | `P5`: LFO 2 Amount  | `P5`: Glide             |
| `P6`: Filter 1 Res      | `P6`: Osc 1 Pan      | `P6`: Osc 2 Pan      | `P6`: Filter 1 Slope       | `P6`: Filter 2 Slope       | `P6`: Amp D Slope   | `P6`: Env 3 Decay   | `P6`: LFO 2 Rate    | `P6`: Sub Gain          |
| `P7`: Global Mod Amount | `P7`: Osc 1 Gain     | `P7`: Osc 2 Gain     | `P7`: Filter 1 LP/HP       | `P7`: Filter 2 LP/HP       | `P7`: Amp R Slope   | `P7`: Env 3 Sustain | `P7`: LFO 2 S. Rate | `P7`: Sub Transpose     |
| `P8`: Volume            | `P8`: Osc 1 On       | `P8`: Osc 2 On       | `P8`: Filter 1 BP/NO/Morph | `P8`: Filter 2 BP/NO/Morph | `P8`: Amp Loop Mode | `P8`: Env 3 Release | `P8`: LFO 2 Sync    | `P8`: Volume            |

[Back to Device Index](#device-index)

* * *

## Looper

| `B0`: Best of Banks | `B1`:               |
| :------------------ | :------------------ |
| `P1`: State         | `P1`: State         |
| `P2`: Speed         | `P2`: Speed         |
| `P3`: Reverse       | `P3`: Reverse       |
| `P4`: Quantization  | `P4`: Quantization  |
| `P5`: Monitor       | `P5`: Monitor       |
| `P6`: Song Control  | `P6`: Song Control  |
| `P7`: Tempo Control | `P7`: Tempo Control |
| `P8`: Feedback      | `P8`: Feedback      |

[Back to Device Index](#device-index)

* * *

## Multiband Dynamics

| `B0`: Best of Banks          | `B1`: Global                | `B2`: Low Band              | `B3`: Mid Band              | `B4`: High Band              | `B5`: Split Frequencies  | `B6`: Side Chain |
| :--------------------------- | :-------------------------- | :-------------------------- | :-------------------------- | :--------------------------- | :----------------------- | :--------------- |
| `P1`: Above Threshold (Low)  | `P1`: Master Output         | `P1`: Input Gain (Low)      | `P1`: Input Gain (Mid)      | `P1`: Input Gain (High)      | `P1`: Low-Mid Crossover  | `P1`:            |
| `P2`: Above Ratio (Low)      | `P2`: Amount                | `P2`: Below Threshold (Low) | `P2`: Below Threshold (Mid) | `P2`: Below Threshold (High) | `P2`: Mid-High Crossover | `P2`:            |
| `P3`: Above Threshold (Mid)  | `P3`: Time Scaling          | `P3`: Below Ratio (Low)     | `P3`: Below Ratio (Mid)     | `P3`: Below Ratio (High)     | `P3`:                    | `P3`:            |
| `P4`: Above Ratio (Mid)      | `P4`: Soft Knee On/Off      | `P4`: Above Threshold (Low) | `P4`: Above Threshold (Mid) | `P4`: Above Threshold (High) | `P4`:                    | `P4`:            |
| `P5`: Above Threshold (High) | `P5`: Peak/RMS Mode         | `P5`: Above Ratio (Low)     | `P5`: Above Ratio (Mid)     | `P5`: Above Ratio (High)     | `P5`:                    | `P5`:            |
| `P6`: Above Ratio (High)     | `P6`: Band Activator (High) | `P6`: Attack Time (Low)     | `P6`: Attack Time (Mid)     | `P6`: Attack Time (High)     | `P6`:                    | `P6`: S/C On     |
| `P7`: Master Output          | `P7`: Band Activator (Mid)  | `P7`: Release Time (Low)    | `P7`: Release Time (Mid)    | `P7`: Release Time (High)    | `P7`:                    | `P7`: S/C Mix    |
| `P8`: Amount                 | `P8`: Band Activator (Low)  | `P8`: Output Gain (Low)     | `P8`: Output Gain (Mid)     | `P8`: Output Gain (High)     | `P8`:                    | `P8`: S/C Gain   |

[Back to Device Index](#device-index)

* * *

## Note Length

| `B0`: Best of Banks   | `B1`:                 |
| :-------------------- | :-------------------- |
| `P1`: Sync On         | `P1`: Sync On         |
| `P2`: Time Length     | `P2`: Time Length     |
| `P3`: Synced Length   | `P3`: Synced Length   |
| `P4`: Gate            | `P4`: Gate            |
| `P5`: On/Off-Balance  | `P5`: On/Off-Balance  |
| `P6`: Decay Time      | `P6`: Decay Time      |
| `P7`: Decay Key Scale | `P7`: Decay Key Scale |
| `P8`:                 | `P8`:                 |

[Back to Device Index](#device-index)

* * *

## Operator

| `B0`: Best of Banks | `B1`: Oscillator A    | `B2`: Oscillator B    | `B3`: Oscillator C    | `B4`: Oscillator D    | `B5`: LFO        | `B6`: Filter      | `B7`: Pitch Modulation | `B8`: Routing    |
| :------------------ | :-------------------- | :-------------------- | :-------------------- | :-------------------- | :--------------- | :---------------- | :--------------------- | :--------------- |
| `P1`: Filter Freq   | `P1`: Ae Attack       | `P1`: Be Attack       | `P1`: Ce Attack       | `P1`: De Attack       | `P1`: Le Attack  | `P1`: Fe Attack   | `P1`: Pe Attack        | `P1`: Time < Key |
| `P2`: Filter Res    | `P2`: Ae Decay        | `P2`: Be Decay        | `P2`: Ce Decay        | `P2`: De Decay        | `P2`: Le Decay   | `P2`: Fe Decay    | `P2`: Pe Decay         | `P2`: Panorama   |
| `P3`: A Coarse      | `P3`: Ae Sustain      | `P3`: Be Sustain      | `P3`: Ce Sustain      | `P3`: De Sustain      | `P3`: Le Sustain | `P3`: Fe Sustain  | `P3`: Pe Sustain       | `P3`: Pan < Key  |
| `P4`: A Fine        | `P4`: Ae Release      | `P4`: Be Release      | `P4`: Ce Release      | `P4`: De Release      | `P4`: Le Release | `P4`: Fe Release  | `P4`: Pe Release       | `P4`: Pan < Rnd  |
| `P5`: B Coarse      | `P5`: A Coarse        | `P5`: B Coarse        | `P5`: C Coarse        | `P5`: D Coarse        | `P5`: LFO Rate   | `P5`: Filter Freq | `P5`: Pe Init          | `P5`: Algorithm  |
| `P6`: B Fine        | `P6`: A Fine          | `P6`: B Fine          | `P6`: C Fine          | `P6`: D Fine          | `P6`: LFO Amt    | `P6`: Filter Res  | `P6`: Glide Time       | `P6`: Time       |
| `P7`: Osc-B Level   | `P7`: Osc-A Lev < Vel | `P7`: Osc-B Lev < Vel | `P7`: Osc-C Lev < Vel | `P7`: Osc-D Lev < Vel | `P7`: LFO Type   | `P7`: Fe R < Vel  | `P7`: Pe Amount        | `P7`: Tone       |
| `P8`: Volume        | `P8`: Osc-A Level     | `P8`: Osc-B Level     | `P8`: Osc-C Level     | `P8`: Osc-D Level     | `P8`: LFO R < K  | `P8`: Fe Amount   | `P8`: Spread           | `P8`: Volume     |

[Back to Device Index](#device-index)

* * *

## Overdrive

| `B0`: Best of Banks     | `B1`:                   |
| :---------------------- | :---------------------- |
| `P1`: Filter Freq       | `P1`: Filter Freq       |
| `P2`: Filter Width      | `P2`: Filter Width      |
| `P3`: Drive             | `P3`: Drive             |
| `P4`: Tone              | `P4`: Tone              |
| `P5`: Preserve Dynamics | `P5`: Preserve Dynamics |
| `P6`:                   | `P6`:                   |
| `P7`:                   | `P7`:                   |
| `P8`: Dry/Wet           | `P8`: Dry/Wet           |

[Back to Device Index](#device-index)

* * *

## Pedal

| `B0`: Best of Banks | `B1`: General | `B2`: Eq       |
| :------------------ | :------------ | :------------- |
| `P1`: Type          | `P1`: Type    | `P1`: Mid Freq |
| `P2`: Gain          | `P2`: Gain    | `P2`:          |
| `P3`: Output        | `P3`: Output  | `P3`:          |
| `P4`: Bass          | `P4`: Bass    | `P4`:          |
| `P5`: Mid           | `P5`: Mid     | `P5`:          |
| `P6`: Treble        | `P6`: Treble  | `P6`:          |
| `P7`: Sub           | `P7`: Sub     | `P7`:          |
| `P8`: Dry/Wet       | `P8`: Dry/Wet | `P8`:          |

[Back to Device Index](#device-index)

* * *

## Phaser

| `B0`: Best of Banks   | `B1`: Frequency Controls | `B2`: LFO / S&H     |
| :-------------------- | :----------------------- | :------------------ |
| `P1`: Frequency       | `P1`: Poles              | `P1`: LFO Amount    |
| `P2`: Feedback        | `P2`: Color              | `P2`: LFO Frequency |
| `P3`: Poles           | `P3`: Dry/Wet            | `P3`: LFO Phase     |
| `P4`: Env. Modulation | `P4`: Frequency          | `P4`: LFO Sync      |
| `P5`: Color           | `P5`: Env. Modulation    | `P5`: LFO Offset    |
| `P6`: LFO Amount      | `P6`: Env. Attack        | `P6`: LFO Sync Rate |
| `P7`: LFO Frequency   | `P7`: Env. Release       | `P7`: LFO Spin      |
| `P8`: Dry/Wet         | `P8`: Feedback           | `P8`: LFO Waveform  |

[Back to Device Index](#device-index)

* * *

## Pitch

| `B0`: Best of Banks | `B1`:        |
| :------------------ | :----------- |
| `P1`: Pitch         | `P1`: Pitch  |
| `P2`: Range         | `P2`: Range  |
| `P3`: Lowest        | `P3`: Lowest |
| `P4`:               | `P4`:        |
| `P5`:               | `P5`:        |
| `P6`:               | `P6`:        |
| `P7`:               | `P7`:        |
| `P8`:               | `P8`:        |

[Back to Device Index](#device-index)

* * *

## Random

| `B0`: Best of Banks | `B1`:         |
| :------------------ | :------------ |
| `P1`: Chance        | `P1`: Chance  |
| `P2`: Choices       | `P2`: Choices |
| `P3`: Scale         | `P3`: Scale   |
| `P4`: Sign          | `P4`: Sign    |
| `P5`:               | `P5`:         |
| `P6`:               | `P6`:         |
| `P7`:               | `P7`:         |
| `P8`:               | `P8`:         |

[Back to Device Index](#device-index)

* * *

## Redux

| `B0`: Best of Banks | `B1`:             |
| :------------------ | :---------------- |
| `P1`: Bit Depth     | `P1`: Bit Depth   |
| `P2`: Sample Mode   | `P2`: Sample Mode |
| `P3`: Sample Hard   | `P3`: Sample Hard |
| `P4`: Sample Soft   | `P4`: Sample Soft |
| `P5`: Bit On        | `P5`: Bit On      |
| `P6`:               | `P6`:             |
| `P7`:               | `P7`:             |
| `P8`:               | `P8`:             |

[Back to Device Index](#device-index)

* * *

## Resonator

| `B0`: Best of Banks | `B1`: General / Mode I | `B2`: Modes II-IV |
| :------------------ | :--------------------- | :---------------- |
| `P1`: Decay         | `P1`: Frequency        | `P1`: II Gain     |
| `P2`: I Note        | `P2`: Width            | `P2`: III Gain    |
| `P3`: II Pitch      | `P3`: Global Gain      | `P3`: IV Gain     |
| `P4`: III Pitch     | `P4`: Dry/Wet          | `P4`: V Gain      |
| `P5`: IV Pitch      | `P5`: Decay            | `P5`: II Pitch    |
| `P6`: V Pitch       | `P6`: I Note           | `P6`: III Pitch   |
| `P7`: Global Gain   | `P7`: Color            | `P7`: IV Pitch    |
| `P8`: Dry/Wet       | `P8`: I Gain           | `P8`: V Pitch     |

[Back to Device Index](#device-index)

* * *

## Reverb

| `B0`: Best of Banks  | `B1`: Reflections     | `B2`: Diffusion Network | `B3`: Global        |
| :------------------- | :-------------------- | :---------------------- | :------------------ |
| `P1`: DecayTime      | `P1`: In Filter Freq  | `P1`: HiShelf Freq      | `P1`: DecayTime     |
| `P2`: Room Size      | `P2`: In Filter Width | `P2`: LowShelf Freq     | `P2`: Freeze On     |
| `P3`: PreDelay       | `P3`: PreDelay        | `P3`: Chorus Rate       | `P3`: Room Size     |
| `P4`: In Filter Freq | `P4`: ER Spin On      | `P4`: Density           | `P4`: Stereo Image  |
| `P5`: ER Level       | `P5`: ER Spin Rate    | `P5`: HiShelf Gain      | `P5`: ER Level      |
| `P6`: Diffuse Level  | `P6`: ER Spin Amount  | `P6`: LowShelf Gain     | `P6`: Diffuse Level |
| `P7`: Stereo Image   | `P7`: ER Shape        | `P7`: Chorus Amount     | `P7`: Dry/Wet       |
| `P8`: Dry/Wet        | `P8`: DecayTime       | `P8`: Scale             | `P8`: Quality       |

[Back to Device Index](#device-index)

* * *

## Sampler

| `B0`: Best of Banks | `B1`: Volume     | `B2`: Filter       | `B3`: Filter Envelope | `B4`: LFO 1         | `B5`: LFO 2         | `B6`: LFO 3         | `B7`: Oscillator | `B8`: Pitch      |
| :------------------ | :--------------- | :----------------- | :-------------------- | :------------------ | :------------------ | :------------------ | :--------------- | :--------------- |
| `P1`: Filter Freq   | `P1`: Volume     | `P1`: Filter Type  | `P1`: Fe Attack       | `P1`: L 1 Wave      | `P1`: L 2 Wave      | `P1`: L 3 Wave      | `P1`: O Mode     | `P1`: Transpose  |
| `P2`: Filter Res    | `P2`: Ve Attack  | `P2`: Filter Morph | `P2`: Fe Decay        | `P2`: L 1 Sync      | `P2`: L 2 Sync      | `P2`: L 3 Sync      | `P2`: O Volume   | `P2`: Spread     |
| `P3`: Fe < Env      | `P3`: Ve Decay   | `P3`: Filter Freq  | `P3`: Fe Sustain      | `P3`: L 1 Sync Rate | `P3`: L 2 Sync Rate | `P3`: L 3 Sync Rate | `P3`: O Coarse   | `P3`: Pe < Env   |
| `P4`: Fe Decay      | `P4`: Ve Sustain | `P4`: Filter Res   | `P4`: Fe Release      | `P4`: L 1 Rate      | `P4`: L 2 Rate      | `P4`: L 3 Rate      | `P4`: O Fine     | `P4`: Pe Attack  |
| `P5`: Ve Attack     | `P5`: Ve Release | `P5`: Filt < Vel   | `P5`: Fe End          | `P5`: Vol < LFO     | `P5`: L 2 R < Key   | `P5`: L 3 R < Key   | `P5`: Oe Attack  | `P5`: Pe Peak    |
| `P6`: Ve Release    | `P6`: Vol < Vel  | `P6`: Filt < Key   | `P6`: Fe Mode         | `P6`: Filt < LFO    | `P6`: L 2 St Mode   | `P6`: L 3 St Mode   | `P6`: Oe Decay   | `P6`: Pe Decay   |
| `P7`: Transpose     | `P7`: Ve R < Vel | `P7`: Fe < Env     | `P7`: Fe Loop         | `P7`: Pan < LFO     | `P7`: L 2 Spin      | `P7`: L 3 Spin      | `P7`: Oe Sustain | `P7`: Pe Sustain |
| `P8`: Volume        | `P8`: Time       | `P8`: Shaper Amt   | `P8`: Fe Retrig       | `P8`: Pitch < LFO   | `P8`: L 2 Phase     | `P8`: L 3 Phase     | `P8`: Oe Release | `P8`: Pe Release |

[Back to Device Index](#device-index)

* * *

## Saturator

| `B0`: Best of Banks | `B1`: General Controls | `B2`: Waveshaper Controls |
| :------------------ | :--------------------- | :------------------------ |
| `P1`: Drive         | `P1`: Drive            | `P1`: WS Drive            |
| `P2`: Type          | `P2`: Base             | `P2`: WS Lin              |
| `P3`: Base          | `P3`: Frequency        | `P3`: WS Curve            |
| `P4`: Frequency     | `P4`: Width            | `P4`: WS Damp             |
| `P5`: Width         | `P5`: Depth            | `P5`: WS Depth            |
| `P6`: Depth         | `P6`: Output           | `P6`: WS Period           |
| `P7`: Output        | `P7`: Dry/Wet          | `P7`: Dry/Wet             |
| `P8`: Dry/Wet       | `P8`: Type             | `P8`:                     |

[Back to Device Index](#device-index)

* * *

## Scale

| `B0`: Best of Banks | `B1`:           |
| :------------------ | :-------------- |
| `P1`: Base          | `P1`: Base      |
| `P2`: Transpose     | `P2`: Transpose |
| `P3`: Range         | `P3`: Range     |
| `P4`: Lowest        | `P4`: Lowest    |
| `P5`:               | `P5`:           |
| `P6`:               | `P6`:           |
| `P7`:               | `P7`:           |
| `P8`:               | `P8`:           |

[Back to Device Index](#device-index)

* * *

## Simpler

| `B0`: Best of Banks | `B1`: Amplitude     | `B2`: Filter      | `B3`: LFO         | `B4`: Pitch Modifiers |
| :------------------ | :------------------ | :---------------- | :---------------- | :-------------------- |
| `P1`: Filter Freq   | `P1`: Ve Attack     | `P1`: Fe Attack   | `P1`: L Attack    | `P1`: Pe Attack       |
| `P2`: Filter Res    | `P2`: Ve Decay      | `P2`: Fe Decay    | `P2`: L Rate      | `P2`: Pe Decay        |
| `P3`: S Start       | `P3`: Ve Sustain    | `P3`: Fe Sustain  | `P3`: L R < Key   | `P3`: Pe Sustain      |
| `P4`: S Length      | `P4`: Ve Release    | `P4`: Fe Release  | `P4`: L Wave      | `P4`: Pe Release      |
| `P5`: Ve Attack     | `P5`: S Start       | `P5`: Filter Freq | `P5`: Vol < LFO   | `P5`: Glide Time      |
| `P6`: Ve Release    | `P6`: S Loop Length | `P6`: Filter Res  | `P6`: Filt < LFO  | `P6`: Spread          |
| `P7`: Transpose     | `P7`: S Length      | `P7`: Filt < Vel  | `P7`: Pitch < LFO | `P7`: Pan             |
| `P8`: Volume        | `P8`: S Loop Fade   | `P8`: Fe < Env    | `P8`: Pan < LFO   | `P8`: Volume          |

[Back to Device Index](#device-index)

* * *

## Tension

| `B0`: Best of Banks  | `B1`: Excitator and String | `B2`: Damper      | `B3`: Termination and Pickup | `B4`: Body          | `B5`: Vibrato        | `B6`: Filter        | `B7`: Envelope and LFO | `B8`: Global        |
| :------------------- | :------------------------- | :---------------- | :--------------------------- | :------------------ | :------------------- | :------------------ | :--------------------- | :------------------ |
| `P1`: Filter Freq    | `P1`: Excitator Type       | `P1`: Damper On   | `P1`: Term On/Off            | `P1`: Body On/Off   | `P1`: Vibrato On/Off | `P1`: Filter On/Off | `P1`: FEG On/Off       | `P1`: Unison On/Off |
| `P2`: Filter Reso    | `P2`: String Decay         | `P2`: Damper Mass | `P2`: Term Mass              | `P2`: Body Type     | `P2`: Vib Delay      | `P2`: Filter Type   | `P2`: FEG Attack       | `P2`: Uni Detune    |
| `P3`: Filter Type    | `P3`: Str Inharmon         | `P3`: D Stiffness | `P3`: Term Fng Stiff         | `P3`: Body Size     | `P3`: Vib Fade-In    | `P3`: Filter Freq   | `P3`: FEG Decay        | `P3`: Porta On/Off  |
| `P4`: Excitator Type | `P4`: Str Damping          | `P4`: D Velocity  | `P4`: Term Fret Stiff        | `P4`: Body Decay    | `P4`: Vib Speed      | `P4`: Filter Reso   | `P4`: FEG Sustain      | `P4`: Porta Time    |
| `P5`: E Pos          | `P5`: Exc ForceMassProt    | `P5`: Damp Pos    | `P5`: Pickup On/Off          | `P5`: Body Low-Cut  | `P5`: Vib Amount     | `P5`: Freq < Env    | `P5`: FEG Release      | `P5`: Voices        |
| `P6`: String Decay   | `P6`: Exc FricStiff        | `P6`: D Damping   | `P6`: Pickup Pos             | `P6`: Body High-Cut | `P6`: Vib < ModWh    | `P6`: Freq < LFO    | `P6`: LFO On/Off       | `P6`: Octave        |
| `P7`: Str Damping    | `P7`: Exc Velocity         | `P7`: D Pos < Vel | `P7`: T Mass < Vel           | `P7`: Body Mix      | `P7`: Vib Error      | `P7`: Reso < Env    | `P7`: LFO Shape        | `P7`: Semitone      |
| `P8`: Volume         | `P8`: E Pos                | `P8`: D Pos Abs   | `P8`: T Mass < Key           | `P8`: Volume        | `P8`: Volume         | `P8`: Reso < LFO    | `P8`: LFO Speed        | `P8`: Volume        |

[Back to Device Index](#device-index)

* * *

## Utility

| `B0`: Best of Banks | `B1`: General Controls | `B2`: Low Frequency |
| :------------------ | :--------------------- | :------------------ |
| `P1`: Left Inv      | `P1`: Left Inv         | `P1`: Bass Mono     |
| `P2`: Right Inv     | `P2`: Right Inv        | `P2`: Bass Freq     |
| `P3`: Channel Mode  | `P3`: Channel Mode     | `P3`: DC Filter     |
| `P4`: Stereo Width  | `P4`: Stereo Width     | `P4`:               |
| `P5`: Mono          | `P5`: Mono             | `P5`:               |
| `P6`: Balance       | `P6`: Balance          | `P6`:               |
| `P7`: Gain          | `P7`: Gain             | `P7`:               |
| `P8`: Mute          | `P8`: Mute             | `P8`:               |

[Back to Device Index](#device-index)

* * *

## Velocity

| `B0`: Best of Banks | `B1`:         |
| :------------------ | :------------ |
| `P1`: Drive         | `P1`: Drive   |
| `P2`: Compand       | `P2`: Compand |
| `P3`: Random        | `P3`: Random  |
| `P4`: Mode          | `P4`: Mode    |
| `P5`: Out Hi        | `P5`: Out Hi  |
| `P6`: Out Low       | `P6`: Out Low |
| `P7`: Range         | `P7`: Range   |
| `P8`: Lowest        | `P8`: Lowest  |

[Back to Device Index](#device-index)

* * *

## Vinyl Distortion

| `B0`: Best of Banks   | `B1`:                 |
| :-------------------- | :-------------------- |
| `P1`: Tracing Freq.   | `P1`: Tracing Freq.   |
| `P2`: Tracing Width   | `P2`: Tracing Width   |
| `P3`: Tracing Drive   | `P3`: Tracing Drive   |
| `P4`: Crackle Density | `P4`: Crackle Density |
| `P5`: Pinch Freq.     | `P5`: Pinch Freq.     |
| `P6`: Pinch Width     | `P6`: Pinch Width     |
| `P7`: Pinch Drive     | `P7`: Pinch Drive     |
| `P8`: Crackle Volume  | `P8`: Crackle Volume  |

[Back to Device Index](#device-index)

* * *

## Vocoder

| `B0`: Best of Banks    | `B1`: Global         | `B2`: Filters/Voicing      | `B3`: Carrier               |
| :--------------------- | :------------------- | :------------------------- | :-------------------------- |
| `P1`: Formant Shift    | `P1`: Formant Shift  | `P1`: Filter Bandwidth     | `P1`: Noise Rate            |
| `P2`: Attack Time      | `P2`: Attack Time    | `P2`: Upper Filter Band    | `P2`: Noise Crackle         |
| `P3`: Release Time     | `P3`: Release Time   | `P3`: Lower Filter Band    | `P3`: Upper Pitch Detection |
| `P4`: Unvoiced Level   | `P4`: Mono/Stereo    | `P4`: Precise/Retro        | `P4`: Lower Pitch Detection |
| `P5`: Gate Threshold   | `P5`: Output Level   | `P5`: Unvoiced Level       | `P5`: Oscillator Pitch      |
| `P6`: Filter Bandwidth | `P6`: Gate Threshold | `P6`: Unvoiced Sensitivity | `P6`: Oscillator Waveform   |
| `P7`: Envelope Depth   | `P7`: Envelope Depth | `P7`: Unvoiced Speed       | `P7`: Ext. In Gain          |
| `P8`: Dry/Wet          | `P8`: Dry/Wet        | `P8`: Enhance              | `P8`:                       |

[Back to Device Index](#device-index)