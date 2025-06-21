# RDMA File Transfer with iWARP and eBPF Monitoring

This project demonstrates a high-performance **file transfer application** using **RDMA over iWARP** with real-time system monitoring powered by **eBPF** and **Python Tkinter GUI**.

## 🚀 Features

* **RDMA (iWARP)** based file transfer using Soft-iWARP
* GUI built with **Tkinter** displaying:

  * Real-time CPU usage
  * Real-time throughput and packet monitoring
* **eBPF (via bpftrace)** script for live metrics during file transmission
* Backend integration with Linux terminal commands via Python

---

## 🛠️ Tech Stack

* Python 3.10+
* Tkinter
* psutil
* matplotlib
* socket
* threading
* **Soft-iWARP kernel module** (siw)
* **bpftrace** for eBPF-based tracing

---

## 🧠 Skills Acquired

* Kernel-level RDMA communication using iWARP (siw0)
* Real-time system monitoring with eBPF
* GUI & multithreaded programming in Python
* Networking, socket programming
* Linux device management and debugging

---

## ⚙️ Setup Instructions

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install -y rdma-core bpftrace python3-tk python3-pip linux-tools-$(uname -r)
sudo pip3 install matplotlib psutil
```

### 2. Setup iWARP (Soft-iWARP)

```bash
# Load the Soft-iWARP kernel module
sudo modprobe siw

# Replace <IFACE> with your Ethernet interface (e.g., enp0s8)
sudo rdma link add siw0 type siw netdev <IFACE>

# Verify setup
rdma link show
ibv_devices
```

### 3. Run RDMA Benchmarks (optional)

```bash
# Server
ib_send_bw -d siw0

# Client
ib_send_bw -d siw0 -R <SERVER_IP> -D 10
```

### 4. Install and Run bpftrace Scripts

```bash
# Save your eBPF trace script as trace_rdma_tcp.bt
sudo bpftrace trace_rdma_tcp.bt
```

> ⚠️ Ensure the script filters only metrics during the RDMA file transfer and stops afterward.

### 5. Run the GUI App

```bash
python3 rdma_gui_transfer.py
```

This will launch the file transfer application. The metrics (throughput, CPU, etc.) are displayed live during transfers.

---

## 🖥️ GUI Snapshot

* File Selection & Send/Receive Buttons
* Real-Time CPU Usage Graph
* Live Throughput Stats from eBPF

---

## 📁 Folder Structure

```
project/
├── rdma_gui_transfer.py
├── trace_rdma_tcp.bt
├── requirements.txt
└── README.md
```

---

## 📌 Notes

* Tested on **Ubuntu 24.10** running on VirtualBox with bridged adapter.
* Interface used: `enp0s8`
* eBPF tracing is limited to root-level access. Use `sudo`.
* `siw0` device may need reconfiguration on reboot.

---

## 👤 Author

**Yugal Kishore Velupula**
B.E. Information Science & Engineering, BMSIT\&M

Feel free to fork, contribute, or raise issues!

---

## 📜 License

[MIT License](LICENSE)

## 📃 Published paper links

https://ieeexplore.ieee.org/document/10969859

https://www.researchgate.net/publication/391254248_Implementing_RDMA_over_Soft-RoCE_with_Basic_eBPF_Monitoring_A_Cost-Effective_Approach_for_High-Performance_Data_Communication
