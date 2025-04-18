from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, END, Frame
from simulator import ARMv7Simulator

class ARMv7SimulatorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("ARMv7 Simulator")
        
        self.simulator = ARMv7Simulator()
        
        self.create_widgets()

    def create_widgets(self):
        self.instruction_label = Label(self.master, text="Enter Instruction:")
        self.instruction_label.pack()

        self.instruction_entry = Entry(self.master, width=50)
        self.instruction_entry.pack()

        self.execute_button = Button(self.master, text="Execute", command=self.execute_instruction)
        self.execute_button.pack()

        self.output_frame = Frame(self.master)
        self.output_frame.pack()

        self.output_text = Text(self.output_frame, width=60, height=20)
        self.output_text.pack(side="left")

        self.scrollbar = Scrollbar(self.output_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.output_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.output_text.yview)

    def execute_instruction(self):
        instruction = self.instruction_entry.get()
        if instruction.strip():
            self.simulator.parse_and_execute(instruction)
            self.visualize()

    def visualize(self):
        self.output_text.delete(1.0, END)
        self.output_text.insert(END, "Registers:\n")
        for reg, value in self.simulator.registers.items():
            self.output_text.insert(END, f"{reg}: {value}\n")
        
        self.output_text.insert(END, "\nMemory (first 16 words):\n")
        for i in range(16):
            self.output_text.insert(END, f"[{i}]: {self.simulator.memory[i]}\n")

def main():
    root = Tk()
    app = ARMv7SimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()