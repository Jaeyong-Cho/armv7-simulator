# ARMv7 Simulator GUI

This project is a graphical user interface (GUI) application for an ARMv7 simulator. It allows users to input ARMv7 assembly instructions and visualize the state of the simulator, including registers and memory.

## Project Structure

```
armv7-simulator-gui
├── src
│   ├── main.py          # Entry point of the application
│   ├── simulator.py     # Contains the ARMv7Simulator class
│   └── gui.py           # Defines the GUI components
├── requirements.txt     # Lists the project dependencies
└── README.md            # Documentation for the project
```

## Requirements

To run this project, you need to install the required dependencies. You can do this by running:

```
pip install -r requirements.txt
```

## Usage

1. Run the application by executing the `main.py` file:

   ```
   python src/main.py
   ```

2. The GUI will open, allowing you to input ARMv7 instructions.

3. Enter instructions such as `MOV`, `ADD`, `STR`, and `LDR` to manipulate the simulator's state.

4. The current state of the registers and memory will be displayed after each instruction is executed.

## Instructions Format

- **MOV Rd, #imm**: Move an immediate value into a register.
- **ADD Rd, Rn, #imm**: Add an immediate value to a register and store the result in another register.
- **STR Rd, [Rn, #imm]**: Store the value from a register into memory at an address calculated from another register and an immediate offset.
- **LDR Rd, [Rn, #imm]**: Load a value from memory into a register from an address calculated from another register and an immediate offset.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.