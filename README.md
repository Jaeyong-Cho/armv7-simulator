# ARMv7 Simulator TUI

This project is a text-based user interface (TUI) application for an ARMv7 simulator. It allows users to input ARMv7 assembly instructions and visualize the state of the simulator, including registers, stack, and memory.

## Project Structure

```
armv7-simulator
├── src
│   ├── main.py          # Entry point of the application
│   ├── simulator.py     # Contains the ARMv7Simulator class
│   ├── tui.py           # Defines the TUI components (curses-based)
│   └── ldr.py           # (Reserved for LDR instruction logic)
├── examples
│   └── ex01.s           # Example ARMv7 assembly file
└── README.md            # Documentation for the project
```

## Requirements

To run this project, you need to install the required dependencies.

> **Note:** The TUI uses the `curses` library, which is included with Python on most Unix-like systems. On Windows, you may need to install `windows-curses`.

## Usage

1. Run the application by executing the `main.py` file:

   ```
   python src/main.py
   ```

   Or, to load and execute an example assembly file up to the breakpoint, then switch to interactive mode:

   ```
   python src/main.py examples/ex01.s
   ```

2. The TUI will open, allowing you to input ARMv7 instructions interactively.

3. Enter instructions such as `MOV`, `ADD`, `STR`, `LDR`, and `PUSH` to manipulate the simulator's state.

4. The current state of the registers, stack, and memory will be displayed after each instruction is executed.

## Instructions Format

- **MOV Rd, #imm**: Move an immediate value into a register.
- **ADD Rd, Rn, #imm**: Add an immediate value to a register and store the result in another register.
- **STR Rd, [Rn, #imm]**: Store the value from a register into memory at an address calculated from another register and an immediate offset.
- **LDR Rd, =label**: Load the address of a label into a register.
- **PUSH {rX-rY, ...}**: Push registers onto the stack.

### `@@` Keyword

The `@@` keyword is used to provide additional information to the simulator. It is not part of standard ARM assembly syntax, but is recognized by this simulator for annotation or reference purposes.

- **`@@ 0xADDR`**: Labels such as `@@ 0xADDR` are used to indicate specific memory addresses in the example code. The simulator may use these addresses for jumps, data storage, or as reference points, but it does not perform actual linking or relocation. These labels are only for clarity and documentation within the example files.

### `@@ break`

If the example file (such as `ex01.s`) contains a `break` instruction, the simulator will execute instructions up to the `break` and then switch to interactive mode. This allows you to step through the rest of the program manually or inspect the state at the breakpoint.

### `.extern label @@ 0xADDR`

If you see comments like `.extern label` in the example assembly files, these are for documentation purposes only. They indicate external symbols or functions that might be referenced, but the simulator does not resolve or link external symbols. You can ignore these comments during simulation.


## Example

You can find an example assembly file in [examples/ex01.s](examples/ex01.s).


## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.