#!/usr/bin/env python3
"""Render actual 6502/APU playback through independent libgme, not synthesis of JSON."""
import argparse
import ctypes as C
import ctypes.util
import json
from pathlib import Path
import wave

ROOT=Path(__file__).resolve().parents[1]

def render(nsf, destination, seconds, sample_rate=44100):
    lib=ctypes.util.find_library('gme')
    if not lib: raise SystemExit('libgme required (Debian: libgme0); ffmpeg libgme is an alternative.')
    gme=C.CDLL(lib)
    gme.gme_open_file.argtypes=[C.c_char_p,C.POINTER(C.c_void_p),C.c_int]
    gme.gme_open_file.restype=C.c_char_p
    gme.gme_start_track.argtypes=[C.c_void_p,C.c_int]
    gme.gme_start_track.restype=C.c_char_p
    gme.gme_play.argtypes=[C.c_void_p,C.c_int,C.POINTER(C.c_short)]
    gme.gme_play.restype=C.c_char_p
    gme.gme_ignore_silence.argtypes=[C.c_void_p,C.c_int]
    gme.gme_warning.argtypes=[C.c_void_p]
    gme.gme_warning.restype=C.c_char_p
    gme.gme_delete.argtypes=[C.c_void_p]
    emu=C.c_void_p()
    def check(err):
        if err: raise RuntimeError(err.decode())
    check(gme.gme_open_file(str(nsf).encode(),C.byref(emu),sample_rate))
    try:
        gme.gme_ignore_silence(emu,1)
        check(gme.gme_start_track(emu,0))
        samples=round(seconds*sample_rate)
        destination.parent.mkdir(exist_ok=True,parents=True)
        with wave.open(str(destination),'wb') as out:
            out.setnchannels(2)
            out.setsampwidth(2)
            out.setframerate(sample_rate)
            for start in range(0,samples,8192):
                count=min(8192,samples-start)*2
                pcm=(C.c_short*count)()
                check(gme.gme_play(emu,count,pcm))
                out.writeframes(bytes(pcm))
        warning=gme.gme_warning(emu)
        if warning: raise RuntimeError('libgme warning: '+warning.decode())
    finally: gme.gme_delete(emu)
    print(f'Rendered {destination.relative_to(ROOT)}: {seconds:.6f}s, {sample_rate} Hz stereo PCM16')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('names',nargs='*')
    parser.add_argument('--loops',type=float,default=1)
    args=parser.parse_args()
    for name in args.names or ['candidate_glass','candidate_lantern','candidate_tidal','lantern_circuit']:
        meta=json.loads((ROOT/'build'/name/'metadata.json').read_text())
        render(ROOT/'deliverables'/f'{name}.nsf',ROOT/'deliverables'/f'{name}.wav',meta['loop_seconds']*args.loops)
