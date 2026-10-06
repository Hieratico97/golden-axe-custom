; Solo Kakashi. Private state F180..F1FF; no Team 7 entities or assist logic.
; FX double buffers 6000..7FFF. Props 8000..91FF, HUD 9200, font 9800.

CustomPlayerUpdate:
    lea $FFFFC176.w,a6
    tst.w $FFFFF160.w
    beq.w PlayerNativeUpdate
    ori.w #$700,sr
    rts
PlayerNativeUpdate:
    jmp (loc_BA06).l

CustomSpriteDMA:
    movem.l d0-a6,-(sp)
    ; A delayed main-loop frame may already be choosing its next pose.
    ; Upload only with a completed SAT; never pair old geometry with new art.
    btst #0,$FFFFC183.w
    beq.w CustomSpriteDMAReturn
    bsr.w CustomSceneUpload
    ; One complete actor pose per VBlank leaves room for effects and the SAT.
    ; Hero first, then rotating enemies retain a complete cached drawing.
    clr.w $FFFFF1FC.w
    ; A late native render can enter this IRQ after its transfer window.
    ; Keep the complete cached actor pose instead of starting a burst in the
    ; visible picture and making the following control frame wait for it.
    tst.w $FFFFF160.w
    bne.s ActorTransferWindowReady
    tst.w $FFFFF204.w
    bne.s ActorTransferWindowReady
    move.w $00C00008,d0
    lsr.w #8,d0
    cmpi.w #224,d0
    bcs.s ActorTransferWindowMissed
    cmpi.w #240,d0
    bcs.s ActorTransferWindowReady
ActorTransferWindowMissed:
    addq.w #1,$FFFFF378.w
    bra.w CustomSpriteDMAReturn
ActorTransferWindowReady:
    lea $FFFFD000.w,a0
    move.l #$70000002,d7
    bsr.w UploadActorPose
    moveq #0,d0
    move.w $FFFFF374.w,d0
    divu.w #3,d0
    swap d0
    mulu.w #24,d0
    lea (ActorDMAOrders).l,a1
    adda.l d0,a1
    moveq #2,d5
ActorDMAOrderLoop:
    movea.l (a1)+,a0
    move.l (a1)+,d7
    movem.l d5/a1,-(sp)
    bsr.w UploadActorPose
    movem.l (sp)+,d5/a1
    dbf d5,ActorDMAOrderLoop
ActorsUploaded:
    bsr.w VillageAnimationUpload
    tst.w $FFFFF204.w
    beq.w EffectDMAContinue
    cmpi.w #2048,$FFFFF1FC.w
    bhi.w EffectDMAEnd
    bsr.w StorySpriteDMA
    bra.w EffectDMAEnd
EffectDMAContinue:
    tst.w $FFFFF160.w
    beq.w EffectDMAEnd
    cmpi.w #2048,$FFFFF1FC.w
    bhi.w EffectDMAEnd
    move.w $FFFFD770.w,d0
    cmp.w $FFFFD772.w,d0
    beq.w EffectDMAEnd
    tst.w $FFFFF1F6.w
    beq.w EffectFirstHalf
    cmp.w $FFFFF1F4.w,d0
    bne.w EffectFirstHalf
    move.l $FFFFD774.w,d1
    cmp.l $FFFFF1F8.w,d1
    bne.w EffectFirstHalf
    moveq #1,d5
    bra.w EffectUploadHalf
EffectFirstHalf:
    move.w d0,$FFFFF1F4.w
    move.l $FFFFD774.w,$FFFFF1F8.w
    move.w $FFFFF1F0.w,d1
    eori.w #1,d1
    move.w d1,$FFFFF1F2.w
    moveq #0,d5
EffectUploadHalf:
    mulu.w #3072,d0
    movea.l $FFFFF1F8.w,a6
    adda.l d0,a6
    move.l #$60000001,d7
    tst.w $FFFFF1F2.w
    beq.w EffectBankAddress
    move.l #$6C000001,d7
EffectBankAddress:
    tst.w d5
    beq.w EffectHalfAddress
    adda.w #1536,a6
    addi.l #$06000000,d7
EffectHalfAddress:
    movem.l d5/a6/d7,-(sp)
    move.w #768,d6
    jsr ($FFFFF410).w
    movem.l (sp)+,d5/d7/a6
    move.l d7,$00C00004
    move.w (a6),$00C00000
    move.w #1,$FFFFF1F6.w
    tst.w d5
    beq.w EffectDMAEnd
    clr.w $FFFFF1F6.w
    move.w $FFFFF1F2.w,$FFFFF1F0.w
    move.w $FFFFF1F4.w,$FFFFD772.w
EffectDMAEnd:
    tst.w $FFFFF348.w
    beq.w ActorResumeBudgetReady
    subq.w #1,$FFFFF348.w
ActorResumeBudgetReady:
CustomSpriteDMAReturn:
    movem.l (sp)+,d0-a6
    rts
CountActorDMA:
    move.w (a0),d0
    cmp.w $2(a0),d0
    beq.w CountActorReturn
    addi.w #2048,$FFFFF1FC.w
CountActorReturn:
    rts

