; Three small resident leaves. Display-only slot DB00 is cleared before AI.
; Motion follows the native game timer; no extra RAM, tile DMA or sound traffic.
RenderVillageWind:
    tst.w $FFFFF204.w
    bne.w VillageWindReturn
    tst.w $FFFFF10A.w
    bne.w VillageWindReturn
    lea $FFFFDB00.w,a0
    move.b #$7F,(a0)
    clr.b $2(a0)
    clr.b $17(a0)
    move.w $FFFFC17A.w,d0
    lsr.w #2,d0
    andi.w #127,d0
    addi.w #192,d0
    move.w d0,$1C(a0)
    move.w $FFFFC17A.w,d0
    lsr.w #3,d0
    andi.w #31,d0
    addi.w #188,d0
    move.w d0,$18(a0)
    move.w #112,$20(a0)
    move.w $FFFFC17A.w,d0
    lsr.w #3,d0
    andi.w #1,d0
    addi.w #CityLeafTile,d0
    move.w d0,$8(a0)
    move.l #VillageLeafMeta,$A(a0)
VillageWindReturn:
    rts
VillageLeafMeta:
    dc.b 2,0,0
    dc.b 246,0,0,0,160
    dc.b 0,0,8,0,0
    dc.b 10,0,16,0,96
    even
