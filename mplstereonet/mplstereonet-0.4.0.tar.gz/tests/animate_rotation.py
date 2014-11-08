import matplotlib.pyplot as plt
import mplstereonet

plt.ion()
fig, ax = mplstereonet.subplots()
ax.grid(True)
for i in range(10, 360, 10):
    ax.set_rotation(i)
    fig.canvas.draw()