UploadActorPose:
    btst #7,(a0)
    beq.w UploadActorReturn
    move.l $74(a0),d0
    beq.w UploadActorReturn
    move.w $70(a0),d0
    cmp.w $72(a0),d0
    beq.w UploadActorReturn
    tst.w $FFFFF348.w
    beq.w ActorNormalBudget
    tst.w $FFFFF1FC.w
    bne.w UploadActorReturn
ActorNormalBudget:
    tst.w $FFFFF1FC.w
    bne.w UploadActorReturn
    cmpi.w #65,d0
    bcc.w UploadActorReturn
    move.w d0,$FFFFF294.w
    mulu.w #2048,d0
    movea.l $74(a0),a6
    adda.l d0,a6
    movem.l a0/a6/d7,-(sp)
    move.w #1024,d6
    jsr ($FFFFF410).w
    movem.l (sp)+,d7/a0/a6
    move.l d7,$00C00004
    move.w (a6),$00C00000
    move.w $FFFFF294.w,$72(a0)
    addi.w #2048,$FFFFF1FC.w
UploadActorReturn:
    rts
ActorDMAOrders:
    dc.l $FFFFD100,$78000002,$FFFFD180,$60000002,$FFFFD200,$50000001
    dc.l $FFFFD180,$60000002,$FFFFD200,$50000001,$FFFFD100,$78000002
    dc.l $FFFFD200,$50000001,$FFFFD100,$78000002,$FFFFD180,$60000002

JutsuUpdate:
    bsr.w JutsuFeedbackTick
    tst.w $FFFFF160.w
    beq.w JutsuDamageChecked
    cmpi.w #16,$FFFFF160.w
    bcs.w JutsuRecoveryDamage
    bclr #1,$FFFFD003.w
    bra.w JutsuDamageChecked
JutsuRecoveryDamage:
    cmpi.w #1,$FFFFF164.w
    beq.w JutsuDamageChecked
    btst #1,$FFFFD003.w
    beq.w JutsuDamageChecked
    clr.w $FFFFF160.w
    clr.w $FFFFF3EE.w
    clr.w $FFFFF1F6.w
JutsuDamageChecked:
    btst #1,$FFFFC17B.w
    bne.w ChakraRegenerated
    btst #0,$FFFFC17B.w
    bne.w ChakraRegenerated
    cmpi.w #120,$FFFFF180.w
    bcc.w ChakraRegenerated
    addq.w #1,$FFFFF180.w
ChakraRegenerated:
    tst.w $FFFFF162.w
    beq.w JutsuInput
    subq.w #1,$FFFFF162.w
JutsuInput:
    tst.w $FFFFF2B2.w
    beq.w JutsuSelectorInput
    subq.w #1,$FFFFF2B2.w
JutsuSelectorInput:
    ; A is a gesture: release casts, any vertical chord cancels that cast.
    ; This also handles A arriving several frames before the direction.
    btst #6,$FFFFC176.w
    beq.w JutsuRelease
    tst.w $FFFFF2BA.w
    bne.w JutsuHeld
    btst #6,$FFFFC177.w
    beq.w JutsuHeld
    move.w #1,$FFFFF2BA.w
JutsuHeld:
    btst #0,$FFFFC176.w
    bne.w JutsuSelectUp
    btst #1,$FFFFC176.w
    bne.w JutsuSelectDown
    andi.b #$BF,$FFFFC177.w
    andi.b #$BF,$FFFFC176.w
    bra.w JutsuTick
JutsuRelease:
    move.w $FFFFF2BA.w,d0
    clr.w $FFFFF2BA.w
    cmpi.w #1,d0
    bne.w JutsuQuickCast
    move.w $FFFFF182.w,d0
    bra.w JutsuBegin
JutsuSelectUp:
    move.w #2,$FFFFF2BA.w
    clr.w $FFFFF2B4.w
    move.b $FFFFC177.w,d0
    andi.b #$41,d0
    bne.w JutsuNext
    bra.w JutsuSelectorConsume
JutsuSelectDown:
    move.w #2,$FFFFF2BA.w
    clr.w $FFFFF2B4.w
    move.b $FFFFC177.w,d0
    andi.b #$42,d0
    bne.w JutsuPrevious
    bra.w JutsuSelectorConsume
JutsuNext:
    addq.w #1,$FFFFF182.w
    cmpi.w #7,$FFFFF182.w
    bcs.w JutsuSelected
    clr.w $FFFFF182.w
    bra.w JutsuSelected
JutsuPrevious:
    subq.w #1,$FFFFF182.w
    bpl.w JutsuSelected
    move.w #6,$FFFFF182.w
JutsuSelected:
    move.w #120,$FFFFF2B2.w
    moveq #11,d0
    bsr.w SfxStart
JutsuSelectorConsume:
    andi.b #$BC,$FFFFC176.w
    andi.b #$BC,$FFFFC177.w
    clr.l $FFFFD030.w
    clr.l $FFFFD028.w
    bra.w JutsuTick
JutsuQuickCast:
    ; Up+B is now the taijutsu uppercut. Jutsus always use the A gesture.
    bra.w JutsuTick
