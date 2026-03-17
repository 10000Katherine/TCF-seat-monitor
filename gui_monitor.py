import json
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext

from monitor_core import (
    MonitorEngine,
    load_app_config,
    load_env,
    load_targets,
    save_app_config,
    write_env,
)


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TCF Seat Monitor")
        self.root.geometry("720x640")
        self.engine = MonitorEngine(self.append_log)

        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.to_email_var = tk.StringVar()
        self.interval_var = tk.StringVar(value="300")
        self.target_vars = {}

        self.build_ui()
        self.load_saved_data()

    def build_ui(self):
        title = tk.Label(self.root, text="TCF Seat Monitor", font=("Segoe UI", 18, "bold"))
        title.pack(pady=10)

        card = tk.Frame(self.root, padx=14, pady=10)
        card.pack(fill="x")

        self._row(card, "Gmail", self.email_var)
        self._row(card, "App Password", self.password_var, show="*")
        self._row(card, "Notify Email", self.to_email_var)
        self._row(card, "Check Interval (seconds)", self.interval_var)

        target_frame = tk.LabelFrame(self.root, text="Locations", padx=10, pady=10)
        target_frame.pack(fill="x", padx=12, pady=8)

        for target in load_targets():
            var = tk.BooleanVar(value=target.get("enabled", True))
            self.target_vars[target["name"]] = var
            text = f"{target['name']}  |  {target.get('note', '')}"
            tk.Checkbutton(target_frame, text=text, variable=var, anchor="w", justify="left").pack(fill="x", anchor="w")

        btns = tk.Frame(self.root)
        btns.pack(pady=10)

        tk.Button(btns, text="Save Config", width=14, command=self.save_config).grid(row=0, column=0, padx=6)
        tk.Button(btns, text="Start Monitoring", width=16, command=self.start_monitor).grid(row=0, column=1, padx=6)
        tk.Button(btns, text="Stop", width=10, command=self.stop_monitor).grid(row=0, column=2, padx=6)
        tk.Button(btns, text="Test Email", width=12, command=self.test_email).grid(row=0, column=3, padx=6)

        log_frame = tk.LabelFrame(self.root, text="Log", padx=8, pady=8)
        log_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.log_box = scrolledtext.ScrolledText(log_frame, wrap="word", height=18)
        self.log_box.pack(fill="both", expand=True)

        footer = tk.Label(
            self.root,
            text="Victoria is keyword-based. Vancouver / Ashton are change-detection alerts and should be confirmed manually.",
            fg="#555555"
        )
        footer.pack(pady=(0, 8))

    def _row(self, parent, label, variable, show=None):
        row = tk.Frame(parent)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
        entry = tk.Entry(row, textvariable=variable, width=50, show=show)
        entry.pack(side="left", fill="x", expand=True)

    def append_log(self, message: str):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def load_saved_data(self):
        env = load_env()
        self.email_var.set(env.get("EMAIL", ""))
        self.password_var.set(env.get("PASSWORD", ""))
        self.to_email_var.set(env.get("TO_EMAIL", ""))
        self.interval_var.set(env.get("CHECK_INTERVAL", "300"))

        app_cfg = load_app_config()
        enabled = app_cfg.get("enabled_targets", {})
        for name, var in self.target_vars.items():
            if name in enabled:
                var.set(enabled[name])

    def save_config(self):
        try:
            interval = int(self.interval_var.get().strip())
            if interval < 30:
                raise ValueError("Interval too short")
        except Exception:
            messagebox.showerror("Error", "Check Interval must be a number and at least 30 seconds.")
            return

        write_env(
            self.email_var.get().strip(),
            self.password_var.get().strip(),
            self.to_email_var.get().strip(),
            interval,
        )

        save_app_config({
            "enabled_targets": {name: var.get() for name, var in self.target_vars.items()}
        })
        self.append_log("Config saved.")
        messagebox.showinfo("Saved", "Configuration saved.")

    def selected_targets(self):
        return [name for name, var in self.target_vars.items() if var.get()]

    def start_monitor(self):
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        to_email = self.to_email_var.get().strip()
        names = self.selected_targets()

        if not email or not password or not to_email:
            messagebox.showerror("Error", "Please fill Gmail, App Password, and Notify Email.")
            return
        if not names:
            messagebox.showerror("Error", "Please select at least one location.")
            return
        try:
            interval = int(self.interval_var.get().strip())
            if interval < 30:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Check Interval must be a number and at least 30 seconds.")
            return

        self.save_config()
        self.engine.start(email, password, to_email, interval, names)

    def stop_monitor(self):
        self.engine.stop()
        self.append_log("Stop requested.")

    def test_email(self):
        from monitor_core import send_email
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        to_email = self.to_email_var.get().strip()
        if not email or not password or not to_email:
            messagebox.showerror("Error", "Please fill Gmail, App Password, and Notify Email.")
            return
        try:
            send_email(
                "TCF Seat Monitor - Test Email",
                "测试邮件发送成功。你的提醒功能可以正常使用。",
                email,
                password,
                to_email
            )
            self.append_log("Test email sent.")
            messagebox.showinfo("Success", "Test email sent.")
        except Exception as e:
            self.append_log(f"Test email failed: {e}")
            messagebox.showerror("Error", f"Test email failed: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
