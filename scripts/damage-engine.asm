; Health-confirmed feedback. Four 16-byte actor records, F380..F3BF.
; +6 reaction kind, +A local contact sequence, +C pin timer, +E pin technique.
; Native collision, invulnerability, launches and corpse cleanup remain intact.
DamageActorState:
    lea $FFFFF380.w,a2
    cmpa.w #$D000,a0
    beq.w DamageStateReturn
    lea $FFFFF390.w,a2
    cmpa.w #$D100,a0
    beq.w DamageStateReturn
    lea $FFFFF3A0.w,a2
    cmpa.w #$D180,a0
    beq.w DamageStateReturn
    lea $FFFFF3B0.w,a2
DamageStateReturn:
    rts
DamageObserve:
    lea $FFFFD000.w,a0
    lea $FFFFF380.w,a2
    moveq #3,d6
DamageObserveLoop:
    tst.w $FFFFF150.w
    bne.w DamageObserveHealth
    tst.w $C(a2)
    beq.w DamagePinTicked
    subq.w #1,$C(a2)
DamagePinTicked:
    tst.w $2(a2)
    beq.w DamageObserveLanding
    subq.w #1,$2(a2)
DamageObserveLanding:
    tst.w $8(a2)
    beq.w DamageObserveHealth
    subq.w #1,$8(a2)
DamageObserveHealth:
    btst #7,(a0)
    beq.w DamageActorGone
    moveq #0,d0
    move.b $64(a0),d0
    cmpa.w #$D000,a0
    bne.w DamageHealthReady
    move.b $FFFFFE7E.w,d0
DamageHealthReady:
    tst.b $1(a2)
    beq.w DamageInitialize
    cmp.b (a2),d0
    bcc.w DamageSaveHealth
    move.w #16,$2(a2)
    addq.w #1,$A(a2)
    addq.w #1,$FFFFF3D0.w
    cmpa.w #$D000,a0
    bne.w DamageSaveHealth
    addq.w #1,$FFFFF3D4.w
    moveq #1,d1
    btst #0,$B(a2)
    bne.w DamagePlayerKindReady
    moveq #2,d1
DamagePlayerKindReady:
    move.w $FFFFF3D4.w,d2
    divu.w #3,d2
    swap d2
    tst.w d2
    bne.w DamagePlayerKindSave
    moveq #3,d1
DamagePlayerKindSave:
    move.w d1,$6(a2)
    movem.l d0/d6/a0/a2,-(sp)
    bsr.w StartImpact
    move.w #4,$FFFFF150.w
    moveq #13,d0
    bsr.w SfxStart
    movem.l (sp)+,d0/d6/a0/a2
    clr.w $FFFFF2B4.w
DamageSaveHealth:
    move.b d0,(a2)
    moveq #0,d1
    cmpi.b #$1A,$43(a0)
    bne.w DamageAirReady
    cmpa.w #$D000,a0
    bne.w DamageEnemyAir
    btst #5,$3(a0)
    beq.w DamageAirReady
    bra.w DamageIsAir
DamageEnemyAir:
    btst #6,$46(a0)
    beq.w DamageAirReady
DamageIsAir:
    moveq #1,d1
DamageAirReady:
    tst.w $4(a2)
    beq.w DamageSaveAir
    tst.w d1
    bne.w DamageSaveAir
    move.w #10,$8(a2)
    move.w #12,$FFFFF3C0.w
    move.w $1C(a0),d2
    add.w $FFFFC210.w,d2
    move.w d2,$FFFFF3C2.w
    move.w $20(a0),$FFFFF3C4.w
    addq.w #1,$FFFFF3D2.w
    movem.l d0-d2/d6/a0/a2,-(sp)
    moveq #12,d0
    bsr.w SfxStart
    movem.l (sp)+,d0-d2/d6/a0/a2
DamageSaveAir:
    move.w d1,$4(a2)
    bra.w DamageNextActor
DamageInitialize:
    move.b #1,$1(a2)
    move.b d0,(a2)
    bra.w DamageNextActor
DamageActorGone:
    clr.l (a2)
    clr.l $4(a2)
    clr.l $8(a2)
    clr.l $C(a2)
DamageNextActor:
    adda.w #16,a2
    cmpa.w #$D000,a0
    bne.w DamageNextEnemy
    lea $FFFFD100.w,a0
    bra.w DamageObserveContinue
DamageNextEnemy:
    lea $80(a0),a0
DamageObserveContinue:
    dbf d6,DamageObserveLoop
    tst.w $FFFFF3C0.w
    beq.w DamageObserveReturn
    subq.w #1,$FFFFF3C0.w