JutsuBegin:
    tst.w $FFFFF162.w
    bne.w JutsuTick
    tst.w $FFFFF160.w
    bne.w JutsuTick
    move.b $FFFFD042.w,d1
    andi.b #$7F,d1
    beq.w JutsuGroundCheck
    cmpi.b #8,d1
    beq.w JutsuFromRun
    ; Keep an A tap made during melee recovery for up to 18 frames.
    cmpi.b #$C,d1
    beq.w JutsuBuffer
    cmpi.b #$10,d1
    beq.w JutsuBuffer
    bra.w JutsuTick
JutsuBuffer:
    move.w #18,$FFFFF2B4.w
    move.w d0,$FFFFF2B6.w
    bra.w JutsuTick
JutsuFromRun:
    clr.w $FFFFD042.w
JutsuGroundCheck:
    btst #5,$FFFFD003.w
    bne.w JutsuTick
    move.w d0,d2
    add.w d2,d2
    lea JutsuCosts(pc),a1
    move.w (a1,d2.w),d1
    cmp.w $FFFFF180.w,d1
    bhi.w JutsuTick
    sub.w d1,$FFFFF180.w
    clr.w $FFFFF2B4.w
    move.w d0,$FFFFF164.w
    move.w #72,$FFFFF160.w
    ; Original magic gives the caster a short, unmistakable anticipation.
    ; Freeze physics for six frames, then release the live technique.
    move.w #6,$FFFFF150.w
    move.w #120,$FFFFF162.w
    clr.w $FFFFF166.w
    clr.w $FFFFF15C.w
    addq.w #1,$FFFFF184.w
    movem.l d0-d2,-(sp)
    add.w d0,d0
    lea JutsuCastSounds(pc),a1
    move.w (a1,d0.w),d0
    bsr.w SfxStart
    movem.l (sp)+,d0-d2
    move.w $FFFFD01C.w,d1
    add.w $FFFFC210.w,d1
    move.w d1,$FFFFF174.w
    move.w d1,$FFFFF168.w
    move.w $FFFFD020.w,$FFFFF16C.w
    move.w $FFFFD018.w,$FFFFF16A.w
    move.w $FFFFD044.w,$FFFFF176.w
    cmpi.w #1,d0
    beq.w KamuiChoose
    moveq #40,d1
    btst #0,$FFFFF176.w
    beq.w JutsuSpawnSide
    neg.w d1
JutsuSpawnSide:
    add.w d1,$FFFFF168.w
    bsr.w JutsuMechanicsBegin
    bra.w JutsuTick
KamuiChoose:
    lea $FFFFD100.w,a0
    moveq #7,d7
    move.w #192,d5
KamuiChooseLoop:
    move.b (a0),d1
    andi.b #$7F,d1
    cmpi.b #$31,d1
    bcs.w KamuiChooseNext
    cmpi.b #$33,d1
    bhi.w KamuiChooseNext
    tst.b $64(a0)
    beq.w KamuiChooseNext
    move.w $1C(a0),d1
    sub.w $FFFFD01C.w,d1
    bpl.w KamuiChooseDistance
    neg.w d1
KamuiChooseDistance:
    cmp.w d5,d1
    bcc.w KamuiChooseNext
    move.w d1,d5
    move.w a0,$FFFFF166.w
    move.w $1C(a0),d1
    add.w $FFFFC210.w,d1
    move.w d1,$FFFFF168.w
    move.w $18(a0),$FFFFF16A.w
    move.w $20(a0),$FFFFF16C.w
KamuiChooseNext:
    lea $80(a0),a0
    dbf d7,KamuiChooseLoop
JutsuTick:
    tst.w $FFFFF160.w
    bne.w JutsuActiveTick
    tst.w $FFFFF2B4.w
    beq.w JutsuReturn
    subq.w #1,$FFFFF2B4.w
    tst.w $FFFFF162.w
    bne.w JutsuReturn
    move.b $FFFFD042.w,d0
    andi.b #$7F,d0
    bne.w JutsuReturn
    move.w $FFFFF2B6.w,d0
    bra.w JutsuBegin
JutsuActiveTick:
    bsr.w JutsuAbsorbShots
    tst.w $FFFFF150.w
    bne.w JutsuLockInput
    subq.w #1,$FFFFF160.w
    cmpi.w #56,$FFFFF160.w
    bne.w JutsuReleaseReady
    bsr.w JutsuReleaseAccent
JutsuReleaseReady:
    clr.l $FFFFD02C.w
    clr.l $FFFFD030.w
    cmpi.w #56,$FFFFF160.w
    bhi.w JutsuLockInput
    cmpi.w #16,$FFFFF160.w
    bcs.w JutsuLockInput
    move.w $FFFFF164.w,d0
    cmpi.w #1,d0
    beq.w KamuiContact
    cmpi.w #3,d0
    bcc.w ElementAdvance
    moveq #3,d1
    tst.w d0
    bne.w LightningSpeedReady
    moveq #6,d1
LightningSpeedReady:
    move.w d1,d2
    add.w d2,$FFFFF3F6.w
    btst #0,$FFFFF176.w
    beq.w LightningAdvance
    neg.w d1
LightningAdvance:
    add.w d1,$FFFFD01C.w
    move.w $FFFFD01C.w,d1
    cmpi.w #$A0,d1
    bcc.w LightningRightClamp
    move.w #$A0,$FFFFD01C.w
LightningRightClamp:
    cmpi.w #$1A0,d1
    bls.w LightningTargetX
    move.w #$1A0,$FFFFD01C.w
