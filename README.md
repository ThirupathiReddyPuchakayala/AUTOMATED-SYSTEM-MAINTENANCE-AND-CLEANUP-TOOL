# AUTOMATED-SYSTEM-MAINTENANCE-AND-CLEANUP-TOOL

A Python-based desktop utility that automates routine system cleanup tasks—like deleting temporary files, empty folders, and recycle bin contents—while ensuring **data safety** through whitelist protection and **email-based confirmation**.

---

## 🚀 Features

- ✅ **Scheduled Cleanup**: Run automatic cleanups on custom days and times.
- 📧 **Email Confirmation**: Sends a confirmation email before cleanup; proceeds only on “YES” reply.
- 🧾 **Whitelist Protection**: Never deletes user-defined critical files or folders.
- 📈 **Disk Usage Reporting**: See storage saved before and after each cleanup.
- 🔔 **Desktop Notifications**: Instant feedback after completion or cancellation.
- 🖥️ **User-Friendly GUI**: Configure schedule, whitelist, and email in a Tkinter interface.
- 🧰 **Cross-Platform Support**: Works on both **Windows** and **Linux** systems.

---

## 🛠️ Technologies Used

- **Python 3.x**
- [Tkinter](https://docs.python.org/3/library/tkinter.html) – GUI
- `psutil`, `plyer`, `schedule`, `smtplib`, `imaplib`, `json`, `threading`

---

## 📷 Screenshots
![image](https://github.com/user-attachments/assets/37f06ec3-41f1-490e-a0cb-95958a98ab1c)
![{50AD4972-A237-48B6-A547-699A159E087E}](https://github.com/user-attachments/assets/94b78266-64aa-4e72-b390-bf8031177436)
![{04D852F0-BD38-40FE-8D00-79D2BE40E46A}](https://github.com/user-attachments/assets/7641f23f-0859-4e23-8e29-47a221ea83d1)
![image](https://github.com/user-attachments/assets/4cff15db-8846-4bc3-a145-91628b91c791)
![{F885A863-82E2-451D-BEDF-FDD4B2F7CE1C}](https://github.com/user-attachments/assets/e305c644-2d87-4ccc-9d79-d74440046e5f)
![image](https://github.com/user-attachments/assets/118dc853-3ef9-4816-b84e-476164e61e5c)


## ⚙️ How to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
2.Install Required Libraries

```bash
   pip install psutil plyer schedule
Run the Tool
```
   python main.py

Make sure to set up your Gmail app password for sending emails (due to 2FA).

## 🧾Configuration

Email sender/receiver
Whitelist file
Scheduled day and time
Stored in config.json

## 🛡️Safety First

This tool never performs cleanup without user confirmation via email. You stay in full control with features like:
Email prompts
Manual "Stop Cleanup" button
Whitelist enforcement

## 📌 Future Scope

Cloud-based cleanup scheduling
AI-based cleanup suggestions
Voice assistant or chatbot interface
Remote control via web dashboard

## 👨‍💻 Developed By

P. Thirupathi Reddy
M. Amani
P. Akshitha
R. Ramana
V. Nikitha

Guided by Mr. E. Satish Babu, Assistant Professor, Dept. of CSE, Jyothishmathi Institute of Technology and Science

📄 License
This project is for academic demonstration purposes.
For reuse or adaptation, please contact the authors.

🔗 References
See the full project report for detailed literature review, architecture, testing, and results.
