; Mangekyo has its own pursuit, flank changes, two clones and a second flame.
; F2EC phase cue, F2EE transitions, F2F0 pattern, F2F2 extra-flame delay,
; F2F4 life, F2F6 X, F2F8 lane, F2FA velocity, F2FC contact, F2FE casts.
BossPhaseUpdate:
    tst.w $FFFFF2EC.w
    beq.w BossPhaseHealth
    subq.w #1,$FFFFF2EC.w
BossPhaseHealth:
    tst.w $FFFFF284.w
    bne.w BossPhaseReturn
    tst.b $FFFFD164.w
    ble.w BossPhaseReturn
    cmpi.b #30,$FFFFD164.w
    bhi.w BossPhaseReturn
    move.w #1,$FFFFF284.w
    move.w #18,$FFFFF2EC.w
    addq.w #1,$FFFFF2EE.w
    clr.w $FFFFF2F0.w
    clr.w $FFFFF226.w
    clr.w $FFFFF224.w
    move.w #30,$FFFFF222.w
    moveq #8,d0
    bsr.w SfxStart
    move.w #1,$FFFFF322.w
    clr.w $FFFFF22A.w
    clr.w $FFFFF2F2.w
    clr.w $FFFFF2F4.w
    moveq #7,d0
    moveq #8,d1
    bsr.w StoryBegin
BossPhaseReturn:
    rts

; Native enemy contact reaches this gate before subtracting health. Boss and
; clones share a faction; player melee, kunai and jutsus keep native routing.
CustomEnemyDamage:
    tst.w $FFFFF220.w
    beq.w EnemyDamageAllowed
    movea.l $38(a0),a1
    cmpa.l #$FFFFD100,a1
    bcs.w EnemyDamageAllowed
    cmpa.l #$FFFFD200,a1
    bhi.w EnemyDamageAllowed
    btst #7,(a1)
    beq.w EnemyDamageAllowed
    bclr #6,$3(a0)
    bclr #6,$4E(a0)
    bclr #1,$3(a0)
    addq.w #1,$FFFFF324.w
    rts
EnemyDamageAllowed:
    bclr #6,$3(a0)
    bclr #6,$4E(a0)
    jmp (EnemyDamageNative).l

BossMangekyoNextPattern:
    bsr.w BossPhaseReposition
    addq.w #1,$FFFFF2F0.w
    cmpi.w #6,$FFFFF2F0.w
    bcs.w BossPatternValid
    clr.w $FFFFF2F0.w
BossPatternValid:
    move.w $FFFFF2F0.w,d0
    add.w d0,d0
    lea BossMangekyoPatterns(pc),a1
    move.w (a1,d0.w),$FFFFF226.w
    rts
BossMangekyoPatterns: dc.w 0,1,2,2,1,0

BossPhaseReposition:
    ; Crow dispersal changes flank; fire/clone casts leave an opening to punish.
    cmpi.w #1,$FFFFF226.w
    bne.w BossPhaseReturn
    btst #6,$FFFFD146.w
    bne.w BossPhaseReturn
    cmpi.b #$C,$FFFFD143.w
    bcc.w BossPhaseReturn
    tst.b $FFFFD164.w
    ble.w BossPhaseReturn
    move.w $FFFFD11C.w,$FFFFF288.w
    move.w $FFFFD120.w,$FFFFF28A.w
    move.w #20,$FFFFF286.w
    move.w #384,d0
    cmpi.w #288,$FFFFD01C.w
    bls.w BossFlankX
    move.w #192,d0
BossFlankX:
    move.w d0,$FFFFD11C.w
    move.w $FFFFD020.w,d0
    addi.w #24,d0
    btst #0,$FFFFF2F1.w
    beq.w BossFlankLane
    subi.w #48,d0
BossFlankLane:
    cmpi.w #132,d0
    bcc.w BossFlankLowerBound
    move.w #132,d0
BossFlankLowerBound:
    cmpi.w #198,d0
    bls.w BossFlankGround
    move.w #198,d0
BossFlankGround:
    move.w d0,$FFFFD120.w
    addi.w #128,d0
    move.w d0,$FFFFD118.w
    clr.l $FFFFD12C.w
    clr.l $FFFFD130.w
    addq.w #1,$FFFFF3EC.w
    rts

BossSpawnClone:
    tst.b (a0)
    bne.w BossSpawnReturn
    movea.l a0,a1
    moveq #31,d0
