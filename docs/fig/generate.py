import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Parámetros de la señal
# -----------------------------
fs = 5000
t = np.arange(0, 1, 1/fs)

f1 = 50
f2 = 120

signal = np.sin(2*np.pi*f1*t) + 0.5*np.sin(2*np.pi*f2*t)

# -----------------------------
# FFT
# -----------------------------
N = len(signal)
fft_vals = np.fft.fft(signal)
fft_vals = np.abs(fft_vals) / N
freqs = np.fft.fftfreq(N, 1/fs)

mask = freqs >= 0
freqs = freqs[mask]
fft_vals = fft_vals[mask]

# -----------------------------
# Gráficas (LADO A LADO)
# -----------------------------
plt.figure(figsize=(12, 4))  # más ancho que alto

# 🔹 Tiempo (izquierda)
plt.subplot(1, 2, 1)

t_zoom = t[:1000]
signal_zoom = signal[:1000]

plt.plot(t_zoom, signal_zoom, linewidth=1)
plt.xlabel("Tiempo (s)")
plt.ylabel("Amplitud")
plt.title("Señal compuesta en el dominio del tiempo (f1 = 50 Hz, f2 = 120 Hz)")
plt.grid(True)

# 🔹 Frecuencia (derecha)
plt.subplot(1, 2, 2)

freq_limit = 200
mask_freq = freqs <= freq_limit

plt.plot(freqs[mask_freq], fft_vals[mask_freq], linewidth=1)
plt.xlabel("Frecuencia (Hz)")
plt.ylabel("Magnitud")
plt.title("Espectro de magnitud de la señal compuesta")
plt.grid(True)

# Anotaciones
plt.text(50, 0.5, "50 Hz", ha='center')
plt.text(120, 0.25, "120 Hz", ha='center')

plt.tight_layout()

# Guardar
plt.savefig("tiempo_frecuencia_lado_a_lado.png", dpi=300)

plt.show()