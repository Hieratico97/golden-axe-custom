; Main-loop metadata uses the pose scheduled for the next VBlank upload.
; Native hurt/attack markers stay unchanged. Four planned pointers F34C..35B,
; four planned poses F35C..363. No extra work in the VBlank transfer window.
PlanSpriteTrims:
    move.w $FFFFC17A.w,$FFFFF374.w
    clr.w $FFFFF364.w
    clr.w $FFFFF366.w
    move.w #2048,d6
TrimPlanHero:
    lea $FFFFD000.w,a0
    lea $FFFFF34C.w,a2
    lea $FFFFF35C.w,a3
    bsr.w PlanActorTrim
    moveq #0,d0
    move.w $FFFFC17A.w,d0
    divu.w #3,d0
    swap d0
    mulu.w #24,d0
    lea (ActorDMAOrders).l,a1
    adda.l d0,a1
    moveq #2,d5
TrimPlanLoop:
    movea.l (a1)+,a0
    addq.l #4,a1
    lea $FFFFF350.w,a2
    lea $FFFFF35E.w,a3
    cmpa.w #$D100,a0
    beq.s TrimPlanReady
    addq.l #4,a2
    addq.l #2,a3
    cmpa.w #$D180,a0
    beq.s TrimPlanReady
    addq.l #4,a2
    addq.l #2,a3
TrimPlanReady:
    movem.l d5/a1,-(sp)
    bsr.w PlanActorTrim
    movem.l (sp)+,d5/a1
    dbf d5,TrimPlanLoop
    rts

PlanActorTrim:
    clr.l (a2)
    moveq #0,d0
    move.w $72(a0),d0
    move.l $74(a0),d4
    btst #7,(a0)
    beq.w TrimPlanStore
    tst.l d4
    beq.w TrimPlanStore
    move.w $70(a0),d1
    cmp.w d0,d1
    beq.s TrimPlannedPose
    cmpi.w #65,d1
    bcc.s TrimPlannedPose
    cmpi.w #2048,d6
    bcs.s TrimPlannedPose
    move.w d1,d0
    subi.w #2048,d6
TrimPlannedPose:
    cmpi.w #65,d0
    bcc.w TrimPlanStore
    moveq #65,d3
    lea (ActorTrimUnionKakashi).l,a4
    cmpi.l #KakashiTiles,d4
    beq.s TrimPlanPointer
    cmpi.w #20,d0
    bcc.s TrimPlanStore
    moveq #20,d3
    lea (ActorTrimUnionNinja).l,a4
    cmpi.l #NinjaTiles,d4
    beq.s TrimPlanPointer
    lea (ActorTrimUnionAnbu).l,a4
    cmpi.l #AnbuTiles,d4
    beq.s TrimPlanPointer
    lea (ActorTrimUnionRenegado).l,a4
    cmpi.l #RenegadoTiles,d4
    beq.s TrimPlanPointer
    lea (ActorTrimUnionItachi).l,a4
    cmpi.l #ItachiTiles,d4
    bne.s TrimPlanStore
TrimPlanPointer:
    moveq #0,d1
    move.w $72(a0),d1
    cmp.w d3,d1
    bcs.s TrimPlanOldValid
    move.w d3,d1
TrimPlanOldValid:
    mulu.w d3,d1
    add.w d0,d1
    mulu.w #48,d1
    adda.l d1,a4
    btst #0,$44(a0)
    beq.s TrimPlanFacingReady
    adda.w #24,a4
TrimPlanFacingReady:
    move.l a4,(a2)
TrimPlanStore:
    move.w d0,(a3)
    rts

