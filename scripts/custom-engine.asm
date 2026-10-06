; Kakashi - Konoha. Solo player, streamed jutsu, interactive street props.
; Private RAM $FFF100-$FFF3FF. Temporary artwork slots are display-only
; and are cleared before native entity dispatch.

CustomBoot:
    jsr (loc_34BC).l
    lea $FFFFF100.w,a0
    move.w #191,d0
WeaponClear:
    clr.l (a0)+
    dbf d0,WeaponClear
    lea $FFFFD960.w,a0
    moveq #7,d0
VillageCacheClear:
    clr.l (a0)+
    dbf d0,VillageCacheClear
    move.w #120,$FFFFF180.w
    lea $FFFFC200.w,a0
    move.w #$147,d0
BootClear:
    clr.l (a0)+
    dbf d0,BootClear
    clr.w $FFFFFE2C.w
    move.w #2,$FFFFC104.w
    move.w #$0909,$FFFFFE7C.w
    move.w #$3030,$FFFFFE7E.w
    clr.w $FFFFFE80.w
    clr.b $FFFFFE83.w
    bsr.w AudioInit
    move.l #KakashiAnimations,$FFFFFE84.w
    move.l #KakashiDMA,$FFFFFE88.w
    move.w #$C,$FFFFC170.w
    jmp (loc_DA6).l

CustomEntities:
    cmpi.w #3,$FFFFF200.w
    bcs.w CustomContinue
    tst.w $FFFFC26C.w
    bne.w CustomContinue
    move.w #$18,$FFFFC170.w
CustomContinue:
    clr.w $FFFFD96E.w
    clr.b $FFFFD500.w
    clr.b $FFFFD580.w
    clr.b $FFFFD600.w
    clr.b $FFFFD680.w
    clr.b $FFFFD700.w
    clr.b $FFFFD780.w
    clr.b $FFFFD800.w
    clr.b $FFFFD880.w
    clr.b $FFFFD900.w
    clr.b $FFFFD980.w
    clr.b $FFFFDA00.w
    clr.b $FFFFDA80.w
    clr.b $FFFFDB00.w
    clr.b $FFFFDB80.w
    clr.b $FFFFDC00.w
    clr.b $FFFFDC80.w
    clr.b $FFFFDD00.w
    clr.b $FFFFDD80.w
    movem.l d0-a6,-(sp)
    move.b $FFFFC176.w,$FFFFF2B0.w
    bsr.w AudioTick
    bsr.w StoryAndBossUpdate
    tst.w $FFFFF204.w
    beq.w StoryGameplay
    move.b $FFFFD042.w,d0
    andi.b #$7F,d0
    cmpi.b #$68,d0
    bne.w StoryPlayerIdle
    clr.w $FFFFD042.w
StoryPlayerIdle:
    lea (SpritePalette).l,a6
    jsr (loc_2ED0).l
    lea (SpritePalette).l,a6
    jsr (loc_2EB4).l
    lea (EnemyPalette).l,a6
    jsr (loc_2ED0).l
    lea (EnemyPalette).l,a6
    jsr (loc_2EB4).l
    lea (EnemyPalette2).l,a6
    jsr (loc_2ED0).l
    lea (EnemyPalette2).l,a6
    jsr (loc_2EB4).l
    bsr.w SfxTick
    movem.l (sp)+,d0-a6
    move.w #$CB00,$FFFFC184.w
    jmp (CustomRender).l
StoryGameplay:
    bsr.w JutsuUpdate
    bsr.w ComboInput
    tst.w $FFFFF150.w
    beq.w CombatRunning
    subq.w #1,$FFFFF150.w
    bsr.w UpdateImpactSound
    movem.l (sp)+,d0-a6
    move.w #$CB00,$FFFFC184.w
    jmp (CustomRender).l
CombatRunning:
    bsr.w VillageAnimationTick
    ; Our player starts inside the screen: skip the inherited auto-entry/tutorial.
    move.b $FFFFD042.w,d0
    andi.b #$7F,d0
    cmpi.b #$68,d0
    bne.w PlayerEntryDone
    clr.w $FFFFD042.w
    clr.l $FFFFD02C.w
PlayerEntryDone:
    bsr.w CustomWeapons
    bsr.w ObjectsUpdate
    andi.b #$BF,$FFFFC176.w
    andi.b #$BF,$FFFFC177.w
