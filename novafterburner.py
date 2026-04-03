import customtkinter as ctk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
from collections import deque

class AfterburnerPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NOVA AFTERBURNER v2.0 - Pro Monitor")
        self.geometry("1200x800")
        ctk.set_appearance_mode("Dark")
        
        # Veri Depoları
        self.cpu_history = deque([0]*30, maxlen=30)
        self.ram_history = deque([0]*30, maxlen=30)
        self.net_history = deque([0]*30, maxlen=30)
        self.time_axis = list(range(30))

        # Network Başlangıç Verisi
        self.last_net_io = psutil.net_io_counters()

        # UI Düzeni
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SOL PANEL (Sidebar) ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0a0a0a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="NOVA ENGINE", font=("Orbitron", 24, "bold"), text_color="#ff3333")
        self.logo.pack(pady=40)

        # Quick Stats in Sidebar
        self.os_label = ctk.CTkLabel(self.sidebar, text=f"Core: {psutil.cpu_count()} Threads", font=("Arial", 12))
        self.os_label.pack(pady=5)

        # --- ANA PANEL ---
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#111111", corner_radius=0)
        self.scroll.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.scroll.grid_columnconfigure((0, 1), weight=1)

        # 📊 GRAFİK BÖLÜMÜ (MSI Stili)
        self.graph_frame = ctk.CTkFrame(self.scroll, fg_color="#181818", corner_radius=15)
        self.graph_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        
        self.fig, self.ax = plt.subplots(figsize=(10, 3), facecolor='#181818')
        self.ax.set_facecolor('#181818')
        self.cpu_line, = self.ax.plot(self.time_axis, self.cpu_history, color='#ff3333', label="CPU %", linewidth=2)
        self.ram_line, = self.ax.plot(self.time_axis, self.ram_history, color='#33ff33', label="RAM %", linewidth=2)
        self.ax.legend(loc="upper left", facecolor='#181818', labelcolor='white', frameon=False)
        self.ax.axis('off')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # ⚡ ÖLÇERLER (Gauges)
        self.card_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.card_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.cpu_val = self.create_metric(self.card_frame, "PROCESSOR LOAD", "0%", 0, "#ff3333")
        self.ram_val = self.create_metric(self.card_frame, "MEMORY USAGE", "0%", 1, "#33ff33")
        self.net_val = self.create_metric(self.card_frame, "NETWORK DOWN", "0 KB/s", 2, "#3399ff")

        # 📑 ALT DETAYLAR (Processes)
        self.proc_list = ctk.CTkTextbox(self.scroll, height=200, fg_color="#0a0a0a", font=("Consolas", 12))
        self.proc_list.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        # Thread Başlat
        threading.Thread(target=self.monitor_engine, daemon=True).start()

    def create_metric(self, master, title, val, col, color):
        frame = ctk.CTkFrame(master, fg_color="#181818", corner_radius=12, border_width=1, border_color="#333")
        frame.grid(row=0, column=col, padx=15, pady=10, sticky="nsew")
        
        l1 = ctk.CTkLabel(frame, text=title, font=("Arial", 11, "bold"), text_color="gray")
        l1.pack(pady=(15, 0))
        
        l2 = ctk.CTkLabel(frame, text=val, font=("Impact", 42), text_color=color)
        l2.pack(pady=15)
        return l2

    def monitor_engine(self):
        while True:
            # CPU & RAM
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            # Network Calculation
            current_net = psutil.net_io_counters()
            download_speed = (current_net.bytes_recv - self.last_net_io.bytes_recv) / 1024 # KB/s
            self.last_net_io = current_net

            # Process List (Top 5 CPU)
            procs = sorted(psutil.process_iter(['name', 'cpu_percent']), 
                          key=lambda x: x.info['cpu_percent'], reverse=True)[:5]
            proc_text = "EN ÇOK KAYNAK TÜKETEN UYGULAMALAR:\n" + "-"*40 + "\n"
            for p in procs:
                proc_text += f"{p.info['name']:<25} | %{p.info['cpu_percent']}\n"

            # Update Lists
            self.cpu_history.append(cpu)
            self.ram_history.append(ram)

            # Update UI
            self.after(0, self.update_display, cpu, ram, download_speed, proc_text)
            time.sleep(1)

    def update_display(self, cpu, ram, net, proc_text):
        self.cpu_val.configure(text=f"%{cpu}")
        self.ram_val.configure(text=f"%{ram}")
        self.net_val.configure(text=f"{net:.1f} KB/s")
        
        self.proc_list.delete("1.0", "end")
        self.proc_list.insert("1.0", proc_text)

        # Graph Update
        self.cpu_line.set_ydata(self.cpu_history)
        self.ram_line.set_ydata(self.ram_history)
        self.canvas.draw_idle()

if __name__ == "__main__":
    app = AfterburnerPro()
    app.mainloop()