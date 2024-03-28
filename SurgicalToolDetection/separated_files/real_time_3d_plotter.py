import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from queue import Queue
import threading

class RealTime3DPlotter:
    def __init__(self, point_3d_queue):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=tk.Toplevel())
        self.canvas.get_tk_widget().pack()
        self.point_3d_queue = point_3d_queue

    def update_3d_plot(self, point_3d):
        self.ax.cla()
        if point_3d:
            self.ax.scatter(point_3d[0], point_3d[1], point_3d[2], c='b', marker='o')
        self.canvas.draw()

    def draw_3d_plot(self, initial_points):
        for point in initial_points:
            self.update_3d_plot(point)

        self.ax.set_xlabel('X-axis')
        self.ax.set_ylabel('Y-axis')
        self.ax.set_zlabel('Z-axis')

    def plotting_thread(self):
        while True:
            try:
                queue_size = self.point_3d_queue.qsize()
                
                if queue_size <= 0:
                    self.update_3d_plot(None)
                else :
                    point_3d = self.point_3d_queue.get(timeout=10)
                    print(f"Received point from queue: {point_3d}")

                    # Update the 3D plot with the received point
                    self.update_3d_plot(point_3d)
            except Exception as e:
                print(f"Error in plotting thread: {e}")

# # Example usage
# point_3d_queue = Queue()
# plotter = RealTime3DPlotter(point_3d_queue)
# plotting_thread = threading.Thread(target=plotter.plotting_thread, daemon=True)
# plotting_thread.start()

# # Simulate adding points to the queue
# point_3d_queue.put([1, 2, 3])
# point_3d_queue.put([10, 1, 1])
# point_3d_queue.put([1, 10, 1])
# point_3d_queue.put([1, 1, 10])
# point_3d_queue.put([10, 10, 10])
# point_3d_queue.put([0, 0, 0])

# # Keep the program running
# tk.mainloop()
