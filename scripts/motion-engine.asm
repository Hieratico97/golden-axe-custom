; Native acceleration, double-tap running and collision are retained.
; F2A0 stride distance, F2A2/4 previous world position, F2A6 initialized,
; F2A8 last native motion state for a contact pose at walk/run transitions.
RenderPlayerMotion:
    move.w $FFFFD01C.w,d0
    add.w $FFFFC210.w,d0
    move.w $FFFFD020.w,d1
    tst.w $FFFFF2A6.w
    bne.w MotionDelta
    move.w #1,$FFFFF2A6.w
    move.w d0,$FFFFF2A2.w
    move.w d1,$FFFFF2A4.w
MotionDelta:
    move.w d0,d2
    sub.w $FFFFF2A2.w,d2
    move.w d0,$FFFFF2A2.w
    move.w d1,d3
    sub.w $FFFFF2A4.w,d3
    move.w d1,$FFFFF2A4.w
    tst.w $FFFFF204.w
    bne.w MotionReturn
    tst.w $FFFFF160.w
    bne.w MotionReturn
    btst #5,$FFFFD003.w
    bne.w MotionReturn
    moveq #0,d4
    move.b $FFFFD042.w,d4
    andi.b #$7F,d4
    beq.w MotionGrounded
    cmpi.b #8,d4
    bne.w MotionReturn
MotionGrounded:
    cmp.w $FFFFF2A8.w,d4
    beq.w MotionCycleReady
    move.w d4,$FFFFF2A8.w
    clr.w $FFFFF2A0.w
MotionCycleReady:
    tst.w d2
    bpl.w MotionXAbs
    neg.w d2
MotionXAbs:
    tst.w d3
    bpl.w MotionYAbs
    neg.w d3
MotionYAbs:
    add.w d3,d2
    beq.w MotionIdle
    cmpi.w #8,d2
    bls.w MotionStride
    moveq #8,d2
MotionStride:
    add.w d2,$FFFFF2A0.w
    andi.w #63,$FFFFF2A0.w
    move.w $FFFFF2A0.w,d0
    lsr.w #3,d0
    addi.w #29,d0
    cmpi.b #8,d4
    bne.w MotionPose
    addq.w #8,d0
    bra.w MotionPose
MotionIdle:
    moveq #0,d0
    clr.w $FFFFF2A0.w
MotionPose:
    move.w d0,$FFFFD070.w
    move.l #KakashiMotionMeta,$FFFFD00A.w
    cmpi.b #8,d4
    bne.w MotionGuardCheck
    move.l #KakashiRunMeta,$FFFFD00A.w
MotionGuardCheck:
    tst.w d0
    bne.w MotionFacing
    move.l #KakashiIdleMeta,$FFFFD00A.w
MotionFacing:
    btst #0,$FFFFD044.w
    beq.w MotionReturn
    move.l #KakashiMotionLeftMeta,$FFFFD00A.w
    cmpi.b #8,d4
    bne.w MotionLeftGuardCheck
    move.l #KakashiRunLeftMeta,$FFFFD00A.w
MotionLeftGuardCheck:
    tst.w d0
    bne.w MotionReturn
    move.l #KakashiIdleLeftMeta,$FFFFD00A.w
MotionReturn:
    rts