DamageObserveReturn:
    move.w $FFFFD070.w,d0
    cmp.w $FFFFF3D6.w,d0
    beq.w DamageSoundReturn
    move.w d0,$FFFFF3D6.w
    tst.w $FFFFF160.w
    bne.w DamageSoundReturn
    cmpi.w #9,d0
    beq.w DamageSwingSound
    cmpi.w #12,d0
    beq.w DamageSwingSound
    cmpi.w #13,d0
    beq.w DamageSwingSound
    cmpi.w #29,d0
    beq.w DamageStepSound
    cmpi.w #33,d0
    beq.w DamageStepSound
    cmpi.w #37,d0
    beq.w DamageStepSound
    cmpi.w #41,d0
    bne.w DamageSoundReturn
DamageStepSound:
    moveq #15,d0
    bsr.w SfxStart
    rts
DamageSwingSound:
    moveq #14,d0
    bsr.w SfxStart
DamageSoundReturn:
    rts

PlayerDamagePose:
    tst.w $FFFFF204.w
    bne.w PlayerDamageReturn
    lea $FFFFD000.w,a0
    bsr.w DamageActorState
    move.b $42(a0),d1
    andi.b #$7F,d1
    cmpi.b #$58,d1
    beq.w PlayerFloorRecovery
    move.b $43(a0),d1
    cmpi.b #$1A,d1
    beq.w PlayerDamageAir
    cmpi.b #$D,d1
    bcs.w PlayerDamageRecovery
    cmpi.b #$10,d1
    bhi.w PlayerDamageReturn
    moveq #22,d0
    cmpi.w #11,$2(a2)
    bcc.w PlayerDamageApply
    moveq #23,d0
    cmpi.w #4,$2(a2)
    bcc.w PlayerDamageApply
    moveq #28,d0
    bra.w PlayerDamageApply
PlayerDamageAir:
    moveq #23,d0
    btst #7,$42(a0)
    beq.w PlayerDamageApply
    moveq #26,d0
    btst #5,$3(a0)
    bne.w PlayerDamageInAir
    tst.l $34(a0)
    bpl.w PlayerDamageApply
    moveq #23,d0
    bra.w PlayerDamageApply
PlayerDamageInAir:
    moveq #24,d0
    tst.l $34(a0)
    bmi.w PlayerDamageApply
    moveq #25,d0
    bra.w PlayerDamageApply
PlayerFloorRecovery:
    moveq #27,d0
    btst #7,$42(a0)
    beq.w PlayerDamageApply
    moveq #26,d0
    tst.b $14(a0)
    beq.w PlayerDamageApply
    moveq #28,d0
    bra.w PlayerDamageApply
PlayerDamageRecovery:
    move.b $42(a0),d1
    andi.b #$7F,d1
    bne.w PlayerDamageReturn
    move.b $FFFFF2B0.w,d1
    andi.b #$F,d1
    bne.w PlayerDamageReturn
    tst.w $8(a2)
    beq.w PlayerDamageReturn
    moveq #26,d0
    cmpi.w #5,$8(a2)
    bcc.w PlayerDamageApply
    moveq #28,d0
PlayerDamageApply:
    ; Preserve the native airborne/floor sequence; vary grounded hit silhouettes.
    cmpi.w #22,d0
    bne.w PlayerDamageMetaApply
    moveq #61,d0
    cmpi.w #2,$6(a2)
    bne.w PlayerDamageMetaApply
    moveq #62,d0
PlayerDamageMetaApply:
    cmpi.w #61,d0
    bne.w PlayerDamageBuckle
    cmpi.w #3,$6(a2)
    bne.w PlayerDamageBuckle
    moveq #63,d0
PlayerDamageBuckle:
    cmpi.w #28,d0
    bne.w PlayerDamageDrawingReady
    cmpi.w #2,$6(a2)
    bne.w PlayerDamageDrawingReady
    moveq #63,d0
PlayerDamageDrawingReady:
    move.w d0,$70(a0)
    lea (KakashiJutsuMeta).l,a1
    btst #0,$44(a0)
    beq.w PlayerDamageMeta
    lea (KakashiJutsuLeftMeta).l,a1
PlayerDamageMeta:
    move.l a1,$A(a0)
PlayerDamageReturn:
    rts

DamagePaletteFlash:
    tst.w $FFFFF204.w
    bne.w DamageFlashReturn
    lea $FFFFD000.w,a0
    moveq #3,d6
DamageFlashActor:
    bsr.w DamageActorState
    cmpi.w #13,$2(a2)
    bcs.w DamageFlashNext
    lea (HitPalette0).l,a6
    cmpa.w #$D000,a0
    beq.w DamageFlashApply
    lea (HitPalette1).l,a6
    cmpi.b #$40,$17(a0)
    bne.w DamageFlashApply
    lea (HitPalette2).l,a6
DamageFlashApply:
    movem.l d6/a0,-(sp)
    move.l a6,-(sp)
    jsr (loc_2ED0).l
    movea.l (sp)+,a6
    jsr (loc_2EB4).l
    movem.l (sp)+,d6/a0
