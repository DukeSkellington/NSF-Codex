# NES Master Composer — Lantern Circuit

An original 64-bar NES composition, a portable JSON score, and a real 6502 music
driver. **128.785 BPM, E minor, 119.268352 seconds per seamless musical loop.**

- [Final NSF](deliverables/lantern_circuit.nsf)
- [WAV preview](deliverables/lantern_circuit.wav): actual NSF emulation, 44.1 kHz stereo PCM16
- [Editable FamiTracker import](deliverables/lantern_circuit_import.ftm)
- [Portable composition](composition/lantern_circuit.json)
- [Three-theme comparison](composition/theme_comparison.json)
- [Musical study and form](docs/composition.md)
- [Engine, hardware, importer, and DPCM notes](docs/engine.md)
- [Test results](reports/test-results.txt) and [measured validation](reports/validation.json)

The candidate NSF/WAV files are also in `deliverables/`: **Lantern Circuit**,
**Glasswork Sprint**, and **Tidal Observatory**, each an eight-bar sketch.
The winning theme was selected using written musical criteria before the full
NSF was built. The comparison is editorial judgment, not an audience study.

## Rebuild

Requirements: Python 3.10+, `ca65` and `ld65` from cc65; `libgme` for WAV rendering;
`py65==1.2.0` for CPU tests. No npm, server, account, samples, or API keys required.
On Debian, cc65 and libgme0 are available as packages. Tested tool revisions are
in [tools/toolchain.lock.json](tools/toolchain.lock.json).

```sh
cd /workspace/NSF-Codex
python3 -m pip install -r requirements-dev.txt
python3 tools/compose.py
python3 tools/build.py
python3 tools/render.py
```

`build.py` finds `ca65`/`ld65` on PATH, honors the `CA65`/`LD65` environment
variables, and also recognizes the toolchain installed under `/workspace/tools`.
To build just one existing score, pass its JSON path. The assembler never reads
the authoring script; you can edit or replace a score independently.

For the optional importer check, build the pinned `nsfimport-cli` revision:

```sh
nsfimport --seconds 122 --silence 0 --pattern-length 256 --no-m3u \
  deliverables/lantern_circuit.nsf deliverables/lantern_circuit_import.ftm
python3 tools/validate.py
```

The validator exercises the delivered FTM as well as the WAVs and NSFs, so retain
the supplied FTM if you do not rebuild the optional importer. It writes the test
log and machine-readable measurements to `reports/` and returns nonzero on failure.
Third-party tools are external prerequisites; their source is not vendored here.

The WAV has one whole loop with no fade. The NSF loops indefinitely. Its first
frame follows normal initialization; the musical return resolves D# to E without
a restart or silence. The FTM is a **122-second frame-sampled capture**, including
the start of the next loop; it is an editing aid, not the portable source score.

The NSF targets standard NTSC 2A03 hardware with no expansion audio or bank
switching, for practical EverDrive N8 Pro compatibility. Emulator and importer
checks passed; a physical N8 Pro and the original Windows importer GUI were not
tested. Audio was rendered and measured, **not listened to**.