EasyMode:
    move.b #9,$FFFFFE7C.w
    ; Gentle health regeneration keeps the requested very easy difficulty.
    move.b $FFFFC17B.w,d0
    andi.b #$1F,d0
    bne.w EasyNinjas
    cmpi.b #$30,$FFFFFE7E.w
    bcc.w EasyNinjas
    addq.b #1,$FFFFFE7E.w
EasyNinjas:
    lea $FFFFD100.w,a0
    moveq #7,d7
EasyNinjaLoop:
    move.b (a0),d0
    andi.b #$7F,d0
    cmpi.b #$31,d0
    bcs.w EasyNinjaNext
    cmpi.b #$33,d0
    bhi.w EasyNinjaNext
    move.b #$20,$17(a0)
    cmpi.b #$33,d0
    bne.w EasyNinjaHealth
    move.b #$40,$17(a0)
EasyNinjaHealth:
    bsr.w NinjaMoveStyle
    tst.b $64(a0)
    ble.w EasyNinjaNext
    tst.w $FFFFF220.w
    beq.w EasyOrdinaryNinja
    cmpa.w #$D100,a0
    beq.w EasyNinjaNext
    cmpa.w #$D180,a0
    beq.w EasyCloneHealth
    cmpa.w #$D200,a0
    bne.w EasyOrdinaryNinja
EasyCloneHealth:
    cmpi.b #8,$64(a0)
    bls.w EasyNinjaNext
    move.b #8,$64(a0)
    bra.w EasyNinjaNext
EasyOrdinaryNinja:
    cmpi.b #6,$64(a0)
    bls.w EasyNinjaNext
    move.b #6,$64(a0)
EasyNinjaNext:
    lea $80(a0),a0
    dbf d7,EasyNinjaLoop
    lea (SpritePalette).l,a6
    jsr (loc_2ED0).l
    lea (SpritePalette).l,a6
    jsr (loc_2EB4).l
    lea (EnemyPalette).l,a6
    jsr (loc_2ED0).l
    lea (EnemyPalette).l,a6
    jsr (loc_2EB4).l
    lea (EnemyPalette2).l,a6
    jsr (loc_2ED0).l
    lea (EnemyPalette2).l,a6
    jsr (loc_2EB4).l
    movem.l (sp)+,d0-a6
    jmp (loc_B954).l

CustomRender:
    movem.l d0-a6,-(sp)
    bsr.w DamageObserve
    bsr.w RenderPlayerMotion
    bsr.w RenderPlayerCombo
    bsr.w CustomDamagePoses
    bsr.w DamagePaletteFlash
    bsr.w RenderLandingDust
    bsr.w RenderObjects
    bsr.w RenderWeapons
    bsr.w RenderJutsu
    bsr.w RenderStoryAndBoss
    bsr.w JutsuWorldFeedbackRender
    lea $FFFFD000.w,a0
    lea $FFFFD900.w,a1
    bsr.w RenderShadow
    lea $FFFFD100.w,a0
    lea $FFFFDA00.w,a1
    bsr.w RenderShadow
    lea $FFFFD180.w,a0
    lea $FFFFDA80.w,a1
    bsr.w RenderShadow
    lea $FFFFD200.w,a0
    lea $FFFFD580.w,a1
    bsr.w RenderShadow
    ; Restore physical held buttons before the next poll derives its edges.
    move.b $FFFFF2B0.w,$FFFFC176.w
    bsr.w PlanSpriteTrims
    movem.l (sp)+,d0-a6
    jmp (CustomDepthRender).l

; Native physics decides launch and landing; only the displayed drawing changes.
CustomDamagePoses:
    bsr.w PlayerDamagePose
    lea $FFFFD100.w,a0
    bsr.w NinjaDamagePose
    lea $FFFFD180.w,a0
    bsr.w NinjaDamagePose
    lea $FFFFD200.w,a0
    bsr.w NinjaDamagePose
    rts
NinjaDamagePose:
    ; A newly spawned native entity has no DMA table until bit 7 is set.
    btst #7,(a0)
    beq.w NinjaDamageDone
    move.b (a0),d0
    andi.b #$7F,d0
    cmpi.b #$31,d0
    bcs.w NinjaDamageDone
    cmpi.b #$33,d0
    bhi.w NinjaDamageDone
    lea (NinjaTiles).l,a1
    cmpi.b #$32,d0
    bne.w NinjaChooseCaptain
    lea (AnbuTiles).l,a1
