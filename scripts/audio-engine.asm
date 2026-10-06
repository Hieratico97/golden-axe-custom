; 68000 YM2612 score. Dedicated FM 0..3 music, 4 Foley, 5 village birds.
; Official SEGA register protocol: busy wait, high frequency before low.
AudioAcquire:
    move.w #$100,$00A11100
AudioBusWait:
    btst #0,$00A11100
    bne.w AudioBusWait
    rts
FMWrite:
    btst #7,(a2)
    bne.w FMWrite
    move.b d0,(a2)
FMWriteDataWait:
    btst #7,(a2)
    bne.w FMWriteDataWait
    move.b d1,$1(a2)
    nop
    nop
    nop
    nop
    rts
MusicPort:
    lea $00A04000,a2
    move.w d5,d4
    cmpi.w #3,d4
    bcs.w MusicPortReturn
    lea $00A04002,a2
    subq.w #3,d4
MusicPortReturn:
    rts
MusicKeyOff:
    lea $00A04000,a2
    move.w d5,d1
    cmpi.w #3,d1
    bcs.w MusicKeyOffReady
    addq.w #1,d1
MusicKeyOffReady:
    moveq #$28,d0
    bra.w FMWrite
AudioInit:
    move.w sr,-(sp)
    ori.w #$700,sr
    bsr.w AudioAcquire
    ; Write while reset is RELEASED and the bus is owned. Writes made with
    ; reset asserted are discarded by the Genesis bus mapping. Then reset
    ; the CPU into DI / JR -3, so inherited mailbox writes cannot play songs.
    move.b #$F3,$00A00000
    move.b #$18,$00A00001
    move.b #$FD,$00A00002
    jsr (loc_3554).l
    lea $00A04000,a2
    moveq #$2B,d0
    moveq #0,d1
    bsr.w FMWrite
    moveq #$27,d0
    bsr.w FMWrite
    moveq #$22,d0
    moveq #8,d1
    bsr.w FMWrite
    moveq #0,d5
AudioPatchLoop:
    bsr.w MusicKeyOff
    bsr.w MusicPort
    move.w d5,d0
    lsl.w #2,d0
    lea (MusicPatchTable).l,a3
    movea.l (a3,d0.w),a3
    move.w (a3)+,d6
    subq.w #1,d6
AudioPatchRegisters:
    moveq #0,d0
    moveq #0,d1
    move.b (a3)+,d0
    move.b (a3)+,d1
    bsr.w FMWrite
    dbf d6,AudioPatchRegisters
    addq.w #1,d5
    cmpi.w #6,d5
    bcs.w AudioPatchLoop
    move.b #$9F,$00C00011
    move.b #$BF,$00C00011
    move.b #$DF,$00C00011
    move.b #$FF,$00C00011
    move.w #$100,$00A11200
    move.w #0,$00A11100
    move.w #-1,$FFFFF300.w
    move.w #180,$FFFFF312.w
    move.w (sp)+,sr
    rts
AudioSilence:
    move.w sr,-(sp)
    ori.w #$700,sr
    bsr.w AudioAcquire
    moveq #5,d5
AudioSilenceLoop:
    bsr.w MusicKeyOff
    dbf d5,AudioSilenceLoop
    move.b #$DF,$00C00011
    move.b #$FF,$00C00011
    clr.w $FFFFF244.w
    clr.w $FFFFF302.w
    clr.l $FFFFF318.w
    move.l #$7F7F7F7F,$FFFFF31C.w
    clr.w $FFFFF314.w
    move.w #0,$00A11100
    move.w (sp)+,sr
    rts
AudioTick:
    tst.b $FFFFC175.w
    bne.w AudioReturn
    move.w sr,-(sp)
    ori.w #$700,sr
    bsr.w AudioAcquire
    addq.w #1,$FFFFF30E.w
    moveq #1,d0
    tst.w $FFFFF200.w
    bne.w AudioBossScene
    moveq #0,d0
AudioBossScene:
    tst.w $FFFFF220.w
    beq.w AudioVictoryScene
    moveq #2,d0
    tst.w $FFFFF284.w
    beq.w AudioVictoryScene
    moveq #4,d0
AudioVictoryScene:
    tst.w $FFFFF10A.w
    beq.w AudioSceneReady
    moveq #3,d0
AudioSceneReady:
    cmp.w $FFFFF300.w,d0
    beq.w AudioSceneCurrent
    move.w d0,$FFFFF300.w
    lsl.w #2,d0
    lea (MusicSceneTable).l,a3
    movea.l (a3,d0.w),a3
    move.w (a3)+,$FFFFF306.w
    move.w (a3)+,$FFFFF30C.w
    move.l (a3)+,$FFFFF308.w
    clr.w $FFFFF304.w
    clr.w $FFFFF302.w
    moveq #3,d5
AudioSceneOff:
    bsr.w MusicKeyOff
    dbf d5,AudioSceneOff
    clr.l $FFFFF318.w
    move.l #$7F7F7F7F,$FFFFF31C.w
    ; Change the four music timbres at scene boundaries, preserving FX/ambient.
    move.w $FFFFF300.w,d0
    lsl.w #2,d0
    lea (MusicScenePatchTable).l,a3
    movea.l (a3,d0.w),a3
    moveq #0,d5
AudioScenePatchLoop:
    movea.l (a3)+,a6
    bsr.w MusicPort
    move.w (a6)+,d6
    subq.w #1,d6
AudioScenePatchRegisters:
    moveq #0,d0
    moveq #0,d1
    move.b (a6)+,d0
    move.b (a6)+,d1
    bsr.w FMWrite
    dbf d6,AudioScenePatchRegisters
    addq.w #1,d5
    cmpi.w #4,d5
    bcs.w AudioScenePatchLoop
