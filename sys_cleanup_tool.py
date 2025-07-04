import os
import shutil
import smtplib
import json
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import schedule
import threading
import time
import psutil
from email.message import EmailMessage
import datetime
from plyer import notification
import re
import platform  # For platform detection

CONFIG_FILE = "config.json"
HISTORY_FILE = "deleted_files.log"
LOCK_FILE = "cleanup.lock"
STOP_FLAG = False
CLEANUP_THREAD = None


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}
def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def notify(title, message):
    print(f"{title}: {message}")
    notification.notify(
        title=title,
        message=message,
        app_name="SysCleanupTool",
        timeout=5
    )
    with open("events.log", "a") as log:
        log.write(f"{datetime.datetime.now()}: {title} - {message}\n")


def send_email(subject, body, config):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config["sender_email"]
    msg["To"] = config["receiver_email"]
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(config["sender_email"], config["app_password"])
        smtp.send_message(msg)


def send_confirmation_email():
    config = load_config()
    try:
        scheduled_time_12hr = datetime.datetime.strptime(config['scheduled_time'], "%H:%M").strftime("%I:%M %p")
    except ValueError:
        scheduled_time_12hr = config['scheduled_time']

    subject = "System Cleanup Alert"
    body = (
        f"This is a confirmation and reminder for your scheduled system cleanup.\n"
        f"Scheduled Time: {config['scheduled_day']} at {scheduled_time_12hr}\n\n"
        f"Please check your whitelist and reply with YES to proceed.\n"
    )
    try:
        send_email(subject, body, config)
        notify("Email Sent", "Confirmation email sent for scheduled cleanup.")
        return True
    except Exception as e:
        notify("Email Failed", f"Failed to send confirmation email: {e}")
        return False


def empty_recycle_bin():
    system = platform.system()
    try:
        if system == "Windows":
            import winshell
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        elif system == "Darwin":  # macOS
            os.system("rm -rf ~/.Trash/*")
        elif system == "Linux":
            os.system("rm -rf ~/.local/share/Trash/files/*")
        return True
    except Exception as e:
        notify("Recycle Bin Error", f"Failed to empty recycle bin: {e}")
        return False


def perform_cleanup():
    global STOP_FLAG, CLEANUP_THREAD
    STOP_FLAG = False

    if os.path.exists(LOCK_FILE):
        notify("Cleanup Running", "A cleanup process is already in progress.")
        return

    open(LOCK_FILE, "w").close()
    config = load_config()
    whitelist_path = config.get("whitelist_path", "")
    whitelist = []
    if os.path.exists(whitelist_path):
        with open(whitelist_path, "r") as f:
            whitelist = [line.strip() for line in f.readlines()]

    deleted_files = []
    for path in [os.getenv("TEMP"), os.getenv("TMP"), "/tmp"]:
        if path and os.path.exists(path) and not STOP_FLAG:
            for root, _, files in os.walk(path):
                for file in files:
                    if STOP_FLAG:
                        break
                    filepath = os.path.join(root, file)
                    if not any(filepath.startswith(w) for w in whitelist):
                        try:
                            os.remove(filepath)
                            deleted_files.append(filepath)
                        except:
                            pass

    if not STOP_FLAG:
        if empty_recycle_bin():
            deleted_files.append("Recycle Bin Emptied")

    if deleted_files:
        with open(HISTORY_FILE, "a") as log:
            for f in deleted_files:
                log.write(f"{datetime.datetime.now()}: {f}\n")

    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

    if STOP_FLAG:
        notify("Cleanup Stopped", "System cleanup was stopped by user.")
        messagebox.showinfo("Cleanup Stopped", "System cleanup was stopped by user.")
    else:
        notify("Cleanup Done", "System cleanup completed successfully.")
        messagebox.showinfo("Cleanup Complete", "System cleanup completed successfully.")

    CLEANUP_THREAD = None


def stop_cleanup():
    global STOP_FLAG, CLEANUP_THREAD
    STOP_FLAG = True
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    if CLEANUP_THREAD and CLEANUP_THREAD.is_alive():
        CLEANUP_THREAD.join(timeout=1)
    notify("Cleanup Stopped", "Cleanup process has been stopped by user.")
    messagebox.showinfo("Cleanup Stopped", "The cleanup process has been stopped successfully.")


def check_email_reply():
    print("Checking email reply logic here... (mocked for demo)")
    return not STOP_FLAG


def is_valid_time_format(time_str):
    return re.match(r"^\d{2}:\d{2}(:\d{2})?$", time_str) is not None


