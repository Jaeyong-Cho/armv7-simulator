from simulator import ARMv7Simulator
from tui import TUI

def main():
    simulator = ARMv7Simulator()
    tui = TUI(simulator)
    tui.run()

if __name__ == "__main__":
    main()