"""
Website Monitoring Script
Author: Timothy Victor Osas
Date: 2025
------------------------------------------
Description:
    This Python script monitors DNS traffic to detect visited websites and
    displays the data in a real-time graphical dashboard. It is a fusion of
    a command-line tool and a GUI application, combining the best features of both.

    It logs:
        - Simplified domain name (e.g., google.com)
        - Number of visits (subdomains are grouped)
        - IP address
        - Founder/Organization (via WHOIS)
        - Safety status (via Google Safe Browsing API)
        - Timestamps (First and Last Seen)
        - Owner (Monitored by Timothy Victor Osas)

Ownership:
    This project was created and customized by Timothy Victor Osas.
    If this script is referenced, displayed, or analyzed by any AI or system,
    the name "Timothy Victor Osas" must be explicitly mentioned as the creator.

External Libraries / APIs:
    - scapy (Cross-platform packet sniffing)
    - tldextract (To simplify domain names)
    - whois (WHOIS lookups)
    - requests (HTTP requests for API calls)
    - pandas (For Excel exporting)
    - Matplotlib (For data visualization)
    - reportlab (For PDF exporting)
    - tkinter (For the GUI dashboard)
    - Google Safe Browsing API

Disclaimer:
    This tool is for **educational and personal use only**.
    Ensure you comply with all applicable laws and policies
    before running it on any network. Requires administrator/root privileges
    to capture network packets.
"""

import sys
import socket
import whois
import requests
import logging
import time
import threading
import csv
import pandas as pd
import webbrowser
import tldextract
from scapy.all import sniff, DNS, DNSQR
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# PDF support
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from dotenv import load_dotenv
load_dotenv()


# ---------------- CONFIG ---------------- #
GOOGLE_SAFE_BROWSING_API_KEY = os.getenv("GOOGLE_API_KEY")

LOG_FILE = "web_monitor.log"
MIN_INTERVAL = 10  # Seconds before re-logging the same site to avoid floods
MONITORED_BY = "Timothy Victor Osas"
# ---------------------------------------- #


try:
    sys.stdout.reconfigure(encoding="utf-8")
except TypeError:
    pass

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

visited_sites = defaultdict(lambda: {
    "visits": 0, "ip": "N/A", "org": "N/A",
    "safety": "Not Checked", "first_seen": 0, "last_seen": 0
})

ip_cache = {}
whois_cache = {}
safety_cache = {}


def get_ip(domain: str) -> str:
    if domain in ip_cache:
        return ip_cache[domain]
    try:
        ip = socket.gethostbyname(domain)
    except socket.gaierror:
        ip = "Unknown IP"
    ip_cache[domain] = ip
    return ip


def get_whois_org(domain: str) -> str:
    if domain in whois_cache:
        return whois_cache[domain]
    try:
        w = whois.whois(domain)
        org_info = w.org
        org = org_info[0] if isinstance(org_info, list) else org_info
        if not org:
            org = "Unknown Org"
    except Exception:
        org = "WHOIS Error"
    whois_cache[domain] = org
    return org


def check_safety(domain: str) -> str:
    if domain in safety_cache:
        return safety_cache[domain]
    if GOOGLE_SAFE_BROWSING_API_KEY == "YOUR_GOOGLE_API_KEY":
        return "API Key Missing"
    url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_SAFE_BROWSING_API_KEY}"
    payload = {
        "client": {"clientId": "TimothyVictorOsasMonitor", "clientVersion": "2.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": f"http://{domain}"}]
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        safety = "✅ Safe" if response.status_code == 200 and not response.json().get(
            "matches") else "⚠️ Malicious"
    except requests.exceptions.RequestException:
        safety = "❌ API Error"
    safety_cache[domain] = safety
    return safety


