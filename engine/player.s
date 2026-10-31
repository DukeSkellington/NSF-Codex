; NES Master Composer: original 2A03 driver, ca65 syntax.
; One play call per NTSC frame. All state is private ZP / $0200 RAM.
; Record per voice: MIDI pitch (0 rest, 1 tie), instrument, volume, flags.
; Noise uses pitch = period index + 2. Flags: $80 scoop, $40 vibrato,
; $20 short gate. No DMC, IRQ, mapper, banking, or undocumented opcodes.
.export init, play, stream_ptr, frames_left, ages, active, base_lo, base_hi
.export song_data, song_end, row_count
.segment "ZEROPAGE"
stream_ptr: .res 2
frames_left: .res 1
tmp: .res 1
duty_age: .res 1
timer_lo: .res 1
timer_hi: .res 1
reg_offset: .res 1
row_count: .res 2
.segment "BSS"
instruments: .res 4
volumes: .res 4
effects: .res 4
ages: .res 4
active: .res 4
base_lo: .res 4
base_hi: .res 4
last_hi: .res 4
phases: .res 4
.segment "CODE"
init:
    cld
    lda #0
    ldx #35
@clear:
    sta instruments,x
    dex
    bpl @clear
    sta frames_left
    sta row_count
    sta row_count+1
    sta $4015
    sta $4010
    sta $4011
    sta $4012
    sta $4013
    lda #$40
    sta $4017
    lda #$08
    sta $4001
    sta $4005
    lda #$30
    sta $4000
    sta $4004
    sta $400c
    lda #$80
    sta $4008
    lda #$0f
    sta $4015
    lda #<song_data
    sta stream_ptr
    lda #>song_data
    sta stream_ptr+1
    rts

play:
    cld
    lda frames_left
    bne @render
    jsr read_row
    lda #FRAMES_PER_ROW
    sta frames_left
@render:
    dec frames_left
    ldx #0
@voice:
    jsr render_voice
    inc phases,x
    lda ages,x
    cmp #63
    bcs @next
    inc ages,x
@next:
    inx
    cpx #4
    bne @voice
    rts

read_row:
    lda stream_ptr+1
    cmp #>song_end
    bne @read
    lda stream_ptr
    cmp #<song_end
    bne @read
    lda #<song_data
    sta stream_ptr
    lda #>song_data
    sta stream_ptr+1
    lda #0
    sta row_count
    sta row_count+1
@read:
    ldy #0
    ldx #0
@channel:
    lda (stream_ptr),y
    cmp #1
    beq @skip
    cmp #0
    beq @rest
    sta tmp
    lda #1
    sta active,x
    lda #0
    sta ages,x
    sta phases,x
    lda #$ff
    sta last_hi,x
    cpx #3
    beq @noise
    sty reg_offset
    ldy tmp
    lda periods_lo,y
    sta base_lo,x
    lda periods_hi,y
    sta base_hi,x
    ldy reg_offset
    jmp @params
@noise:
    lda tmp
    sec
    sbc #2
    sta base_lo,x
    jmp @params
@rest:
    lda #0
    sta active,x
@params:
    iny
    lda (stream_ptr),y
    sta instruments,x
    iny
    lda (stream_ptr),y
    sta volumes,x
    iny
    lda (stream_ptr),y
    sta effects,x
    iny
    jmp @next
@skip:
    iny
    iny
    iny
    iny
@next:
    inx
    cpx #4
    bne @channel
    clc
    lda stream_ptr
    adc #16
    sta stream_ptr
    bcc @counter
    inc stream_ptr+1
@counter:
    inc row_count
    bne @done
    inc row_count+1
@done:
    rts

render_voice:
    txa
    asl
    asl
    sta reg_offset
    lda active,x
    bne @active
    jmp mute_voice
@active:
    lda effects,x
    and #$20
    beq @sustain
    lda ages,x
    cmp #5
    bcc @sustain
    jmp mute_voice
@sustain:
    cpx #3
    bne @tonal
    jmp render_noise
