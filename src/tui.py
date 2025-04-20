import curses
import datetime

class TUI:
    def __init__(self, simulator):
        self.simulator = simulator
        self.last_message = ""
        self.exit = False
        self.input_exception_log = ""
        self.highlight_registers = set()
        self.highlight_memory = set()
        self.highlight_stack = set()
        self.highlight_color_pair = 2  # 항상 초록색 사용
        self.mem_scroll = 0  # 메모리 스크롤 오프셋(라인 단위)
        # --- 디버깅 로그 파일 열기 ---
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.debug_log = open(f"debug_log_{now}.txt", "w", encoding="utf-8")

    def log_debug_info(self, command, before_regs, after_regs, before_mem, after_mem, before_stack, after_stack):
        self.debug_log.write(f"\n=== Command: {command} ===\n")
        self.debug_log.write("Registers (before):\n")
        for mode, regs in before_regs.items():
            self.debug_log.write(f"  <{mode}> {regs}\n")
        self.debug_log.write("Registers (after):\n")
        for mode, regs in after_regs.items():
            self.debug_log.write(f"  <{mode}> {regs}\n")
        self.debug_log.write("Memory (before):\n")
        for addr in sorted(before_mem.keys()):
            self.debug_log.write(f"  {addr:08X}: {before_mem[addr]:08X}\n")
        self.debug_log.write("Memory (after):\n")
        for addr in sorted(after_mem.keys()):
            self.debug_log.write(f"  {addr:08X}: {after_mem[addr]:08X}\n")
        self.debug_log.write("Stack (before):\n")
        for mode, stack in before_stack.items():
            self.debug_log.write(f"  <{mode}> {stack}\n")
        self.debug_log.write("Stack (after):\n")
        for mode, stack in after_stack.items():
            self.debug_log.write(f"  <{mode}> {stack}\n")
        self.debug_log.write("="*40 + "\n")
        self.debug_log.flush()

    def set_highlight(self, before, after, kind):
        changed = set()
        if kind == "registers":
            for mode in after:
                for reg in after[mode]:
                    if mode not in before or reg not in before[mode] or before[mode][reg] != after[mode][reg]:
                        changed.add((mode, reg))
            self.highlight_registers = changed
        elif kind == "memory":
            for i, (b, a) in enumerate(zip(before, after)):
                if b != a:
                    self.highlight_memory.add(i)
        elif kind == "stack":
            for mode in after:
                if mode not in before or before[mode] != after[mode]:
                    self.highlight_stack.add(mode)
        self.highlight_color_pair = 2  # 항상 초록색

    def clear_highlight(self):
        self.highlight_registers = set()
        self.highlight_memory = set()
        self.highlight_stack = set()
        self.highlight_color_pair = 2

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
                    attr = 0
                    if ("com", name) in self.highlight_registers and curses.has_colors():
                        attr = curses.color_pair(self.highlight_color_pair) | curses.A_BOLD
                    win.addstr(row, 3, line[:max_x-4], attr)
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
                        attr = 0
                        if (mode, rname) in self.highlight_registers and curses.has_colors():
                            attr = curses.color_pair(self.highlight_color_pair) | curses.A_BOLD
                        win.addstr(row, 3, line[:max_x-4], attr)
                        row += 1

    def draw_memory(self, win):
        win.clear()
        win.box()
        # 총 메모리 사용량 계산 (4바이트 단위)
        memory = self.simulator.memory
        used_bytes = len(memory) * 4
        win.addstr(0, 2, f"[Memory Map]  Used: {used_bytes} bytes")
        addresses = sorted(memory.keys())
        max_y, max_x = win.getmaxyx()
        visible_lines = max_y - 2
        total_lines = len(addresses)
        # 스크롤 오프셋 보정
        if self.mem_scroll > total_lines - visible_lines:
            self.mem_scroll = max(0, total_lines - visible_lines)
        if self.mem_scroll < 0:
            self.mem_scroll = 0
        # 스크롤된 위치부터 출력
        for line_idx in range(visible_lines):
            addr_idx = self.mem_scroll + line_idx
            if addr_idx >= total_lines:
                break
            addr = addresses[addr_idx]
            val = memory.get(addr, 0)
            out_str = f"{addr:08X}: {val:08X}"
            win.addstr(1 + line_idx, 1, out_str[:max_x])

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
                attr = 0
                if mode in self.highlight_stack and curses.has_colors():
                    attr = curses.color_pair(self.highlight_color_pair) | curses.A_BOLD
                if row < max_y - 1:
                    win.addstr(row, 3, line[:max_x-4], attr)
                    row += 1

    def draw_reserved(self, win, scroll_offset=0):
        win.clear()
        win.box()
        win.addstr(0, 2, "[Reserved Commands]")
        reserved = self.simulator.get_reserved() if hasattr(self.simulator, "get_reserved") else []
        max_y, max_x = win.getmaxyx()
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

        reg_names = []
        for mode in self.simulator.registers:
            reg_names.extend(self.simulator.registers[mode].keys())
        reg_names = list(set(reg_names))

        cursor_pos = len(input_str)
        prev_input_str = input_str

        while True:
            input_win.move(2, 2)
            input_win.clrtoeol()
            if curses.has_colors():
                common_prefix_len = 0
                for a, b in zip(prev_input_str, input_str):
                    if a == b:
                        common_prefix_len += 1
                    else:
                        break
                input_win.addstr(2, 2, prompt)
                input_win.addstr(2, 2 + len(prompt), input_str[:common_prefix_len])
                if common_prefix_len < len(input_str):
                    input_win.addstr(2, 2 + len(prompt) + common_prefix_len, input_str[common_prefix_len:], curses.color_pair(2) | curses.A_BOLD)
                input_win.addstr(2, 2 + len(prompt) + len(input_str), " " * (max_x - len(prompt) - len(input_str) - 4))
            else:
                input_win.addstr(2, 2, prompt + input_str + " " * (max_x - len(prompt) - len(input_str) - 4))
            input_win.move(2, 2 + len(prompt) + cursor_pos)
            input_win.refresh()
            key = input_win.getch()
            prev_input_str = input_str
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
            elif key == 9:
                parts = input_str.strip().split()
                if parts:
                    if len(parts) == 1:
                        prefix = parts[0].upper()
                        matches = [cmd for cmd in command_list if cmd.startswith(prefix)]
                        if matches:
                            parts[0] = matches[0]
                            input_str = " ".join(parts)
                            cursor_pos = len(input_str)
            elif key == 3:
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
                pass

    def _main(self, stdscr):
        curses.curs_set(1)
        curses.noecho()
        input_str = ""
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 초록색
        stdscr.keypad(True)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
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

            usable_height = height - 6
            reg_win_width = max(18, width // 4)
            stack_win_width = max(18, width // 4)
            mem_win_width = max(24, width // 4)
            cmd_win_width = max(16, width // 4)
            reserved_win_width = max(18, width // 4)

            reg_win_height = min(50 + 3, usable_height)
            stack_win_height = usable_height
            mem_win_height = usable_height
            cmd_win_height = min(len(self.simulator.command_list) + 3, usable_height)
            reserved_win_height = usable_height - cmd_win_height
            reserved_win_y = cmd_win_height
            reserved_win_x = reg_win_width + stack_win_width + mem_win_width

            reg_win_x = 0
            stack_win_x = reg_win_x + reg_win_width
            mem_win_x = stack_win_x + stack_win_width
            cmd_win_x = mem_win_x + mem_win_width

            reg_win = curses.newwin(reg_win_height, reg_win_width, 0, reg_win_x)
            stack_win = curses.newwin(stack_win_height, stack_win_width, 0, stack_win_x)
            mem_win = curses.newwin(mem_win_height, mem_win_width, 0, mem_win_x)
            cmd_win = curses.newwin(cmd_win_height, cmd_win_width, 0, cmd_win_x)
            reserved_win = curses.newwin(reserved_win_height, reserved_win_width, reserved_win_y, cmd_win_x)

            # --- 추가: 항상 화면을 그려줌 ---
            self.draw_registers(reg_win)
            reg_win.refresh()
            self.draw_stack(stack_win)
            stack_win.refresh()
            self.draw_memory(mem_win)
            mem_win.refresh()
            self.draw_commands(cmd_win)
            cmd_win.refresh()
            self.draw_reserved(reserved_win)
            reserved_win.refresh()
            # --- 여기까지 ---

            input_win_height = 5
            input_win = curses.newwin(input_win_height, width, height - input_win_height, 0)
            input_win.keypad(True)
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 2, "Enter ARMv7 instruction (or 'q' to quit):")
            # --- 다음 reserved 명령어를 입력창에 미리 보여줌 ---
            next_reserved = ""
            reserved_list = self.simulator.get_reserved() if hasattr(self.simulator, "get_reserved") else []
            if reserved_list:
                next_reserved = reserved_list[0]
            input_prompt_str = input_str
            # 하이라이트: 입력이 없고 reserved 명령어가 있으면 초록색 bold로 표시
            if not input_str and next_reserved:
                if curses.has_colors():
                    input_win.addstr(2, 2, "> ")
                    input_win.addstr(2, 4, next_reserved, curses.color_pair(2) | curses.A_BOLD)
                    input_win.addstr(2, 4 + len(next_reserved), " " * (width - len(next_reserved) - 4))
                else:
                    input_win.addstr(2, 2, "> " + next_reserved + " " * (width - len(next_reserved) - 4))
            else:
                input_win.addstr(2, 2, "> " + input_str + " " * (width - len(input_str) - 4))
            # -------------------------------------------------
            if hasattr(self, "input_exception_log") and self.input_exception_log:
                input_win.addstr(3, 2, f"Error: {self.input_exception_log}"[:width-4], curses.color_pair(1) if curses.has_colors() else 0)
            else:
                input_win.addstr(3, 2, " " * (width-4))
            input_win.refresh()

            msg_y = height - input_win_height - 1
            msg_win = curses.newwin(1, width, msg_y, 0)
            msg_win.addstr(0, 0, self.last_message[:width-1] + " " * (width - len(self.last_message) - 1))
            msg_win.refresh()

            if self.simulator.get_reserved():
                self.input_exception_log = ""
                msg_win.clear()
                msg_win.addstr(0, 0, "Press ENTER to execute next reserved command, or 'q' to quit.")
                msg_win.refresh()
                key = input_win.getch()
                if key in (curses.KEY_ENTER, 10, 13):
                    before_regs = {k: v.copy() for k, v in self.simulator.registers.items()}
                    before_mem = self.simulator.memory.copy()  # <-- 여기!
                    before_stack = {k: v[:] for k, v in self.simulator.stack.items()}
                    next_cmd = self.simulator.pop_reserved()
                    if next_cmd:
                        try:
                            self.simulator.parse_and_execute(next_cmd)
                            self.last_message = f"Executed: {next_cmd}"
                            self.input_exception_log = ""
                        except Exception as e:
                            self.last_message = f"Error: {e}"
                            self.input_exception_log = str(e)
                            msg_win.clear()
                            msg_win.addstr(0, 0, self.last_message[:width-1] + " " * (width - len(self.last_message) - 1))
                            msg_win.refresh()
                    self.clear_highlight()
                    self.set_highlight(before_regs, self.simulator.registers, "registers")
                    self.set_highlight(before_mem, self.simulator.memory, "memory")
                    self.set_highlight(before_stack, self.simulator.stack, "stack")
                    # --- 디버깅 정보 기록 ---
                    after_regs = {k: v.copy() for k, v in self.simulator.registers.items()}
                    after_mem = self.simulator.memory.copy()
                    after_stack = {k: v[:] for k, v in self.simulator.stack.items()}
                    self.log_debug_info(next_cmd, before_regs, after_regs, before_mem, after_mem, before_stack, after_stack)
                    # ---------------------
                    input_str = ""
                    self.draw_registers(reg_win)
                    reg_win.refresh()
                    self.draw_stack(stack_win)
                    stack_win.refresh()
                    self.draw_memory(mem_win)
                    mem_win.refresh()
                    continue
                elif key in (ord('q'), ord('Q')):
                    self.exit = True
                    break
                else:
                    continue
            key = stdscr.getch()
            if key == curses.KEY_MOUSE:
                _, mx, my, _, mouse_state = curses.getmouse()
                # 메모리 윈도우 영역에서만 스크롤 처리
                if (mem_win_y := 0) <= my < (mem_win_y + mem_win_height) and (mem_win_x <= mx < mem_win_x + mem_win_width):
                    if mouse_state & curses.BUTTON4_PRESSED:  # wheel up
                        self.mem_scroll = max(0, self.mem_scroll - 1)
                    elif mouse_state & curses.BUTTON5_PRESSED:  # wheel down
                        self.mem_scroll += 1
            input_str = self.get_user_input(input_win, input_str)
            command = input_str.strip()
            if command.lower() == 'q':
                self.exit = True
                break
            elif command:
                before_regs = {k: v.copy() for k, v in self.simulator.registers.items()}
                before_mem = self.simulator.memory.copy()  # <-- 여기!
                before_stack = {k: v[:] for k, v in self.simulator.stack.items()}
                try:
                    self.simulator.parse_and_execute(command)
                    self.last_message = f"Executed: {command}"
                    self.input_exception_log = ""
                except Exception as e:
                    self.last_message = f"Error: {e}"
                    self.input_exception_log = str(e)
                    msg_win.clear()
                    msg_win.addstr(0, 0, self.last_message[:width-1] + " " * (width - len(self.last_message) - 1))
                    msg_win.refresh()
                    input_win.clear()
                    input_win.box()
                    input_win.addstr(1, 2, "Enter ARMv7 instruction (or 'q' to quit):")
                    input_win.addstr(2, 2, "> " + input_str + " " * (width - len(input_str) - 4))
                    input_win.addstr(3, 2, f"Error: {self.input_exception_log}"[:width-4], curses.color_pair(1) if curses.has_colors() else 0)
                    input_win.refresh()

                self.clear_highlight()
                self.set_highlight(before_regs, self.simulator.registers, "registers")
                self.set_highlight(before_mem, self.simulator.memory, "memory")
                self.set_highlight(before_stack, self.simulator.stack, "stack")
                # --- 디버깅 정보 기록 ---
                after_regs = {k: v.copy() for k, v in self.simulator.registers.items()}
                after_mem = self.simulator.memory.copy()
                after_stack = {k: v[:] for k, v in self.simulator.stack.items()}
                self.log_debug_info(command, before_regs, after_regs, before_mem, after_mem, before_stack, after_stack)
                # ---------------------
                self.draw_registers(reg_win)
                reg_win.refresh()
                self.draw_stack(stack_win)
                stack_win.refresh()
                self.draw_memory(mem_win)
                mem_win.refresh()
            input_str = ""

    def __del__(self):
        # 프로그램 종료 시 파일 닫기
        if hasattr(self, "debug_log") and self.debug_log:
            self.debug_log.close()

# 사용 예시:
# from simulator import ARMv7Simulator
# sim = ARMv7Simulator()
# tui = TUI(sim)
# tui.run()