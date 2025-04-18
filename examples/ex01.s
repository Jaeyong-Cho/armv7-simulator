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