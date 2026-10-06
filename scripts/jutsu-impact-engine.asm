; F3E0 rumble life, F3E2 display offset, F3E4 scene flash, F3E6 technique,
; F3E8 contacts, F3EA absorbed shots, F3EC boss flanks, F3EE wall life,
; F3F0 wall X, F3F2 lane, F3F4 fire AOE, F3F6 dash pixels,
; F3F8 water pushes, F3FA wall blocks, F3FC boss extra hits, F3FE dog binds.
JutsuFeedbackTick:
    bsr.w JutsuDispelFire
    clr.w $FFFFF3E2.w
    tst.w $FFFFF3E4.w
    beq.w JutsuShakeTick
    subq.w #1,$FFFFF3E4.w
JutsuShakeTick:
    tst.w $FFFFF3E0.w
    beq.w JutsuWallTick
    subq.w #1,$FFFFF3E0.w
    beq.w JutsuWallTick
    move.w $FFFFF3E0.w,d0
    andi.w #3,d0
    add.w d0,d0
    lea JutsuShakeOffsets(pc),a1
    move.w (a1,d0.w),$FFFFF3E2.w
JutsuWallTick:
    tst.w $FFFFF150.w
    bne.w JutsuFeedbackReturn
    tst.w $FFFFF3EE.w
    beq.w JutsuFeedbackReturn
    subq.w #1,$FFFFF3EE.w
    tst.w $FFFFF160.w
    beq.w JutsuWallCollision
    cmpi.w #54,$FFFFF160.w
    bhi.w JutsuFeedbackReturn
JutsuWallCollision:
    bsr.w EarthBlock
JutsuFeedbackReturn:
    rts
JutsuShakeOffsets: dc.w -3,3,-2,2

; A released elemental technique tears through hostile fire where its
; visible field overlaps. Kamui and Doton keep their own absorb/block rules.
; F368 counts real fire counters, F36A holds the short release accent.
JutsuDispelFire:
    tst.w $FFFFF36A.w
    beq.s JutsuDispelTimerReady
    subq.w #1,$FFFFF36A.w
JutsuDispelTimerReady:
    cmpi.w #56,$FFFFF160.w
    bhi.w JutsuDispelReturn
    cmpi.w #16,$FFFFF160.w
    bcs.w JutsuDispelReturn
    cmpi.w #1,$FFFFF164.w
    beq.w JutsuDispelReturn
    cmpi.w #5,$FFFFF164.w
    bcc.w JutsuDispelReturn
    tst.w $FFFFF22A.w
    beq.s JutsuDispelSecond
    cmpi.w #1,$FFFFF232.w
    beq.s JutsuDispelSecond
    move.w $FFFFF22C.w,d0
    move.w $FFFFF22E.w,d1
    bsr.s JutsuDispelOverlap
    tst.w d0
    beq.s JutsuDispelSecond
    clr.w $FFFFF22A.w
    bsr.w JutsuDispelAccent
JutsuDispelSecond:
    tst.w $FFFFF2F4.w
    beq.s JutsuDispelReturn
    move.w $FFFFF2F6.w,d0
    move.w $FFFFF2F8.w,d1
    bsr.s JutsuDispelOverlap
    tst.w d0
    beq.s JutsuDispelReturn
    clr.w $FFFFF2F4.w
    bsr.w JutsuDispelAccent
JutsuDispelReturn:
    rts
JutsuDispelOverlap:
    sub.w $FFFFF16C.w,d1
    bpl.s JutsuDispelLane
    neg.w d1
JutsuDispelLane:
    cmpi.w #40,d1
    bhi.s JutsuDispelMiss
    add.w $FFFFC210.w,d0
    sub.w $FFFFF168.w,d0
    bpl.s JutsuDispelDistance
    neg.w d0
JutsuDispelDistance:
    cmpi.w #80,d0
    bhi.s JutsuDispelMiss
    moveq #1,d0
    rts
JutsuDispelMiss:
    moveq #0,d0
    rts
JutsuDispelAccent:
    addq.w #1,$FFFFF368.w
    move.w #6,$FFFFF36A.w
    move.w #4,$FFFFF3E4.w
    move.w #8,$FFFFF3E0.w
    move.w $FFFFF164.w,d0
    addi.w #16,d0
    bsr.w SfxStart
    rts

JutsuReleaseAccent:
    movem.l d0-d1/a1,-(sp)
    move.w $FFFFF164.w,d0
    add.w d0,d0
    lea JutsuReleaseRumble(pc),a1
    move.w (a1,d0.w),$FFFFF3E0.w
    cmpi.w #8,d0
    beq.w JutsuReleaseAccentDone
    cmpi.w #12,d0
    beq.w JutsuReleaseAccentDone
    move.w #4,$FFFFF3E4.w
