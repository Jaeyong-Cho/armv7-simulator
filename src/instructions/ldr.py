def handle_ldr(sim, tokens):
    rd = tokens[1].lower()
    label = tokens[2][1:]  # '=' 제거
    addr = sim.get_label(label)
    if addr is None:
        raise Exception(f"Label '{label}' not found")
    if rd in sim.registers["com"]:
        sim.registers["com"][rd] = addr
    else:
        found = False
        for mode in sim.registers:
            if rd in sim.registers[mode]:
                sim.registers[mode][rd] = addr
                found = True
                break
        if not found:
            raise Exception(f"Register {rd} not found")