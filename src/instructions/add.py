def handle_add(sim, tokens):
    rd = tokens[1].lower()
    rn = tokens[2].lower()
    imm = int(tokens[3].replace('#', ''), 0)
    if rd in sim.registers["com"] and rn in sim.registers["com"]:
        sim.registers["com"][rd] = sim.registers["com"][rn] + imm
    else:
        found = False
        for mode in sim.registers:
            if rd in sim.registers[mode] and rn in sim.registers[mode]:
                sim.registers[mode][rd] = sim.registers[mode][rn] + imm
                found = True
                break
        if not found:
            raise Exception(f"Register {rd} or {rn} not found")