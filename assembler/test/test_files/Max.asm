// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/06/max/Max.asm

// Computes M[2] = max(M[0], M[1])  where M stands for RAM

   A := 0
   D = *A           // D = first number
   A := 1
   D = D - *A       // D = first number - second number
   A := @OUTPUT_FIRST
   D; jgt           // if D>0 (first is greater) goto output_first
   A := 1
   D = *A           // D = second number
   A := @OUTPUT_D
   0; jmp           // goto output_d
OUTPUT_FIRST:
   A := 0
   D = *A           // D = first number
OUTPUT_D:
   A := 2
   *A = D           // M[2] = D (greatest number)
INFINITE_LOOP:
   A := @INFINITE_LOOP
   0; jmp          // infinite loop
