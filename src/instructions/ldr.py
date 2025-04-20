def handle_ldr(sim, tokens):
    rd = tokens[1].lower()
    # ldr r0, =label 형태
    if tokens[2].startswith('='):
        label = tokens[2][1:]  # '=' 제거
        addr = sim.get_label(label)
        if addr is None:
            raise Exception(f"Label '{label}' not found")
        value = addr
    # ldr r0, [r0] 형태
    elif tokens[2].startswith('[') and tokens[2].endswith(']'):
        rn = tokens[2][1:-1].lower()
        # rn이 어떤 모드에 있는지 찾기
        value = None
        for mode in sim.registers:
            if rn in sim.registers[mode]:
                addr = sim.registers[mode][rn]
                # 메모리에서 4바이트 읽기 (word 단위)
                if 0 <= addr // 4 < len(sim.memory):
                    value = sim.memory[addr // 4]
                else:
                    raise Exception(f"Memory address out of range: {addr}")
                break
        if value is None:
            raise Exception(f"Register {rn} not found")
    else:
        raise Exception("Unsupported LDR format")

    # 결과를 rd에 저장
    for mode in sim.registers:
        if rd in sim.registers[mode]:
            sim.registers[mode][rd] = value
            return
    raise Exception(f"Register {rd} not found")