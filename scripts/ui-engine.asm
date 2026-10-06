; Two-row shinobi headband HUD with quarter-tile meters and damage trail.
CustomHUD:
    movem.l d0-a6,-(sp)
    tst.w $FFFFF10C.w
    bne.w UIInitialized
    move.w #1,$FFFFF10C.w
    move.l #$40000003,$00C00004
    move.w #$7FF,d0
UIClearPlane:
    move.w #0,$00C00000
    dbf d0,UIClearPlane
UIInitialized:
    bsr.w DrawStoryPanel
    ; Erase the dialogue first; rebuild the HUD on the following frame.
    cmpi.w #2,$FFFFF348.w
    beq.w UIReturn
    tst.w $FFFFF204.w
    bne.w UIReturn
    tst.w $FFFFF292.w
    bne.w UIDynamic
    move.w #1,$FFFFF292.w
    lea $FFFFF2C0.w,a0
    moveq #7,d0
UICacheClear:
    move.w #-1,(a0)+
    dbf d0,UICacheClear
    move.l #$4D000003,d7
    moveq #1,d5
    move.w #$82F8,d2
UIPanelRows:
    move.l d7,$00C00004
    moveq #39,d6
UIPanelCells:
    move.w d2,$00C00000
    dbf d6,UIPanelCells
    addi.l #$800000,d7
    addq.w #1,d2
    dbf d5,UIPanelRows
    lea UIFrameCells(pc),a0
    moveq #11,d0
UIFrameCell:
    move.l (a0)+,$00C00004
    move.w (a0)+,$00C00000
    dbf d0,UIFrameCell
    move.l #$4D020003,d7
    move.w #$8490,d0
    moveq #1,d5
UIFaceRow:
    move.l d7,$00C00004
    moveq #1,d6
UIFaceCell:
    move.w d0,$00C00000
    addq.w #1,d0
    dbf d6,UIFaceCell
    addi.l #$800000,d7
    dbf d5,UIFaceRow
    move.l #$4D060003,$00C00004
    move.w #$84FE,$00C00000
    move.l #$4D860003,$00C00004
    move.w #$82FD,$00C00000
    move.l #$4D220003,$00C00004
    move.w #$82FC,$00C00000
    move.w #$84D9,$00C00000
UIDynamic:
    moveq #0,d3
    move.b $FFFFFE7E.w,d3
    cmpi.w #-1,$FFFFF2C0.w
    bne.w UIHealthChanged
    move.w d3,$FFFFF36E.w
    clr.w $FFFFF370.w
UIHealthChanged:
    cmp.w $FFFFF2C0.w,d3
    bcc.w UIHealthClamp
    move.w #18,$FFFFF370.w
UIHealthClamp:
    cmp.w $FFFFF36E.w,d3
    bcs.w UIHealthDecay
    move.w d3,$FFFFF36E.w
    clr.w $FFFFF370.w
    bra.w UIHealthDraw
UIHealthDecay:
    tst.b $FFFFC175.w
    bne.w UIHealthDraw
    tst.w $FFFFF150.w
    bne.w UIHealthDraw
    tst.w $FFFFF370.w
    beq.w UIHealthDrain
    subq.w #1,$FFFFF370.w
    bra.w UIHealthDraw
UIHealthDrain:
    move.w $FFFFC17A.w,d0
    andi.w #3,d0
    bne.w UIHealthDraw
    subq.w #1,$FFFFF36E.w
UIHealthDraw:
    cmp.w $FFFFF2C0.w,d3
    bne.w UIHealthRedraw
    move.w $FFFFF36E.w,d2
    cmp.w $FFFFF372.w,d2
    beq.w UIChakra
UIHealthRedraw:
    move.w d3,$FFFFF2C0.w
    move.w $FFFFF36E.w,d2
    move.w d2,$FFFFF372.w
    moveq #12,d4
    move.l #$4D080003,d7
    bsr.w DrawHealthTrail
UIChakra:
    moveq #0,d3
    move.w $FFFFF180.w,d3
    mulu.w #4,d3
    divu.w #10,d3
    andi.w #$FFFF,d3
    cmp.w $FFFFF2C2.w,d3
    beq.w UISelected
    move.w d3,$FFFFF2C2.w
    moveq #12,d4
    move.w #$82EE,d5
    move.l #$4D880003,d7
    bsr.w DrawSmoothMeter
