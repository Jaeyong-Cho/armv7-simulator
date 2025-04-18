import re

class ARMv7Simulator:
    def __init__(self):
        self.registers = {f"R{i}": 0 for i in range(16)}
        self.memory = [0] * 64  # 64 words (256 bytes)

    def parse_and_execute(self, instruction):
        tokens = instruction.strip().split()
        if not tokens:
            return

        op = tokens[0].upper()
        if op == "MOV" or op == "mov":
            rd, imm = re.findall(r'R\d+', tokens[1])[0], int(tokens[2].replace('#', ''))
            self.registers[rd] = imm
        elif op == "ADD" or op == "add":
            rd, rn, imm = re.findall(r'R\d+', tokens[1] + tokens[2]), int(tokens[3].replace('#', ''))
            self.registers[rd[0]] = self.registers[rd[1]] + imm
        elif op == "STR" or op == "str":
            rd, rn = re.findall(r'R\d+', tokens[1] + tokens[2])
            imm = int(re.findall(r'#(\d+)', tokens[2])[0])
            addr = self.registers[rn] + imm
            if 0 <= addr < len(self.memory):
                self.memory[addr] = self.registers[rd]
        elif op == "LDR" or op == "ldr":
            rd, rn = re.findall(r'R\d+', tokens[1] + tokens[2])
            imm = int(re.findall(r'#(\d+)', tokens[2])[0])
            addr = self.registers[rn] + imm
            if 0 <= addr < len(self.memory):
                self.registers[rd] = self.memory[addr]
        else:
            print(f"Unsupported instruction: {instruction}")

    def get_registers(self):
        return self.registers

    def get_memory(self):
        return self.memory

    def visualize(self):
        return self.get_registers(), self.get_memory()[:16]  # Return first 16 words of memory for visualization