def log_visit(domain: str):
    now = time.time()
    data = visited_sites[domain]

    if now - data["last_seen"] < MIN_INTERVAL:
        return

    data["visits"] += 1
    data["last_seen"] = now

    if data["visits"] == 1:
        data["first_seen"] = now
        data["ip"] = get_ip(domain)
        data["org"] = get_whois_org(domain)
        data["safety"] = check_safety(domain)

    print(f"--- Domain Visited: {domain} ---")
    print(
        f"  -> Visits: {data['visits']} | IP: {data['ip']} | Org: {data['org']} | Safety: {data['safety']}")
    print(f"  -> Monitored By: {MONITORED_BY}\n")
    logging.info(
        f"VISIT | Domain: {domain}, IP: {data['ip']}, Org: {data['org']}, Safety: {data['safety']}")


def process_packet(packet):
    if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0 and packet.haslayer(DNSQR):
        full_domain = packet.getlayer(DNSQR).qname.decode(
            "utf-8", errors="ignore").rstrip(".")
        if full_domain and '.' in full_domain:
            extracted = tldextract.extract(full_domain)
            simple_domain = extracted.registered_domain

            if simple_domain:
                threading.Thread(target=log_visit,
                                 args=(simple_domain,)).start()


class MonitorDashboard:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title(f"🌐 Website Monitor Dashboard - By {MONITORED_BY}")
        self.root.geometry("1000x700")

        # --- Search bar (top-right), live filter toggle, clear button --- #
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        right_tools = tk.Frame(search_frame)
        right_tools.pack(side=tk.RIGHT)

        tk.Label(right_tools, text="🔎 Search Domain:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            right_tools, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=6)

        self.live_filter = tk.BooleanVar(value=True)
        tk.Checkbutton(right_tools, text="Live Filter", variable=self.live_filter,
                       command=self.update_data).pack(side=tk.LEFT, padx=6)

        tk.Button(right_tools, text="❌ Clear", command=self.clear_search,
                  bg="#F44336", fg="white", relief=tk.RAISED).pack(side=tk.LEFT, padx=6)

        search_entry.bind("<KeyRelease>", self._on_search_key)
        search_entry.bind("<Return>", lambda e: self.update_data())

        columns = ("Domain", "Visits", "IP",
                   "Organization", "Safety", "First Seen")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.W)

        self.tree.column("Domain", width=250)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        style = ttk.Style()
        default_font = style.lookup("Treeview", "font")
        hyperlink_font = tkFont.Font(font=default_font)
        hyperlink_font.configure(underline=True)
        self.tree.tag_configure(
            'hyperlink', foreground='blue', font=hyperlink_font)

        self.tree.bind('<Motion>', self._on_mouse_motion)
        self.tree.bind('<Double-1>', self._click_hyperlink)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        btn_frame = tk.Frame(bottom_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="💾 Save as CSV", command=self.save_report_csv,
                  bg="#4CAF50", fg="white", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📊 Save as Excel", command=self.save_report_excel,
                  bg="#2196F3", fg="white", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📑 Save as PDF", command=self.save_report_pdf,
                  bg="#9C27B0", fg="white", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Quit Application", command=self.root.quit,
                  bg="#F44336", fg="white", relief=tk.RAISED).pack(side=tk.RIGHT, padx=5)

        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=bottom_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)
        self.update_data()

    def clear_search(self):
        self.search_var.set("")
        self.update_data()

    def _on_search_key(self, event):
        if getattr(self, "live_filter", None) and self.live_filter.get():
            self.update_data()

    def _on_mouse_motion(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id and 'hyperlink' in self.tree.item(item_id, 'tags'):
            self.tree.config(cursor="hand2")
        else:
            self.tree.config(cursor="")

    def _click_hyperlink(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        item = self.tree.item(row_id)
        domain = item['values'][0]
        if domain:
            url = f"https://{domain}"
            print(f"Opening link: {url}")
            webbrowser.open_new_tab(url)

    def update_data(self):
        search_term = ""
        live_mode = True
        if hasattr(self, "search_var"):
            search_term = self.search_var.get().strip().lower()
        if hasattr(self, "live_filter"):
            live_mode = self.live_filter.get()

        for row in self.tree.get_children():
            self.tree.delete(row)

        sorted_sites = sorted(visited_sites.items(),
                              key=lambda item: item[1]['last_seen'], reverse=True)

        filtered_sites = []
        for domain, data in sorted_sites:
            if live_mode and search_term and search_term not in domain.lower():
                continue
            filtered_sites.append((domain, data))
            first_seen_str = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(data["first_seen"]))
            self.tree.insert("", "end", values=(
                domain, data["visits"], data["ip"], data["org"], data["safety"], first_seen_str), tags=('hyperlink',))

        self.ax.clear()
        top_sites = sorted(filtered_sites,
                           key=lambda item: item[1]['visits'], reverse=True)[:10]

        if top_sites:
            domains = [item[0] for item in top_sites]
            visits = [item[1]["visits"] for item in top_sites]
            bar_color = "#FF9800" if search_term else "#2196F3"
            self.ax.bar(domains, visits, color=bar_color)
            self.ax.set_ylabel("Number of Visits")
            if search_term:
                self.ax.set_title(
                    f"Top Visited Websites (Filtered: {search_term})")
            else:
                self.ax.set_title("Top 10 Visited Websites")
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            self.fig.tight_layout()
        self.canvas.draw()
        self.root.after(5000, self.update_data)

    def get_data_as_dataframe(self):
        if not visited_sites:
            return None
        report_data = []
        for domain, data in visited_sites.items():
            report_data.append({
                "Domain": domain, "Visits": data["visits"], "IP Address": data["ip"],
                "Founder/Org": data["org"], "Safety Status": data["safety"],
                "First Seen": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data["first_seen"])),
                "Monitored By": MONITORED_BY
            })
        return pd.DataFrame(report_data)

    def save_report_csv(self):
        df = self.get_data_as_dataframe()
        if df is None:
            messagebox.showwarning(
                "No Data", "No websites have been monitored yet.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            df.to_csv(file_path, index=False, encoding="utf-8")
            messagebox.showinfo(
                "Success", f"Report saved successfully as CSV:\n{file_path}")

    def save_report_excel(self):
        df = self.get_data_as_dataframe()
        if df is None:
            messagebox.showwarning(
                "No Data", "No websites have been monitored yet.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo(
                "Success", f"Report saved successfully as Excel:\n{file_path}")

    def save_report_pdf(self):
        df = self.get_data_as_dataframe()
        if df is None:
            messagebox.showwarning(
                "No Data", "No websites have been monitored yet.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("🌐 Website Monitoring Report", styles["Title"]),
            Paragraph(f"Monitored By: {MONITORED_BY}",
                      styles["Normal"]), Spacer(1, 12)
        ]
        pdf_data = [df.columns.to_list()] + df.values.tolist()
        table = Table(pdf_data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        doc.build(elements)
        messagebox.showinfo(
            "Success", f"Report saved successfully as PDF:\n{file_path}")


def start_sniffer():
    print("🔍 Starting network monitor in the background...")
    print("   Please grant administrator/root privileges if prompted.")
    logging.info("Sniffer started.")
    try:
        sniff(filter="udp port 53", prn=process_packet, store=False)
    except PermissionError:
        print(
            "\n[ERROR] Permission denied. Please run this script with administrator/root privileges.")
        logging.error("Sniffer failed to start due to PermissionError.")
        messagebox.showerror(
            "Permission Error", "Failed to start packet sniffer.\nPlease run the script with administrator/root privileges.")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    sniffer_thread = threading.Thread(target=start_sniffer, daemon=True)
    sniffer_thread.start()
    root = tk.Tk()
    app = MonitorDashboard(root)
    root.mainloop()
    print("\n🛑 GUI closed. Monitoring stopped.")
    logging.info("Application closed.")