UISelected:
    moveq #0,d0
    move.w $FFFFF182.w,d0
    cmp.w $FFFFF2C4.w,d0
    beq.w UICooldown
    move.w d0,$FFFFF2C4.w
    lsl.w #2,d0
    lea UIJutsuNames(pc),a1
    movea.l (a1,d0.w),a0
    move.l #$4D300003,d7
    bsr.w DrawHUDLabel
    move.w $FFFFF182.w,d0
    add.w d0,d0
    lea EffectFamilies(pc),a1
    move.w (a1,d0.w),d0
    cmpi.w #6,d0
    beq.w UINinkenIcon
    lsl.w #2,d0
    addi.w #$84A8,d0
    bra.w UIIconReady
UINinkenIcon:
    move.w #$8494,d0
UIIconReady:
    move.l #$4D2A0003,$00C00004
    move.w d0,$00C00000
    addq.w #1,d0
    move.w d0,$00C00000
    move.l #$4DAA0003,$00C00004
    addq.w #1,d0
    move.w d0,$00C00000
    addq.w #1,d0
    move.w d0,$00C00000
UICooldown:
    moveq #0,d3
    move.w #120,d3
    sub.w $FFFFF162.w,d3
    mulu.w #4,d3
    divu.w #15,d3
    andi.w #$FFFF,d3
    cmp.w $FFFFF2C6.w,d3
    beq.w UICombo
    move.w d3,$FFFFF2C6.w
    moveq #8,d4
    move.w #$82F3,d5
    move.l #$4DB00003,d7
    bsr.w DrawSmoothMeter
UICombo:
    moveq #0,d0
    move.w $FFFFF152.w,d0
    cmp.w $FFFFF2C8.w,d0
    beq.w UIHints
    move.w d0,$FFFFF2C8.w
    move.l #$4D440003,$00C00004
    moveq #5,d1
UIComboClear:
    move.w #$82FE,$00C00000
    dbf d1,UIComboClear
    cmpi.w #2,d0
    bcs.w UIHints
    cmpi.w #99,d0
    bls.w UIComboValue
    moveq #99,d0
UIComboValue:
    divu.w #10,d0
    move.l #$4D440003,$00C00004
    addi.w #$84D0,d0
    move.w d0,$00C00000
    swap d0
    addi.w #$84D0,d0
    move.w d0,$00C00000
    lea UIHit(pc),a0
    move.l #$4D4A0003,d7
    bsr.w DrawHUDLabel
UIHints:
    moveq #0,d0
    cmpi.w #2,$FFFFF2BA.w
    beq.w UIHintActive
    tst.w $FFFFF2B2.w
    beq.w UIHintState
UIHintActive:
    moveq #1,d0
UIHintState:
    cmp.w $FFFFF2CA.w,d0
    beq.w UIClearNative
    move.w d0,$FFFFF2CA.w
    lea UIHintBlank(pc),a0
    tst.w d0
    beq.w UIHintLabel
    lea UIHint(pc),a0
UIHintLabel:
    move.l #$4DC40003,d7
    bsr.w DrawHUDLabel
UIClearNative:
    move.l #$42B80003,d7
    moveq #5,d5
UIGO:
    move.l d7,$00C00004
    moveq #11,d6
UIGOCell:
    move.w #0,$00C00000
    dbf d6,UIGOCell
    addi.l #$800000,d7
    dbf d5,UIGO
    ; The native health routine still writes its old orange blocks at y=200.
    ; Clear those two foreground rows; the new panel starts at y=208.
    move.l #$4C000003,d7
    moveq #1,d5
UINativeBarsRows:
    move.l d7,$00C00004
    moveq #39,d6
UINativeBarsCells:
    move.w #0,$00C00000
    dbf d6,UINativeBarsCells
    addi.l #$800000,d7
    dbf d5,UINativeBarsRows
    moveq #0,d0
    tst.w $FFFFF220.w
    beq.w UIBossState
    tst.b $FFFFD100.w
    beq.w UIBossState
    move.w $FFFFF282.w,d0
    addq.w #1,d0
UIBossState:
    cmp.w $FFFFF2CC.w,d0
    beq.w UIReturn
    move.w d0,$FFFFF2CC.w
    move.l #$40000003,d7
    moveq #1,d5
    moveq #0,d2
    tst.w d0
    beq.w UIBossClearRows
    move.w #$82F8,d2
UIBossClearRows:
    move.l d7,$00C00004
    moveq #39,d6
