```markdown
# 🌐 Website Monitoring Dashboard

A real-time **website monitoring and analysis tool** with a **graphical dashboard** for visualizing, logging, and reporting network activity.  
It captures DNS traffic, extracts website information, checks safety with Google Safe Browsing, and generates professional reports.

---

## 🚀 Features

- 🔍 **Real-time DNS Monitoring** – tracks domains visited on your system using Scapy.
- 🌍 **Domain Insights** – resolves:
  - IP Address
  - Organization (WHOIS lookup)
  - Safety Status (Google Safe Browsing API)
  - Timestamps (First Seen & Last Seen)
- 📊 **Interactive Dashboard** – displays domains in a searchable Treeview with clickable links.
- 📈 **Bar Chart Visualization** – top visited websites shown dynamically with filtering support.
- 📄 **Export Reports**:
  - Save results as **CSV**
  - Export to **Excel**
  - Generate formatted **PDF reports**
- 📝 **Log Management** – auto-logs results to `.csv` and `.log` files.
- 🎯 **Search & Filter** – live filtering of domains with optional manual search.
- 🔗 **Clickable Domains** – open domains directly from the dashboard with a double-click.
- 🛡 **Security Insights** – integrates Google Safe Browsing API to flag malicious domains.

---

## 📂 Project Structure
```

Website-Monitoring-Dashboard/
│── web_monitor.py # Main project file
│── web_monitor_log.csv # Auto-generated CSV logs
│── web_monitor.log # Auto-generated log file
│── requirements.txt # Dependencies
│── README.md # Project documentation
│── assets/ # Dashboard & report screenshots

````

---

## ⚡ Quick Start (Copy & Paste)

### 🐧 Linux / macOS
```bash
git clone https://github.com/Osvic1/Website-Monitoring-Dashboard..git
cd Website-Monitoring-Dashboard.
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your_api_key_here" > .env
python web_monitor.py
````

### 🪟 Windows (PowerShell)

```powershell
git clone https://github.com/Osvic1/Website-Monitoring-Dashboard..git
cd Website-Monitoring-Dashboard.
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
echo GOOGLE_API_KEY=your_api_key_here > .env
python web_monitor.py
```

### 🛡 Kali Linux (Debian-based)

```bash
git clone https://github.com/Osvic1/Website-Monitoring-Dashboard..git
cd Website-Monitoring-Dashboard.
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --break-system-packages
echo "GOOGLE_API_KEY=your_api_key_here" > .env
python web_monitor.py
```

---

## 🐳 Run with Docker (No Python Needed)

### 1. Build the Docker image

```bash
git clone https://github.com/Osvic1/Website-Monitoring-Dashboard..git
cd Website-Monitoring-Dashboard.
docker build -t web-monitor .
```

### 2. Run the container

```bash
docker run -it --rm \
  -e GOOGLE_API_KEY=your_api_key_here \
  -v $(pwd):/app \
  web-monitor
```

- `-e GOOGLE_API_KEY=your_api_key_here` → sets your API key inside the container
- `-v $(pwd):/app` → mounts your current project folder for logs/reports

### 3. GUI Access (Tkinter inside Docker)

If you want the Tkinter GUI while running inside Docker:

#### Linux

```bash
xhost +local:docker
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e GOOGLE_API_KEY=your_api_key_here \
  -v $(pwd):/app \
  web-monitor
```

#### Windows/macOS

- Install **XQuartz (macOS)** or **VcXsrv (Windows)**.
- Run Docker with the same command, but ensure your X11 server is running.

---

## ▶ Usage

Run the project with:

```bash
python web_monitor.py
```

- The dashboard will launch automatically.
- Use the **search bar** to filter domains.
- The **bar chart** updates dynamically with results.
- Double-click on any domain to open it in your browser.
- Export reports as **CSV, Excel, or PDF**.

---

## 📊 Example Dashboard

![Dashboard Screenshot](assets/web-monitor-live-report.png)

---

## 📑 Requirements

Dependencies are listed in **requirements.txt**:

- scapy
- tldextract
- python-whois
- requests
- pandas
- matplotlib
- reportlab
- tkinter (standard with Python)
- python-dotenv

---

## 💡 Future Improvements

- Add email/SMS alerts for suspicious domains.
- Support for multiple users and network-wide monitoring.
- Deploy as a web app (Flask/Django + React).
- Add database support (SQLite/PostgreSQL).

---

## 👤 Author

**Timothy Victor Osas**

- 📧 Email: [Timothyv952@gmail.com](mailto:Timothyv952@gmail.com)
- 💼 LinkedIn: [https://www.linkedin.com/in/timothy-victor-a61421223/](https://www.linkedin.com/in/timothy-victor-a61421223/)
- 🐙 GitHub: [https://github.com/Osvic1](https://github.com/Osvic1)

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---

### 📊 Example Reports

|                          Overview                           |                  Live Monitoring                   |                     PDF Report                      |
| :---------------------------------------------------------: | :------------------------------------------------: | :-------------------------------------------------: |
| ![Dashboard Overview](assets/website-monitor-dashboard.png) | ![Live Report](assets/Web-monitor-live-report.png) | ![Printed PDF](assets/dashboard-printed-report.png) |

```

```

Perfect 👍 I’ll add a **new section in your README.md** that:

1. Explains **what the Google Safe Browsing API does** in your project.
2. Shows a **step-by-step guide** on how users can get their own API key.
3. Explains **why it’s needed** and how to keep it secure.

Here’s the updated section you can paste into your README.md:

---

````markdown
---

## 🔑 Google Safe Browsing API Key

This project integrates with **Google Safe Browsing** to check if a domain is **safe or malicious**.  
The API is used to detect:

- ⚠️ Phishing & deceptive websites  
- ⚠️ Malware-infected domains  
- ⚠️ Sites distributing harmful or unwanted software  

Whenever your system visits a domain, the dashboard queries Google’s Safe Browsing API and flags it as:

- ✅ **Safe** – no issues found  
- ❌ **Unsafe** – flagged by Google as phishing, malware, or malicious  

---

### 🛠 How to Get a Google Safe Browsing API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with your Google account.
3. Create a **new project** (or use an existing one).
4. Enable the **Safe Browsing API**:
   - Go to **APIs & Services > Library**.
   - Search for **Safe Browsing API**.
   - Click **Enable**.
5. Create **API credentials**:
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > API Key**.
   - Copy the generated key.

---

### 🔒 Storing the API Key Securely

Do **not** paste your API key directly in the code.  
Instead, create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_api_key_here
```
````

The program will automatically load this key when running.

---

### 📌 Why It’s Needed

Without this key:

- The dashboard cannot check domains against Google’s security database.
- Malicious websites will **not be flagged**.

With the key:

- Every captured domain is verified against Google’s live database.
- You get **real-time alerts** about unsafe websites directly in your dashboard.

---

```

```