NinjaChooseCaptain:
    cmpi.b #$33,d0
    bne.w NinjaSetCostume
    lea (RenegadoTiles).l,a1
NinjaSetCostume:
    tst.w $FFFFF220.w
    beq.w NinjaSetBank
    cmpa.w #$D100,a0
    beq.w NinjaItachiBank
    cmpa.w #$D180,a0
    beq.w NinjaItachiBank
    cmpa.w #$D200,a0
    bne.w NinjaSetBank
NinjaItachiBank:
    lea (ItachiTiles).l,a1
    move.b #$20,$17(a0)
NinjaSetBank:
    cmpa.l $74(a0),a1
    beq.w NinjaCostumeReady
    move.l a1,$74(a0)
    move.w #-1,$72(a0)
NinjaCostumeReady:
    bsr.w DamageActorState
    tst.w $C(a2)
    beq.w NinjaBossCastPose
    tst.b $64(a0)
    ble.w NinjaBossCastPose
    cmpi.b #$C,$43(a0)
    bcc.w NinjaBossCastPose
    moveq #18,d0
    cmpi.w #2,$E(a2)
    bne.w NinjaPinnedDrawing
    moveq #19,d0
NinjaPinnedDrawing:
    move.w d0,$70(a0)
    bra.w NinjaDamageDone
NinjaBossCastPose:
    cmpa.w #$D100,a0
    bne.w NinjaCheckDamage
    tst.w $FFFFF220.w
    beq.w NinjaCheckDamage
    tst.w $FFFFF224.w
    beq.w NinjaCheckDamage
    tst.b $64(a0)
    ble.w NinjaCheckDamage
    cmpi.b #$C,$43(a0)
    bcc.w NinjaCheckDamage
    moveq #5,d0
    cmpi.w #50,$FFFFF224.w
    bhi.w NinjaDamageApply
    moveq #6,d0
    cmpi.w #40,$FFFFF224.w
    bhi.w NinjaDamageApply
    moveq #15,d0
    tst.w $FFFFF226.w
    beq.w NinjaDamageApply
    moveq #8,d0
    cmpi.w #1,$FFFFF226.w
    beq.w NinjaDamageApply
    moveq #7,d0
    bra.w NinjaDamageApply
NinjaCheckDamage:
    move.b $43(a0),d0
    cmpi.b #$1A,d0
    beq.w NinjaAirPose
    cmpi.b #$18,d0
    beq.w NinjaFloorPose
    cmpi.b #$D,d0
    bcs.w NinjaDamageDone
    cmpi.b #$17,d0
    bhi.w NinjaDamageDone
    bsr.w DamageActorState
    moveq #9,d0
    cmpi.w #8,$2(a2)
    bcc.w NinjaStaggerApply
    moveq #10,d0
    cmpi.w #4,$2(a2)
    bcc.w NinjaStaggerApply
    moveq #15,d0
NinjaStaggerApply:
    ; Head/body impacts, low sweeps and electric stuns have distinct silhouettes.
    cmpi.w #11,$2(a2)
    bcs.w NinjaStaggerLate
    moveq #16,d0
    cmpi.w #2,$6(a2)
    bne.w NinjaStaggerBodyReady
    moveq #17,d0
NinjaStaggerBodyReady:
    cmpi.w #3,$6(a2)
    bne.w NinjaStaggerElectric
    moveq #18,d0
NinjaStaggerElectric:
    cmpi.w #6,$6(a2)
    bne.w NinjaStaggerLate
    moveq #19,d0
NinjaStaggerLate:
    ; Keep the native stagger hitbox so the next strike can continue the combo.
    move.w d0,$70(a0)
    rts
NinjaFloorPose:
    moveq #14,d0
    tst.b $64(a0)
    ble.w NinjaDamageApply
    bsr.w DamageActorState
    cmpi.w #3,$6(a2)
    bne.w NinjaDamageApply
    moveq #18,d0
    bra.w NinjaDamageApply
NinjaAirPose:
    moveq #10,d0
    btst #7,$42(a0)
    beq.w NinjaDamageApply
    moveq #14,d0
    btst #6,$46(a0)
    beq.w NinjaDamageApply
    moveq #12,d0
    bsr.w DamageActorState
    cmpi.w #6,$6(a2)
    bne.w NinjaAirVelocity
    moveq #19,d0
NinjaAirVelocity:
    tst.l $34(a0)
    bmi.w NinjaDamageApply
    moveq #13,d0