LightningTargetX:
    move.w $FFFFD01C.w,d1
    add.w $FFFFC210.w,d1
    moveq #40,d2
    btst #0,$FFFFF176.w
    beq.w LightningTargetSide
    neg.w d2
LightningTargetSide:
    add.w d2,d1
    move.w d1,$FFFFF168.w
    bra.w JutsuTargets
ElementAdvance:
    cmpi.w #5,d0
    beq.w EarthContact
    moveq #5,d1
    cmpi.w #6,d0
    bne.w ElementDirection
    moveq #6,d1
ElementDirection:
    btst #0,$FFFFF176.w
    beq.w ElementTravel
    neg.w d1
ElementTravel:
    add.w d1,$FFFFF168.w
    bra.w JutsuTargets
EarthContact:
    ; The wall hits while rising, then blocks. A single contact frame could
    ; miss a ninja that stepped through the edge between animation updates.
    cmpi.w #54,$FFFFF160.w
    bhi.w EarthWallBlock
    cmpi.w #42,$FFFFF160.w
    bcc.w JutsuTargets
EarthWallBlock:
    bsr.w EarthBlock
    bra.w JutsuLockInput
JutsuTargets:
    lea $FFFFD100.w,a0
    moveq #7,d6
JutsuTargetLoop:
    move.b (a0),d0
    andi.b #$7F,d0
    cmpi.b #$31,d0
    bcs.w JutsuTargetNext
    cmpi.b #$33,d0
    bhi.w JutsuTargetNext
    tst.b $64(a0)
    beq.w JutsuTargetNext
    move.w $20(a0),d0
    sub.w $FFFFF16C.w,d0
    bpl.w JutsuTargetLane
    neg.w d0
JutsuTargetLane:
    move.w $FFFFF164.w,d1
    add.w d1,d1
    lea JutsuLaneRanges(pc),a1
    cmp.w (a1,d1.w),d0
    bhi.w JutsuTargetNext
    move.w $1C(a0),d0
    add.w $FFFFC210.w,d0
    sub.w $FFFFF168.w,d0
    bpl.w JutsuTargetDistance
    neg.w d0
JutsuTargetDistance:
    lea JutsuDistanceRanges(pc),a1
    cmp.w (a1,d1.w),d0
    bhi.w JutsuTargetNext
    movem.l d6/a0,-(sp)
    bsr.w JutsuHit
    movem.l (sp)+,d6/a0
JutsuTargetNext:
    lea $80(a0),a0
    dbf d6,JutsuTargetLoop
    bra.w JutsuLockInput
KamuiContact:
    cmpi.w #24,$FFFFF160.w
    bne.w JutsuLockInput
    tst.w $FFFFF166.w
    beq.w JutsuLockInput
    movea.w $FFFFF166.w,a0
    tst.b $64(a0)
    beq.w JutsuLockInput
    bsr.w JutsuHit
JutsuLockInput:
    andi.b #$80,$FFFFC176.w
    andi.b #$80,$FFFFC177.w
JutsuReturn:
    rts
JutsuHit:
    moveq #6,d3
    cmpi.w #1,$FFFFF164.w
    bne.w JutsuDogDamage
    moveq #9,d3
JutsuDogDamage:
    cmpi.w #6,$FFFFF164.w
    bne.w JutsuDamageReady
    moveq #3,d3
JutsuDamageReady:
    bsr.w CustomHurt
    tst.w d0
    beq.w JutsuHitReturn
    bsr.w JutsuHitMotion
    move.w $FFFFF164.w,d0
    add.w d0,d0
    lea $FFFFF190.w,a1
    addq.w #1,(a1,d0.w)
    addq.w #1,$FFFFF16E.w
    cmpi.w #1,$FFFFF164.w
    bne.w JutsuDefeat
    addq.w #1,$FFFFF170.w
JutsuDefeat:
JutsuHitReturn:
    rts
JutsuCosts: dc.w 30,40,25,30,35,25,30
EffectFamilies: dc.w 0,1,2,3,4,5,6
JutsuCastSounds: dc.w 2,3,23,4,5,6,7

EarthBlock:
    lea $FFFFD100.w,a0
    moveq #2,d6
EarthBlockLoop:
    tst.b (a0)
    beq.w EarthBlockNext
    tst.b $64(a0)
    beq.w EarthBlockNext
    btst #6,$46(a0)
    bne.w EarthBlockNext
    move.w $20(a0),d0
    sub.w $FFFFF16C.w,d0
    bpl.w EarthBlockLane
    neg.w d0
EarthBlockLane:
    cmpi.w #24,d0
    bhi.w EarthBlockNext
    move.w $1C(a0),d0
    add.w $FFFFC210.w,d0
    sub.w $FFFFF168.w,d0
    move.w d0,d1
    bpl.w EarthBlockDistance
    neg.w d1
EarthBlockDistance:
    cmpi.w #32,d1
    bcc.w EarthBlockNext
    move.w $FFFFF168.w,d1
    sub.w $FFFFC210.w,d1
    tst.w d0
    bmi.w EarthBlockLeft
    addi.w #32,d1
    bra.w EarthBlockApply
EarthBlockLeft:
    subi.w #32,d1