; Replace the native piece writer, keeping its depth order and linked SAT.
; Actor geometry is precomputed; every omitted column is transparent.
CustomSpriteEntry:
    bsr.w DamageSpritePosition
    move.l $A(a0),d1
    beq.w TrimSpriteEntryDone
    movea.l d1,a1
    moveq #0,d1
    move.b (a1)+,d1
    move.b (a1)+,$4(a0)
    move.b (a1)+,$5(a0)
    moveq #0,d4
    cmpa.w #$D000,a0
    beq.s TrimEntryHero
    cmpa.w #$D100,a0
    beq.s TrimEntryFirst
    cmpa.w #$D180,a0
    beq.s TrimEntrySecond
    cmpa.w #$D200,a0
    bne.s TrimEntryMetaReady
    move.l $FFFFF358.w,d4
    bra.s TrimEntryMetaReady
TrimEntryHero:
    move.l $FFFFF34C.w,d4
    bra.s TrimEntryMetaReady
TrimEntryFirst:
    move.l $FFFFF350.w,d4
    bra.s TrimEntryMetaReady
TrimEntrySecond:
    move.l $FFFFF354.w,d4
TrimEntryMetaReady:
    tst.l d4
    beq.s TrimEntryNativeBody
    movea.l d4,a1
    move.b (a1)+,d1
    addq.w #1,$FFFFF364.w
TrimEntryNativeBody:
    movea.w $FFFFC184.w,a2
TrimEntryPiece:
    move.b (a1)+,d0
    ext.w d0
    add.w d2,d0
    move.w d0,(a2)+
    move.b (a1)+,(a2)+
    move.b d7,(a2)+
    addq.b #1,d7
    andi.b #$7F,d7
    move.b (a1)+,d0
    move.b (a1)+,d4
    add.b $9(a0),d4
    move.b d4,$1(a2)
    move.b $8(a0),d4
    addx.b d4,d0
    or.b $17(a0),d0
    move.b d0,(a2)
    addq.w #2,a2
    move.b (a1)+,d0
    ext.w d0
    add.w d3,d0
    andi.w #$1FF,d0
    bne.s TrimEntryXReady
    moveq #1,d0
TrimEntryXReady:
    move.w d0,(a2)+
    cmpi.w #448,d0
    bcc.s TrimEntryHide
    cmpi.w #128,d0
    bcc.s TrimEntryNext
    moveq #0,d4
    move.b -6(a2),d4
    lsr.w #2,d4
    andi.w #3,d4
    addq.w #1,d4
    lsl.w #3,d4
    add.w d4,d0
    cmpi.w #128,d0
    bhi.s TrimEntryNext
TrimEntryHide:
    clr.w -8(a2)
    addq.w #1,$FFFFF366.w
TrimEntryNext:
    dbf d1,TrimEntryPiece
    move.w a2,$FFFFC184.w
TrimSpriteEntryDone:
    rts

JutsuTrimEffectMeta:
    move.w $FFFFF164.w,d0
    add.w d0,d0
    lea EffectFamilies(pc),a1
    move.w (a1,d0.w),d0
    lsl.w #2,d0
    lea (EffectTrimMetaTable).l,a1
    movea.l (a1,d0.w),a1
    moveq #0,d0
    move.w $72(a0),d0
    mulu.w #128,d0
    adda.l d0,a1
    btst #0,$FFFFF176.w
    beq.s JutsuTrimFacingReady
    adda.w #64,a1
JutsuTrimFacingReady:
    move.l a1,$A(a0)
    rts

; Same native depth buckets and stable entity order. Unroll their clears and
; visit only the occupied depth span instead of 256 empty rows every frame.
CustomDepthRender:
    tst.w $FFFFF376.w
    bne.s TrimDepthSetup
    move.w #1,$FFFFF376.w
    lea $00FF6000,a6
    moveq #63,d7
TrimDepthClear:
    clr.b (a6)
    clr.b $20(a6)
    clr.b $40(a6)
    clr.b $60(a6)
    lea $80(a6),a6
    dbf d7,TrimDepthClear
TrimDepthSetup:
    lea $FFFFD000.w,a0
    lea $00FF6000,a6
    moveq #63,d7
    moveq #0,d0
    moveq #0,d2
    move.w #$FFFF,d5
    moveq #0,d6