UIBossClearCells:
    move.w d2,$00C00000
    dbf d6,UIBossClearCells
    addi.l #$800000,d7
    tst.w d2
    beq.w UIBossNextRow
    addq.w #1,d2
UIBossNextRow:
    dbf d5,UIBossClearRows
    tst.w d0
    beq.w UIReturn
    move.l #$40220003,$00C00004
    move.w #$82FF,$00C00000
    move.l #$404C0003,$00C00004
    move.w #$82FB,$00C00000
    lea UIBossName(pc),a0
    move.l #$40020003,d7
    bsr.w DrawHUDLabel
    lea HUDSharingan(pc),a0
    tst.w $FFFFF284.w
    beq.w UIBossTitle
    lea HUDMangekyo(pc),a0
UIBossTitle:
    move.l #$40820003,d7
    bsr.w DrawHUDLabel
    moveq #0,d3
    move.w $FFFFF282.w,d3
    mulu.w #4,d3
    divu.w #3,d3
    moveq #20,d4
    move.w #$82E9,d5
    move.l #$40240003,d7
    bsr.w DrawSmoothMeter
UIReturn:
    movem.l (sp)+,d0-a6
    rts
UIBossName: dc.b "ITACHI",0
UIHit: dc.b "HIT",0
UIHint: dc.b "ELEGIR",0
UIHintBlank: dc.b "      ",0
    even
; Quantity is in quarter-tile units; all five native meter tiles are used.
DrawSmoothMeter:
    move.l d7,$00C00004
UISmoothCell:
    move.w d3,d0
    cmpi.w #4,d0
    bls.w UISmoothLevel
    moveq #4,d0
UISmoothLevel:
    add.w d5,d0
    move.w d0,$00C00000
    subq.w #4,d3
    bcc.w UISmoothNext
    moveq #0,d3
UISmoothNext:
    subq.w #1,d4
    bne.w UISmoothCell
    rts
DrawHealthTrail:
    move.l d7,$00C00004
    lea UIHealthTrailTiles(pc),a1
UIHealthCell:
    move.w d3,d0
    cmpi.w #4,d0
    bls.w UIHealthLevel
    moveq #4,d0
UIHealthLevel:
    move.w d2,d1
    cmpi.w #4,d1
    bls.w UITrailLevel
    moveq #4,d1
UITrailLevel:
    mulu.w #5,d0
    add.w d1,d0
    add.w d0,d0
    move.w (a1,d0.w),$00C00000
    subq.w #4,d3
    bcc.w UIHealthNext
    moveq #0,d3
UIHealthNext:
    subq.w #4,d2
    bcc.w UITrailNext
    moveq #0,d2
UITrailNext:
    subq.w #1,d4
    bne.w UIHealthCell
    rts
UIHealthTrailTiles:
    dc.w $82E9,$82F4,$82F5,$82F6,$82F7
    dc.w $82EA,$82EA,$8498,$8499,$849A
    dc.w $82EB,$82EB,$82EB,$849B,$849C
    dc.w $82EC,$82EC,$82EC,$82EC,$849D
    dc.w $82ED,$82ED,$82ED,$82ED,$82ED
UIFrameCells:
    dc.l $4D000003
    dc.w $82FA
    dc.l $4D800003
    dc.w $82FA
    dc.l $4D4E0003
    dc.w $82FB
    dc.l $4DCE0003
    dc.w $82FB
    dc.l $4D200003
    dc.w $82FB
    dc.l $4DA00003
    dc.w $82FB
    dc.l $4D280003
    dc.w $82FA
    dc.l $4DA80003
    dc.w $82FA
    dc.l $4D2E0003
    dc.w $82FB
    dc.l $4DAE0003
    dc.w $82FB
    dc.l $4D400003
    dc.w $82FB
    dc.l $4DC00003
    dc.w $82FB
    even
UIJutsuNames: dc.l UIJutsu0,UIJutsu1,UIJutsu2,UIJutsu3,UIJutsu4,UIJutsu5,UIJutsu6
UIJutsu0: dc.b "RAIKIRI ",0
UIJutsu1: dc.b "KAMUI   ",0
UIJutsu2: dc.b "CHIDORI ",0
UIJutsu3: dc.b "KATON   ",0
UIJutsu4: dc.b "SUITON  ",0
UIJutsu5: dc.b "DOTON   ",0
UIJutsu6: dc.b "NINKEN  ",0
    even