EarthBlockApply:
    move.w d1,$1C(a0)
    clr.l $2C(a0)
    addq.w #1,$FFFFF3FA.w
EarthBlockNext:
    lea $80(a0),a0
    dbf d6,EarthBlockLoop
    rts

RenderJutsu:
    tst.w $FFFFF160.w
    beq.w RenderDotonWall
    moveq #16,d0
    cmpi.w #60,$FFFFF160.w
    bhi.w JutsuBodyPose
    moveq #17,d0
    cmpi.w #54,$FFFFF160.w
    bhi.w JutsuBodyPose
    move.w $FFFFF164.w,d1
    lea JutsuBodyPoses(pc),a1
    add.w d1,d1
    move.w (a1,d1.w),d0
    tst.w $FFFFF164.w
    bne.w JutsuBodyRecovery
    move.w $FFFFC17A.w,d0
    lsr.w #2,d0
    andi.w #3,d0
    add.w d0,d0
    addi.w #37,d0
JutsuBodyRecovery:
    cmpi.w #16,$FFFFF160.w
    bcc.w JutsuBodyPose
    moveq #15,d0
JutsuBodyPose:
    move.w d0,$FFFFD070.w
    move.l #KakashiCastMeta,$FFFFD00A.w
    cmpi.w #16,$FFFFF160.w
    bcc.w JutsuBodyInvulnerable
    cmpi.w #1,$FFFFF164.w
    beq.w JutsuBodyInvulnerable
    tst.w $FFFFF164.w
    bne.w JutsuBodyFacing
    cmpi.w #56,$FFFFF160.w
    bhi.w JutsuBodyFacing
JutsuBodyInvulnerable:
    move.l #KakashiJutsuMeta,$FFFFD00A.w
JutsuBodyFacing:
    btst #0,$FFFFF176.w
    beq.w JutsuEffectSetup
    move.l #KakashiCastLeftMeta,$FFFFD00A.w
    cmpi.w #16,$FFFFF160.w
    bcc.w JutsuBodyLeftInvulnerable
    cmpi.w #1,$FFFFF164.w
    beq.w JutsuBodyLeftInvulnerable
    tst.w $FFFFF164.w
    bne.w JutsuEffectSetup
    cmpi.w #56,$FFFFF160.w
    bhi.w JutsuEffectSetup
JutsuBodyLeftInvulnerable:
    move.l #KakashiJutsuLeftMeta,$FFFFD00A.w
JutsuEffectSetup:
    lea $FFFFD700.w,a0
    move.w $FFFFF164.w,d0
    add.w d0,d0
    lea EffectFamilies(pc),a1
    move.w (a1,d0.w),d0
    lsl.w #2,d0
    lea (EffectBankTable).l,a1
    move.l (a1,d0.w),d1
    cmp.l $74(a0),d1
    beq.w JutsuBankReady
    move.l d1,$74(a0)
    move.w #-1,$72(a0)
    clr.w $FFFFF1F6.w
JutsuBankReady:
    move.l #EffectDMA,$78(a0)
    moveq #72,d0
    sub.w $FFFFF160.w,d0
    cmpi.w #6,$FFFFF164.w
    bne.w EffectGrowthFrame
    lsr.w #3,d0
    andi.w #3,d0
    bra.w EffectPoseReady
EffectGrowthFrame:
    divu.w #12,d0
    andi.w #$FFFF,d0
    move.w $FFFFF164.w,d1
    mulu.w #6,d1
    add.w d1,d0
    lea JutsuAnimationPhrases(pc),a1
    move.b (a1,d0.w),d0
    andi.w #$FF,d0
EffectPoseReady:
    move.w d0,$70(a0)
    cmpi.w #-1,$72(a0)
    beq.w RenderJutsuReturn
    cmpi.w #64,$FFFFF160.w
    bhi.w RenderJutsuReturn
    move.b #$7F,(a0)
    clr.b $2(a0)
    clr.b $17(a0)
    move.w $FFFFF164.w,d0
    add.w d0,d0
    lea JutsuEffectPalettes(pc),a1
    move.w (a1,d0.w),d0
    move.b d0,$17(a0)
    move.w #$300,$8(a0)
    tst.w $FFFFF1F0.w
    beq.w EffectVisibleBank
    move.w #$360,$8(a0)
EffectVisibleBank:
    bsr.w JutsuTrimEffectMeta
JutsuEffectPosition:
    move.w $FFFFF168.w,d0
    sub.w $FFFFC210.w,d0
    ; Lightning starts in the hand, then grows into its travelling release.
    cmpi.w #56,$FFFFF160.w
    bls.w JutsuEffectWorldPosition
    tst.w $FFFFF164.w
    beq.w JutsuChargeHand
    cmpi.w #2,$FFFFF164.w
    bne.w JutsuEffectWorldPosition
JutsuChargeHand:
    move.w $FFFFD01C.w,d0
    moveq #16,d1
    btst #0,$FFFFF176.w
    beq.w JutsuChargeHandSide
    neg.w d1
JutsuChargeHandSide:
    add.w d1,d0
JutsuEffectWorldPosition:
    move.w d0,$1C(a0)
    move.w $FFFFF16C.w,d0
    addq.w #2,d0
    cmpi.w #5,$FFFFF164.w
    bne.w EffectDepthReady
    subq.w #4,d0