TrimDepthActor:
    tst.b (a0)
    beq.s TrimDepthNext
    btst #7,$2(a0)
    bne.s TrimDepthNext
    move.w $18(a0),d2
    move.w d2,d3
    subi.w #$70,d3
    cmpi.w #$130,d3
    bhi.s TrimDepthNext
    move.w $1C(a0),d3
    move.w d3,d4
    subi.w #$20,d4
    cmpi.w #$1E0,d4
    bcc.s TrimDepthNext
    cmpi.w #$20,d4
    bcs.s TrimDepthNext
    move.w $20(a0),d1
    andi.w #$1FE,d1
    lsl.w #4,d1
    cmp.w d5,d1
    bcc.s TrimDepthMinReady
    move.w d1,d5
TrimDepthMinReady:
    cmp.w d6,d1
    bls.s TrimDepthMaxReady
    move.w d1,d6
TrimDepthMaxReady:
    lea (a6,d1.w),a1
    moveq #0,d4
    move.b (a1),d4
    lea $1(a1,d4.w),a2
    move.b d0,(a2)
    addq.b #1,(a1)
TrimDepthNext:
    lea $80(a0),a0
    addq.w #1,d0
    dbf d7,TrimDepthActor
    cmpi.w #$FFFF,d5
    beq.s TrimDepthEnd
    adda.w d6,a6
    sub.w d5,d6
    lsr.w #5,d6
    lea $FFFFD000.w,a4
    moveq #1,d7
TrimDepthBucket:
    movea.l a6,a5
    tst.b (a5)
    beq.s TrimDepthPrevious
    moveq #0,d5
    move.b (a5)+,d5
    ; Every occupied bucket is consumed once. Reset its count immediately;
    ; unused buckets stay empty instead of clearing all 256 on every frame.
    clr.b -1(a5)
    subq.w #1,d5
    cmpi.w #$20,d5
    bcs.s TrimDepthCountReady
    moveq #$1F,d5
TrimDepthCountReady:
    moveq #0,d4
    move.b (a5)+,d4
    lsl.l #7,d4
    lea (a4,d4.w),a0
    bsr.w CustomSpriteEntry
    dbf d5,TrimDepthCountReady
TrimDepthPrevious:
    lea -$20(a6),a6
    dbf d6,TrimDepthBucket
TrimDepthEnd:
    movea.w $FFFFC184.w,a2
    clr.l (a2)+
    clr.l (a2)+
    move.w a2,$FFFFC184.w
    bsr.w TrimPropFetchBudget
    rts

; Protect actors and attack drawings from the H40 fetch limit. Equipment,
; shadows and landing dust may yield a piece in any crowded combat frame.
; Eight-line buckets are conservative, use 436 temporary stack bytes, and keep
; the original SAT links/depth intact. F36C counts deferred pieces this frame.
TrimPropFetchBudget:
    clr.w $FFFFF36C.w
    ; Ten hardware pieces cannot exceed either H40 per-line limit.
    move.w $FFFFC184.w,d0
    subi.w #$CB08,d0
    cmpi.w #80,d0
    bls.w TrimFetchReturn
TrimFetchStart:
    lea -436(sp),sp
    movea.l sp,a3
    lea 116(a3),a5
    movea.l a5,a4
    moveq #0,d6
    movea.l a3,a1
    moveq #28,d0
TrimFetchClear:
    clr.l (a1)+
    dbf d0,TrimFetchClear
    movea.w $FFFFC184.w,a6
    subq.l #8,a6
    moveq #0,d5
TrimFetchPass:
    lea $FFFFCB00.w,a0
TrimFetchEntry:
    cmpa.l a6,a0
    bcc.w TrimFetchPassDone
    ; Fully hidden pieces have no fetch cost. Reject them before classification.
    move.w (a0),d0
    andi.w #$1FF,d0
    cmpi.w #96,d0
    bls.w TrimFetchNext
    cmpi.w #352,d0
    bcc.w TrimFetchNext
    move.w $4(a0),d4
    andi.w #$7FF,d4
    moveq #0,d7
    cmpi.w #$2C1,d4
    bcs.s TrimFetchPropKind
    cmpi.w #$2CC,d4
    bcs.s TrimFetchOptional
