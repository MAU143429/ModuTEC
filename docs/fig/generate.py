import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Parámetros de la señal
# -----------------------------
f = 2
t_cont = np.linspace(0, 2, 1000)

signal_cont = np.sin(2 * np.pi * f * t_cont)

# -----------------------------
# Muestreo
# -----------------------------
fs = 10
Ts = 1 / fs

t_samples = np.arange(0, 2, Ts)
signal_samples = np.sin(2 * np.pi * f * t_samples)

# -----------------------------
# Gráfica
# -----------------------------
plt.figure(figsize=(10, 5))

plt.plot(t_cont, signal_cont, label="Señal continua")
plt.scatter(t_samples, signal_samples, zorder=3, label="Muestras")

for ts in t_samples:
    plt.axvline(x=ts, linestyle="--", linewidth=0.8)

plt.title("Muestreo de una señal continua")
plt.xlabel("Tiempo (s)")
plt.ylabel("Amplitud")
plt.grid(True, linestyle=":", linewidth=0.5)

# 🔥 LEYENDA DENTRO DEL PLOT (ESQUINA SUPERIOR DERECHA)
plt.legend(loc="upper right")

plt.savefig("muestreo.png", dpi=300, bbox_inches="tight")
plt.show()