NinjaDamageApply:
    move.w d0,$70(a0)
    lea (NinjaFallMeta).l,a1
    btst #0,$44(a0)
    beq.w NinjaDamageMeta
    lea (NinjaFallLeftMeta).l,a1
NinjaDamageMeta:
    move.l a1,$A(a0)
NinjaDamageDone:
    rts

; Change only grounded pursuit speed. Native attacks, damage and jumps remain.
NinjaMoveStyle:
    cmpi.b #$32,d0
    bcs.w NinjaMoveDone
    btst #6,$46(a0)
    bne.w NinjaMoveDone
    cmpi.b #2,$43(a0)
    bhi.w NinjaMoveDone
    tst.l $2C(a0)
    beq.w NinjaMoveDone
    move.l #$14000,d1
    cmpi.b #$33,d0
    bne.w NinjaMoveSign
    move.l #$C000,d1
    tst.w $FFFFF220.w
    beq.w NinjaMoveSign
    tst.w $FFFFF284.w
    beq.w NinjaMoveSign
    move.l #$14000,d1
    cmpa.w #$D100,a0
    bne.w NinjaMoveSign
    move.l #$18000,d1
NinjaMoveSign:
    tst.l $2C(a0)
    bpl.w NinjaMoveApply
    neg.l d1
NinjaMoveApply:
    move.l d1,$2C(a0)
NinjaMoveDone:
    rts

RenderShadow:
    ; The release flash washes out contact shadows for its short climax.
    cmpi.w #64,$FFFFF160.w
    bhi.w ShadowVisible
    cmpi.w #16,$FFFFF160.w
    bcc.w ShadowReturn
ShadowVisible:
    tst.b (a0)
    beq.w ShadowReturn
    move.b #$7F,(a1)
    clr.b $2(a1)
    clr.b $17(a1)
    move.w $20(a0),d0
    move.w d0,$20(a1)
    addi.w #128,d0
    sub.w $FFFFC20C.w,d0
    move.w d0,$18(a1)
    move.w $1C(a0),$1C(a1)
    move.w #$2C8,$8(a1)
    move.l #ShadowMeta,$A(a1)
ShadowReturn:
    rts

CustomPauseGate:
    tst.w $FFFFF204.w
    beq.w PauseAllowToggle
    tst.b $FFFFC175.w
    rts
PauseAllowToggle:
    movem.l d0-a6,-(sp)
    move.b $FFFFC175.w,d6
    btst #1,$FFFFC105.w
    beq.w PauseCheckSecondPlayer
    btst #7,$FFFFC177.w
    beq.w PauseCheckSecondPlayer
    jsr (loc_283E).l
    bra.w PauseStateChanged
PauseCheckSecondPlayer:
    jsr (loc_282C).l
PauseStateChanged:
    cmp.b $FFFFC175.w,d6
    beq.w PauseGateReturn
    clr.w $FFFFF2BA.w
    clr.w $FFFFF2B4.w
    bsr.w AudioSilence
    tst.b $FFFFC175.w
    beq.w PauseHidePanel
    lea (HUDRule).l,a0
    move.l #$44000003,d7
    bsr.w DrawCustomText
    lea (PauseTitle).l,a0
    move.l #$44800003,d7
    bsr.w DrawCustomText
    lea (PauseContinue).l,a0
    move.l #$45000003,d7
    bsr.w DrawCustomText
    lea (PauseKeys).l,a0
    move.l #$45800003,d7
    bsr.w DrawCustomText
    lea (PauseTechniques).l,a0
    move.l #$46000003,d7
    bsr.w DrawCustomText
    lea (PauseKamui).l,a0
    move.l #$46800003,d7
    bsr.w DrawCustomText
    lea (HUDRule).l,a0
    move.l #$47000003,d7
    bsr.w DrawCustomText
    bra.w PauseGateReturn
PauseHidePanel:
    move.l #$44000003,d7
    moveq #6,d5
PauseClearRow:
    move.l d7,$00C00004
    moveq #39,d4
PauseClearCell:
    move.w #0,$00C00000
    dbf d4,PauseClearCell
    addi.l #$800000,d7
    dbf d5,PauseClearRow
PauseGateReturn:
    movem.l (sp)+,d0-a6
    tst.b $FFFFC175.w
    rts
