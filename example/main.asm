.p816
.i16
.a8

.include "snes.inc"
.include "charmap.inc"

.segment "HEADER"
.byte "Graphics test"

.segment "ROMINFO"
.byte $30
.byte $50
.byte $07
.byte $01
.byte $01
.byte $00
.byte $00
.word $AAAA,$5555

.segment "CODE"
	jmp start

start:
	clc
	xce
	rep #$10
	sep #$20
	ldx #$33
@reset_reg_loop:
	stz INIDISP,x
	stz NMITIMEN,x
	dex
	bpl @reset_reg_loop
	
	lda #$8F ;fblank is on until all is ready
	sta INIDISP
	
	lda #$81 ;enable nmi & auto joypad
	sta NMITIMEN
	lda #$13 ;mode 3, 16x16 tiles on bg1
	sta BGMODE
	
	;store CGRAM
	
	;bg vram stuff
	lda #$50 ;tilemap location ($5000)
	sta BG1SC
	stz BG12NBA
	
	lda #$03
	sta OBSEL ;obj size & vram location
	
	;prepare to put vramdata data into vram
	;y = high byte of x (since cpx can't check high byte)
	ldy #$0000
	stz VMAIN
	stz VMADDL
	stz VMADDH
	ldx #$0000
@sprite_vram_transfer:
	lda vramdata,x
	sta VMDATAH
	inx
	lda vramdata,x
	sta VMDATAL
	inx
	
	cpx #$00
	bne @sprite_vram_transfer
	iny
	cpy #$04 ;high byte of how many byte are to be transferred
	bne @sprite_vram_transfer
	cpx #$00 ;low byte of how many byte are to be transferred
	bne @sprite_vram_transfer
	
	;no need to write to oam. it's already all $00s
	
	;enable screen
	lda #$10
	sta TM
	sta TS
	
	;disable fblank
	lda #$0F
	sta INIDISP
main:
	wai ;wait for vblank/nmi
	jmp main

nmi:
	rep #$10
	sep #$20
	phd
	pha
	phx
	phy
	
	lda RDNMI
	ply
	plx
	pla
	pld
return_from_interrupt:
	rti

vramdata:
	.incbin "vramdata.bin",0,1024

.segment "VECTORS"
.word 0, 0 ;native mode
.word return_from_interrupt
.word return_from_interrupt
.word return_from_interrupt
.word nmi
.word start
.word return_from_interrupt

.word 0, 0 ;emulation mode
.word return_from_interrupt
.word 0
.word return_from_interrupt
.word nmi
.word start
.word return_from_interrupt