from simulator import ARMv7Simulator
from tui import TUI
import sys

def main():
    simulator = ARMv7Simulator()
    commands = []
    reserved_commands = []

    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            break_found = False
            for line in f:
                cmd = line.strip()
                if not cmd or cmd.startswith("#"):
                    continue
                if cmd.startswith("@@ break"):
                    break_found = True
                    print("Breakpoint encountered. Switching to interactive mode.")
                    continue
                if not break_found:
                    commands.append(cmd)
                else:
                    reserved_commands.append(cmd)
        # break 전까지 일괄 실행
        for cmd in commands:
            try:
                simulator.parse_and_execute(cmd)
                print(f"Executed: {cmd}")
            except Exception as e:
                print(f"Error: {e} (cmd: {cmd})")
        # break 이후 명령어 reserved에 추가
        for cmd in reserved_commands:
            simulator.add_reserved(cmd)
        # break 이후부터는 TUI로
        tui = TUI(simulator)
        tui.run()
    else:
        tui = TUI(simulator)
        tui.run()

if __name__ == "__main__":
    main()