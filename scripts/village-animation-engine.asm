; Background NPCs. D960..7F are unused cache fields of the D900 shadow.
; +60 age, +62 resident frame, +64 paints, +66 bytes, +68 maximum bytes,
; +6A copied tiles. No additional sprite actor or combat hitbox is created.
VillageAnimationTick:
    move.w #1,$FFFFD96E.w
    addq.w #1,$FFFFD960.w
    rts

; Scene streaming always installs the current resident animation frame.
; The dense logical-tile lookup makes reverse scroll equally inexpensive.
VillageNpcSource:
    movem.l d0-d2/a1,-(sp)
    move.w d0,d2
    mulu.w #32,d0
    lea (SceneAllTiles).l,a6
    adda.l d0,a6
    add.w d2,d2
    lea (SceneNpcLookup).l,a1
    move.w (a1,d2.w),d1
    beq.w VillageSourceDone
    subq.w #1,d1
    move.w $FFFFD962.w,d0
    lea (SceneNpcIndex).l,a1
    mulu.w (a1),d0
    add.w d1,d0
    mulu.w #32,d0
    lea (SceneNpcTiles).l,a6
    adda.l d0,a6
VillageSourceDone:
    movem.l (sp)+,d0-d2/a1
    rts

VillageAnimationUpload:
    tst.w $FFFFD96E.w
    beq.w VillageAnimationReturn
    tst.w $FFFFF2E0.w
    beq.w VillageAnimationReturn
    tst.b $FFFFC175.w
    bne.w VillageAnimationReturn
    tst.w $FFFFF204.w
    bne.w VillageAnimationReturn
    tst.w $FFFFF160.w
    bne.w VillageAnimationReturn
    tst.w $FFFFF150.w
    bne.w VillageAnimationReturn
    ; Use a VBlank with no actor pose transfers. Background gestures can wait
    ; a few frames; controller polling and combat DMA must keep their cadence.
    tst.w $FFFFF1FC.w
    bne.w VillageAnimationReturn
    move.w $FFFFD960.w,d5
    lsr.w #5,d5
    andi.w #3,d5
    cmp.w $FFFFD962.w,d5
    beq.w VillageAnimationReturn
    lea (SceneNpcIndex).l,a3
    move.w (a3)+,d4
    subq.w #1,d4
    bmi.w VillageAnimationReturn
    move.w $FFFFF2E2.w,d2
    subq.w #1,d2
    move.w d2,d3
    addi.w #42,d3
    ; Check the complete batch before writing any tiles, so a delayed upload
    ; never leaves half a person in the old phase and half in the new one.
    move.w d4,d1
    movea.l a3,a1
    moveq #0,d6
VillageBudgetLoop:
    move.w (a1),d0
    cmp.w d2,d0
    blt.w VillageBudgetNext
    cmp.w d3,d0
    bgt.w VillageBudgetNext
    addi.w #32,d6
VillageBudgetNext:
    adda.w #8,a1
    dbf d1,VillageBudgetLoop
    add.w $FFFFF1FC.w,d6
    cmpi.w #4096,d6
    bhi.w VillageAnimationReturn
    clr.w $FFFFD966.w
    clr.w $FFFFD96A.w
    clr.w $FFFFD96C.w
    move.w d5,d0
    lea (SceneNpcIndex).l,a1
    mulu.w (a1),d0
    mulu.w #32,d0
    lea (SceneNpcTiles).l,a5
    adda.l d0,a5
VillagePaintLoop:
    moveq #1,d1
    move.w (a3),d0
    cmp.w d2,d0
    blt.w VillagePaintNext
    cmp.w d3,d0
    bgt.w VillagePaintNext
    movea.l a3,a1
    adda.w #8,a1
    move.w $2(a3),d0
    addq.w #1,d0
    move.w $4(a3),d6
    addq.w #1,d6
VillageRunExtend:
    cmp.w d4,d1
    bhi.w VillageRunReady
    move.w (a3),d7
    cmp.w (a1),d7
    bne.w VillageRunReady
    cmp.w $2(a1),d0
    bne.w VillageRunReady
    cmp.w $4(a1),d6
    bne.w VillageRunReady
    addq.w #1,d1
    addq.w #1,d0
    addq.w #1,d6
    adda.w #8,a1
    bra.w VillageRunExtend
VillageRunReady:
    movem.l d0-a6,-(sp)
    moveq #0,d7
    move.w $2(a3),d7
    lsl.w #5,d7
    move.w d7,d0
    lsr.w #8,d0
    lsr.w #6,d0
    andi.w #3,d0
    andi.l #$3FFF,d7
    swap d7
    ori.l #$40000000,d7
    or.w d0,d7
    moveq #0,d0
    move.w $4(a3),d0
    mulu.w #32,d0
    movea.l a5,a6
    adda.l d0,a6
    movem.l a6/d7,-(sp)
    move.w d1,d6
    lsl.w #4,d6
    jsr ($FFFFF410).w
    movem.l (sp)+,d7/a6
    move.l d7,$00C00004
    move.w (a6),$00C00000
    movem.l (sp)+,d0-a6
    add.w d1,$FFFFD96A.w
    addq.w #1,$FFFFD96C.w
    move.w d1,d0
    lsl.w #5,d0
    add.w d0,$FFFFF1FC.w
    add.w d0,$FFFFD966.w
VillagePaintNext:
    sub.w d1,d4
    addq.w #1,d4
    move.w d1,d0
    lsl.w #3,d0
    adda.w d0,a3
    dbf d4,VillagePaintLoop
    move.w d5,$FFFFD962.w
    addq.w #1,$FFFFD964.w
    move.w $FFFFD966.w,d0
    cmp.w $FFFFD968.w,d0
    bls.w VillageAnimationReturn
    move.w d0,$FFFFD968.w
VillageAnimationReturn:
    rts
