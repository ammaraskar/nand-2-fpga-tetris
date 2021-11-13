// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/06/rect/Rect.asm

// Draws a rectangle at the top-left corner of the screen.
// The rectangle is 16 pixels wide and R0 pixels high.

   A := 0
   D = *A
   A := @INFINITE_LOOP
   D; jle 
   A := $counter
   *A = D
   A := $screen
   D = A
   A := $address
   *A = D
loop:
   A := $address
   A = *A
   *A = -1
   A := $address
   D = *A
   A = 32
   D = D + A
   A := $address
   *A = D
   A := $counter
   *A, D = *A - 1
   A := @loop
   D; jgt
INFINITE_LOOP:
   A := @INFINITE_LOOP
   0; jmp          // infinite loop