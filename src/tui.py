import curses

class TUI:
    def __init__(self, simulator):
        self.simulator = simulator
        self.last_message = ""
        self.command_list = [
            "MOV Rd, #imm",
            "ADD Rd, Rn, Rm",
            "SUB Rd, Rn, Rm",
            "LDR Rd, [Rn]",
            "STR Rd, [Rn]",
            "B label",
            "BL label",
            "NOP",
            "q (quit)"
        ]

    def draw_registers(self, win):
        win.addstr(0, 0, "[Registers]")
        for idx, (name, value) in enumerate(self.simulator.registers.items(), start=1):
            win.addstr(idx, 0, f"{name:>3}: 0x{value:08X}")

    def draw_memory(self, win):
        win.addstr(0, 0, "[Memory Map]")
        memory = self.simulator.memory
        for i in range(0, min(len(memory), 128), 8):
            line = ' '.join(f"{b:02X}" for b in memory[i:i+8])
            win.addstr(1 + i // 8, 0, f"{i*4:04X}: {line}")

    def draw_commands(self, win):
        win.addstr(0, 0, "[Command List]")
        for idx, cmd in enumerate(self.command_list, start=1):
            win.addstr(idx, 0, cmd)

    def get_user_input(self, stdscr, prompt_y, prompt_x, input_str):
        prompt = "> "
        while True:
            stdscr.move(prompt_y, prompt_x + len(prompt) + len(input_str))
            stdscr.refresh()
            key = stdscr.getch()
            if key in (curses.KEY_ENTER, 10, 13):
                return input_str
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                input_str = input_str[:-1]
            elif 32 <= key <= 126:
                input_str += chr(key)
            # 입력창을 항상 prompt와 함께 다시 그림
            stdscr.addstr(prompt_y, prompt_x, prompt + input_str + " " * 10)

    def run(self):
        curses.wrapper(self._main)

    def _main(self, stdscr):
        curses.curs_set(1)  # 커서 깜빡임 활성화
        curses.echo()
        input_str = ""
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            reg_win_width = max(18, width // 4)
            reg_win_height = len(self.simulator.registers) + 2
            reg_win = curses.newwin(reg_win_height, reg_win_width, 0, 0)
            self.draw_registers(reg_win)
            reg_win.box()
            reg_win.refresh()

            mem_win_width = width // 2 - reg_win_width - 2
            mem_win_height = min(len(self.simulator.memory)//8 + 3, height - 4)
            mem_win = curses.newwin(mem_win_height, mem_win_width, 0, reg_win_width + 1)
            self.draw_memory(mem_win)
            mem_win.box()
            mem_win.refresh()

            # 명령어 리스트 창
            cmd_win_width = width - (reg_win_width + mem_win_width + 3)
            cmd_win_height = len(self.command_list) + 2
            cmd_win = curses.newwin(cmd_win_height, cmd_win_width, 0, reg_win_width + mem_win_width + 2)
            self.draw_commands(cmd_win)
            cmd_win.box()
            cmd_win.refresh()

            stdscr.addstr(height-4, 0, "Enter ARMv7 instruction (or 'q' to quit):")
            stdscr.addstr(height-3, 0, "> " + input_str)
            stdscr.addstr(height-2, 0, self.last_message[:width-1])
            stdscr.move(height-3, 2 + len(input_str))
            stdscr.refresh()

            # 입력 함수로 분리
            input_str = self.get_user_input(stdscr, height-3, 0, input_str)
            command = input_str.strip()
            if command.lower() == 'q':
                break
            elif command:
                try:
                    self.simulator.parse_and_execute(command)
                    self.last_message = f"Executed: {command}"
                except Exception as e:
                    self.last_message = f"Error: {e}"
            input_str = ""

# 사용 예시:
# from simulator import ARMv7Simulator
# sim = ARMv7Simulator()
# tui = TUI(sim)
# tui.run()