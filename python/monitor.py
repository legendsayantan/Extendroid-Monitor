import socket
import io
from PIL import Image, ImageTk
import threading
import tkinter as tk

UDP_IP = str(input("Enter the ip: "))
UDP_PORT = int(input("Enter the port number: "))
MESSAGE = 0

class ExtendroidMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Extendroid Monitor")

        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.sendto(bytes([MESSAGE]), (UDP_IP, UDP_PORT))

        # Start the thread to receive images
        self.receive_thread = threading.Thread(target=self.receive_image)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.img_item = None

    def receive_image(self):
        while True:
            data, addr = self.sock.recvfrom(65507)
            image_stream = io.BytesIO(data)
            try:
                image = Image.open(image_stream)

                self.original_img = image
                self.update_image()
            except Exception as e:
                print(f"Error processing image: {e}")

    def update_image(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        img_width, img_height = self.original_img.size

        scale = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        resized_image = self.original_img.resize((new_width, new_height))
        self.img = ImageTk.PhotoImage(resized_image)

        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2

        if self.img_item is None:
            self.img_item = self.canvas.create_image(x, y, anchor=tk.NW, image=self.img)
        else:
            self.canvas.itemconfig(self.img_item, image=self.img)
            self.canvas.coords(self.img_item, x, y)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExtendroidMonitor(root)
    root.mainloop()
