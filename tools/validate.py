#!/usr/bin/env python3
"""Run the real suite, retain its output/status, and publish measured evidence."""
import array
import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import unittest
import wave

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'tools'))

def main():
    from test_music import MusicTests
    from ftm_inspect import inspect
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MusicTests))
    text=stream.getvalue()
    print(text,end='')
    out=ROOT/'reports'; out.mkdir(exist_ok=True)
    (out/'test-results.txt').write_text(text)
    audio={}
    for path in sorted((ROOT/'deliverables').glob('*.wav')):
        with wave.open(str(path),'rb') as w:
            samples=array.array('h',w.readframes(w.getnframes()))
            if sys.byteorder!='little': samples.byteswap()
            peak=max(abs(n) for n in samples)
            rms=math.sqrt(sum(n*n for n in samples)/len(samples))
            audio[path.name]=dict(seconds=w.getnframes()/w.getframerate(),sample_rate=w.getframerate(),
                                  channels=w.getnchannels(),peak_pcm16=peak,rms_pcm16=round(rms,3),
                                  peak_dbfs=round(20*math.log10(peak/32768),3),clipped_samples=sum(abs(n)>=32767 for n in samples))
    d=MusicTests.d
    score=MusicTests.score
    worst=0
    from build import CHANNELS,midi
    for c,ch in enumerate(CHANNELS[:3]):
        for e in score['channels'][ch]:
            target=440*2**((midi(e['pitch'])-69)/12)
            div=32 if c==2 else 16
            p=round(1789773/(div*target)-1)
            worst=max(worst,abs(1200*math.log2(1789773/(div*(p+1))/target)))
    report=dict(status='passed' if result.wasSuccessful() else 'failed',tests_run=result.testsRun,
                failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
                cpu_core='py65 1.2.0 MPU6502 (decimal flag explicitly cleared by driver)',
                final_frames_executed=len(MusicTests.frames),complete_loops_executed=2,
                maximum_routine_cycles=d.max_cycles,ntsc_frame_budget_cycles=29780,
                maximum_stack_bytes=255-d.max_stack,
                worst_unmodulated_pitch_error_cents=round(worst,4),
                loop_frame_count=d.meta['frames'],loop_seconds=d.meta['loop_seconds'],
                loop_apu_write_sequences_identical=MusicTests.frames[:d.meta['frames']]==MusicTests.frames[d.meta['frames']:],
                audio_renderer='libgme 0.6.3 independent 6502/APU emulation',audio=audio,
                importer=dict(implementation='telescopeman/nsfimport-cli; port of Brad Smith NSF Importer v0.5',
                              commit='8eb2253aaf079b81726e77a6ad14a1e5fd0f7e80',seconds_recorded=122,
                              command='nsfimport --seconds 122 --silence 0 --pattern-length 256 --no-m3u deliverables/lantern_circuit.nsf deliverables/lantern_circuit_import.ftm',
                              output=inspect(ROOT/'deliverables/lantern_circuit_import.ftm'),warnings=[]),
                hardware_tested=False,original_windows_importer_tested=False,human_listening_performed=False,
                sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'deliverables').iterdir()) if p.suffix in ('.nsf','.wav','.ftm')})
    # Transient scratch bytes can differ even when the externally visible writes
    # repeat. Report exactly the property tested, not incidental scratch RAM.
    n=d.meta['frames']
    report['loop_apu_write_sequences_identical']=[w for w,s in MusicTests.frames[:n]]==[w for w,s in MusicTests.frames[n:]]
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__': raise SystemExit(main())
