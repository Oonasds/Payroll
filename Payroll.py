import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import qrcode
from PIL import Image, ImageTk
import pyqrcode


class Employee:
    def __init__(self, name, hourly_rate=0.0):
        self.name = name
        self.hourly_rate = hourly_rate
        self.worked_hours = 0

    def calculate_salary(self):
        return self.hourly_rate * self.worked_hours

    def reset(self):
        self.worked_hours = 0

class PayrollSystem:
    def __init__(self):
        self.employees = []

    def add_employee(self, name, hourly_rate):
        employee = Employee(name, hourly_rate)
        self.employees.append(employee)

    def add_worked_hours(self, name, hours):
        employee = next((emp for emp in self.employees if emp.name == name), None)

        if employee:
            employee.worked_hours += hours
        else:
            raise ValueError(f"Employee {name} not found.")

    def reset_employee(self, name):
        employee = next((emp for emp in self.employees if emp.name == name), None)

        if employee:
            employee.reset()
        else:
            raise ValueError(f"Employee {name} not found.")

    def edit_hourly_rate(self, name, new_hourly_rate):
        employee = next((emp for emp in self.employees if emp.name == name), None)

        if employee:
            employee.hourly_rate = new_hourly_rate
        else:
            raise ValueError(f"Employee {name} not found.")

    def delete_employee(self, name):
        self.employees = [emp for emp in self.employees if emp.name != name]

    def calculate_payroll(self):
        payroll_info = []
        for i, employee in enumerate(self.employees):
            payroll_info.append(f"Employee Payroll\n================\nPayroll for: {i + 1} - {employee.name}\n- Hourly Rate: ${employee.hourly_rate:.2f}\n- Worked Hours: {employee.worked_hours}\n- Check amount: ${employee.calculate_salary():.2f}\n")
        return '\n'.join(payroll_info)

class EmployeeEntryWindow:
    def __init__(self, root, payroll_system, payroll_window):
        self.root = root
        self.root.title("Enter Employee Information")

        self.payroll_system = payroll_system
        self.payroll_window = payroll_window

        self.name_label = ttk.Label(root, text="Enter employee name:")
        self.name_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        self.name_entry = ttk.Entry(root, font=('Arial', 12))
        self.name_entry.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        self.rate_label = ttk.Label(root, text="Enter hourly rate:")
        self.rate_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        self.rate_entry = ttk.Entry(root, font=('Arial', 12))
        self.rate_entry.grid(row=1, column=1, pady=10, padx=10, sticky="ew")

        self.submit_button = ttk.Button(root, text="Submit", command=self.submit_employee)
        self.submit_button.grid(row=2, column=0, columnspan=2, pady=20, padx=10, sticky="ew")

        self.shutdown_button = ttk.Button(root, text="Shutdown", command=self.shutdown)
        self.shutdown_button.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    def submit_employee(self):
        name = self.name_entry.get()
        rate_str = self.rate_entry.get()

        try:
            rate = float(rate_str)

            if rate < 0:
                raise ValueError("Hourly rate must be non-negative.")

            self.payroll_system.add_employee(name, rate)
            self.payroll_window.refresh_employee_list()
            self.payroll_window.refresh_payroll()
            messagebox.showinfo("Success", "Employee information submitted successfully!")
            self.root.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def shutdown(self):
        self.root.destroy()

