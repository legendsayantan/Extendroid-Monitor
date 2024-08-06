import socket
import io
import time as tm
from PIL import Image, ImageTk
import threading
import tkinter as tk

UDP_IP = str(input("Enter the ip: "))
UDP_PORT = int(input("Enter the port number: "))
msg_connect = 0
msg_motionevent = 1

class EventBuilder:
    def build(self,action,x,y):
        time = int(tm.time()*1000)
        if(action==0):
            self.downTime = time
        
        return '{"downTime":'+str(self.downTime)+',"eventTime":'+str(time)+',"action":'+str(action)+',"x":'+str(float(x))+',"y":'+str(float(y))+' }'

class ExtendroidMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Extendroid Monitor")

        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events to handler functions
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<ButtonRelease-1>",self.on_mouse_release)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.sendto(bytes([msg_connect]), (UDP_IP, UDP_PORT))

        # Start the thread to receive images
        self.receive_thread = threading.Thread(target=self.receive_image)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.img_item = None

        self.eventBuilder = EventBuilder()

    def on_mouse_press(self, event):
        self.handle_event(0,event)

    def on_mouse_release(self, event):
        self.handle_event(1,event)

    def on_mouse_drag(self, event):
        self.handle_event(2,event)

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

        self.imgscale = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * self.imgscale)
        new_height = int(img_height * self.imgscale)

        resized_image = self.original_img.resize((new_width, new_height))
        self.img = ImageTk.PhotoImage(resized_image)

        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2

        self.imgpos = (x,y)

        if self.img_item is None:
            self.img_item = self.canvas.create_image(x, y, anchor=tk.NW, image=self.img)
        else:
            self.canvas.itemconfig(self.img_item, image=self.img)
            self.canvas.coords(self.img_item, x, y)

    def handle_event(self,action,event):
        try:
            x = (event.x-self.imgpos[0])/self.imgscale
            y = (event.y-self.imgpos[1])/self.imgscale
            if x >= 0 and x <= self.original_img.size[0] and y >= 0 and y <= self.original_img.size[1]:
                self.sock.sendto(bytes([msg_motionevent])+bytes(self.eventBuilder.build(action,x,y),"utf-8"), (UDP_IP, UDP_PORT))
        except Exception as e:
            print(f"Error processing event: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExtendroidMonitor(root)
    root.mainloop()
