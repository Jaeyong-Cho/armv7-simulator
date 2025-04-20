def handle_push(sim, tokens):
    regs_token = tokens[1].strip("{}").lower()
    sp_mode = "usr/sys"
    sp = sim.registers[sp_mode]["sp"]

    reg_list = []
    for part in regs_token.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            start = start.strip()
            end = end.strip()
            if start.startswith('r') and end.startswith('r'):
                for i in range(int(start[1:]), int(end[1:]) + 1):
                    reg_list.append(f"r{i}")
        else:
            reg_list.append(part)

    for reg in reg_list:
        reg_val = None
        for mode in sim.registers:
            if reg in sim.registers[mode]:
                reg_val = sim.registers[mode][reg]
                break
        if reg_val is not None:
            sp -= 4
            sim.registers[sp_mode]["sp"] = sp
            sim.stack[sp_mode].append((sp, reg_val))
            # 메모리에도 반영 (sp 주소에 reg_val 저장)
            sim.memory[sp] = reg_val
        else:
            raise Exception(f"Register {reg} not found")