class PayrollWindow:
    def __init__(self, root, payroll_system):
        self.root = root
        self.root.title("Payroll System")

        self.payroll_system = payroll_system

        self.name_label = ttk.Label(root, text="Select employee:", font=('Arial', 12, 'bold'))
        self.name_label.grid(row=0, column=0, pady=10, padx=20, sticky="w")

        self.name_var = tk.StringVar()
        self.name_combobox = ttk.Combobox(root, textvariable=self.name_var, values=self.get_employee_names(), font=('Arial', 12))
        self.name_combobox.grid(row=0, column=1, pady=10, padx=20, sticky="ew")

        self.delete_employee_button = ttk.Button(root, text="Delete Employee", command=self.delete_employee)
        self.delete_employee_button.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        self.add_employee_button = ttk.Button(root, text="Add Employee", command=self.show_entry_window)
        self.add_employee_button.grid(row=0, column=2, pady=10, padx=20, sticky="ew")

        self.edit_rate_button = ttk.Button(root, text="Edit Employee", command=self.show_edit_window)
        self.edit_rate_button.grid(row=1, column=1, pady=10, padx=20, sticky="ew")

        self.clear_employee_button = ttk.Button(root, text="Clear Employee", command=self.clear_employee)
        self.clear_employee_button.grid(row=1, column=2, pady=10, padx=20, sticky="ew")

        self.hours_label = ttk.Label(root, text="Enter worked hours:", font=('Arial', 12, 'bold'))
        self.hours_label.grid(row=2, column=0, pady=10, padx=20, sticky="w")

        self.hours_entry = ttk.Entry(root, font=('Arial', 10))
        self.hours_entry.grid(row=2, column=1, pady=10, padx=20, sticky="ew")

        self.submit_hours_button = ttk.Button(root, text="Submit Hours", command=self.submit_hours)
        self.submit_hours_button.grid(row=2, column=2, pady=20, padx=10, sticky="ew")

        self.qr_button = ttk.Button(root, text="Generate QR Code", command=self.generate_qr_code)
        self.qr_button.grid(row=3, column=0, columnspan=2, pady=10, padx=20, sticky="ew")

        self.shutdown_button = ttk.Button(root, text="Shutdown", command=self.shutdown)
        self.shutdown_button.grid(row=3, column=2, pady=10, padx=20, sticky="ew")

        self.payroll_text = tk.Text(root, height=10, width=80, wrap=tk.WORD, borderwidth=2, relief="solid", font=("Arial", 10))
        self.payroll_text.grid(row=0, column=3, rowspan=4, pady=(10, 20), padx=20, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(root, command=self.payroll_text.yview)
        self.scrollbar.grid(row=0, column=4, rowspan=4, pady=(10, 20), sticky="nsew")
        self.payroll_text['yscrollcommand'] = self.scrollbar.set

        self.payroll_text.tag_configure('center', justify='center')
        self.payroll_text.insert(tk.END, "Employee Payroll\n================\n", 'center')
        self.payroll_text.tag_configure('left', justify='left')
        self.payroll_text.insert(tk.END, "\n", 'left')

        self.refresh_payroll()

    
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)
        root.columnconfigure(3, weight=0)  # Column 3 is used for spacing
        root.columnconfigure(4, weight=1)  # Column 4 is used for the text field
        root.rowconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)
        root.rowconfigure(3, weight=1)

        
        for i in range(7):
            root.columnconfigure(i, weight=1)
        root.rowconfigure(2, weight=1)

    def refresh_employee_list(self):
        self.name_combobox['values'] = self.get_employee_names()

    def refresh_payroll(self):
        payroll_info = self.payroll_system.calculate_payroll()
        self.payroll_text.delete("1.0", tk.END)  
        self.payroll_text.insert(tk.END, payroll_info)

    def show_entry_window(self):
        entry_root = tk.Toplevel(self.root)
        entry_window = EmployeeEntryWindow(entry_root, self.payroll_system, self)
        entry_root.mainloop()

    def show_edit_window(self):
        name = self.name_var.get()
        if name:
            edit_root = tk.Toplevel(self.root)
            edit_window = EditHourlyRateWindow(edit_root, self.payroll_system, self, name)
            edit_root.mainloop()
        else:
            messagebox.showwarning("Warning", "Please select or enter an employee.")

    def clear_employee(self):
        name = self.name_var.get()
        try:
            self.payroll_system.reset_employee(name)
            messagebox.showinfo("Success", f"{name}'s payroll has been cleared.")
            self.refresh_payroll()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_employee(self):
        name = self.name_var.get()
        try:
            self.payroll_system.delete_employee(name)
            messagebox.showinfo("Success", f"{name} has been deleted.")
            self.refresh_employee_list()
            self.refresh_payroll()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def submit_hours(self):
        name = self.name_var.get()
        hours_str = self.hours_entry.get()

        try:
            hours = float(hours_str)

            if hours < 0:
                raise ValueError("Worked hours must be non-negative.")

            self.payroll_system.add_worked_hours(name, hours)
            messagebox.showinfo("Success", f"Worked hours submitted successfully for {name}!")
            self.refresh_payroll()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def generate_qr_code(self):
        name = self.name_var.get()
        employee = next((emp for emp in self.payroll_system.employees if emp.name == name), None)

        if employee:
            total_salary = employee.calculate_salary()
            qr_data = f"Employee: {employee.name}\nHourly Rate: ${employee.hourly_rate:.2f}\nWorked Hours: {employee.worked_hours}\nTotal Salary: ${total_salary:.2f}"
            self.show_qr_code(qr_data)
        else:
            messagebox.showwarning("Warning", "Please select or enter an employee.")

    def show_qr_code(self, qr_data):
        qr_code = pyqrcode.create(qr_data)
        qr_code.show()

    def shutdown(self):
        self.root.destroy()

    def get_employee_names(self):
        return sorted([emp.name for emp in self.payroll_system.employees])



class EditHourlyRateWindow:
    def __init__(self, root, payroll_system, payroll_window, employee_name):
        self.root = root
        self.root.title("Edit Hourly Rate")

        self.payroll_system = payroll_system
        self.payroll_window = payroll_window
        self.employee_name = employee_name

        self.current_hourly_rate = self.get_current_hourly_rate()

        self.rate_label = ttk.Label(root, text=f"Current Hourly Ratefor {employee_name}: ${self.current_hourly_rate:.2f}")
        self.rate_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        self.new_rate_label = ttk.Label(root, text="Enter new hourly rate:")
        self.new_rate_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        self.new_rate_entry = ttk.Entry(root, font=('Arial', 12))
        self.new_rate_entry.grid(row=1, column=1, pady=10, padx=10, sticky="ew")

        self.submit_button = ttk.Button(root, text="Submit", command=self.submit_new_rate)
        self.submit_button.grid(row=2, column=0, columnspan=2, pady=20, padx=10, sticky="ew")

        self.shutdown_button = ttk.Button(root, text="Shutdown", command=self.shutdown)
        self.shutdown_button.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    def get_current_hourly_rate(self):
        employee = next((emp for emp in self.payroll_system.employees if emp.name == self.employee_name), None)
        if employee:
            return employee.hourly_rate
        else:
            raise ValueError(f"Employee {self.employee_name} not found.")

    def submit_new_rate(self):
        new_rate_str = self.new_rate_entry.get()

        try:
            new_rate = float(new_rate_str)

            if new_rate < 0:
                raise ValueError("Hourly rate must be non-negative.")

            self.payroll_system.edit_hourly_rate(self.employee_name, new_rate)
            self.payroll_window.refresh_employee_list()
            self.payroll_window.refresh_payroll()
            messagebox.showinfo("Success", f"Hourly rate updated successfully for {self.employee_name}!")
            self.root.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def shutdown(self):
        self.root.destroy()

def main():
    payroll_system = PayrollSystem()

    root = tk.Tk()
    root.geometry("1200x600")  # Increased the window size
    payroll_window = PayrollWindow(root, payroll_system)
    root.mainloop()

if __name__ == "__main__":
    main()

