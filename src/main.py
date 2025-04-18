from simulator import ARMv7Simulator

def print_state(simulator):
    print("\nRegisters:")
    for k, v in simulator.registers.items():
        print(f"{k}: {v}")
    print("\nMemory (first 16 words):")
    for i in range(16):
        print(f"[{i}]: {simulator.memory[i]}")
    print("-" * 40)

def main():
    simulator = ARMv7Simulator()
    print("ARMv7 Simulator (TUI)")
    print("Type 'visualize' to show state, 'exit' to quit.\n")
    while True:
        instruction = input("Enter Instruction: ").strip()
        if instruction.lower() == "exit":
            print("Exiting.")
            break
        elif instruction.lower() == "visualize":
            print_state(simulator)
        elif instruction:
            simulator.parse_and_execute(instruction)
        else:
            continue

if __name__ == "__main__":
    main()