@tonal:
    lda base_lo,x
    sta timer_lo
    lda base_hi,x
    sta timer_hi
    ; A positive timer offset starts below pitch, landing within 8 frames.
    lda effects,x
    bpl @vibrato
    lda ages,x
    cmp #8
    bcs @vibrato
    asl
    eor #$ff
    clc
    adc #17
    jmp @offset
@vibrato:
    lda effects,x
    and #$40
    beq @write
    lda ages,x
    cmp #10
    bcc @write
    lda phases,x
    and #7
    tay
    lda vibrato,y
@offset:
    sta tmp
    clc
    adc timer_lo
    sta timer_lo
    lda tmp
    bmi @negative
    lda #0
    beq @add_high
@negative:
    lda #$ff
@add_high:
    adc timer_hi
    sta timer_hi
@write:
    cpx #2
    beq render_triangle
    jsr envelope
    sta tmp
    lda ages,x
    lsr
    cmp #8
    bcc @duty_age
    lda #7
@duty_age:
    sta duty_age
    lda instruments,x
    asl
    asl
    asl
    ora duty_age
    tay
    lda duties,y
    ora #$30
    ora tmp
    ldy reg_offset
    sta $4000,y
    lda timer_lo
    sta $4002,y
    jmp write_pulse_high

mute_voice:
    cpx #2
    beq @tri
    cpx #3
    beq @noise
    ldy reg_offset
    lda #$30
    sta $4000,y
    rts
@tri:
    lda #$80
    sta $4008
    rts
@noise:
    lda #$30
    sta $400c
    rts

render_triangle:
    lda #$ff
    sta $4008
    lda timer_lo
    sta $400a
    lda timer_hi
    cmp last_hi,x
    beq @done
    sta last_hi,x
    ora #$f8
    sta $400b
@done:
    rts

render_noise:
    jsr envelope
    ora #$30
    sta $400c
    lda base_lo,x
    ; Kick falls from a brighter noise period to a low thud.
    ldy instruments,x
    cpy #4
    bne @period
    ldy ages,x
    cpy #2
    bcs @period
    sec
    sbc #3
@period:
    sta $400e
    lda last_hi,x
    cmp #$ff
    bne @done
    lda #0
    sta last_hi,x
    lda #$f8
    sta $400f
@done:
    rts

envelope:
    lda ages,x
    lsr
    cmp #16
    bcc @age
    lda #15
@age:
    sta tmp
    lda instruments,x
    asl
    asl
    asl
    asl
    ora tmp
    tay
    lda volumes,x
    sec
    sbc envelopes,y
    bcs @done
    lda #0
@done:
    rts

write_pulse_high:
    lda timer_hi
    cmp last_hi,x
    beq @done
    sta last_hi,x
    ora #$f8
    sta $4003,y
@done:
    rts

.segment "RODATA"
vibrato: .byte 0,1,2,1,0,$ff,$fe,$ff
; Duty: lead, glass arpeggio, soft counterline, bright lead, kick/snare/hat.
duties:
    .byte $40,$80,$80,$80,$80,$80,$80,$80
    .byte $80,$40,$40,$00,$00,$00,$00,$00
    .byte $40,$40,$40,$40,$40,$40,$40,$40
    .byte $00,$40,$80,$80,$40,$40,$40,$40
envelopes:
    .byte 0,0,1,1,2,2,2,2,3,3,3,3,4,4,4,4
    .byte 0,2,4,5,6,7,8,9,10,11,12,13,14,15,15,15
    .byte 1,1,1,2,2,2,3,3,3,3,4,4,4,4,5,5
    .byte 0,0,1,1,1,2,2,3,3,3,4,4,4,4,5,5
    .byte 0,3,7,11,15,15,15,15,15,15,15,15,15,15,15,15
    .byte 0,2,5,8,11,14,15,15,15,15,15,15,15,15,15,15
    .byte 0,6,12,15,15,15,15,15,15,15,15,15,15,15,15,15
.include "score.inc"
