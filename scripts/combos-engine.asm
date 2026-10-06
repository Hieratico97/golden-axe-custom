; F2D2 queued route, F2D4 active route, F2D6 previous animation,
; F2D8..DF confirmed contacts: neutral, lunge, sweep, uppercut.
ComboChooseRoute:
    clr.w $FFFFF2D2.w
    btst #0,$FFFFC176.w
    beq.w ComboDirectionalRoute
    move.w #3,$FFFFF2D2.w
    andi.b #$FE,$FFFFC176.w
    andi.b #$FE,$FFFFC177.w
    bra.w ComboRouteConsume
ComboDirectionalRoute:
    cmpi.w #2,$FFFFF152.w
    bcs.w ComboRouteReturn
    move.b $FFFFC176.w,d0
    andi.b #$C,d0
    beq.w ComboRouteReturn
    move.w #1,$FFFFF2D2.w
    btst #0,$FFFFD044.w
    beq.w ComboRouteFacingRight
    cmpi.b #4,d0
    beq.w ComboRouteConsume
    bra.w ComboRouteBack
ComboRouteFacingRight:
    cmpi.b #8,d0
    beq.w ComboRouteConsume
ComboRouteBack:
    move.w #2,$FFFFF2D2.w
ComboRouteConsume:
    andi.b #$F3,$FFFFC176.w
    andi.b #$F3,$FFFFC177.w
ComboRouteReturn:
    rts

RenderPlayerCombo:
    tst.w $FFFFF204.w
    bne.w ComboPoseReturn
    tst.w $FFFFF160.w
    bne.w ComboPoseReturn
    btst #5,$FFFFD003.w
    bne.w ComboPoseReturn
    moveq #0,d0
    move.b $FFFFD043.w,d0
    cmpi.w #3,d0
    bcs.w ComboPoseReset
    cmpi.w #12,d0
    bhi.w ComboPoseReset
    move.b $FFFFD042.w,d1
    andi.b #$7F,d1
    cmpi.b #8,d1
    beq.w ComboPoseReset
    cmp.w $FFFFF2D6.w,d0
    beq.w ComboPosePhase
    move.w d0,$FFFFF2D6.w
    move.w $FFFFF2D2.w,$FFFFF2D4.w
ComboPosePhase:
    move.w $FFFFF2D4.w,d2
    beq.w ComboPoseReturn
    move.w $FFFFD070.w,d0
    cmpi.w #45,d0
    bcc.w ComboPhaseNew
    cmpi.w #8,d0
    bcs.w ComboPoseReturn
    cmpi.w #15,d0
    bhi.w ComboPoseReturn
    subi.w #8,d0
    lea ComboOldPhases(pc),a1
    move.b (a1,d0.w),d0
    andi.w #3,d0
    bra.w ComboPhaseReady
ComboPhaseNew:
    subi.w #45,d0
    andi.w #3,d0
ComboPhaseReady:
    add.w d2,d2
    lea ComboRoutePoses(pc),a1
    add.w (a1,d2.w),d0
    move.w d0,$FFFFD070.w
    rts
ComboPoseReset:
    clr.w $FFFFF2D6.w
    clr.w $FFFFF2D4.w
ComboPoseReturn:
    rts
ComboOldPhases: dc.b 0,1,2,0,1,0,1,3
    even
ComboRoutePoses: dc.w 0,53,49,45

ComboHitMotion:
    movem.l d0-a6,-(sp)
    move.w $FFFFF2D4.w,d0
    add.w d0,d0
    lea $FFFFF2D8.w,a2
    addq.w #1,(a2,d0.w)
    tst.b $64(a0)
    ble.w ComboHitReturn
    cmpi.w #6,d0
    beq.w ComboUppercutMotion
    cmpi.w #4,d0
    beq.w ComboSweepMotion
    cmpi.w #2,d0
    bne.w ComboHitReturn
    ; A forward remate drives the target away and advances one short step.
    move.w #$2C1A,$42(a0)
    clr.b $14(a0)
    jsr (loc_F868).l
    move.l #$48000,$2C(a0)
    moveq #6,d0
    btst #0,$FFFFD044.w
    beq.w ComboLungeStep
    neg.l $2C(a0)
    neg.w d0
ComboLungeStep:
    add.w d0,$FFFFD01C.w
    cmpi.w #$A0,$FFFFD01C.w
    bcc.w ComboLungeRightClamp
    move.w #$A0,$FFFFD01C.w
ComboLungeRightClamp:
    cmpi.w #$1A0,$FFFFD01C.w
    bls.w ComboHitReturn
    move.w #$1A0,$FFFFD01C.w
    bra.w ComboHitReturn
ComboUppercutMotion:
    move.w #$2C1A,$42(a0)
    clr.b $14(a0)
    jsr (loc_F868).l
    move.l #$FFFB0000,$34(a0)
    move.l #$18000,$2C(a0)
    bra.w ComboHitDirection
ComboSweepMotion:
    move.w #$2C1A,$42(a0)
    clr.b $14(a0)
    jsr (loc_F868).l
    move.l #$FFFE8000,$34(a0)
    move.l #$30000,$2C(a0)
ComboHitDirection:
    btst #0,$FFFFD044.w
    beq.w ComboHitReturn
    neg.l $2C(a0)
ComboHitReturn:
    movem.l (sp)+,d0-a6
    rts