BossSpawnClear:
    clr.l (a1)+
    dbf d0,BossSpawnClear
    move.w #$3300,(a0)
    move.b #8,$64(a0)
    move.l #ItachiTiles,$74(a0)
    move.w #-1,$72(a0)
    moveq #18,d1
    moveq #-48,d2
    cmpa.w #$D180,a0
    bne.w BossSpawnSecond
    bset #0,$FFFFF2D1.w
    bra.w BossSpawnPlace
BossSpawnSecond:
    bset #1,$FFFFF2D1.w
    moveq #-18,d1
    moveq #48,d2
BossSpawnPlace:
    move.w $FFFFD120.w,d0
    add.w d1,d0
    cmpi.w #132,d0
    bcc.w BossSpawnLowerBound
    move.w #132,d0
BossSpawnLowerBound:
    cmpi.w #202,d0
    bls.w BossSpawnGround
    move.w #202,d0
BossSpawnGround:
    move.w d0,$20(a0)
    addi.w #128,d0
    move.w d0,$18(a0)
    move.w #$8000,$24(a0)
    move.w $FFFFD11C.w,d0
    add.w d2,d0
    cmpi.w #160,d0
    bcc.w BossSpawnRightBound
    move.w #160,d0
BossSpawnRightBound:
    cmpi.w #416,d0
    bls.w BossSpawnX
    move.w #416,d0
BossSpawnX:
    move.w d0,$1C(a0)
    addq.w #1,$FFFFC26C.w
    addq.w #1,$FFFFF236.w
    move.w #24,$FFFFF286.w
    move.w $1C(a0),$FFFFF288.w
    move.w $20(a0),$FFFFF28A.w
    moveq #9,d0
    bsr.w SfxStart
BossSpawnReturn:
    rts

BossSecondFireTick:
    tst.w $FFFFF2F2.w
    beq.w BossSecondFireMove
    subq.w #1,$FFFFF2F2.w
    bne.w BossSecondFireMove
    move.w #72,$FFFFF2F4.w
    move.w $FFFFD11C.w,$FFFFF2F6.w
    move.w $FFFFD020.w,d0
    addi.w #24,d0
    cmpi.w #204,d0
    bls.w BossSecondFireLane
    move.w #156,d0
BossSecondFireLane:
    move.w d0,$FFFFF2F8.w
    move.w $FFFFF230.w,$FFFFF2FA.w
    clr.w $FFFFF2FC.w
    addq.w #1,$FFFFF2FE.w
BossSecondFireMove:
    tst.w $FFFFF2F4.w
    beq.w BossSecondFireReturn
    subq.w #1,$FFFFF2F4.w
    move.w $FFFFF2FA.w,d0
    add.w d0,$FFFFF2F6.w
    tst.w $FFFFF2FC.w
    bne.w BossSecondFireReturn
    btst #5,$FFFFD003.w
    bne.w BossSecondFireReturn
    tst.w $FFFFF160.w
    beq.w BossSecondVulnerable
    cmpi.w #16,$FFFFF160.w
    bcc.w BossSecondFireReturn
    cmpi.w #1,$FFFFF164.w
    beq.w BossSecondFireReturn
BossSecondVulnerable:
    move.w $FFFFF2F8.w,d0
    sub.w $FFFFD020.w,d0
    bpl.w BossSecondLane
    neg.w d0
BossSecondLane:
    cmpi.w #19,d0
    bhi.w BossSecondFireReturn
    move.w $FFFFF2F6.w,d0
    sub.w $FFFFD01C.w,d0
    bpl.w BossSecondDistance
    neg.w d0
BossSecondDistance:
    cmpi.w #28,d0
    bhi.w BossSecondFireReturn
    move.w #1,$FFFFF2FC.w
    addq.w #1,$FFFFF23C.w
    addq.w #1,$FFFFF3FC.w
    move.b #4,$FFFFD007.w
    bset #1,$FFFFD003.w
    move.l #$FFFFD100,$FFFFD038.w
BossSecondFireReturn:
    rts

RenderBossSecondFire:
    tst.w $FFFFF2F4.w
    beq.w BossSecondFireReturn
    lea $FFFFDD80.w,a0
    move.b #$7F,(a0)
    clr.b $2(a0)
    move.b #$60,$17(a0)
    move.w $FFFFF2F6.w,$1C(a0)
    move.w $FFFFF2F8.w,d0
    move.w d0,$20(a0)
    addi.w #112,d0
    move.w d0,$18(a0)
    move.w #$3C0,$8(a0)
    move.l #BossFireMeta,$A(a0)
    tst.w $FFFFF2FA.w
    bpl.w BossSecondFireReturn
    move.l #BossFireLeftMeta,$A(a0)
    rts