EffectDepthReady:
    move.w d0,$20(a0)
    move.w $FFFFF16A.w,d0
    cmpi.w #3,$FFFFF164.w
    bcc.w ElementFootAnchor
    cmpi.w #1,$FFFFF164.w
    beq.w ElementFootAnchor
    subi.w #16,d0
ElementFootAnchor:
    cmpi.w #3,$FFFFF164.w
    bne.w EffectFootAnchor
    subi.w #14,d0
EffectFootAnchor:
    move.w d0,$18(a0)
RenderJutsuReturn:
    rts
JutsuBodyPoses: dc.w 21,17,21,19,20,18,18
JutsuEffectPalettes: dc.w 0,0,0,$60,0,$60,$60

LegacyHUD:
    movem.l d0-a6,-(sp)
    tst.w $FFFFF10C.w
    bne.w ArcadeHUDReady
    move.w #1,$FFFFF10C.w
    move.l #$40000003,$00C00004
    move.w #$7FF,d0
ArcadeClearPlane:
    move.w #0,$00C00000
    dbf d0,ArcadeClearPlane
    move.l #$40000003,d7
    moveq #3,d5
ArcadePanelRow:
    move.l d7,$00C00004
    moveq #39,d6
ArcadePanelCell:
    move.w #$84C0,$00C00000
    dbf d6,ArcadePanelCell
    addi.l #$800000,d7
    dbf d5,ArcadePanelRow
    move.l #$40000003,d7
    move.w #$8490,d0
    moveq #3,d5
ArcadePortraitRow:
    move.l d7,$00C00004
    moveq #3,d6
ArcadePortraitCell:
    move.w d0,$00C00000
    addq.w #1,d0
    dbf d6,ArcadePortraitCell
    addi.l #$800000,d7
    dbf d5,ArcadePortraitRow
    lea ArcadeName(pc),a0
    move.l #$400A0003,d7
    bsr.w DrawHUDLabel
    lea ArcadeVillage(pc),a0
    move.l #$403C0003,d7
    bsr.w DrawHUDLabel
    move.l #$403A0003,$00C00004
    move.w #$84A4,$00C00000
    move.l #$41880003,$00C00004
    moveq #35,d0
ArcadePanelEdge:
    move.w #$84A7,$00C00000
    dbf d0,ArcadePanelEdge
ArcadeHUDReady:
    moveq #0,d3
    move.b $FFFFFE7E.w,d3
    divu.w #6,d3
    moveq #8,d4
    move.w #$84A0,d5
    move.w #$84A1,d6
    move.l #$408A0003,d7
    bsr.w DrawArcadeMeter
    move.w $FFFFF180.w,d3
    divu.w #20,d3
    moveq #6,d4
    move.w #$84A2,d5
    move.w #$84A3,d6
    move.l #$410A0003,d7
    bsr.w DrawArcadeMeter
    move.w $FFFFF182.w,d0
    lsl.w #2,d0
    lea (JutsuNames).l,a1
    movea.l (a1,d0.w),a0
    move.l #$40A60003,d7
    bsr.w DrawHUDLabel
    move.w $FFFFF182.w,d0
    add.w d0,d0
    lea EffectFamilies(pc),a1
    move.w (a1,d0.w),d0
    lsl.w #2,d0
    addi.w #$84A8,d0
    move.l #$40A00003,$00C00004
    move.w d0,$00C00000
    addq.w #1,d0
    move.w d0,$00C00000
    move.l #$41200003,$00C00004
    addq.w #1,d0
    move.w d0,$00C00000
    addq.w #1,d0
    move.w d0,$00C00000
    lea ArcadeReady(pc),a0
    tst.w $FFFFF162.w
    beq.w ArcadeCastStatus
    lea ArcadeRecharge(pc),a0
ArcadeCastStatus:
    move.l #$41260003,d7
    bsr.w DrawHUDLabel
    move.w $FFFFC210.w,d0
    divu.w #224,d0
    addq.w #1,d0
    divu.w #10,d0
    move.l #$40C00003,$00C00004
    addi.w #$84D0,d0
    move.w d0,$00C00000
    swap d0
    addi.w #$84D0,d0
    move.w d0,$00C00000
    move.w #$84CF,$00C00000
    move.w #$84D1,$00C00000
    move.w #$84D0,$00C00000
    lea ArcadeCombo(pc),a0
    move.l #$413C0003,d7
    bsr.w DrawHUDLabel
    move.w $FFFFF152.w,d0
    cmpi.w #9,d0
    bls.w ArcadeComboDigit
    moveq #9,d0
ArcadeComboDigit:
    addi.w #$84D0,d0
    move.l #$41460003,$00C00004
    move.w d0,$00C00000
    ; Erase inherited GO and bottom life glyphs; the street fills the viewport.
    move.l #$42B80003,d7
    moveq #5,d5
ArcadeEraseGO:
    move.l d7,$00C00004
    moveq #11,d6
ArcadeEraseGOCell:
    move.w #0,$00C00000
    dbf d6,ArcadeEraseGOCell
    addi.l #$800000,d7
    dbf d5,ArcadeEraseGO
    move.l #$4C000003,d7
    moveq #3,d5
