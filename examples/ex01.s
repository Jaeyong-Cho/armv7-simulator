mov r0, #0
mov r1, #1
mov r2, #2
mov r3, #3
mov r4, #4
mov r5, #5
mov r6, #6
mov r7, #7
mov r8, #8
mov r9, #9
mov r10, #10
mov r11, #11
mov r12, #12
mov sp, #0xE0

.extern curr_pcb @@ 0x1000

@@ break
push {r0-r12, lr}

ldr r0, =curr_pcb
ldr r0, [r0]
add r0, r0, #0

ldmia sp!, {r1-r12} // r0~r11
stmia r0!, {r1-r12} // curr_pcb->regs[0] ~ regs[11]
ldm sp!, {r1} // r12
str r1, [r0], #4 // curr_pcb->regs[12] : r12

stm r0!, {sp, lr}^  // curr_pcb->regs[13] ~ regs[14] : sp (User 모드 sp) lr (User 모드 lr)

ldm sp!, {r2} // lr
sub r2, r2, #4
str r2, [r0], #4 // curr_pcb->regs[15] : pc (복귀 주소)

mrs r1, spsr
str r1, [r0], #4 // curr_pcb->regs[16] : spsr

bl Timer0_ISR

ldr r0, =curr_pcb
ldr r0, [r0]
add r0, r0, #0

// ldr r1 < curr_pcb->regs[16]
ldr r2, =0x10
ldr r1, [r0, r2, lsl #2] // curr_pcb->regs[16] : spsr
ldmfd r0, {r0-r12, sp, lr, pc}^