AudioSceneCurrent:
    lea $FFFFF318.w,a4
    moveq #0,d5
AudioGates:
    tst.b (a4)
    beq.w AudioGateNext
    subq.b #1,(a4)
    bne.w AudioGateNext
    bsr.w MusicKeyOff
AudioGateNext:
    addq.l #1,a4
    addq.w #1,d5
    cmpi.w #4,d5
    bcs.w AudioGates
    bsr.w MusicDucking
    bsr.w VillageAmbient
    tst.w $FFFFF302.w
    beq.w AudioPlayStep
    subq.w #1,$FFFFF302.w
    bra.w AudioRelease
AudioPlayStep:
    move.w $FFFFF306.w,$FFFFF302.w
    subq.w #1,$FFFFF302.w
    moveq #0,d0
    move.w $FFFFF304.w,d0
    mulu.w #16,d0
    movea.l $FFFFF308.w,a3
    adda.l d0,a3
    lea $FFFFF318.w,a4
    moveq #0,d5
AudioVoice:
    moveq #0,d2
    move.b (a3)+,d2
    lsl.w #8,d2
    move.b (a3)+,d2
    moveq #0,d3
    move.b (a3)+,d3
    moveq #0,d6
    move.b (a3)+,d6
    cmpi.w #$FFFF,d2
    beq.w AudioVoiceNext
    bsr.w MusicKeyOff
    clr.b (a4)
    tst.w d2
    beq.w AudioVoiceNext
    lea $FFFFF31C.w,a6
    move.b d3,(a6,d5.w)
    add.w $FFFFF320.w,d3
    cmpi.w #127,d3
    bls.w AudioVoiceLevelReady
    moveq #127,d3
AudioVoiceLevelReady:
    bsr.w MusicPort
    move.w d4,d0
    addi.w #$A4,d0
    move.w d2,d1
    lsr.w #8,d1
    bsr.w FMWrite
    move.w d4,d0
    addi.w #$A0,d0
    move.w d2,d1
    bsr.w FMWrite
    move.w d4,d0
    addi.w #$48,d0
    move.w d3,d1
    bsr.w FMWrite
    move.w d4,d0
    addi.w #$4C,d0
    bsr.w FMWrite
    lea $00A04000,a2
    move.w d5,d1
    cmpi.w #3,d1
    bcs.w AudioVoiceKey
    addq.w #1,d1
AudioVoiceKey:
    ori.b #$F0,d1
    moveq #$28,d0
    bsr.w FMWrite
    move.b d6,(a4)
AudioVoiceNext:
    addq.l #1,a4
    addq.w #1,d5
    cmpi.w #4,d5
    bcs.w AudioVoice
    addq.w #1,$FFFFF310.w
    addq.w #1,$FFFFF304.w
    move.w $FFFFF304.w,d0
    cmp.w $FFFFF30C.w,d0
    bcs.w AudioRelease
    clr.w $FFFFF304.w
AudioRelease:
    move.w #0,$00A11100
    move.w (sp)+,sr
AudioReturn:
    rts

; Cached carrier levels F31C..1F; attack/release envelope F320, 0..12 TL.
; Jutsu/cinematic sounds retain their separate FM/PSG channels and full level.
MusicDucking:
    moveq #0,d6
    tst.w $FFFFF244.w
    beq.w MusicDuckTarget
    move.w $FFFFF246.w,d0
    lea (SfxPriorities).l,a3
    cmpi.b #3,(a3,d0.w)
    bcs.w MusicDuckTarget
    moveq #12,d6
MusicDuckTarget:
    move.w $FFFFF320.w,d3
    cmp.w d6,d3
    beq.w MusicDuckReturn
    bhi.w MusicDuckRelease
    addq.w #4,d3
    bra.w MusicDuckWrite
MusicDuckRelease:
    subq.w #1,d3
MusicDuckWrite:
    move.w d3,$FFFFF320.w
    lea $FFFFF31C.w,a3
    moveq #0,d5
MusicDuckChannel:
    bsr.w MusicPort
    moveq #0,d1
    move.b (a3)+,d1
    add.w d3,d1
    cmpi.w #127,d1
    bls.w MusicDuckLevel
    moveq #127,d1
MusicDuckLevel:
    move.w d4,d0
    addi.w #$48,d0
    bsr.w FMWrite
    move.w d4,d0
    addi.w #$4C,d0
    bsr.w FMWrite
    addq.w #1,d5
    cmpi.w #4,d5
    bcs.w MusicDuckChannel
MusicDuckReturn:
    rts
VillageAmbient:
    tst.w $FFFFF314.w
    beq.w VillageBirdWait
    subq.w #1,$FFFFF314.w
    bne.w VillageBirdPitch
    moveq #5,d5
    bsr.w MusicKeyOff
    rts
VillageBirdPitch:
    lea $00A04002,a2
    moveq #$A6,d0
    moveq #$32,d1
    bsr.w FMWrite
    moveq #$A2,d0
    move.w $FFFFF314.w,d1
    lsl.w #5,d1
    addi.w #$84,d1
    bsr.w FMWrite
    rts
VillageBirdWait:
    cmpi.w #1,$FFFFF300.w
    bne.w VillageBirdReturn
    subq.w #1,$FFFFF312.w
    bne.w VillageBirdReturn
    move.w #300,$FFFFF312.w
    move.w #12,$FFFFF314.w
    addq.w #1,$FFFFF316.w
    lea $00A04002,a2
    moveq #$A6,d0
    moveq #$32,d1
    bsr.w FMWrite
    moveq #$A2,d0
    moveq #$64,d1
    bsr.w FMWrite
    lea $00A04000,a2
    moveq #$28,d0
    move.w #$F6,d1
    bsr.w FMWrite
VillageBirdReturn:
    rts