PauseTitle: dc.b "                 PAUSA",0
PauseContinue: dc.b "       ENTER / START PARA CONTINUAR",0
PauseKeys: dc.b " S/B COMBO  D/C SALTO  SUELTA A: JUTSU",0
PauseTechniques: dc.b " ARRIBA+B UPPERCUT    A+ARRIBA SELECTOR",0
PauseKamui: dc.b "         ABAJO+A JUTSU ANTERIOR",0
    even

DrawHUDBar:
    move.l d7,$00C00004
    moveq #0,d1
HUDBarLoop:
    move.w #$848D,d0
    cmp.w d3,d1
    bcc.w HUDBarEmpty
    move.w #$848B,d0
HUDBarEmpty:
    move.w d0,$00C00000
    addq.w #1,d1
    cmp.w d4,d1
    bcs.w HUDBarLoop
    rts

DrawCustomText:
    move.l d7,$00C00004
    moveq #39,d2
DrawTextLoop:
    moveq #0,d0
    move.b (a0)+,d0
    beq.w DrawTextBlank
    subi.w #32,d0
    addi.w #$84C0,d0
    move.w d0,$00C00000
    dbf d2,DrawTextLoop
    rts
DrawTextBlank:
    move.w #$84C0,$00C00000
    dbf d2,DrawTextBlank
    rts

CustomVictory:
    tst.w $FFFFF10A.w
    bne.w VictoryWait
    move.w #1,$FFFFF10A.w
    clr.b $FFFFD500.w
    jsr (loc_2DCA).l
    move.l #$40000003,$00C00004
    move.w #$7FF,d0
VictoryClear:
    move.w #$84C0,$00C00000
    dbf d0,VictoryClear
    lea (VictoryTitle).l,a0
    move.l #$45000003,d7
    bsr.w DrawCustomText
    lea (VictoryText).l,a0
    move.l #$46800003,d7
    bsr.w DrawCustomText
    lea (VictoryAgain).l,a0
    move.l #$48800003,d7
    bsr.w DrawCustomText
    jsr (loc_2DC2).l
VictoryWait:
    movem.l d0-a6,-(sp)
    bsr.w AudioTick
    bsr.w SfxTick
    movem.l (sp)+,d0-a6
    btst #7,$FFFFC176.w
    beq.w VictoryFrame
    jmp (CustomBoot).l
VictoryFrame:
    moveq #2,d0
    jmp (loc_DA8).l

HUDRule: dc.b "________________________________________",0
VictoryTitle: dc.b "       MISION COMPLETADA",0
VictoryText: dc.b "     EL GENJUTSU SE HA ROTO",0
VictoryAgain: dc.b "       START PARA VOLVER A JUGAR",0
    even

CityDescriptor:
    dc.l SpritePalette,EnemyPalette,EnemyPalette2,CityPalette,0
    dc.l $40000000,CityTiles
    dc.l $52000002,HUDTiles
    dc.l $40000002,PropTiles
    dc.l $59000001,ShadowTiles
    dc.l $58200001,DustTiles
    dc.l $59800001,WeaponTiles
    dc.l $78000001,BossFXTiles
    dc.l $5D200001,UITrimTiles
    dc.l $58000002,CustomFont
    dc.l 0
    dc.l CityBlocks,CityMap
    dc.w 14,160
    dc.w 0,0
    dc.l CityEvents,CityHeight,CityHeightBlocks,CityEnemies
    dc.w 172,$D0,172,$D0,$81
CityEvents:
    dc.w 16,$1000,240,$1000,464,$1000,688,$1000,912,$1000
    dc.w 1136,$1000,1360,$1000,1584,$1000,1808,$1000,2032,$1000
    dc.w 2224,$2000,$A00,0
CityEnemies:
    dc.w 0,0,224,1,448,2,672,3,896,4
    dc.w 1120,5,1344,6,1568,7,1792,8,2016,9,-1
CustomWaveTable:
    dc.l CustomWave0,CustomWave1,CustomWave2,CustomWave3,CustomWave4
    dc.l CustomWave5,CustomWave6,CustomWave7,CustomWave8,CustomWave9
CustomWave0: dc.w 0
    dc.l CustomGroup0
CustomWave1: dc.w 0
    dc.l CustomGroup1
CustomWave2: dc.w 0
    dc.l CustomGroup2
CustomWave3: dc.w 0
    dc.l CustomGroup3
CustomWave4: dc.w 0
    dc.l CustomGroup4
CustomWave5: dc.w 0
    dc.l CustomGroup5
CustomWave6: dc.w 0
    dc.l CustomGroup6
