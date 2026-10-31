# Musical design and technique study

## Approach

The ten composers supply complementary ideas about economy, melodic memory,
orchestration, and dramatic pacing. This is a study and synthesis of established
musical characteristics from the works below, using prior musical knowledge;
no new listening session, score transcription, or measured musicological survey
is claimed. No source melody, sample, or driver was copied. Descriptions apply to
selected works rather than every piece by a composer. Several reference platforms
have capabilities the NES does not: the aim is to translate musical functions.

| Composer; reference repertoire | Technique studied | Application in this original score |
| --- | --- | --- |
| Rob Hubbard; *Monty on the Run*, *Commando* (C64) | Propulsive bass as a second hook; harmonic information distributed across rapidly changing voices; long-form variation over small cells | Triangle's offbeat fifth/octave figures, approach tones, and cadential pedals; pulse 2 carries thirds and sevenths across time. SID filtering is not imitated. |
| Koji Kondo; *Super Mario Bros.*, *The Legend of Zelda* (NES) | Short identifiable rhythm, register-aware phrases, conversational rests, functional cycles that invite repetition | The E–B–D–E opening cell has a dotted-eighth/sixteenth shape, a lift, and a breath; its answer changes at the cadence. The dominant ending resolves into the opening E. |
| Tim Follin; *Solstice*, *Silver Surfer* (NES) | Large perceived ensemble from few voices; strong changes in density, timbre and register; extended harmony | Glass-like broken chords against the lead, width changes within attacks, and a thin bridge before the full return. No attempt to reproduce his specific arpeggios. |
| Yuzo Koshiro; *Ys*, *Streets of Rage* | Rhythmically independent bass, dance-music syncopation, modal/minor color and deliberate buildup | The bass anticipates beat 3; kicks at sixteenth 6 lean against snares at 4 and 12. Climax bass has additional octave syncopations. FM timbres become pulse articulation, not sampled FM. |
| Manami Matsumae; *Mega Man* (NES) | Clear diatonic shapes with energetic leaps, bright register, economical accompaniment | The rising minor third E–G expands to B and eventually high E. The lead remains singable rather than becoming a continuous arpeggio. |
| Takashi Tateishi; *Mega Man 2* (NES) | Repeatable anthemic cells, sequential lift, dramatic melodic peaks against driving harmony | The second eight bars answer the first with A–B–D at the top of the phrase; the climax expands the opening into E6 instead of just repeating louder. |
| Junko Tamiya; *Bionic Commando* (NES) | Dramatic minor harmony, angular action phrasing, contrast between forward motion and poised sustained notes | B7(b9) introduces D# and C against E-minor material; the bridge separates broad notes from short ascending dominant figures. |
| David Wise; *Battletoads* (NES), *Donkey Kong Country* (SNES) | Ostinato as atmosphere, patient contrast, independent melodic layers, percussion color | Lower, less dense bridge with a soft counterline and sparse hats; the accompaniment keeps a recognizable space while the melody changes. SNES sampled ambience is translated into spacing. |
| Hirokazu Tanaka; *Metroid*, *Kid Icarus* (NES) | Silence as orchestration, distinctive noise gestures, tension from limited harmonic material | Explicit rests in the opening/bridge, three noise kit colors, ghost notes, and a dominant pedal before release. Noise is written as a part, not a constant volume metronome. |
| Chris Hülsbeck; *The Great Giana Sisters*, *Turrican* | Broad melodic arcs, arpeggiated harmonic propulsion, bright contrasts and returning hooks | Relative-major B section, rising upper-register climax, and altered reprise. Amiga sample layering is reduced to a lead, broken harmony, and bass with distinct jobs. |

## Candidate stage

All three themes exist as fully specified eight-bar scores and playable sketches.
Each has the same basic instrumentation and tempo, making comparison less
dependent on production. Weights and scores are in `theme_comparison.json`.

