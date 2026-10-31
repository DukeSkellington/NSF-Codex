"""Behavioral checks: execute the assembled driver on an independent 6502 core."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import unittest
import wave

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
# Local onboarding installation; normal users install requirements-dev.txt.
if Path('/workspace/tools/python').exists(): sys.path.insert(0,'/workspace/tools/python')
from py65.devices.mpu6502 import MPU
from build import CHANNELS, FLAGS, INSTRUMENTS, midi, rows_for, validate
from ftm_inspect import inspect as inspect_ftm

class Bus(list):
    def __init__(self,payload):
        super().__init__([0]*65536)
        self[0x8000:0x8000+len(payload)]=payload
        self.writes=[]
        self.bad_writes=[]
        self.apu={}
    def __setitem__(self,key,value):
        if isinstance(key,int) and hasattr(self,'writes'):
            if 0x4000<=key<=0x4017:
                self.writes.append((key,value))
                self.apu[key]=value
            elif not (0<=key<0x100 or 0x100<=key<0x300):
                self.bad_writes.append((key,value))
        super().__setitem__(key,value)

class Driver:
    def __init__(self,name='lantern_circuit'):
        self.nsf=(ROOT/'deliverables'/f'{name}.nsf').read_bytes()
        self.meta=json.loads((ROOT/'build'/name/'metadata.json').read_text())
        self.labels=self.meta['labels']
        self.bus=Bus(self.nsf[128:])
        self.cpu=MPU(memory=self.bus)
        self.max_cycles=0
        self.max_stack=255
        self.call(self.meta['init_address'])
    def call(self,address):
        c=self.cpu
        c.sp=255
        # RTS returns to a sentinel just below loaded ROM.
        c.stPushWord(0x7ffe)
        c.pc=address
        before=c.processorCycles
        for _ in range(20000):
            if c.pc==0x7fff: break
            self.max_stack=min(self.max_stack,c.sp)
            c.step()
        else: raise AssertionError('Driver failed to return')
        assert c.sp==255, 'Unbalanced stack'
        cycles=c.processorCycles-before
        self.max_cycles=max(self.max_cycles,cycles)
        return cycles
    def frame(self):
        self.bus.writes=[]
        return self.call(self.meta['play_address'])
    def state(self):
        return bytes(self.bus[:256])+bytes(self.bus[512:544]),dict(self.bus.apu)

class MusicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.score=json.loads((ROOT/'composition/lantern_circuit.json').read_text())
        cls.d=Driver()
        cls.frames=[]
        cls.periods=[]
        for _ in range(cls.d.meta['frames']*2):
            cls.d.frame()
            cls.frames.append((tuple(cls.d.bus.writes),cls.d.state()))
            cls.periods.append(tuple((cls.d.bus.apu.get(0x4002+4*c,0)|((cls.d.bus.apu.get(0x4003+4*c,0)&7)<<8)) for c in range(3)))

    def test_header_all_four_files(self):
        for path in sorted((ROOT/'deliverables').glob('*.nsf')):
            with self.subTest(path=path.name):
                data=path.read_bytes(); h=data[:128]
                self.assertEqual(h[:8],b'NESM\x1a\x01\x01\x01')
                load,init,play=struct.unpack_from('<HHH',h,8)
                self.assertEqual(load,0x8000)
                self.assertTrue(all(load<=a<load+len(data)-128 for a in (init,play)))
                self.assertLessEqual(len(data)-128,32768)
                self.assertEqual(struct.unpack_from('<H',h,110)[0],16639)
                self.assertEqual(h[112:120],bytes(8))
                self.assertEqual(h[122:128],bytes(6))
                for offset in (14,46,78): self.assertIn(0,h[offset:offset+32])

    def test_portable_scores_and_comparison(self):
        for path in (ROOT/'composition').glob('*.json'):
            if path.name!='theme_comparison.json': validate(json.loads(path.read_text()))
        c=json.loads((ROOT/'composition/theme_comparison.json').read_text())
        self.assertEqual(len(c['candidates']),3)
        for item in c['candidates']:
            total=sum(w*s/5 for w,s in zip(c['criteria_weights'].values(),item['scores']))
            self.assertEqual(total,item['weighted_total'])
        self.assertEqual(max(c['candidates'],key=lambda c:c['weighted_total'])['id'],c['selected'])
        self.assertEqual(self.score['bars'],64)
        self.assertGreaterEqual(len({m['section'] for m in self.score['sections']}),7)

    def test_6502_full_two_loops_return_memory_and_budget(self):
        self.assertEqual(len(self.frames),14336)
        self.assertFalse(self.d.bus.bad_writes)
        self.assertLess(self.d.max_cycles,8000) # NTSC frame: about 29,780 cycles
        self.assertGreaterEqual(self.d.max_stack,0xe0)

    def test_exact_loop_apu_events(self):
        n=self.d.meta['frames']
        # No initialization at loop. Each channel's first attack is explicit;
        # all frame-level writes must repeat, including noise and vibrato.
        self.assertEqual([w for w,s in self.frames[:n]],[w for w,s in self.frames[n:]])

    def test_row_stream_does_not_drift(self):
        d=Driver()
        rows=rows_for(self.score)
        for i in range(d.meta['frames']+1):
            if i%7==0:
                expected=(i//7)%len(rows)
                d.frame()
                ptr=d.bus[d.labels['stream_ptr']]|d.bus[d.labels['stream_ptr']+1]<<8
                self.assertEqual(ptr,d.labels['song_data']+(expected+1)*16)
            else: d.frame()

    def test_note_attacks_match_score_pitch_and_volume(self):
        for c,channel in enumerate(CHANNELS[:3]):
            for e in self.score['channels'][channel]:
                frame=e['at']*7
                n=midi(e['pitch'])+(12 if c==2 else 0)
                expected=round(1789773/(16*440*2**((n-69)/12))-1)
                if 'scoop' in e['effects']: expected+=16
                self.assertEqual(self.periods[frame][c],expected,(channel,e))
                if c<2:
                    vol=dict(self.frames[frame][1][1])[0x4000+4*c]&15
                    attenuation=1 if e['instrument']=='soft_counter' else 0
                    self.assertEqual(vol,e['velocity']-attenuation)

    def test_pitch_accuracy_ntsc(self):
        worst=0
        for c,channel in enumerate(CHANNELS[:3]):
            for e in self.score['channels'][channel]:
                hz=440*2**((midi(e['pitch'])-69)/12)
                divider=32 if c==2 else 16
                period=round(1789773/(divider*hz)-1)
                cents=abs(1200*math.log2((1789773/(divider*(period+1)))/hz))
                worst=max(worst,cents)
        self.assertLess(worst,20)

    def test_no_dpcm_irq_or_mapper_writes(self):
        self.assertEqual(self.d.bus.apu[0x4015],15)
        self.assertEqual(self.d.bus.apu[0x4010],0)
        self.assertEqual(self.d.bus.apu[0x4011],0)
        self.assertEqual(self.d.bus.apu[0x4017],64)
        for writes,state in self.frames:
            self.assertFalse(any(0x4010<=addr<=0x4017 for addr,value in writes))

    def test_effects_are_audibly_nonconstant_register_behaviors(self):
        # Register evidence only, not a claim to human audition.
        e=next(e for e in self.score['channels']['melody'] if 'scoop' in e['effects'])
        start=e['at']*7
        self.assertEqual(self.periods[start][0]-self.periods[start+7][0],14)
        e=next(e for e in self.score['channels']['melody'] if e['duration']>=4 and e['effects']==['vibrato'])
        start=e['at']*7
        self.assertGreater(len({self.periods[start+i][0] for i in range(10,24)}),2)
        duties={self.frames[start+i][1][1][0x4000]>>6 for i in range(8)}
        self.assertGreater(len(duties),1)
        hats=[e['velocity'] for e in self.score['channels']['percussion'] if e['instrument']=='hat']
        self.assertGreater(len(set(hats)),1)

    def test_pulse_high_not_retriggered_every_frame(self):
        high_writes=sum(addr==0x4003 for w,s in self.frames for addr,val in w)
        self.assertLess(high_writes,len(self.frames)//2)

    def test_candidates_execute_two_loops(self):
        for name in ('candidate_lantern','candidate_glass','candidate_tidal'):
            with self.subTest(candidate=name):
                d=Driver(name)
                hashes=[]
                for loop in range(2):
                    digest=hashlib.sha256()
                    for _ in range(d.meta['frames']):
                        d.frame()
                        digest.update(bytes(v for pair in d.bus.writes for v in (pair[0]&255,pair[0]>>8,pair[1])))
                    hashes.append(digest.digest())
                self.assertEqual(hashes[0],hashes[1])
                self.assertFalse(d.bus.bad_writes)

    def test_reinit_is_deterministic(self):
        d=Driver()
        first=[]
        for _ in range(64): d.frame(); first.append(tuple(d.bus.writes))
        d.call(d.meta['init_address'])
        second=[]
        for _ in range(64): d.frame(); second.append(tuple(d.bus.writes))
        self.assertEqual(first,second)

    def test_dirty_ram_and_decimal_flag(self):
        d=Driver()
        for i in range(0x800): d.bus[i]=(i*37+19)&255
        d.cpu.a=0; d.cpu.x=0; d.cpu.p|=8
        d.call(d.meta['init_address'])
        d.cpu.p|=8
        d.frame()
        self.assertEqual(tuple(d.bus.writes),self.frames[0][0])

    def test_rest_tie_short_gate_and_sustained_envelope(self):
        d=Driver()
        start=d.labels['song_data']
        # Inject a 9-row sustained E5 with explicit short gate, then rest.
        for row in range(10):
            d.bus[start+row*16:start+(row+1)*16]=[0]*16
            d.bus[start+row*16:start+row*16+4]=([76,0,12,32] if row==0 else [1,0,0,0])
        d.bus[start+9*16]=0
        for frame in range(70):
            d.frame()
            volume=d.bus.apu[0x4000]&15
            self.assertEqual(volume==0,frame>=5)
        # Long ungated sustain exercises envelope saturation, not array overrun.
        d=Driver()
        for row in range(12):
            d.bus[start+row*16:start+(row+1)*16]=[0]*16
            d.bus[start+row*16:start+row*16+4]=([76,0,12,64] if row==0 else [1,0,0,0])
        for frame in range(84): d.frame()
        self.assertEqual(d.bus.apu[0x4000]&15,8)
        self.assertFalse(any(addr>=0x8000 for addr,val in d.bus.bad_writes))

    def test_actual_brad_smith_importer_cli_output(self):
        info=inspect_ftm(ROOT/'deliverables/lantern_circuit_import.ftm')
        self.assertEqual(info['channels'],5)
        self.assertEqual(info['order_count'],29)
        self.assertEqual(info['speed'],1)
        for c in range(4): self.assertGreater(info['note_cells_by_channel'][c],50)
        self.assertNotIn(4,info['note_cells_by_channel'])

    def test_independent_libgme_wav(self):
        # Actual audio emitted by a second CPU+APU implementation.
        for path in sorted((ROOT/'deliverables').glob('*.wav')):
            with self.subTest(wav=path.name),wave.open(str(path),'rb') as wav:
                self.assertEqual(wav.getframerate(),44100)
                self.assertEqual(wav.getsampwidth(),2)
                self.assertEqual(wav.getnchannels(),2)
                meta=json.loads((ROOT/'build'/path.stem/'metadata.json').read_text())
                self.assertEqual(wav.getnframes(),round(meta['loop_seconds']*44100))
                import array
                data=array.array('h',wav.readframes(wav.getnframes()))
                if sys.byteorder!='little': data.byteswap()
                self.assertGreater(max(abs(x) for x in data),1000)
                self.assertLess(max(abs(x) for x in data),32767)
                # No silent half-second windows anywhere, including the bridge.
                for i in range(0,len(data)-44100,44100):
                    self.assertGreater(sum(x*x for x in data[i:i+44100])/44100,100)
        self.assertEqual(len(list((ROOT/'deliverables').glob('*.wav'))),4)

if __name__=='__main__': unittest.main(verbosity=2)