DamageFlashNext:
    cmpa.w #$D000,a0
    bne.w DamageFlashNextEnemy
    lea $FFFFD100.w,a0
    bra.w DamageFlashContinue
DamageFlashNextEnemy:
    lea $80(a0),a0
DamageFlashContinue:
    dbf d6,DamageFlashActor
DamageFlashReturn:
    rts

; Replace only the native renderer's position loads; physical RAM never shakes.
DamageSpritePosition:
    move.w $18(a0),d2
    move.w $1C(a0),d3
    add.w $FFFFF3E2.w,d3
    cmpa.w #$D000,a0
    beq.w DamagePositionActor
    cmpa.w #$D100,a0
    beq.w DamagePositionActor
    cmpa.w #$D180,a0
    beq.w DamagePositionActor
    cmpa.w #$D200,a0
    bne.w DamagePositionReturn
DamagePositionActor:
    movem.l d0-d1/a2,-(sp)
    bsr.w DamageActorState
    move.w $2(a2),d0
    cmpi.w #16,d0
    bhi.w DamagePositionRestore
    tst.w d0
    beq.w DamagePositionRestore
    lea DamageRecoilEnvelope(pc),a2
    moveq #0,d1
    move.b (a2,d0.w),d1
    cmpa.w #$D000,a0
    beq.w DamageHeroFacing
    move.w $1C(a0),d0
    sub.w $FFFFD01C.w,d0
    bpl.w DamageRecoilAdd
    neg.w d1
    bra.w DamageRecoilAdd
DamageHeroFacing:
    btst #0,$44(a0)
    bne.w DamageRecoilAdd
    neg.w d1
DamageRecoilAdd:
    add.w d1,d3
DamagePositionRestore:
    movem.l (sp)+,d0-d1/a2
DamagePositionReturn:
    rts
DamageRecoilEnvelope: dc.b 0,0,0,1,1,2,2,3,4,5,6,7,8,8,6,4,2
    even

RenderLandingDust:
    tst.w $FFFFF3C0.w
    beq.w DustReturn
    lea $FFFFD780.w,a0
    move.b #$7F,(a0)
    clr.b $2(a0)
    clr.b $17(a0)
    move.w $FFFFF3C2.w,d0
    sub.w $FFFFC210.w,d0
    move.w d0,$1C(a0)
    move.w $FFFFF3C4.w,d0
    move.w d0,$20(a0)
    addi.w #128,d0
    move.w d0,$18(a0)
    moveq #12,d0
    sub.w $FFFFF3C0.w,d0
    divu.w #4,d0
    add.w d0,d0
    addi.w #$2C1,d0
    move.w d0,$8(a0)
    move.l #DustMeta,$A(a0)
DustReturn:
    rts

MeleeReaction:
    movem.l d0-d2/a2,-(sp)
    bsr.w DamageActorState
    moveq #1,d1
    move.w $FFFFF152.w,d0
    btst #0,d0
    bne.w MeleeReactionRoute
    moveq #2,d1
MeleeReactionRoute:
    move.w $FFFFF2D4.w,d0
    cmpi.w #1,d0
    bne.w MeleeReactionSweep
    moveq #5,d1
    bra.w MeleeReactionSave
MeleeReactionSweep:
    cmpi.w #2,d0
    bne.w MeleeReactionUppercut
    moveq #3,d1
    bra.w MeleeReactionSave
MeleeReactionUppercut:
    cmpi.w #3,d0
    bne.w MeleeReactionSave
    moveq #4,d1
MeleeReactionSave:
    move.w d1,$6(a2)
    ; Three small, timed skids give light hits recoil without breaking the chain.
    tst.b $64(a0)
    ble.w MeleeReactionReturn
    cmpi.w #2,d1
    bhi.w MeleeReactionReturn
    btst #6,$46(a0)
    bne.w MeleeReactionReturn
    moveq #2,d0
    btst #0,$FFFFD044.w
    beq.w MeleeRecoilFacing
    neg.w d0
MeleeRecoilFacing:
    add.w d0,$1C(a0)
MeleeReactionReturn:
    movem.l (sp)+,d0-d2/a2
    rts

MeleeReactionSound:
    movem.l d0/a2,-(sp)
    bsr.w DamageActorState
    move.w $6(a2),d0
    cmpi.w #1,d0
    beq.w MeleeHeadSound
    cmpi.w #2,d0
    beq.w MeleeBodySound
    cmpi.w #5,d0
    beq.w MeleeSlashSound
    moveq #27,d0
    bra.w MeleeSoundReady
MeleeHeadSound:
    moveq #24,d0
    bra.w MeleeSoundReady
MeleeBodySound:
    moveq #25,d0
    bra.w MeleeSoundReady
MeleeSlashSound:
    moveq #26,d0
MeleeSoundReady:
    bsr.w SfxStart
    movem.l (sp)+,d0/a2
    rts
