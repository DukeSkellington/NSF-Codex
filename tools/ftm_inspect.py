#!/usr/bin/env python3
"""Inspect the frame-sampled FamiTracker 0.3.7 module made by NSF Importer."""
from collections import Counter
from pathlib import Path
import json
import struct

def inspect(path):
    data=Path(path).read_bytes()
    assert data[:18]==b'FamiTracker Module'
    version=struct.unpack_from('<I',data,18)[0]
    assert version==0x420
    pos=22
    blocks={}
    while data[pos:pos+3]!=b'END':
        name=data[pos:pos+16].split(b'\0')[0].decode()
        ver,size=struct.unpack_from('<II',data,pos+16)
        pos+=24
        assert pos+size<=len(data)
        blocks[name]=(ver,data[pos:pos+size]); pos+=size
    assert pos+3==len(data)
    params=blocks['PARAMS'][1]
    channels=struct.unpack_from('<I',params,1)[0]
    header=blocks['HEADER'][1]
    assert header[0]==0  # one subsong
    p=header.index(0,1)+1
    effect_columns={}
    for c in range(channels):
        kind,count=header[p:p+2]; p+=2
        effect_columns[c]=count+1
    frames,speed,tempo,length=struct.unpack_from('<IIII',blocks['FRAMES'][1])
    pattern_data=blocks['PATTERNS'][1]
    counts=Counter(); pitched=Counter(); max_frame=0; p=0
    while p<len(pattern_data):
        track,c,pattern,items=struct.unpack_from('<IIII',pattern_data,p); p+=16
        assert track==0 and c<channels and pattern<frames
        for _ in range(items):
            row,note,octave,instrument,volume=struct.unpack_from('<IBBBB',pattern_data,p)
            p+=8+effect_columns[c]*2
            assert row<length
            counts[c]+=1
            if 1<=note<=12: pitched[c]+=1
            max_frame=max(max_frame,pattern*length+row)
    assert p==len(pattern_data)
    return dict(format_version=hex(version),channels=channels,order_count=frames,
                rows_per_pattern=length,speed=speed,tempo=tempo,
                populated_cells_by_channel=dict(counts),note_cells_by_channel=dict(pitched),
                last_populated_frame=max_frame)

if __name__=='__main__':
    import sys
    print(json.dumps(inspect(sys.argv[1]),indent=2))
