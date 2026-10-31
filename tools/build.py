#!/usr/bin/env python3
"""Compile portable score JSON to a frame-driven NSF 1 image."""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
INSTRUMENTS={'singing_lead':0,'glass':1,'soft_counter':2,'bright_lead':3,'triangle':0,'kick':4,'snare':5,'hat':6}
FLAGS={'scoop':128,'vibrato':64,'short_gate':32}
NOISE_PERIODS={'kick':13,'snare':7,'hat':2}
CHANNELS=['melody','counterline','bass','percussion']

def midi(p):
    return 12*(int(p[-1])+1)+{'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[p[0]]+p[1:-1].count('#')-p[1:-1].count('b')

def validate(score):
    assert score['format']=='nes-master-composer.score' and score['version']==1
    assert score['time_unit']=='sixteenth_note' and score['meter']==[4,4]
    total=score['bars']*16
    assert score['loop']=={'start':0,'end':total}
    assert abs(score['tempo_bpm']-60_000_000/(16639*7*4))<0.001
    assert len(score['sections'])==score['bars']
    for channel in CHANNELS:
        occupied=set()
        for e in score['channels'][channel]:
            assert all(isinstance(e[k],int) for k in ('at','duration','velocity'))
            assert e['duration']>0 and e['at']>=0 and e['at']+e['duration']<=total
            assert 0<=e['velocity']<=15 and e['instrument'] in INSTRUMENTS
            assert len(set(e['effects']))==len(e['effects']) and set(e['effects'])<=FLAGS.keys()
            cells=set(range(e['at'],e['at']+e['duration']))
            assert not cells&occupied, (channel,e)
            occupied|=cells
            if channel=='percussion':
                assert e['pitch'] is None
                assert e['instrument'] in ('kick','snare','hat')
            else:
                n=midi(e['pitch'])
                assert 33<=n<=96
                assert e['instrument'] not in ('kick','snare','hat')
                # The triangle divider is twice the pulse divider.
                divisor=32 if channel=='bass' else 16
                period=round(1789773/(divisor*440*2**((n-69)/12))-1)
                assert 8<=period<=2047

def rows_for(score):
    validate(score)
    rows=[[[0,0,0,0] for _ in CHANNELS] for _ in range(score['bars']*16)]
    for c,channel in enumerate(CHANNELS):
        for e in score['channels'][channel]:
            n=NOISE_PERIODS[e['instrument']]+2 if c==3 else midi(e['pitch'])
            # Triangle uses the same timer table with a one-octave transpose.
            if c==2: n+=12
            rows[e['at']][c]=[n,INSTRUMENTS[e['instrument']],e['velocity'],sum(FLAGS[f] for f in e['effects'])]
            for i in range(1,e['duration']): rows[e['at']+i][c]=[1,0,0,0]
    return rows

def tool(name):
    value=os.environ.get(name.upper()) or shutil.which(name)
    local=Path('/workspace/tools/cc65/bin')/name
    if value: return value
    if local.exists(): return str(local)
    raise SystemExit(f'{name} missing: install cc65 or set {name.upper()}')

def build(path):
    score=json.loads(path.read_text())
    rows=rows_for(score)
    out=ROOT/'build'/path.stem
    out.mkdir(parents=True,exist_ok=True)
    periods=[max(0,min(2047,round(1789773/(16*440*2**((n-69)/12))-1))) for n in range(128)]
    lines=['FRAMES_PER_ROW = 7','periods_lo:', '.byte '+','.join(str(p&255) for p in periods),
           'periods_hi:', '.byte '+','.join(str(p>>8) for p in periods),'song_data:']
    lines += ['.byte '+','.join(str(v) for c in row for v in c) for row in rows]
    lines += ['song_end:']
    (out/'score.inc').write_text('\n'.join(lines)+'\n')
    subprocess.run([tool('ca65'),'-g','-I',str(out),str(ROOT/'engine/player.s'),'-o',str(out/'player.o')],check=True)
    subprocess.run([tool('ld65'),'-C',str(ROOT/'engine/nsf.cfg'),'-o',str(out/'player.bin'),
                    '-Ln',str(out/'labels.txt'),'-m',str(out/'map.txt'),str(out/'player.o')],check=True)
    labels={line.split()[2].lstrip('.'):int(line.split()[1],16) for line in (out/'labels.txt').read_text().splitlines() if len(line.split())==3}
    data=(out/'player.bin').read_bytes()
    assert len(data)<=32768
    header=bytearray(128)
    header[:8]=b'NESM\x1a\x01\x01\x01'
    struct.pack_into('<HHH',header,8,0x8000,labels['init'],labels['play'])
    for offset,value in [(14,score['title']),(46,score['author']),(78,'2026 Original composition')]:
        encoded=value.encode('ascii')[:31]
        header[offset:offset+len(encoded)]=encoded
    struct.pack_into('<H',header,110,16639)
    struct.pack_into('<H',header,120,19997)
    # $7A=0: NTSC only; $7B=0: base 2A03, no expansion chip.
    artifact=ROOT/'deliverables'/f'{path.stem}.nsf'
    artifact.parent.mkdir(exist_ok=True)
    artifact.write_bytes(header+data)
    metadata=dict(title=score['title'],frames=len(rows)*7,frame_period_us=16639,
                  loop_seconds=len(rows)*7*16639/1_000_000,load_address=32768,
                  init_address=labels['init'],play_address=labels['play'],bytes=128+len(data),
                  labels=labels,source=str(path.relative_to(ROOT)))
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(f'{artifact.relative_to(ROOT)}: {len(data)+128} bytes; {metadata["loop_seconds"]:.6f}s loop')
    return artifact

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('scores',nargs='*',type=Path)
    args=parser.parse_args()
    for path in args.scores or sorted((ROOT/'composition').glob('candidate_*.json'))+[ROOT/'composition/lantern_circuit.json']:
        build(path)