JutsuReleaseAccentDone:
    movem.l (sp)+,d0-d1/a1
    rts
JutsuReleaseRumble: dc.w 8,10,7,9,6,10,6
JutsuAnimationPhrases:
    dc.b 0,1,2,1,2,3
    dc.b 0,1,2,3,2,3
    dc.b 0,1,2,1,2,3
    dc.b 0,1,1,2,2,3
    dc.b 0,1,2,3,2,3
    dc.b 0,1,2,2,1,1
    dc.b 0,1,2,3,2,3
    even

JutsuMechanicsBegin:
    clr.w $FFFFF3EE.w
    cmpi.w #5,$FFFFF164.w
    bne.w JutsuFeedbackReturn
    move.w #150,$FFFFF3EE.w
    move.w $FFFFF168.w,$FFFFF3F0.w
    move.w $FFFFF16C.w,$FFFFF3F2.w
    rts

JutsuAbsorbShots:
    cmpi.w #1,$FFFFF164.w
    bne.w JutsuFeedbackReturn
    tst.w $FFFFF160.w
    beq.w JutsuFeedbackReturn
    tst.w $FFFFF22A.w
    beq.w JutsuAbsorbSecond
    move.w $FFFFF22C.w,d0
    bsr.w JutsuAbsorbDistance
    tst.w d0
    beq.w JutsuAbsorbSecond
    clr.w $FFFFF22A.w
    addq.w #1,$FFFFF3EA.w
JutsuAbsorbSecond:
    tst.w $FFFFF2F4.w
    beq.w JutsuFeedbackReturn
    move.w $FFFFF2F6.w,d0
    bsr.w JutsuAbsorbDistance
    tst.w d0
    beq.w JutsuFeedbackReturn
    clr.w $FFFFF2F4.w
    addq.w #1,$FFFFF3EA.w
    rts
JutsuAbsorbDistance:
    move.w d0,d1
    sub.w $FFFFD01C.w,d1
    bpl.w JutsuAbsorbHeroDistance
    neg.w d1
JutsuAbsorbHeroDistance:
    cmpi.w #96,d1
    bls.w JutsuAbsorbAccept
    add.w $FFFFC210.w,d0
    sub.w $FFFFF168.w,d0
    bpl.w JutsuAbsorbVortexDistance
    neg.w d0
JutsuAbsorbVortexDistance:
    cmpi.w #64,d0
    bls.w JutsuAbsorbAccept
    moveq #0,d0
    rts
JutsuAbsorbAccept:
    moveq #1,d0
    rts

JutsuHitMotion:
    movem.l d0-a6,-(sp)
    bsr.w StartImpact
    move.w #12,$FFFFF12C.w
    move.w $FFFFF164.w,d0
    move.w d0,$FFFFF3E6.w
    bsr.w DamageActorState
    move.w d0,d1
    add.w d1,d1
    lea JutsuReactionKinds(pc),a1
    move.w (a1,d1.w),$6(a2)
    addq.w #1,$FFFFF3E8.w
    lea JutsuRumbleLengths(pc),a1
    move.w (a1,d1.w),$FFFFF3E0.w
    move.w #4,$FFFFF3E4.w
    lea JutsuHitStops(pc),a1
    move.w (a1,d1.w),$FFFFF150.w
    addi.w #16,d0
    bsr.w SfxStart
    tst.b $64(a0)
    ble.w JutsuHitMotionReturn
    move.w $FFFFF164.w,d0
    cmpi.w #2,d0
    beq.w JutsuStunTarget
    cmpi.w #6,d0
    beq.w JutsuBindTarget
    move.w #$2C1A,$42(a0)
    clr.b $14(a0)
    jsr (loc_F868).l
    move.w $FFFFF164.w,d0
    move.l #$40000,$2C(a0)
    move.l #$FFFD0000,$34(a0)
    cmpi.w #1,d0
    beq.w JutsuKamuiLaunch
    cmpi.w #3,d0
    beq.w JutsuFireLaunch
    cmpi.w #4,d0
    beq.w JutsuWaterLaunch
    cmpi.w #5,d0
    beq.w JutsuEarthLaunch
    bra.w JutsuLaunchFacing
JutsuKamuiLaunch:
    move.l #$FFFB0000,$34(a0)
    move.l #$8000,$2C(a0)
    bra.w JutsuLaunchFacing
JutsuFireLaunch:
    move.l #$28000,$2C(a0)
    move.l #$FFFE0000,$34(a0)
    addq.w #1,$FFFFF3F4.w
    bra.w JutsuLaunchFacing
JutsuWaterLaunch:
    move.l #$60000,$2C(a0)
    move.l #$FFFE8000,$34(a0)
    addq.w #1,$FFFFF3F8.w
    bra.w JutsuLaunchFacing
