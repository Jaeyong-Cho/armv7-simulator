import curses

class TUI:
    def __init__(self, simulator):
        self.simulator = simulator
        self.last_message = ""
        self.exit = False

    def draw_registers(self, win):
        win.clear()
        win.box()
        win.addstr(0, 2, "[Registers]")
        row = 1
        max_y, max_x = win.getmaxyx()
        # 공통 레지스터(com)
        if "com" in self.simulator.registers:
            if row < max_y - 1:
                win.addstr(row, 1, "<com>"[:max_x-2])
                row += 1
            for name, value in self.simulator.registers["com"].items():
                if row < max_y - 1:
                    line = f"{name:>4}: 0x{value:08X}"
                    win.addstr(row, 3, line[:max_x-4])
                    row += 1
        # 각 모드별 레지스터
        for mode in ["usr/sys", "svc", "mon", "abt", "und", "irq", "fiq"]:
            if mode in self.simulator.registers:
                if row < max_y - 1:
                    win.addstr(row, 1, f"<{mode}>"[:max_x-2])
                    row += 1
                for rname, rval in self.simulator.registers[mode].items():
                    if row < max_y - 1:
                        line = f"{rname:>4}: 0x{rval:08X}"
                        win.addstr(row, 3, line[:max_x-4])
                        row += 1

    def draw_memory(self, win):
        win.clear()
        win.box()
        win.addstr(0, 2, "[Memory Map]")
        memory = self.simulator.memory
        for i in range(0, min(len(memory), 128), 8):
            line = ' '.join(f"{b:02X}" for b in memory[i:i+8])
            win.addstr(1 + i // 8, 1, f"{i*4:04X}: {line}")

    def draw_commands(self, win):
        win.clear()
        win.box()
        win.addstr(0, 2, "[Command List]")
        for idx, cmd in enumerate(self.simulator.command_list, start=1):
            win.addstr(idx, 1, cmd)

    def draw_stack(self, win):
        win.clear()
        win.box()
        win.addstr(0, 2, "[Stack]")
        row = 1
        max_y, max_x = win.getmaxyx()
        for mode in self.simulator.stack:
            if row < max_y - 1:
                win.addstr(row, 1, f"<{mode}>")
                row += 1
            stack_entries = list(reversed(self.simulator.stack[mode]))
            if not stack_entries:
                if row < max_y - 1:
                    win.addstr(row, 3, "(empty)")
                    row += 1
            for idx, entry in enumerate(stack_entries):
                if isinstance(entry, tuple) and len(entry) == 2:
                    addr, val = entry
                    line = f"{idx:02d}: [0x{addr:02X}] 0x{val:08X}"
                else:
                    line = f"{idx:02d}: 0x{entry:08X}"
                if row < max_y - 1:
                    win.addstr(row, 3, line[:max_x-4])
                    row += 1

    def draw_reserved(self, win, scroll_offset=0):
        win.clear()
        win.box()
        win.addstr(0, 2, "[Reserved Commands]")
        reserved = self.simulator.get_reserved() if hasattr(self.simulator, "get_reserved") else []
        max_y, max_x = win.getmaxyx()
        # 스크롤 없이 처음부터 보이도록
        for idx, cmd in enumerate(reserved[:max_y-2], start=1):
            if idx < max_y - 1:
                win.addstr(idx, 1, cmd[:max_x-3])

    def get_user_input(self, input_win, input_str):
        prompt = "> "
        input_win.clear()
        input_win.box()
        input_win.addstr(1, 2, "Enter ARMv7 instruction (or 'q' to quit):")
        history = self.simulator.get_history() if hasattr(self.simulator, "get_history") else []
        hist_idx = len(history)
        max_x = input_win.getmaxyx()[1]
        command_list = self.simulator.command_list

        # 레지스터 이름 목록 생성
        reg_names = []
        for mode in self.simulator.registers:
            reg_names.extend(self.simulator.registers[mode].keys())
        reg_names = list(set(reg_names))  # 중복 제거

        cursor_pos = len(input_str)  # 커서 위치 변수

        while True:
            input_win.move(2, 2)
            input_win.clrtoeol()
            # 입력창에 현재 커서 위치 반영
            input_win.addstr(2, 2, prompt + input_str + " " * (max_x - len(prompt) - len(input_str) - 4))
            input_win.move(2, 2 + len(prompt) + cursor_pos)
            input_win.refresh()
            key = input_win.getch()
            if key in (curses.KEY_ENTER, 10, 13):
                return input_str
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                if cursor_pos > 0:
                    input_str = input_str[:cursor_pos-1] + input_str[cursor_pos:]
                    cursor_pos -= 1
            elif key == curses.KEY_LEFT:
                if cursor_pos > 0:
                    cursor_pos -= 1
            elif key == curses.KEY_RIGHT:
                if cursor_pos < len(input_str):
                    cursor_pos += 1
            elif key == curses.KEY_UP:
                if history and hist_idx > 0:
                    hist_idx -= 1
                    input_str = history[hist_idx]
                    cursor_pos = len(input_str)
            elif key == curses.KEY_DOWN:
                if history and hist_idx < len(history) - 1:
                    hist_idx += 1
                    input_str = history[hist_idx]
                    cursor_pos = len(input_str)
                else:
                    input_str = ""
                    hist_idx = len(history)
                    cursor_pos = 0
            elif key == 9:  # Tab key for auto-completion
                parts = input_str.strip().split()
                if parts:
                    if len(parts) == 1:
                        prefix = parts[0].upper()
                        matches = [cmd for cmd in command_list if cmd.startswith(prefix)]
                        if matches:
                            parts[0] = matches[0]
                            input_str = " ".join(parts)
                            cursor_pos = len(input_str)
            elif key == 3:  # Ctrl+C
                input_str = ""
                cursor_pos = 0
            elif 32 <= key <= 126:
                input_str = input_str[:cursor_pos] + chr(key) + input_str[cursor_pos:]
                cursor_pos += 1

    def run(self):
        while self.exit is False:
            try:
                curses.wrapper(self._main)
            except KeyboardInterrupt:
                pass  # Ctrl+C 무시

    def _main(self, stdscr):
        curses.curs_set(1)
        curses.noecho()
        input_str = ""
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            min_width = 60
            min_height = 20
            if width < min_width or height < min_height:
                stdscr.addstr(0, 0, f"터미널 크기를 최소 {min_width}x{min_height} 이상으로 늘려주세요.")
                stdscr.refresh()
                stdscr.getch()
                continue

            usable_height = height - 6  # 입력창 window 높이(3) + 메시지창(1) + 여유(2)
            reg_win_width = max(18, width // 4)
            stack_win_width = max(18, width // 4)
            mem_win_width = max(24, width // 4)
            cmd_win_width = max(16, width // 4)
            reserved_win_width = max(18, width // 4)
            # 나머지 공간은 입력창/메시지창

            reg_win_height = min(50 + 3, usable_height)
            stack_win_height = usable_height
            mem_win_height = min(len(self.simulator.memory)//8 + 3, usable_height)
            cmd_win_height = min(len(self.simulator.command_list) + 3, usable_height)
            # reserved window는 command list window 아래에 배치
            reserved_win_height = usable_height - cmd_win_height
            reserved_win_y = cmd_win_height
            reserved_win_x = reg_win_width + stack_win_width + mem_win_width

            reg_win_x = 0
            stack_win_x = reg_win_x + reg_win_width
            mem_win_x = stack_win_x + stack_win_width
            cmd_win_x = mem_win_x + mem_win_width

            reg_win = curses.newwin(reg_win_height, reg_win_width, 0, reg_win_x)
            self.draw_registers(reg_win)
            reg_win.refresh()

            stack_win = curses.newwin(stack_win_height, stack_win_width, 0, stack_win_x)
            self.draw_stack(stack_win)
            stack_win.refresh()

            mem_win = curses.newwin(mem_win_height, mem_win_width, 0, mem_win_x)
            self.draw_memory(mem_win)
            mem_win.refresh()

            cmd_win = curses.newwin(cmd_win_height, cmd_win_width, 0, cmd_win_x)
            self.draw_commands(cmd_win)
            cmd_win.refresh()

            reserved_win = curses.newwin(reserved_win_height, reserved_win_width, reserved_win_y, cmd_win_x)
            self.draw_reserved(reserved_win)  # scroll_offset 인자 제거
            reserved_win.refresh()

            # 입력창 window (높이 4, 화면 하단에서 4줄 위)
            input_win_height = 4
            input_win = curses.newwin(input_win_height, width, height - input_win_height, 0)
            input_win.keypad(True)
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, "Enter ARMv7 instruction (or 'q' to quit):")
            input_win.addstr(2, 2, "> " + input_str + " " * (width - len(input_str) - 4))
            input_win.refresh()

            # 메시지창 (입력창 바로 위)
            msg_y = height - input_win_height - 1
            msg_win = curses.newwin(1, width, msg_y, 0)
            msg_win.addstr(0, 0, self.last_message[:width-1] + " " * (width - len(self.last_message) - 1))
            msg_win.refresh()

            # 입력 받기
            input_str = self.get_user_input(input_win, input_str)
            command = input_str.strip()
            if command.lower() == 'q':
                self.exit = True
                break
            elif command:
                try:
                    self.simulator.parse_and_execute(command)
                    self.last_message = f"Executed: {command}"
                except Exception as e:
                    self.last_message = f"Error: {e}"
                    msg_win.clear()
                    msg_win.addstr(0, 0, self.last_message[:width-1] + " " * (width - len(self.last_message) - 1))
                    msg_win.refresh()
                    input_win.clear()
                    input_win.box()
                    input_win.addstr(1, 2, "Enter ARMv7 instruction (or 'q' to quit):")
                    input_win.addstr(2, 2, "> " + input_str + " " * (width - len(input_str) - 4))
                    input_win.refresh()
                    curses.napms(1200)
            input_str = ""

# 사용 예시:
# from simulator import ARMv7Simulator
# sim = ARMv7Simulator()
# tui = TUI(sim)
# tui.run()