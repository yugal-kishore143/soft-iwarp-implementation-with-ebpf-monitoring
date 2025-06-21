import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import psutil
import os
import csv
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BUFFER_SIZE = 1048576  # 1 MB optimized buffer size

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RDMA File Transfer with Real-Time Metrics")
        self.root.geometry("1000x700")

        self.filename = ""
        self.server_thread = None
        self.client_thread = None
        self.transfer_data = []
        self.metrics_active = False

        self.setup_ui()

    def setup_ui(self):
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10)

        self.lbl_file = tk.Label(file_frame, text="Selected File: None", width=80, anchor='w')
        self.lbl_file.pack(side=tk.LEFT, padx=5)

        btn_browse = tk.Button(file_frame, text="Browse", command=self.browse_file)
        btn_browse.pack(side=tk.LEFT, padx=5)

        ip_port_frame = tk.Frame(self.root)
        ip_port_frame.pack(pady=5)

        tk.Label(ip_port_frame, text="IP Address:").pack(side=tk.LEFT, padx=5)
        self.entry_ip = tk.Entry(ip_port_frame, width=15)
        self.entry_ip.pack(side=tk.LEFT, padx=5)
        self.entry_ip.insert(0, "192.168.56.1")

        tk.Label(ip_port_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.entry_port = tk.Entry(ip_port_frame, width=5)
        self.entry_port.pack(side=tk.LEFT, padx=5)
        self.entry_port.insert(0, "50000")

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_send = tk.Button(btn_frame, text="Send", command=self.start_client_thread, width=15)
        self.btn_send.pack(side=tk.LEFT, padx=5)

        self.btn_receive = tk.Button(btn_frame, text="Receive", command=self.start_server_thread, width=15)
        self.btn_receive.pack(side=tk.LEFT, padx=5)

        self.btn_clear = tk.Button(btn_frame, text="Clear Data", command=self.clear_data, width=15)
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        self.btn_export = tk.Button(btn_frame, text="Export CSV", command=self.export_csv, width=15)
        self.btn_export.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(self.root, orient='horizontal', mode='determinate', length=700)
        self.progress.pack(pady=10)

        self.graph_frame = tk.Frame(self.root)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.canvas_graph = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas_graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax.set_title("Throughput & CPU Usage Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Throughput (KB/s) / CPU Usage (%)")

        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        self.table = ttk.Treeview(self.table_frame, columns=("Time", "Bytes Transferred", "Throughput", "CPU Usage"), show="headings")
        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", stretch=True)
        self.table.pack(fill=tk.BOTH, expand=True)

        self.text_widget = tk.Text(self.root, height=10, bg='black', fg='lime', wrap='word')
        self.text_widget.pack(fill=tk.BOTH, expand=True)

    def browse_file(self):
        self.filename = filedialog.askopenfilename()
        if self.filename:
            self.lbl_file.config(text=f"Selected File: {self.filename}")

    def start_server_thread(self):
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

    def start_client_thread(self):
        self.client_thread = threading.Thread(target=self.run_client, daemon=True)
        self.client_thread.start()

    def run_server(self):
        ip = self.entry_ip.get()
        port = self.entry_port.get()
        output_file = "received_file"
        self.metrics_active = True
        try:
            self.print_to_log(f"Starting receiver on port {port}...")
            start_time = time.time()
            proc = subprocess.Popen(["nc", "-l", "-p", port], stdout=open(output_file, "wb"))
            proc.wait()
            self.metrics_active = False
            elapsed = time.time() - start_time
            size = os.path.getsize(output_file)
            throughput = (size / 1024) / (elapsed + 0.001)
            timestamp = time.strftime("%H:%M:%S")
            cpu_usage = psutil.cpu_percent()
            self.transfer_data.append((timestamp, size, round(throughput, 2), cpu_usage))
            self.table.insert("", "end", values=(timestamp, size, f"{throughput:.2f}", f"{cpu_usage:.2f}"))
            self.update_graph()
            self.progress.config(value=100)
            self.print_to_log("File received successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_client(self):
        if not self.filename:
            messagebox.showerror("Error", "Please select a file to send.")
            return
        ip = self.entry_ip.get()
        port = self.entry_port.get()
        filesize = os.path.getsize(self.filename)
        self.metrics_active = True
        try:
            self.print_to_log(f"Sending file to {ip}:{port}...")
            start_time = time.time()
            proc = subprocess.Popen(["nc", "-q", "1", ip, port], stdin=open(self.filename, "rb"))
            proc.wait()
            self.metrics_active = False
            elapsed = time.time() - start_time
            throughput = (filesize / 1024) / (elapsed + 0.001)
            timestamp = time.strftime("%H:%M:%S")
            cpu_usage = psutil.cpu_percent()
            self.transfer_data.append((timestamp, filesize, round(throughput, 2), cpu_usage))
            self.table.insert("", "end", values=(timestamp, filesize, f"{throughput:.2f}", f"{cpu_usage:.2f}"))
            self.update_graph()
            self.progress.config(value=100)
            self.print_to_log("File sent successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_data(self):
        self.transfer_data = []
        for row in self.table.get_children():
            self.table.delete(row)
        self.ax.clear()
        self.ax.set_title("Throughput & CPU Usage Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Throughput (KB/s) / CPU Usage (%)")
        self.canvas_graph.draw()
        self.progress['value'] = 0

    def update_graph(self):
        if not self.transfer_data or not self.metrics_active:
            return
        times = [data[0] for data in self.transfer_data]
        throughput = [data[2] for data in self.transfer_data]
        cpu = [data[3] for data in self.transfer_data]

        self.ax.clear()
        self.ax.plot(times, throughput, label='Throughput (KB/s)', color='blue', marker='o')
        self.ax.plot(times, cpu, label='CPU Usage (%)', color='red', marker='x')
        self.ax.set_xticklabels(times, rotation=45, ha='right')
        self.ax.set_title("Throughput & CPU Usage Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Throughput (KB/s) / CPU Usage (%)")
        self.ax.legend(loc='upper left')
        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas_graph.draw()

    def export_csv(self):
        if not self.transfer_data:
            messagebox.showinfo("No Data", "No transfer data to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file:
            return
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Bytes Transferred", "Throughput (KB/s)", "CPU (%)"])
            writer.writerows(self.transfer_data)
        messagebox.showinfo("Exported", f"Data exported to {file}")

    def print_to_log(self, message):
        print(message)
        self.text_widget.insert(tk.END, f"{message}\n")
        self.text_widget.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop()