ArcadeEraseBottom:
    move.l d7,$00C00004
    moveq #39,d6
ArcadeEraseBottomCell:
    move.w #0,$00C00000
    dbf d6,ArcadeEraseBottomCell
    addi.l #$800000,d7
    dbf d5,ArcadeEraseBottom
    movem.l (sp)+,d0-a6
    rts
DrawHUDLabel:
    move.l d7,$00C00004
HUDLabelLoop:
    moveq #0,d0
    move.b (a0)+,d0
    beq.w HUDLabelReturn
    subi.w #32,d0
    addi.w #$84C0,d0
    move.w d0,$00C00000
    bra.w HUDLabelLoop
HUDLabelReturn:
    rts
DrawArcadeMeter:
    move.l d7,$00C00004
    moveq #0,d1
ArcadeMeterLoop:
    move.w d6,d0
    cmp.w d3,d1
    bcc.w ArcadeMeterEmpty
    move.w d5,d0
ArcadeMeterEmpty:
    move.w d0,$00C00000
    addq.w #1,d1
    cmp.w d4,d1
    bcs.w ArcadeMeterLoop
    rts
ArcadeName: dc.b "KAKASHI",0
ArcadeVillage: dc.b "KONOHA",0
ArcadeCombo: dc.b "COMBO ",0
ArcadeReady: dc.b "A LISTO  ",0
ArcadeRecharge: dc.b "RECARGA  ",0
    even
JutsuNames: dc.l NameRaikiri,NameKamui,NameChidori,NameKaton,NameSuiton,NameDoton,NameNinken
NameRaikiri: dc.b "RAIKIRI  ",0
NameKamui: dc.b "KAMUI    ",0
NameChidori: dc.b "CHIDORI  ",0
NameKaton: dc.b "GOKAKYU  ",0
NameSuiton: dc.b "SUIRYUDAN",0
NameDoton: dc.b "DORYUHEKI",0
NameNinken: dc.b "NINKEN   ",0
    even

; 13 world objects. State 0 intact, 1 chakra scroll, 2 collected.
ObjectsUpdate:
    tst.w $FFFFF1E0.w
    beq.w ObjectsBegin
    subq.w #1,$FFFFF1E0.w
ObjectsBegin:
    lea ObjectLayout(pc),a3
    lea $FFFFF1A0.w,a4
    moveq #12,d7
ObjectLoop:
    cmpi.w #2,(a4)
    beq.w ObjectNext
    move.w $FFFFD01C.w,d0
    add.w $FFFFC210.w,d0
    subi.w #128,d0
    sub.w (a3),d0
    move.w d0,d2
    bpl.w ObjectAbsoluteX
    neg.w d2
ObjectAbsoluteX:
    move.w $FFFFD020.w,d1
    sub.w $2(a3),d1
    bpl.w ObjectAbsoluteY
    neg.w d1
ObjectAbsoluteY:
    tst.w (a4)
    beq.w ObjectIntact
    cmpi.w #120,$FFFFF180.w
    bcc.w ObjectNext
    cmpi.w #18,d2
    bhi.w ObjectNext
    cmpi.w #16,d1
    bhi.w ObjectNext
    move.w #2,(a4)
    addi.w #40,$FFFFF180.w
    cmpi.w #120,$FFFFF180.w
    bls.w ObjectChakraCapped
    move.w #120,$FFFFF180.w
ObjectChakraCapped:
    addq.w #1,$FFFFF1E8.w
    bra.w ObjectNext
ObjectIntact:
    cmpi.w #3,$4(a3)
    bcc.w ObjectSolid
    cmpi.w #32,d2
    bhi.w ObjectJutsuCheck
    cmpi.w #18,d1
    bhi.w ObjectJutsuCheck
    move.w d0,d3
    btst #0,$FFFFD044.w
    bne.w ObjectAttackSide
    neg.w d3
ObjectAttackSide:
    tst.w d3
    bmi.w ObjectJutsuCheck
    move.b $FFFFD042.w,d3
    andi.b #$7F,d3
    cmpi.b #$C,d3
    beq.w ObjectSwingFrame
    move.b $FFFFD043.w,d3
    cmpi.b #3,d3
    bcs.w ObjectJutsuCheck
    cmpi.b #10,d3
    bhi.w ObjectJutsuCheck
ObjectSwingFrame:
    ; A run-to-attack transition still carries the old stride frame until
    ; native initialization. Do not break wood before a swing is displayed.
    btst #7,$FFFFD042.w
    beq.w ObjectJutsuCheck
    cmpi.b #9,$FFFFD043.w
    beq.w ObjectDashContact
    cmpi.b #1,$FFFFD014.w
    bcs.w ObjectJutsuCheck
    bra.w ObjectBreak
ObjectDashContact:
    cmpi.w #13,$FFFFD070.w
    bne.w ObjectJutsuCheck
    bra.w ObjectBreak
ObjectJutsuCheck:
    tst.w $FFFFF160.w
    beq.w ObjectSolid
    cmpi.w #56,$FFFFF160.w
    bhi.w ObjectSolid
    move.w $FFFFF168.w,d3
    subi.w #128,d3
    sub.w (a3),d3
    bpl.w ObjectJutsuDistance
    neg.w d3
