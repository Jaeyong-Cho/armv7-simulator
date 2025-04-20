def handle_mov(sim, tokens):
    rd = tokens[1].lower()
    imm = int(tokens[2].replace('#', ''), 0)
    if rd in sim.registers["com"]:
        sim.registers["com"][rd] = imm
    else:
        found = False
        for mode in sim.registers:
            if rd in sim.registers[mode]:
                sim.registers[mode][rd] = imm
                found = True
                break
        if not found:
            raise Exception(f"Register {rd} not found")