CustomWave7: dc.w 0
    dc.l CustomGroup7
CustomWave8: dc.w 0
    dc.l CustomGroup8
CustomWave9: dc.w 0
    dc.l CustomGroup9
CustomGroup0:
    dc.b 0,0
    dc.w 1
    dc.b 0,$31
    dc.w 172,$1B0,0,0
CustomGroup1:
    dc.b 0,0
    dc.w 2
    dc.b 0,$31
    dc.w 172,$1B0,0,0
    dc.b 1,$32
    dc.w 188,$1C8,0,0
CustomGroup2:
    dc.b 0,0
    dc.w 1
    dc.b 0,$32
    dc.w 172,$1B0,0,0
CustomGroup3:
    dc.b 0,0
    dc.w 2
    dc.b 0,$31
    dc.w 172,$1B0,0,0
    dc.b 1,$32
    dc.w 188,$1C8,0,0
CustomGroup4:
    dc.b 0,0
    dc.w 1
    dc.b 0,$32
    dc.w 172,$1B0,0,0
CustomGroup5:
    dc.b 0,0
    dc.w 2
    dc.b 0,$31
    dc.w 172,$1B0,0,0
    dc.b 1,$33
    dc.w 188,$1C8,0,0
CustomGroup6:
    dc.b 0,0
    dc.w 1
    dc.b 0,$32
    dc.w 172,$1B0,0,0
CustomGroup7:
    dc.b 0,0
    dc.w 2
    dc.b 0,$31
    dc.w 172,$1B0,0,0
    dc.b 1,$32
    dc.w 188,$1C8,0,0
CustomGroup8:
    dc.b 0,0
    dc.w 1
    dc.b 0,$33
    dc.w 172,$1B0,0,0
CustomGroup9:
    dc.b 0,0
    dc.w 1
    dc.b 0,$33
    dc.w 172,$1B0,0,0
    even

; Private weapon state $F120-$F14F. Down+B throws one kunai.
CustomWeapons:
    tst.w $FFFFF12C.w
    beq.w WeaponImpactExpired
    subq.w #1,$FFFFF12C.w
WeaponImpactExpired:
    tst.w $FFFFF122.w
    beq.w WeaponInput
    subq.w #1,$FFFFF122.w
WeaponInput:
    btst #1,$FFFFC176.w
    beq.w WeaponAdvance
    btst #4,$FFFFC177.w
    beq.w WeaponAdvance
    andi.b #$EF,$FFFFC176.w
    andi.b #$EF,$FFFFC177.w
    tst.w $FFFFF122.w
    bne.w WeaponAdvance
    tst.w $FFFFF120.w
    bne.w WeaponAdvance
    move.w #48,$FFFFF120.w
    move.w #16,$FFFFF122.w
    moveq #10,d0
    bsr.w SfxStart
    move.w $FFFFD01C.w,d0
    add.w $FFFFC210.w,d0
    move.w d0,$FFFFF124.w
    move.w $FFFFD020.w,$FFFFF126.w
    move.w $FFFFD018.w,d0
    subi.w #26,d0
    move.w d0,$FFFFF128.w
    move.w #6,$FFFFF12A.w
    btst #0,$FFFFD044.w
    beq.w WeaponAdvance
    move.w #-6,$FFFFF12A.w
WeaponAdvance:
    tst.w $FFFFF120.w
    beq.w WeaponMelee
    subq.w #1,$FFFFF120.w
    move.w $FFFFF12A.w,d0
    add.w d0,$FFFFF124.w
    lea $FFFFD100.w,a0
    moveq #7,d6
WeaponTarget:
    move.b (a0),d0
    andi.b #$7F,d0
    cmpi.b #$31,d0
    bcs.w WeaponNext
    cmpi.b #$33,d0
    bhi.w WeaponNext
    move.w $FFFFF126.w,d0
    sub.w $20(a0),d0
    bpl.w WeaponLane
    neg.w d0
WeaponLane:
    cmpi.w #13,d0
    bcc.w WeaponNext
    move.w $FFFFF124.w,d0
    sub.w $FFFFC210.w,d0
    sub.w $1C(a0),d0
    bpl.w WeaponDistance
    neg.w d0
WeaponDistance:
    cmpi.w #16,d0
    bcc.w WeaponNext
    moveq #2,d3
    movem.l d6/a0,-(sp)
    bsr.w CustomHurt
    movem.l (sp)+,d6/a0
    tst.w d0
    beq.w WeaponNext
    clr.w $FFFFF120.w
    addq.w #1,$FFFFF134.w
    bra.w WeaponMelee
