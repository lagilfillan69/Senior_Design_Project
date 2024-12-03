import sys
import tkinter
import tkinter.messagebox
from tkintermapview import TkinterMapView


class App(tkinter.Tk):

    APP_NAME = "WALLE-Control"
    WIDTH = 800
    HEIGHT = 750

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Return>", self.search)

        if sys.platform == "darwin":
            self.bind("<Command-q>", self.on_closing)
            self.bind("<Command-w>", self.on_closing)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Title Label
        title_label = tkinter.Label(, text="Wall-e Control", font=("Arial", 28, "bold"), fg="white", bg="#2c3e50")
        title_label.pack(pady=10)

        control_frame = Frame(self)
        control_frame.pack(pady=10)

        message_variable = tk.StringVar()
        input_buffer = tk.StringVar()

        self.start_button = tkinter.Button(control_frame, text="Start", style="TButton",
                                                command=lambda: start())
        self.start_button.grid(row=0, column=0, padx=20, pady=10, sticky="nsew", ipadx=20)

        self.stop_button = tkinter.Button(control_frame, text="Stop", style="TButton",
                                             command=lambda: asyncio.create_task(BLE.write("STOP\t")))
        self.stop_button.grid(row=0, column=2, padx=20, pady=10, sticky="nsew", ipadx=20)

        self.pause_button = tkinter.Button(control_frame, text="Pause", style="TButton",
                                              command=lambda: asyncio.create_task(BLE.write("PAUS\t")))
        self.pause_button.grid(row=0, column=1, padx=20, pady=10, sticky="nsew", ipadx=20)

        self.map_widget = TkinterMapView(width=self.WIDTH, height=600, corner_radius=0)
        self.map_widget.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.marker_list_box = tkinter.Listbox(self, height=8)
        self.marker_list_box.grid(row=2, column=0, columnspan=1, sticky="ew", padx=10, pady=10)

        self.listbox_button_frame = tkinter.Frame(master=self)
        self.listbox_button_frame.grid(row=2, column=1, sticky="nsew", columnspan=2)

        self.listbox_button_frame.grid_columnconfigure(0, weight=1)

        self.save_marker_button = tkinter.Button(master=self.listbox_button_frame, width=20, text="save current marker",
                                                 command=self.save_marker)
        self.save_marker_button.grid(row=0, column=0, pady=10, padx=10)

        self.clear_marker_button = tkinter.Button(master=self.listbox_button_frame, width=20, text="clear marker list",
                                                  command=self.clear_marker_list)
        self.clear_marker_button.grid(row=1, column=0, pady=10, padx=10)

        self.connect_marker_button = tkinter.Button(master=self.listbox_button_frame, width=20, text="connect marker with path",
                                                    command=self.connect_marker)
        self.connect_marker_button.grid(row=2, column=0, pady=10, padx=10)

        self.map_widget.set_address("NYC")

        self.marker_list = []
        self.marker_path = None

        self.search_marker = None
        self.search_in_progress = False

    def send_start(self):
        print("Start")


    def save_marker(self):
        if self.search_marker is not None:
            self.marker_list_box.insert(tkinter.END, f" {len(self.marker_list)}. {self.search_marker.text} ")
            self.marker_list_box.see(tkinter.END)
            self.marker_list.append(self.search_marker)

    def clear_marker_list(self):
        for marker in self.marker_list:
            self.map_widget.delete(marker)

        self.marker_list_box.delete(0, tkinter.END)
        self.marker_list.clear()
        self.connect_marker()

    def connect_marker(self):
        print(self.marker_list)
        position_list = []

        for marker in self.marker_list:
            position_list.append(marker.position)

        if self.marker_path is not None:
            self.map_widget.delete(self.marker_path)

        if len(position_list) > 0:
            self.marker_path = self.map_widget.set_path(position_list)

    def clear(self):
        self.search_bar.delete(0, last=tkinter.END)
        self.map_widget.delete(self.search_marker)

    def on_closing(self, event=0):
        self.destroy()
        exit()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()