JutsuEarthLaunch:
    move.l #$A000,$2C(a0)
    move.l #$FFFC0000,$34(a0)
JutsuLaunchFacing:
    btst #0,$FFFFF176.w
    beq.w JutsuHitMotionReturn
    neg.l $2C(a0)
    bra.w JutsuHitMotionReturn
JutsuStunTarget:
    moveq #30,d2
    bra.w JutsuPinTarget
JutsuBindTarget:
    moveq #96,d2
    addq.w #1,$FFFFF3FE.w
JutsuPinTarget:
    bsr.w DamageActorState
    move.w d2,$C(a2)
    move.w $FFFFF164.w,$E(a2)
    move.w #$300D,$42(a0)
    clr.b $14(a0)
    bclr #6,$46(a0)
    move.w #$8000,$24(a0)
    clr.l $34(a0)
    clr.l $2C(a0)
    clr.l $30(a0)
    move.w $20(a0),d0
    addi.w #128,d0
    move.w d0,$18(a0)
JutsuHitMotionReturn:
    movem.l (sp)+,d0-a6
    rts
JutsuHitStops: dc.w 6,8,4,6,5,7,4
JutsuReactionKinds: dc.w 6,4,6,2,3,4,3
JutsuRumbleLengths: dc.w 16,18,12,16,14,16,12
JutsuLaneRanges: dc.w 24,28,22,48,32,28,28
JutsuDistanceRanges: dc.w 40,44,36,72,56,44,36

JutsuEnemyControl:
    movem.l d1-d2/a2,-(sp)
    moveq #0,d0
    cmpa.w #$D100,a0
    bcs.w JutsuEnemyControlReturn
    cmpa.w #$D200,a0
    bhi.w JutsuEnemyControlReturn
    btst #7,(a0)
    beq.w JutsuEnemyControlReturn
    bsr.w DamageActorState
    tst.w $C(a2)
    beq.w JutsuEnemyControlReturn
    tst.b $64(a0)
    ble.w JutsuEnemyControlReturn
    cmpi.b #$C,$43(a0)
    bcc.w JutsuEnemyControlReturn
    clr.l $2C(a0)
    clr.l $30(a0)
    clr.w $42(a0)
    moveq #1,d0
JutsuEnemyControlReturn:
    movem.l (sp)+,d1-d2/a2
    rts

CustomSceneHScroll:
    move.w $FFFFC21A.w,(a1)
    move.w d0,-(sp)
    move.w $FFFFC21E.w,d0
    add.w $FFFFF3E2.w,d0
    move.w d0,(a1)
    move.w (sp)+,d0
    rts

JutsuWorldFeedbackRender:
    lea (CityPalette).l,a6
    cmpi.w #2,$FFFFF200.w
    bne.w JutsuWorldDaylight
    tst.w $FFFFF284.w
    beq.w JutsuWorldDaylight
    moveq #18,d0
    sub.w $FFFFF2EC.w,d0
    lsr.w #2,d0
    cmpi.w #3,d0
    bls.w JutsuWorldPhaseIndex
    moveq #3,d0
JutsuWorldPhaseIndex:
    lsl.w #2,d0
    lea (CityPhasePalettes).l,a1
    tst.w $FFFFF3E4.w
    beq.w JutsuWorldPhaseTable
    lea (CityPhaseHitPalettes).l,a1
JutsuWorldPhaseTable:
    movea.l (a1,d0.w),a6
    bra.w JutsuWorldPalette
JutsuWorldDaylight:
    tst.w $FFFFF3E4.w
    beq.w JutsuWorldPalette
    lea (CityHitPalette).l,a6
JutsuWorldPalette:
    move.l a6,-(sp)
    jsr (loc_2ED0).l
    movea.l (sp)+,a6
    jsr (loc_2EB4).l
    rts

RenderDotonWall:
    tst.w $FFFFF3EE.w
    beq.w JutsuFeedbackReturn
    lea $FFFFD700.w,a0
    cmpi.w #-1,$72(a0)
    beq.w JutsuFeedbackReturn
    move.b #$7F,(a0)
    clr.b $2(a0)
    move.b #$60,$17(a0)
    move.w #$300,$8(a0)
    tst.w $FFFFF1F0.w
    beq.w JutsuWallBank
    move.w #$360,$8(a0)
JutsuWallBank:
    bsr.w JutsuTrimEffectMeta
    move.w $FFFFF3F0.w,d0
    sub.w $FFFFC210.w,d0
    move.w d0,$1C(a0)
    move.w $FFFFF3F2.w,d0
    move.w d0,$20(a0)
    addi.w #128,d0
    move.w d0,$18(a0)
    rts
