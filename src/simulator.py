import re

class ARMv7Simulator:
    def __init__(self):
        self.registers = {
            "com": {"r0": 0, "r1": 0, "r2": 0, "r3": 0, "r4": 0, "r5": 0, "r6": 0, "r7": 0,
                    "r8": 0, "r9": 0, "r10": 0, "r11": 0, "r12": 0, "pc": 0, "cpsr": 0},
            "usr/sys": {"sp": 0, "lr": 0, "spsr": 0},
            "svc": {"sp": 0, "lr": 0, "spsr": 0},
            "abt": {"sp": 0, "lr": 0, "spsr": 0},
            "und": {"sp": 0, "lr": 0, "spsr": 0},
            "irq": {"sp": 0, "lr": 0, "spsr": 0},
            "mon": {"sp": 0, "lr": 0, "spsr": 0},
            "fiq": {"r8": 0, "r9": 0, "r10": 0, "r11": 0, "r12": 0, "sp": 0, "lr": 0, "spsr": 0}
        }
        self.memory = [0] * 64  # 64 words (256 bytes)
        self.command_list = [
            "MOV",
            "ADD",
            "SUB",
            "LDR",
            "STR",
            "B",
            "BL",
            "NOP",
            "q"
        ]
        self.history = []  # 명령어 히스토리 추가

    def parse_and_execute(self, instruction):
        self.history.append(instruction)  # 히스토리 기록
        tokens = instruction.strip().replace(',', '').split()
        if not tokens:
            return

        op = tokens[0].upper()
        # MOV rX, #imm
        if op == "MOV":
            rd = tokens[1].lower()
            imm = int(tokens[2].replace('#', ''), 0)
            if rd in self.registers["com"]:
                self.registers["com"][rd] = imm
            else:
                for mode in self.registers:
                    if rd in self.registers[mode]:
                        self.registers[mode][rd] = imm
                        break
        # ADD rX, rY, #imm
        elif op == "ADD":
            rd = tokens[1].lower()
            rn = tokens[2].lower()
            imm = int(tokens[3].replace('#', ''), 0)
            if rd in self.registers["com"] and rn in self.registers["com"]:
                self.registers["com"][rd] = self.registers["com"][rn] + imm
            else:
                for mode in self.registers:
                    if rd in self.registers[mode] and rn in self.registers[mode]:
                        self.registers[mode][rd] = self.registers[mode][rn] + imm
                        break
        # PUSH {rX}
        elif op == "PUSH":
            # 예: PUSH {r0}
            reg_token = tokens[1].strip("{}").lower()
            # 우선 "com"의 sp 사용, 없으면 각 모드 sp 사용
            sp_mode = "com"
            if "sp" not in self.registers["com"]:
                # usr/sys, svc, abt, und, irq, fiq, mon 중 첫 sp 찾기
                for mode in ["usr/sys", "svc", "abt", "und", "irq", "fiq", "mon"]:
                    if "sp" in self.registers[mode]:
                        sp_mode = mode
                        break
            sp = self.registers[sp_mode]["sp"]
            # 스택은 감소 방향 (Full Descending)
            sp -= 1
            self.registers[sp_mode]["sp"] = sp
            # 메모리 경계 체크
            if 0 <= sp < len(self.memory):
                # rX 값 찾기
                reg_val = None
                for mode in self.registers:
                    if reg_token in self.registers[mode]:
                        reg_val = self.registers[mode][reg_token]
                        break
                if reg_val is not None:
                    self.memory[sp] = reg_val
                else:
                    print(f"Register {reg_token} not found")
            else:
                print("Stack Overflow/Underflow")
        # SUB, LDR, STR 등은 필요에 따라 추가 구현
        else:
            print(f"Unsupported instruction: {instruction}")

    def get_registers(self):
        return self.registers

    def get_exception_registers(self):
        return self.exception_registers

    def get_memory(self):
        return self.memory

    def get_history(self):
        return self.history

    def visualize(self):
        return self.get_registers(), self.get_memory()[:16]  # Return first 16 words of memory for visualization