ObjectJutsuDistance:
    cmpi.w #32,d3
    bhi.w ObjectSolid
    move.w $FFFFF16C.w,d3
    sub.w $2(a3),d3
    bpl.w ObjectJutsuLane
    neg.w d3
ObjectJutsuLane:
    cmpi.w #20,d3
    bhi.w ObjectSolid
ObjectBreak:
    move.w #1,(a4)
    addq.w #1,$FFFFF1E6.w
    move.w #16,$FFFFF1E0.w
    move.w (a3),d3
    addi.w #128,d3
    move.w d3,$FFFFF1E2.w
    move.w $2(a3),$FFFFF1E4.w
    move.w #3,$FFFFF150.w
    moveq #1,d0
    movem.l d7/a3/a4,-(sp)
    bsr.w SfxStart
    movem.l (sp)+,d7/a3/a4
    bra.w ObjectNext
ObjectSolid:
    btst #5,$FFFFD003.w
    bne.w ObjectNext
    tst.w $FFFFF160.w
    bne.w ObjectNext
    cmpi.w #14,d2
    bcc.w ObjectNext
    cmpi.w #12,d1
    bcc.w ObjectNext
    move.w (a3),d3
    sub.w $FFFFC210.w,d3
    addi.w #128,d3
    tst.w d0
    bmi.w ObjectPushLeft
    addi.w #14,d3
    bra.w ObjectPushApply
ObjectPushLeft:
    subi.w #14,d3
ObjectPushApply:
    move.w d3,$FFFFD01C.w
ObjectNext:
    addq.l #6,a3
    addq.l #2,a4
    dbf d7,ObjectLoop
    rts
RenderObjects:
    lea ObjectLayout(pc),a3
    lea $FFFFF1A0.w,a4
    lea $FFFFDB80.w,a0
    moveq #3,d6
    moveq #12,d7
ObjectDrawLoop:
    cmpi.w #2,(a4)
    beq.w ObjectDrawNext
    move.w (a3),d0
    sub.w $FFFFC210.w,d0
    addi.w #128,d0
    cmpi.w #112,d0
    bcs.w ObjectDrawNext
    cmpi.w #464,d0
    bhi.w ObjectDrawNext
    move.w d0,$1C(a0)
    move.w $2(a3),d0
    move.w d0,$20(a0)
    addi.w #128,d0
    move.w d0,$18(a0)
    move.w $4(a3),d0
    tst.w (a4)
    beq.w ObjectDrawKind
    moveq #3,d0
    move.w $FFFFC17A.w,d1
    lsr.w #3,d1
    andi.w #3,d1
    sub.w d1,$18(a0)
ObjectDrawKind:
    move.w d0,d1
    lsl.w #4,d1
    lea (PropTrimMetas).l,a1
    adda.w d1,a1
    move.l a1,$A(a0)
    mulu.w #24,d0
    addi.w #$400,d0
    move.w d0,$8(a0)
    move.b #$7F,(a0)
    clr.b $2(a0)
    move.b #$60,$17(a0)
    lea $80(a0),a0
    subq.w #1,d6
    bmi.w ObjectDrawDebris
ObjectDrawNext:
    addq.l #6,a3
    addq.l #2,a4
    dbf d7,ObjectDrawLoop
ObjectDrawDebris:
    tst.w $FFFFF1E0.w
    beq.w ObjectDrawReturn
    lea $FFFFD500.w,a0
    move.b #$7F,(a0)
    clr.b $2(a0)
    move.b #$60,$17(a0)
    move.w $FFFFF1E2.w,d0
    sub.w $FFFFC210.w,d0
    move.w d0,$1C(a0)
    move.w $FFFFF1E4.w,d0
    move.w d0,$20(a0)
    addi.w #128,d0
    move.w d0,$18(a0)
    move.w #$460,$8(a0)
    move.l #PropTrimMetas+64,$A(a0)
ObjectDrawReturn:
    rts
ObjectLayout:
    dc.w 128,172,0,288,196,1,496,128,2,688,172,0
    dc.w 912,196,1,1168,128,5,1328,172,0,1536,192,1
    dc.w 1696,128,2,1888,172,0,2080,196,1,2304,172,0,2448,208,5
    even

ObjectComboRange:
    lea ObjectLayout(pc),a0
    lea $FFFFF1A0.w,a1
    moveq #12,d7
ObjectComboLoop:
    tst.w (a1)
    bne.w ObjectComboNext
    cmpi.w #3,$4(a0)
    bcc.w ObjectComboNext
    move.w $2(a0),d0
    sub.w $FFFFD020.w,d0
    bpl.w ObjectComboLane
    neg.w d0
ObjectComboLane:
    cmpi.w #18,d0
    bhi.w ObjectComboNext
    move.w (a0),d0
    addi.w #128,d0
    sub.w $FFFFC210.w,d0
    sub.w $FFFFD01C.w,d0
    btst #0,$FFFFD044.w
    beq.w ObjectComboFacing
    neg.w d0
ObjectComboFacing:
    tst.w d0
    bmi.w ObjectComboNext
    cmpi.w #36,d0
    bhi.w ObjectComboNext
    moveq #1,d0
    rts
ObjectComboNext:
    addq.l #6,a0
    addq.l #2,a1
    dbf d7,ObjectComboLoop
    moveq #0,d0
    rts