WeaponNext:
    lea $80(a0),a0
    dbf d6,WeaponTarget
WeaponMelee:
    lea $FFFFD100.w,a0
    lea $FFFFF140.w,a1
    moveq #7,d6
MeleeImpactLoop:
    move.b (a0),d0
    andi.b #$7F,d0
    cmpi.b #$31,d0
    bcs.w MeleeReset
    cmpi.b #$33,d0
    bhi.w MeleeReset
    move.b $64(a0),d0
    tst.w $FFFFF220.w
    beq.w MeleeOrdinaryHealth
    cmpa.w #$D100,a0
    beq.w MeleeCompare
    cmpa.w #$D180,a0
    beq.w MeleeCloneHealth
    cmpa.w #$D200,a0
    bne.w MeleeOrdinaryHealth
MeleeCloneHealth:
    cmpi.b #8,d0
    bls.w MeleeCompare
    moveq #8,d0
    bra.w MeleeCompare
MeleeOrdinaryHealth:
    cmpi.b #6,d0
    bls.w MeleeCompare
    moveq #6,d0
MeleeCompare:
    cmp.b (a1),d0
    bcc.w MeleeSave
    ; Preserve jutsu impulses: their damage must not be counted as a melee hit.
    tst.w $FFFFF160.w
    bne.w MeleeSave
    movem.l d0/a0/a1,-(sp)
    bsr.w MeleeContact
    movem.l (sp)+,d0/a0/a1
MeleeSave:
    move.b d0,(a1)
    bra.w MeleeNext
MeleeReset:
    clr.b (a1)
MeleeNext:
    addq.l #1,a1
    lea $80(a0),a0
    dbf d6,MeleeImpactLoop
    bsr.w UpdateImpactSound
WeaponReturn:
    rts
UpdateImpactSound:
    bra.w SfxTick
StartImpact:
    move.w #9,$FFFFF12C.w
    move.w $1C(a0),d0
    add.w $FFFFC210.w,d0
    move.w d0,$FFFFF12E.w
    move.w $18(a0),d0
    subi.w #28,d0
    move.w d0,$FFFFF130.w
    move.w $20(a0),$FFFFF132.w
    addq.w #1,$FFFFF136.w
    moveq #0,d0
    bra.w SfxStart
WriteImpactPSG:
    move.w sr,-(sp)
    ori.w #$700,sr
    move.w #$100,$00A11100
ImpactBusWait:
    btst #0,$00A11100
    bne.w ImpactBusWait
    move.b d0,$00C00011
    move.w #0,$00A11100
    move.w (sp)+,sr
    rts
RenderWeapons:
    tst.w $FFFFF120.w
    beq.w RenderImpact
    lea $FFFFD600.w,a0
    move.b #$7F,(a0)
    clr.b $2(a0)
    clr.b $17(a0)
    move.w $FFFFF124.w,d0
    sub.w $FFFFC210.w,d0
    move.w d0,$1C(a0)
    move.w $FFFFF128.w,$18(a0)
    move.w $FFFFF126.w,$20(a0)
    move.w #$2CC,$8(a0)
    move.l #KunaiMeta,$A(a0)
    tst.w $FFFFF12A.w
    bpl.w RenderImpact
    move.l #KunaiLeftMeta,$A(a0)
RenderImpact:
    ; Elemental releases already carry their own contact drawing and flash.
    ; Keep the punch star/scatter for taijutsu instead of overlaying it on FX.
    cmpi.w #64,$FFFFF160.w
    bhi.w RenderImpactVisible
    cmpi.w #16,$FFFFF160.w
    bcc.w RenderWeaponReturn