def schedule_cleanup():
    global CLEANUP_THREAD
    config = load_config()
    schedule.clear()
    scheduled_day = config.get("scheduled_day")
    scheduled_time = config.get("scheduled_time")

    if not scheduled_day or not scheduled_time or not is_valid_time_format(scheduled_time):
        notify("Invalid Schedule", f"Scheduled time '{scheduled_time}' is invalid or missing.")
        return

    def task():
        global CLEANUP_THREAD
        if not STOP_FLAG and (CLEANUP_THREAD is None or not CLEANUP_THREAD.is_alive()):
            cleanup_thread = threading.Thread(target=perform_cleanup)
            cleanup_thread.start()
            CLEANUP_THREAD = cleanup_thread

    try:
        getattr(schedule.every(), scheduled_day.lower()).at(scheduled_time).do(task)
    except Exception as e:
        notify("Scheduling Error", f"Failed to schedule cleanup: {e}")
        return

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()


def get_disk_usage():
    usage = psutil.disk_usage('/')
    return f"Disk Usage: {usage.percent}% ({usage.used // (2 ** 30)}GB used of {usage.total // (2 ** 30)}GB)"


def show_settings_window():
    config = load_config()

    def save_and_send():
        config["sender_email"] = sender_email_entry.get()
        config["app_password"] = app_password_entry.get()
        config["receiver_email"] = receiver_email_entry.get()
        config["whitelist_path"] = whitelist_path_entry.get()
        config["scheduled_day"] = day_var.get()
        config["scheduled_time"] = time_entry.get()

        save_config(config)
        schedule_cleanup()

        if send_confirmation_email():
            messagebox.showinfo("Success", "Configuration saved and confirmation email sent.")
        else:
            messagebox.showerror("Error", "Failed to send confirmation email.")

    def browse_whitelist():
        path = filedialog.askopenfilename()
        if path:
            whitelist_path_entry.delete(0, tk.END)
            whitelist_path_entry.insert(0, path)

    def edit_whitelist():
        path = whitelist_path_entry.get()
        if os.path.exists(path):
            edit_win = tk.Toplevel(window)
            edit_win.title("Edit Whitelist")
            text = scrolledtext.ScrolledText(edit_win, width=60, height=20)
            text.pack()
            with open(path, "r") as f:
                text.insert(tk.END, f.read())

            def save_text():
                with open(path, "w") as f:
                    f.write(text.get("1.0", tk.END))
                edit_win.destroy()

            tk.Button(edit_win, text="Save", command=save_text).pack()

    win = tk.Toplevel(window)
    win.title("Settings")

    tk.Label(win, text="Sender Email").grid(row=0, column=0)
    sender_email_entry = tk.Entry(win, width=40)
    sender_email_entry.insert(0, config.get("sender_email", ""))
    sender_email_entry.grid(row=0, column=1)

    tk.Label(win, text="App Password").grid(row=1, column=0)
    app_password_entry = tk.Entry(win, show="*", width=40)
    app_password_entry.insert(0, config.get("app_password", ""))
    app_password_entry.grid(row=1, column=1)

    tk.Label(win, text="Receiver Email").grid(row=2, column=0)
    receiver_email_entry = tk.Entry(win, width=40)
    receiver_email_entry.insert(0, config.get("receiver_email", ""))
    receiver_email_entry.grid(row=2, column=1)

    tk.Label(win, text="Whitelist Path").grid(row=3, column=0)
    whitelist_path_entry = tk.Entry(win, width=40)
    whitelist_path_entry.insert(0, config.get("whitelist_path", ""))
    whitelist_path_entry.grid(row=3, column=1)
    tk.Button(win, text="Browse", command=browse_whitelist).grid(row=3, column=2)
    tk.Button(win, text="Edit", command=edit_whitelist).grid(row=3, column=3)

    tk.Label(win, text="Scheduled Day").grid(row=4, column=0)
    day_var = tk.StringVar(value=config.get("scheduled_day", "Monday"))
    tk.OptionMenu(win, day_var, *["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]).grid(
        row=4, column=1)

    tk.Label(win, text="Scheduled Time (HH:MM)").grid(row=5, column=0)
    time_entry = tk.Entry(win, width=20)
    time_entry.insert(0, config.get("scheduled_time", "12:00"))
    time_entry.grid(row=5, column=1)

    tk.Button(win, text="Save Settings", command=save_and_send).grid(row=6, column=0, columnspan=2, pady=10)


def show_history():
    history_win = tk.Toplevel(window)
    history_win.title("Deleted Files History")
    text = scrolledtext.ScrolledText(history_win, width=80, height=20)
    text.pack()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            text.insert(tk.END, f.read())

    def clear_history():
        open(HISTORY_FILE, "w").close()
        text.delete("1.0", tk.END)

    tk.Button(history_win, text="Clear History", command=clear_history).pack()


# Main window setup
window = tk.Tk()
window.title("System Cleanup Automation Tool")

tk.Label(window, text="System Cleanup Tool", font=("Arial", 16)).pack(pady=10)
tk.Button(window, text="Settings", width=20, command=show_settings_window).pack(pady=5)
tk.Button(window, text="View Deleted File History", width=25, command=show_history).pack(pady=5)
tk.Button(window, text="Stop Cleanup", width=20, command=stop_cleanup, bg="#ff9999").pack(pady=5)
tk.Label(window, text=get_disk_usage()).pack(pady=10)

schedule_cleanup()
window.mainloop()
