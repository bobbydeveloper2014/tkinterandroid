import tkinter as tk

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Máy Tính")
        master.geometry("400x600")
        master.config(bg="#f0f0f0")

        # Khởi tạo các biến
        self.result_var = tk.StringVar()

        # Tạo giao diện
        self.create_widgets()

    def create_widgets(self):
        # Hiển thị kết quả với chữ màu đen
        entry = tk.Entry(self.master, textvariable=self.result_var, font=("Arial", 24), bd=10, 
                         insertwidth=4, width=14, borderwidth=4, fg="black", bg="white")  # Màu chữ đen
        entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Tạo các nút
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('C', 4, 1), ('=', 4, 2), ('+', 4, 3),
        ]

        for (text, row, column) in buttons:
            self.create_button(text, row, column)

    def create_button(self, text, row, column):
        button = tk.Button(self.master, text=text, padx=20, pady=20, font=("Arial", 20), 
                           command=lambda: self.on_button_click(text), bg="#4CAF50", fg="black",  # Chữ màu đen
                           activebackground="#45a049")
        button.grid(row=row, column=column, padx=5, pady=5)

    def on_button_click(self, char):
        if char == 'C':
            self.result_var.set("")  # Xóa kết quả
        elif char == '=':
            try:
                # Tính toán và cập nhật kết quả
                result = eval(self.result_var.get())
                self.result_var.set(result)
            except Exception as e:
                self.result_var.set("Error")
        else:
            # Cập nhật biểu thức
            current_text = self.result_var.get()
            self.result_var.set(current_text + char)

if __name__ == "__main__":
    root = tk.Tk()
    calc = Calculator(root)
    root.mainloop()
