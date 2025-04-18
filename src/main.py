from tkinter import Tk, Label, Entry, Button, Text, END, Scrollbar, Frame
from simulator import ARMv7Simulator

class ARMv7SimulatorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("ARMv7 Simulator")
        
        self.simulator = ARMv7Simulator()

        self.instruction_label = Label(master, text="Enter Instruction:")
        self.instruction_label.pack()

        self.instruction_entry = Entry(master)
        self.instruction_entry.pack()

        self.execute_button = Button(master, text="Execute", command=self.execute_instruction)
        self.execute_button.pack()

        self.output_text = Text(master, height=15, width=50)
        self.output_text.pack()

        self.scrollbar = Scrollbar(master, command=self.output_text.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.output_text.config(yscrollcommand=self.scrollbar.set)

        self.visualize_button = Button(master, text="Visualize", command=self.visualize)
        self.visualize_button.pack()

    def execute_instruction(self):
        instruction = self.instruction_entry.get()
        if instruction.strip():
            self.simulator.parse_and_execute(instruction)
            self.instruction_entry.delete(0, END)

    def visualize(self):
        self.output_text.delete(1.0, END)
        self.output_text.insert(END, "Registers:\n")
        for k, v in self.simulator.registers.items():
            self.output_text.insert(END, f"{k}: {v}\n")
        self.output_text.insert(END, "\nMemory (first 16 words):\n")
        for i in range(16):
            self.output_text.insert(END, f"[{i}]: {self.simulator.memory[i]}\n")
        self.output_text.insert(END, "-" * 40 + "\n")

def main():
    root = Tk()
    app = ARMv7SimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()