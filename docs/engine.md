# Playback architecture and practical compatibility

## Separation and score contract

`composition/*.json` is the composition. `tools/compose.py` is its deterministic
authoring source; `tools/build.py` is the NES backend; `engine/player.s` is the
independent 6502 interpreter. No assembler labels, APU addresses, NES timer
periods, or bank assignments appear in the portable events. Percussion pitch is
null and the kit name is semantic; only the backend chooses noise periods.
The score could be mapped to MIDI, a synthesizer, or another chip without
interpreting NES bytecode. Those other backends are not implemented here.

Version 1 uses integer sixteenth-note onsets and durations, 4/4 meter, A440,
scientific pitch notation, semantic instruments, and 0–15 velocities. Melody,
counterline, bass, and percussion are monophonic logical parts. Gaps are rests;
overlaps in one part are rejected. Effects are named `vibrato`, `scoop`, and
`short_gate`. Sections include every bar's chord, inversion bass and available
voicing tones. Loop start/end are in the same units as events. Validation checks
meter, bounds, overlaps, effect/instrument names and hardware pitch ranges.

The current NES backend supports this score's fixed tempo: seven frames per
sixteenth. It rejects a different tempo rather than silently changing timing.
The four-byte backend event is `[note, instrument, velocity, flags]` for each of
four channels. Zero is rest, one is continuation; ordinary pitches are MIDI
numbers. Triangle pitches receive a backend-only +12 semitone table offset
because its oscillator divides the CPU clock by 32 rather than 16. Noise pitches
in bytecode are period+2. This backend layout is not the portable file format.

## Real 6502 driver

The init and play entry points are assembled machine code. INIT initializes all
owned state, disables DMC/IRQs, initializes sweep, silences voices, and enables
only the four intended channels. PLAY consumes a row every seven calls and
updates envelopes, duty, delayed vibrato and optional pitch scoops each call.
The row pointer jumps directly to its first row at the end; INIT is never called
at the musical loop. There is no synthesized-WAV payload disguised as an NSF.

Only legal 6502 instructions are used. The driver clears decimal mode, uses
private zero page plus $0200 RAM, balances its stack and returns promptly. There
is no PPU access, IRQ handler, mapper access, expansion chip, banking, or SRAM.
Timer high bytes are written at attack or when their actual value changes;
avoiding unconditional writes prevents pulse phase resets every frame. Software
volume envelopes permit per-frame capture by NSF importers. Triangle gates use
the linear counter. Noise envelopes, color changes, and gate lengths are also
software controlled. Longer sustained notes retain moving vibrato after their
volume-envelope age saturates.

## NSF and NTSC hardware

The delivered file is NSF version 1, one song, initial song 1, load $8000,
16639 microseconds per PLAY call, NTSC region flag 0, expansion flags 0, and
eight zero banking bytes. Header strings are null-terminated ASCII; reserved
bytes are zero. Payload fits in the ordinary $8000–$FFFF ROM window. INIT and
PLAY addresses are resolved by the linker; the test report and build metadata
record their exact values. No reset/NMI/IRQ vectors are required for this NSF
calling convention.

This is deliberately a conservative format for the **EverDrive N8 Pro**:
copy `lantern_circuit.nsf` to the SD card and select it in the NSF player on an
NTSC NES/Famicom with current firmware. There are no expansion-audio routing or
DPCM-bank complications. PAL playback is not supported by the musical timing
or tuning; the PAL speed field is populated conventionally but the region flag
is NTSC-only. A physical cartridge test was not available, so hardware success
is an expectation from the validated architecture, not an observation.

## Importer check

An actual 122-second import was run using the pinned
[nsfimport-cli](https://github.com/telescopeman/nsfimport-cli) port of **Brad
Smith's NSF Importer v0.5**, including its NotSo Fatso CPU/APU core. It produced
one subsong, one 2A03 instrument, zero DPCM samples, and 29 patterns without
warnings. The supplied `.ftm` is the resulting editable capture. A parser checks
its FamiTracker signature, blocks, frames, pattern bounds and populated note
data on all four audible channels; the DPCM channel has no sample notes.

This tests a Linux port, not the original Windows GUI or playback of the FTM in
a tracker. Importers reconstruct register activity rather than the original
phrases. They may represent vibrato/width changes as per-frame effects and volume
columns, and triangle gates shorter than a frame can lose detail. Here changes
are frame based, sweep is disabled, and no subframe PCM tricks are used. The FTM
uses speed 1/tempo 150, 256 rows per pattern, and includes a few seconds of the
next loop. It is intentionally an unedited import rather than a promised
lossless musical-score reconstruction. Use the JSON for reusable composition.

## Optional DPCM investigation

DPCM was evaluated but is **not required or enabled** in this release. The final
NSF does not read sample memory or enable DMC. Its noise kit supplies the complete
rhythm section. Source inspection of NSFPlay's DMC implementation confirms:

- DMC uses delta-coded one-bit steps, not ordinary PCM WAV bytes. A converter
  must encode and audition the quantized result, including the DAC's starting
  level and its end level.
- The start is `$C000 + 64 * $4012`; data must be mapped and 64-byte aligned.
  Length is `16 * $4013 + 1` bytes, up to 4081. Crossing $FFFF wraps to $8000;
  the optional design should avoid that wrap and code/data overlap.
- `$4010` controls rate/loop/IRQ; `$4015` bit 4 triggers playback. Disable DMC
  IRQs for a host-driven NSF. DMC DMA steals CPU cycles and the DAC changes the
  nonlinear triangle/noise mixer balance, so repeat CPU and mix validation.

A practical future option is a separately linked sample region at **$D000**,
which is beyond this payload's end. A 257-byte original kick would use start
register $40 and length register $10; at the highest NTSC rate its 2056 bits last
about 62 ms. Extend/pad the ROM image to include that region, add a semantic
optional sample layer to the score, and preserve noise hits as the fallback.
No fake sample data, unlicensed samples, raw-PCM substitute, or untested DPCM
playback is included. Such a backend extension would need fresh tests for DMA,
ROM bounds, retrigger behavior, DAC balance and importer sample extraction.

## Evidence and references

- Independent execution: py65 CPU tests over two full final-song loops, plus
  two loops of each candidate; header, timing, tuning, gates, envelope, width,
  vibrato, scoop, memory, reinitialization, stack and cycle-budget checks.
- Independent rendering: system libgme 0.6.3 runs the actual NSF and emits the
  WAVs; amplitude, duration, clipping and silence-window checks inspect them.
- A third execution path is the importer port's NotSo Fatso core.
- NSF layout inspected in [NSFPlay's parser](https://github.com/bbbradsmith/nsfplay/blob/6af5406e3325b5507bea1ae1a57c77d5efe5c7f3/xgm/player/nsf/nsf.cpp).
- DMC behavior inspected in [NSFPlay's implementation](https://github.com/bbbradsmith/nsfplay/blob/6af5406e3325b5507bea1ae1a57c77d5efe5c7f3/xgm/devices/Sound/nes_dmc.cpp).
- [Importer documentation](https://github.com/telescopeman/nsfimport-cli/blob/8eb2253aaf079b81726e77a6ad14a1e5fd0f7e80/README.md)
  describes the v0.5 lineage, frame capture and known limitations.

Dependency sources, versions and commits are pinned in `tools/toolchain.lock.json`.
No third-party engine source is copied into this project's original driver.