RenderImpactVisible:
    tst.w $FFFFF12C.w
    beq.w RenderWeaponReturn
    lea $FFFFD680.w,a0
    move.b #$7F,(a0)
    clr.b $2(a0)
    clr.b $17(a0)
    move.w $FFFFF12E.w,d0
    sub.w $FFFFC210.w,d0
    move.w d0,$1C(a0)
    move.w $FFFFF130.w,$18(a0)
    move.w $FFFFF132.w,$20(a0)
    addq.w #2,$20(a0)
    moveq #12,d0
    sub.w $FFFFF12C.w,d0
    divu.w #4,d0
    mulu.w #9,d0
    addi.w #$2CE,d0
    move.w d0,$8(a0)
    move.l #ImpactMeta,$A(a0)
    lea $FFFFD800.w,a0
    move.b #$7F,(a0)
    clr.b $2(a0)
    clr.b $17(a0)
    move.w $FFFFF12E.w,d0
    sub.w $FFFFC210.w,d0
    move.w d0,$1C(a0)
    move.w $FFFFF130.w,$18(a0)
    move.w $FFFFF132.w,$20(a0)
    addq.w #3,$20(a0)
    move.w #$2C7,$8(a0)
    moveq #12,d0
    sub.w $FFFFF12C.w,d0
    divu.w #4,d0
    lsl.w #2,d0
    lea (ImpactScatterMetas).l,a1
    move.l (a1,d0.w),$A(a0)
RenderWeaponReturn:
    rts

; Combat input buffer and confirmed-hit chain. RAM F150..F15F.
ComboInput:
    tst.w $FFFFF154.w
    beq.w ComboExpired
    subq.w #1,$FFFFF154.w
    bne.w ComboKeep
ComboExpired:
    clr.w $FFFFF152.w
ComboKeep:
    btst #1,$FFFFC176.w
    bne.w ComboThrow
    btst #4,$FFFFC177.w
    bne.w ComboQueue
    btst #4,$FFFFC176.w
    beq.w ComboBufferTick
    ; Holding B repeats only when a ninja is in front and within melee range.
    ; This lets the player keep walking between waves while holding the button.
    lea $FFFFD100.w,a0
    moveq #7,d7
ComboRangeLoop:
    move.b (a0),d0
    andi.b #$7F,d0
    cmpi.b #$31,d0
    bcs.w ComboRangeNext
    cmpi.b #$33,d0
    bhi.w ComboRangeNext
    tst.b $64(a0)
    beq.w ComboRangeNext
    move.w $20(a0),d0
    sub.w $FFFFD020.w,d0
    bpl.w ComboLaneAbsolute
    neg.w d0
ComboLaneAbsolute:
    cmpi.w #12,d0
    bcc.w ComboRangeNext
    move.w $1C(a0),d0
    sub.w $FFFFD01C.w,d0
    btst #0,$FFFFD044.w
    beq.w ComboFacingRight
    neg.w d0
ComboFacingRight:
    tst.w d0
    bmi.w ComboRangeNext
    cmpi.w #36,d0
    bls.w ComboQueue
ComboRangeNext:
    lea $80(a0),a0
    dbf d7,ComboRangeLoop
    bsr.w ObjectComboRange
    tst.w d0
    bne.w ComboQueue
    bra.w ComboBufferTick
ComboQueue:
    move.w #12,$FFFFF15C.w
    bsr.w ComboChooseRoute
ComboBufferTick:
    tst.w $FFFFF15C.w
    beq.w ComboInputReturn
    subq.w #1,$FFFFF15C.w
    move.b $FFFFD042.w,d0
    andi.b #$7F,d0
    bne.w ComboInputReturn
    btst #5,$FFFFD003.w
    bne.w ComboInputReturn
    ori.b #$10,$FFFFC177.w
    move.w $FFFFF2D2.w,$FFFFF2D4.w
    clr.w $FFFFF15C.w
ComboInputReturn:
    rts
ComboThrow:
    clr.w $FFFFF15C.w
    rts
MeleeContact:
    bsr.w ComboHitMotion
    bsr.w MeleeReaction
    addq.w #1,$FFFFF156.w
    addq.w #1,$FFFFF152.w
    move.w #72,$FFFFF154.w
    move.w $FFFFF152.w,d0
    cmp.w $FFFFF15A.w,d0
    bls.w ComboBestDone
    move.w d0,$FFFFF15A.w
ComboBestDone:
    bsr.w StartImpact
    bsr.w MeleeReactionSound
    move.w #3,$FFFFF150.w
    move.b $FFFFD043.w,d0
    cmpi.b #6,d0
    beq.w ComboFinisher
    cmpi.b #8,d0
    bcs.w ComboRegular
    cmpi.b #12,d0
    bls.w ComboFinisher
ComboRegular:
    cmpi.w #3,$FFFFF152.w
    bcs.w ComboContactReturn
ComboFinisher:
    move.w #6,$FFFFF150.w
    move.w #12,$FFFFF12C.w
    addq.w #1,$FFFFF158.w
    moveq #1,d0
    bsr.w SfxStart
ComboContactReturn:
    rts
