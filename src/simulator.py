import re
from instructions.mov import handle_mov
from instructions.add import handle_add
from instructions.ldr import handle_ldr
from instructions.push import handle_push

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
        self.memory = {}  # 리스트에서 dict로 변경
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
        self.labels = {}  # label 주소

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

    def add_label(self, name, addr):
        """label 변수 등록 (예: add_labels('curr_pcb', 0x1000))"""
        self.labels[name] = addr

    def get_label(self, name):
        """label 변수 주소 반환"""
        return self.labels.get(name)

    def parse_and_execute(self, instruction):
        self.history.append(instruction)
        tokens = instruction.strip().replace(',', '').split()
        if not tokens:
            return

        if tokens[0].lower() == ".extern":
            # extern 라벨 선언 처리 (.extern label @@ 0xADDR)
            name = tokens[1]
            addr = 0
            for i, t in enumerate(tokens):
                if t == "@@":
                    # 다음 토큰이 주소임
                    if i + 1 < len(tokens) and tokens[i + 1].startswith("0x"):
                        addr = int(tokens[i + 1], 16)
            self.add_label(name, addr)
            return

        op = tokens[0].upper()
        if op == "MOV":
            handle_mov(self, tokens)
        elif op == "ADD":
            handle_add(self, tokens)
        elif op == "LDR" and len(tokens) == 3 and tokens[2].startswith('='):
            handle_ldr(self, tokens)
        elif op == "PUSH":
            handle_push(self, tokens)
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
        # 메모리의 전체 주소를 정렬해서 반환
        mem_keys = sorted(self.memory.keys())
        mem_view = [self.memory.get(addr, 0) for addr in mem_keys]
        return self.get_registers(), mem_view