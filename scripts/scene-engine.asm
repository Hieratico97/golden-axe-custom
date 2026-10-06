; Precomputed tile lifetimes: large Konoha art without a runtime tile hash.
; 0000..4FFF scene, 5000..57FF reserved for a third independent ninja bank.
; F2E0 initialized, F2E2 camera column, F2E4 bytes this VBlank,
; F2E6 maximum tile bytes, F2E8 loaded columns, F2EA reverse columns.
CustomSceneMapInit:
    movem.l d0-a6,-(sp)
    lea (SceneInitialMap).l,a6
    move.l #$60000003,d7
    movem.l a6/d7,-(sp)
    move.w #4096,d6
    jsr ($FFFFF410).w
    movem.l (sp)+,d7/a6
    move.l d7,$00C00004
    move.w (a6),$00C00000
    move.w #1,$FFFFF2E0.w
    clr.w $FFFFF2E2.w
    movem.l (sp)+,d0-a6
    rts

CustomSceneScroll:
    bclr #6,$FFFFC200.w
    rts

CustomSceneUpload:
    clr.w $FFFFF2E4.w
    tst.w $FFFFF2E0.w
    beq.w SceneUploadReturn
    move.w $FFFFC210.w,d2
    lsr.w #3,d2
    cmpi.w #280,d2
    bls.w SceneCameraValid
    move.w #280,d2
SceneCameraValid:
    move.w $FFFFF2E2.w,d5
    cmp.w d2,d5
    beq.w SceneUploadReturn
    bhi.w SceneMoveLeft
SceneMoveRight:
    addq.w #1,d5
    moveq #2,d3
    bsr.w SceneLoadEvent
    move.w d5,d0
    addi.w #41,d0
    bsr.w SceneMapColumn
    addq.w #1,$FFFFF2E8.w
    cmp.w d2,d5
    bcs.w SceneMoveRight
    bra.w SceneUploadDone
SceneMoveLeft:
    moveq #4,d3
    bsr.w SceneLoadEvent
    subq.w #1,d5
    move.w d5,d0
    subq.w #1,d0
    bsr.w SceneMapColumn
    addq.w #1,$FFFFF2E8.w
    addq.w #1,$FFFFF2EA.w
    cmp.w d2,d5
    bhi.w SceneMoveLeft
SceneUploadDone:
    move.w d5,$FFFFF2E2.w
    move.w $FFFFF2E4.w,d0
    cmp.w $FFFFF2E6.w,d0
    bls.w SceneUploadReturn
    move.w d0,$FFFFF2E6.w
SceneUploadReturn:
    rts

SceneLoadEvent:
    move.w d5,d0
    lsl.w #2,d0
    lea (SceneEventOffsets).l,a3
    move.l (a3,d0.w),d0
    lea (SceneEvents).l,a3
    adda.l d0,a3
    move.w (a3)+,d4
    subq.w #1,d4
    bmi.w SceneEventReturn
SceneEventTile:
    movem.l d0-a6,-(sp)
    moveq #0,d7
    move.w (a3),d7
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
    move.w (a3,d3.w),d0
    bsr.w VillageNpcSource
    movem.l a6/d7,-(sp)
    move.w #16,d6
    jsr ($FFFFF410).w
    movem.l (sp)+,d7/a6
    move.l d7,$00C00004
    move.w (a6),$00C00000
    addi.w #32,$FFFFF2E4.w
    movem.l (sp)+,d0-a6
    adda.w #6,a3
    dbf d4,SceneEventTile
SceneEventReturn:
    rts

SceneMapColumn:
    movem.l d0-a6,-(sp)
    move.w d0,d1
    andi.w #63,d1
    add.w d1,d1
    swap d1
    clr.w d1
    ori.l #$60000003,d1
    tst.w d0
    bpl.w SceneColumnNonnegative
    moveq #0,d0
SceneColumnNonnegative:
    cmpi.w #319,d0
    bls.w SceneColumnValid
    move.w #319,d0
SceneColumnValid:
    mulu.w #56,d0
    lea (SceneColumns).l,a6
    adda.l d0,a6
    move.w #$8F80,$00C00004
    move.l d1,$00C00004
    moveq #27,d0
SceneMapWrite:
    move.w (a6)+,$00C00000
    dbf d0,SceneMapWrite
    move.w #$8F02,$00C00004
    movem.l (sp)+,d0-a6
    rts