| Theme | Memory 30% | Phrasing 20% | Harmony 20% | Channel fit 15% | Development 15% | /100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Lantern Circuit | 5 | 5 | 4 | 5 | 5 | **96** |
| Glasswork Sprint | 3 | 3 | 4 | 4 | 4 | 70 |
| Tidal Observatory | 4 | 4 | 4 | 5 | 3 | 80 |

Scores are on a 1–5 scale. Lantern wins because its rhythmic identity survives
changes of harmony and register. Glass has color and drive but its continuous
leaps leave too little conversational space. Tidal is lyrical and economical,
but its long notes would make it harder to create a contrasting quiet bridge.
These are explicit compositional judgments made from the written themes; the
candidate WAVs are supplied so a listener can disagree or choose another direction.

## Final form

| Bars (one-based) | Time, approximately | Section | Musical purpose |
| --- | --- | --- | --- |
| 1–4 | 0:00 | Intro | Fragmented hook; harmony and percussion enter with space; D# pickup leads into E. |
| 5–20 | 0:07.45 | A | Two eight-bar periods. Antecedent rises to G, answer tightens on F#/D#; second period reaches D6 and makes the dominant more explicit. |
| 21–28 | 0:37.27 | B | Relative-major G center; longer notes and a high E6 apex. D9→G/B affirms the major center, A13/C# adds secondary-dominant color before B7 pulls back. |
| 29–36 | 0:52.18 | A2 | Familiar motif with a different second-bar answer and fourth-bar cadence. Brief scoops mark the return. |
| 37–44 | 1:07.09 | Bridge | A-Dorian region: Am6→D9/F#→Gmaj9→Em9. F# distinguishes it from A Aeolian. F#ø7→B7 points back toward E; density and register drop. |
| 45–60 | 1:22.00 | Climax | Opening cell expanded upward to E6, brighter duty movement, more active bass. The second half restates the hook at a new register rather than substituting unrelated virtuosity. |
| 61–64 | 1:51.81 | Turnaround | Cmaj9→Am9→B7(b9)→B7(b9). Last D#5 resolves up a semitone to the loop's first E5; chromatic bass approach also resolves into E. |

The minor/relative-major move is a deliberate change of tonal emphasis, not a
transposition of every track. The bridge is a temporary modal region and a
predominant/dominant route home. A13/C# is secondary color, not a claim of a
fully established remote key. This is a more coherent choice for a two-minute
piece than modulation simply to demonstrate complexity.

## Voice leading and expression

The principal rhythm is **3+1, 2+2, 3+1, 2+rest** sixteenths. E–B is a downward
fourth, D–E a stepwise recovery, and E–G the lift. Subsequent phrases preserve
that rhythm while widening the range. Four- and six-sixteenth notes receive
delayed vibrato; selected reprise/climax attacks scoop into pitch over eight
NTSC frames. The engine changes pulse width during each note, giving a narrower
attack and a fuller body. Volumes vary within the phrase, not only by section.

Pulse 2 supplies thirds, sevenths and upper extensions in a lower register.
The NES cannot sustain five-note chords while retaining melody and bass: the
named ninth/eleventh harmonies describe **successive voicing tones**, not five
simultaneous oscillators. Broken chords are balanced with offset responses and
longer counterline gestures in the bridge. Chord-tone order is deterministic
and the harmonic plan is explicitly stored in the score.

Triangle dynamics come from note length, rests, inversion, approach tones, and
register, since the channel has no ordinary volume control. The bass includes
offbeat fifths, octave anticipations, chromatic pickups, quieter bridge spacing,
and repeated dominant roots at phrase ends. Thus its expression is articulation
and contour, not a fictitious triangle volume envelope.

Noise percussion separates a falling low-color kick, a longer mid-color snare,
and a very short bright hat. Snares accent beats 2 and 4, offbeat kicks push the
phrase, hats have varied velocities, and low-velocity ghosts/four-hit fills mark
phrase boundaries. The bridge and first half of the intro have their own kit
density. The entire score is complete without DPCM samples.

The final preview is unnormalized emulator audio. Numeric checks establish
activity, headroom, tuning, timing and repeatability, not enjoyment or the
subjective balance a human listener would hear. No audio audition is claimed.
