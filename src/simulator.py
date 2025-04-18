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
        self.stack = {
            "com": [],
            "usr/sys": [],
            "svc": [],
            "abt": [],
            "und": [],
            "irq": [],
            "mon": [],
            "fiq": []
        }
        self.memory = [0] * 64  # 64 words (256 bytes)
        self.command_list = [
            "ADD",
            "B",
            "BL",
            "LDR",
            "MOV",
            "NOP",
            "STR",
            "SUB",
            "PUSH",
            "q",
        ]
        self.history = []  # 명령어 히스토리 추가
        self.reserved = []  # break 이후 명령어 저장

    def add_reserved(self, instruction):
        self.reserved.append(instruction)

    def get_reserved(self):
        return self.reserved

    def pop_reserved(self):
        """
        reserved 리스트에서 가장 앞의 명령어를 꺼내 반환합니다.
        명령어가 없으면 None을 반환합니다.
        """
        if self.reserved:
            return self.reserved.pop(0)
        return None

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
                found = False
                for mode in self.registers:
                    if rd in self.registers[mode]:
                        self.registers[mode][rd] = imm
                        found = True
                        break
                if not found:
                    raise Exception(f"Register {rd} not found")
        # ADD rX, rY, #imm
        elif op == "ADD":
            rd = tokens[1].lower()
            rn = tokens[2].lower()
            imm = int(tokens[3].replace('#', ''), 0)
            if rd in self.registers["com"] and rn in self.registers["com"]:
                self.registers["com"][rd] = self.registers["com"][rn] + imm
            else:
                found = False
                for mode in self.registers:
                    if rd in self.registers[mode] and rn in self.registers[mode]:
                        self.registers[mode][rd] = self.registers[mode][rn] + imm
                        found = True
                        break
                if not found:
                    raise Exception(f"Register {rd} or {rn} not found")
        # PUSH {rX} 또는 PUSH {rX-rY, ...}
        elif op == "PUSH":
            regs_token = tokens[1].strip("{}").lower()
            sp_mode = "usr/sys"
            sp = self.registers[sp_mode]["sp"]

            # 여러 레지스터 처리 (예: r0-r12, lr)
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

            # 레지스터 순서대로 stack에 저장 (Full Descending, 4바이트씩 감소)
            for reg in reg_list:
                reg_val = None
                for mode in self.registers:
                    if reg in self.registers[mode]:
                        reg_val = self.registers[mode][reg]
                        break
                if reg_val is not None:
                    sp -= 4
                    # self.registers[sp_mode]["sp"] = sp
                    # self.memory[sp] = reg_val  # 필요시 메모리에도 저장
                    self.stack[sp_mode].append((sp, reg_val))
                else:
                    raise Exception(f"Register {reg} not found")
        # SUB, LDR, STR 등은 필요에 따라 추가 구현
        else:
            raise Exception(f"Unsupported instruction: {instruction}")

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