#!/usr/bin/env python3
"""Author the portable score. No NES register values or engine bytecode here."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Deliberately authored bars; lengths are sixteenth notes, R is a rest.
LANTERN = [
    'E5:3 B4:1 D5:2 E5:2 G5:3 F#5:1 E5:2 R:2',
    'B4:2 D5:2 E5:4 G5:2 B5:2 A5:2 G5:2',
    'F#5:3 G5:1 A5:2 F#5:2 D5:4 B4:2 R:2',
    'E5:2 F#5:2 G5:2 A5:2 F#5:4 D5:2 R:2',
    'E5:3 B4:1 D5:2 E5:2 A5:3 G5:1 E5:2 C5:2',
    'D#5:2 F#5:2 A5:2 C6:2 B5:4 A5:2 F#5:2',
    'G5:3 F#5:1 E5:4 B4:2 D5:2 E5:2 G5:2',
    'F#5:2 D#5:2 B4:4 R:2 B4:2 D#5:2 F#5:2',
    'E5:3 B4:1 D5:2 E5:2 B5:3 A5:1 G5:2 R:2',
    'A5:2 G5:2 E5:4 D5:2 E5:2 G5:2 B5:2',
    'A5:3 B5:1 D6:2 B5:2 A5:4 G5:2 F#5:2',
    'E5:2 G5:2 F#5:2 E5:2 D5:4 B4:2 R:2',
    'C5:2 E5:2 A5:4 G5:2 E5:2 D5:2 C5:2',
    'D#5:2 F#5:2 A5:2 C6:2 B5:3 A5:1 F#5:2 D#5:2',
    'E5:4 G5:2 F#5:2 E5:4 D5:2 B4:2',
    'D#5:2 F#5:2 B5:4 A5:2 F#5:2 D#5:2 R:2',
]
GLASS = [
    'C5:2 G5:2 E5:2 B5:2 G5:2 E5:2 D5:2 G5:2',
    'D5:3 A5:1 F#5:2 C6:2 A5:2 F#5:2 E5:2 A5:2',
    'E5:2 B5:2 G5:2 D6:2 B5:2 A5:2 G5:2 E5:2',
    'F#5:2 A5:2 C6:2 D#6:2 B5:4 F#5:2 R:2',
    'C6:3 B5:1 G5:2 E5:2 D5:2 E5:2 G5:2 B5:2',
    'A5:2 F#5:2 D5:2 E5:2 F#5:2 A5:2 C6:2 A5:2',
    'G5:4 E5:2 D5:2 B4:2 D5:2 E5:2 G5:2',
    'F#5:2 D#5:2 B4:2 A4:2 F#4:4 R:4',
]
TIDAL = [
    'A4:4 C5:2 E5:2 G5:4 E5:2 R:2',
    'F#5:4 E5:2 D5:2 C5:4 A4:4',
    'B4:3 D5:1 F#5:4 A5:4 F#5:2 D5:2',
    'E5:6 D5:2 B4:4 R:4',
    'A4:2 C5:2 E5:4 B5:4 A5:2 G5:2',
    'F#5:4 A5:2 F#5:2 E5:4 C5:4',
    'D5:2 E5:2 G5:4 F#5:2 E5:2 D5:2 C5:2',
    'D#5:4 F#5:4 B4:6 R:2',
]
BRIGHT = [
    'B5:4 A5:2 G5:2 D5:4 G5:2 A5:2',
    'B5:3 A5:1 G5:4 E5:2 G5:2 A5:2 B5:2',
    'C6:4 B5:2 A5:2 G5:4 E5:2 D5:2',
    'F#5:3 G5:1 A5:4 D5:4 R:2 A5:2',
    'G5:4 B5:2 D6:2 E6:4 D6:2 B5:2',
    'C6:2 B5:2 A5:4 F#5:2 A5:2 C6:2 A5:2',
    'B5:4 G5:2 F#5:2 E5:4 D#5:2 F#5:2',
    'A5:2 F#5:2 D#5:4 C6:2 B5:2 A5:2 F#5:2',
]
BRIDGE = [
    'A4:6 E5:2 G5:4 B5:2 A5:2',
    'F#5:4 E5:2 D5:2 B4:4 R:4',
    'G4:3 A4:1 B4:4 D5:4 F#5:2 G5:2',
    'E5:4 D5:2 B4:2 G4:4 R:4',
    'F#4:2 A4:2 C5:4 E5:4 D#5:2 C5:2',
    'B4:2 D#5:2 F#5:4 A5:2 F#5:2 D#5:2 B4:2',
    'C5:2 E5:2 A5:4 G5:2 E5:2 C5:2 A4:2',
    'B4:2 D#5:2 F#5:2 A5:2 B5:4 D#5:2 F#5:2',
]

# Chord voicings are pitch classes/spellings, not mere root labels. A separate
# bass note preserves inversions. These also seed chord-tone countermelodies.
CHORDS = {
    'Em9': ('E2', ['E4','G4','B4','D5','F#5']),
    'Cmaj9#11': ('C3', ['C4','E4','G4','B4','F#5']),
    'Gmaj9': ('G2', ['G3','B3','D4','F#4','A4']),
    'D6/F#': ('F#2', ['D4','F#4','A4','B4','E5']),
    'Am9': ('A2', ['A3','C4','E4','G4','B4']),
    'B7b9': ('B2', ['B3','D#4','F#4','A4','C5']),
    'Em/G': ('G2', ['E4','G4','B4','D5','F#5']),
    'Cmaj9': ('C3', ['C4','E4','G4','B4','D5']),
    'D9': ('D3', ['D4','F#4','A4','C5','E5']),
    'A13/C#': ('C#3', ['A3','C#4','E4','G4','F#5']),
    'G6/B': ('B2', ['G3','B3','D4','E4','A4']),
    'Am6': ('A2', ['A3','C4','E4','F#4','B4']),
    'D9/F#': ('F#2', ['D4','F#4','A4','C5','E5']),
    'F#halfdim7': ('F#2', ['F#3','A3','C4','E4','G4']),
}
MAIN_HARMONY = ['Em9','Cmaj9#11','Gmaj9','D6/F#','Am9','B7b9','Em/G','B7b9',
                'Em9','Cmaj9','D9','G6/B','Am9','B7b9','Em9','B7b9']

def midi(pitch):
    names = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    return 12*(int(pitch[-1])+1) + names[pitch[0]] + pitch[1:-1].count('#') - pitch[1:-1].count('b')

def pitch(number):
    return ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][number%12] + str(number//12-1)

def parse_bar(text):
    notes = [(p, int(d)) for p,d in (token.split(':') for token in text.split())]
    assert sum(d for _,d in notes) == 16, text
    return notes

def event(at, duration, note, instrument, velocity, effects=None):
    return dict(at=at, duration=duration, pitch=note, instrument=instrument,
                velocity=velocity, effects=effects or [])

def make_score(title, melodies, harmony, section_plan):
    channels = {c:[] for c in ['melody','counterline','bass','percussion']}
    measures = []
    for bar,(mel,chord,section) in enumerate(zip(melodies,harmony,section_plan)):
        at=bar*16
        bass,tones=CHORDS[chord]
        measures.append(dict(bar=bar+1,section=section,chord=chord,bass=bass,tones=tones))
        pos=0
        for i,(p,d) in enumerate(parse_bar(mel)):
            if p != 'R':
                fx = ['vibrato'] if d >= 4 else []
                if i == 0 and section in ('A2','climax') and bar%4 == 0: fx += ['scoop']
                vel=12 if pos in (0,6,8) else 10
                if section == 'bridge': vel-=2
                channels['melody'].append(event(at+pos,d,p,'bright_lead' if section=='climax' else 'singing_lead',vel,fx))
            pos+=d
        # Pulse 2 alternates moving broken harmony with independent answers.
        # It leaves breathing room under the lead and supplies missing 3rds/7ths.
        if section == 'bridge':
            pattern = [(0,4,tones[1]),(6,2,tones[3]),(10,4,tones[2]),(15,1,tones[4])]
        elif section in ('B','climax') and bar%2==1:
            pattern = [(0,2,tones[1]),(3,1,tones[2]),(6,2,tones[3]),(8,2,tones[4]),(11,1,tones[2]),(14,2,tones[1])]
        else:
            order=[0,2,1,3,2,4,1,2]
            pattern=[(2*i,1 if i%2 else 2,tones[t]) for i,t in enumerate(order)]
        for pos,d,p in pattern:
            channels['counterline'].append(event(at+pos,d,p,'soft_counter' if section=='bridge' else 'glass',7 if section=='bridge' else 8+(pos==6),[]))
        # Bass has root/fifth/third, syncopation, inversion and an approach into
        # the next harmony. Short rests articulate triangle without volume control.
        root=midi(bass)
        nextroot=midi(CHORDS[harmony[(bar+1)%len(harmony)]][0])
        third=(midi(tones[1])%12)+12*3
        while third-root>12: third-=12
        while third<36: third+=12
        approach=nextroot-1 if nextroot>=root else nextroot+1
        while approach<33: approach+=12
        while approach>55: approach-=12
        bassline=[(0,3,root),(4,2,root+7),(7,1,root+12),(8,3,third),(12,2,root+7),(15,1,approach)]
        if section=='climax' and bar%4==0:
            bassline=[(0,3,root),(4,1,root+12),(6,1,root+7),(8,2,third),(11,1,root+12),(12,2,root+7),(15,1,approach)]
        if bar%8==7:
            bassline=[(0,3,root),(4,3,root),(8,2,root+7),(11,1,third),(12,2,root),(15,1,approach)]
        if section=='bridge': bassline=[(0,6,root),(8,4,root+7),(14,1,approach)]
        if section=='intro' and bar<2: bassline=[(0,7,root),(8,6,root+7)]
        for pos,d,n in bassline:
            channels['bass'].append(event(at+pos,d,pitch(n),'triangle',12))
        # Noise kit: different decay, color, accents and ghost hits. No samples.
        hits=[]
        if section=='bridge':
            hits=[(0,'kick',12),(4,'hat',5),(8,'snare',9),(12,'hat',6),(15,'hat',4)]
        elif section=='intro' and bar<2:
            hits=[(0,'hat',5),(8,'hat',6),(14,'hat',4)]
        else:
            hits=[(0,'kick',14),(6,'kick',11),(8,'kick',13),(4,'snare',13),(12,'snare',14)]
            hits += [(p,'hat',7 if p%4==2 else 5) for p in (2,7,10,14)]
            if bar%4==2: hits += [(11,'snare',5),(15,'hat',5)]
            if bar%8==7: hits=[h for h in hits if h[0]<12]+[(12,'snare',11),(13,'snare',7),(14,'snare',12),(15,'snare',15)]
        for pos,kit,v in sorted(hits):
            channels['percussion'].append(event(at+pos,1,None,kit,v))
    return dict(format='nes-master-composer.score',version=1,title=title,author='NES Master Composer',
                time_unit='sixteenth_note',meter=[4,4],tempo_bpm=60_000_000/(16639*7*4),
                tuning_hz=440, bars=len(melodies),loop=dict(start=0,end=len(melodies)*16),
                instruments={
                    'singing_lead':dict(role='melody',timbre='pulse',duty_motion=[0.25,0.5],envelope='gentle_decay'),
                    'glass':dict(role='broken_harmony',timbre='pulse',duty_motion=[0.5,0.25,0.125],envelope='pluck'),
                    'soft_counter':dict(role='countermelody',timbre='pulse',duty_motion=[0.25],envelope='soft_decay'),
                    'bright_lead':dict(role='melody',timbre='pulse',duty_motion=[0.125,0.25,0.5,0.25],envelope='gentle_decay'),
                    'triangle':dict(role='bass',timbre='triangle',envelope='gated'),
                    'kick':dict(role='percussion',timbre='noise',envelope='fast_decay'),
                    'snare':dict(role='percussion',timbre='noise',envelope='medium_decay'),
                    'hat':dict(role='percussion',timbre='noise',envelope='very_fast_decay')},
                sections=measures,channels=channels)

def main():
    out=ROOT/'composition'
    out.mkdir(exist_ok=True)
    candidates=[
        ('lantern','Lantern Circuit',LANTERN[:8],MAIN_HARMONY[:8]),
        ('glass','Glasswork Sprint',GLASS,['Cmaj9#11','D9','Em9','B7b9']*2),
        ('tidal','Tidal Observatory',TIDAL,['Am6','D9/F#','Gmaj9','Em9','Am6','D9','Cmaj9','B7b9']),
    ]
    for name,title,mel,harm in candidates:
        data=make_score(title,mel,harm,['candidate']*8)
        (out/f'candidate_{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    intro=['E5:4 R:4 B4:2 D5:2 E5:2 R:2',
           'G5:4 R:4 E5:4 R:4',
           'F#5:4 A5:2 G5:2 F#5:4 D5:2 R:2',
           'R:8 B4:2 D#5:2 F#5:2 D#5:2']
    reprise=LANTERN[:8].copy()
    reprise[1]='G5:2 E5:2 B5:4 A5:2 G5:2 E5:2 D5:2'
    reprise[3]='E5:2 F#5:2 A5:4 G5:2 F#5:2 D5:2 R:2'
    # The reprise shortens its answer; the climax expands the original idea.
    climax=LANTERN.copy()
    climax[0]='E5:3 B4:1 D5:2 E5:2 G5:2 B5:2 E6:2 D6:2'
    climax[8]='E6:3 B5:1 D6:2 E6:2 B5:3 A5:1 G5:2 R:2'
    climax[14]='E6:4 B5:2 G5:2 E5:4 G5:2 B5:2'
    turn=['C6:4 B5:2 G5:2 E5:4 R:4',
          'A5:3 G5:1 E5:4 C5:4 B4:2 A4:2',
          'F#5:2 A5:2 C6:4 B5:2 A5:2 F#5:2 D#5:2',
          'B4:4 D#5:2 F#5:2 A5:2 F#5:2 D#5:4']
    mel=intro+LANTERN+BRIGHT+reprise+BRIDGE+climax+turn
    harm=['Em9','Cmaj9#11','D6/F#','B7b9']+MAIN_HARMONY+[
        'Gmaj9','Em9','Cmaj9','D9','G6/B','A13/C#','Em9','B7b9']+MAIN_HARMONY[:8]+[
        'Am6','D9/F#','Gmaj9','Em9','F#halfdim7','B7b9','Am9','B7b9']+MAIN_HARMONY+[
        'Cmaj9','Am9','B7b9','B7b9']
    sections=['intro']*4+['A']*16+['B']*8+['A2']*8+['bridge']*8+['climax']*16+['turnaround']*4
    assert len(mel)==len(harm)==len(sections)==64
    score=make_score('Lantern Circuit',mel,harm,sections)
    (out/'lantern_circuit.json').write_text(json.dumps(score,indent=2)+'\n')
    comparison=dict(criteria_weights=dict(memorability=30,phrasing=20,harmonic_direction=20,channel_fit=15,development=15),
        scoring='Composer judgement on a 1–5 scale; these are editorial scores, not listening-test results.',
        candidates=[
            dict(id='lantern',scores=[5,5,4,5,5],weighted_total=96,
                 rationale='Distinctive 3+1 pickup cell; space after the answer; D# dominant gives a strong return. Best balance of singing theme and room for a second voice.'),
            dict(id='glass',scores=[3,3,4,4,4],weighted_total=70,
                 rationale='Energetic wide chord leaps and extensions; near-continuous eighths obscure phrase breathing and compete with the arpeggio voice.'),
            dict(id='tidal',scores=[4,4,4,5,3],weighted_total=80,
                 rationale='Long lyrical arch and Dorian color; excellent channel economy, but less rhythmic identity and less contrast available for a later bridge.')],
        selected='lantern',before_final_nsf=True)
    (out/'theme_comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
    print('Authored three 8-bar candidates, compared them, and developed Lantern Circuit: 64 bars.')

if __name__=='__main__': main()