TrimFetchPropKind:
    cmpi.w #$400,d4
    bcs.s TrimFetchKind
    cmpi.w #$490,d4
    bcc.s TrimFetchKind
TrimFetchOptional:
    moveq #1,d7
TrimFetchKind:
    tst.w d7
    beq.s TrimFetchGeometry
    ; Retain optional pointers once. The second pass visits only these pieces.
    move.l a0,(a4)+
    addq.w #1,d6
    bra.w TrimFetchNext
TrimFetchGeometry:
    move.w (a0),d0
    andi.w #$1FF,d0
    subi.w #128,d0
    moveq #0,d1
    move.b $2(a0),d1
    move.w d1,d2
    andi.w #3,d1
    addq.w #1,d1
    lsl.w #3,d1
    add.w d0,d1
    subq.w #1,d1
    bmi.w TrimFetchNext
    cmpi.w #224,d0
    bge.w TrimFetchNext
    tst.w d0
    bpl.s TrimFetchTop
    moveq #0,d0
TrimFetchTop:
    cmpi.w #223,d1
    ble.s TrimFetchBottom
    move.w #223,d1
TrimFetchBottom:
    lsr.w #3,d0
    lsr.w #3,d1
    sub.w d0,d1
    lsl.w #2,d0
    lea (a3,d0.w),a1
    lsr.w #2,d2
    andi.w #3,d2
    addq.w #1,d2
    lsl.w #3,d2
    move.w d2,d7
    swap d7
    move.w #1,d7
    tst.w d5
    beq.s TrimFetchDifference
    movea.l a1,a2
    move.w d1,d3
TrimFetchCheck:
    move.w (a2),d4
    add.w d2,d4
    cmpi.w #320,d4
    bhi.s TrimFetchDefer
    cmpi.w #20,$2(a2)
    bcc.s TrimFetchDefer
    addq.l #4,a2
    dbf d3,TrimFetchCheck
    bra.s TrimFetchAdd
TrimFetchDifference:
    ; Mandatory ranges use two endpoint updates. Their prefix sum is built
    ; once, avoiding repeated bucket writes for every actor piece.
    add.l d7,(a1)
    move.w d1,d0
    lsl.w #2,d0
    sub.l d7,4(a1,d0.w)
    bra.s TrimFetchNext
TrimFetchAdd:
    ; Packed width/count adds share one memory operation. Sprite height is
    ; at most 32px, hence at most five touched eight-line buckets.
    move.w d1,d0
    addq.w #1,d0
    add.w d0,d0
    neg.w d0
    lea TrimFetchAddEnd(pc),a2
    jmp (a2,d0.w)
    add.l d7,(a1)+
    add.l d7,(a1)+
    add.l d7,(a1)+
    add.l d7,(a1)+
    add.l d7,(a1)+
TrimFetchAddEnd:
    bra.s TrimFetchNext
TrimFetchDefer:
    clr.w (a0)
    addq.w #1,$FFFFF36C.w
TrimFetchNext:
    tst.w d5
    bne.s TrimFetchOptionalNext
    addq.l #8,a0
    bra.w TrimFetchEntry
TrimFetchOptionalNext:
    subq.w #1,d6
    beq.s TrimFetchDone
    movea.l (a4)+,a0
    bra.w TrimFetchGeometry
TrimFetchPassDone:
    tst.w d6
    beq.s TrimFetchDone
    movea.l a3,a1
    moveq #0,d7
    moveq #27,d0
TrimFetchPrefix:
    add.l (a1),d7
    move.l d7,(a1)+
    dbf d0,TrimFetchPrefix
    moveq #1,d5
    movea.l a5,a4
    movea.l (a4)+,a0
    bra.w TrimFetchGeometry
TrimFetchDone:
    lea 436(sp),sp
TrimFetchReturn:
    rts
