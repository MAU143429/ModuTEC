import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, freqz

# -----------------------------
# Parámetros
# -----------------------------
fs = 5000
t = np.arange(0, 0.2, 1/fs)

fm = 10      # frecuencia mensaje
fc = 100     # frecuencia portadora

# -----------------------------
# Señal mensaje
# -----------------------------
m = np.cos(2 * np.pi * fm * t)

# Señal AM (simplificada)
s = m * np.cos(2 * np.pi * fc * t)

# -----------------------------
# Demodulación coherente
# Multiplicación
# -----------------------------
r = s * np.cos(2 * np.pi * fc * t)

# -----------------------------
# Filtro pasa bajas
# -----------------------------
fcorte = 20  # frecuencia de corte (Hz)

b, a = butter(4, fcorte / (fs/2))  # filtro Butterworth
m_rec = filtfilt(b, a, r)

# -----------------------------
# Respuesta en frecuencia del filtro
# -----------------------------
w, h = freqz(b, a, worN=1024, fs=fs)

# -----------------------------
# FIGURA (2 columnas)
# -----------------------------
fig, axs = plt.subplots(1, 2, figsize=(12, 4))

# ====================================================
# SUBPLOT IZQUIERDA → DOMINIO DEL TIEMPO
# ====================================================
axs[0].plot(t, r, color='gray', linewidth=1, label='Señal tras multiplicación r(t)')
axs[0].plot(t, m_rec, color='black', linewidth=2.5, label='Señal filtrada m(t)')
axs[0].plot(t, m, 'r--', linewidth=1.5, label='Mensaje original (ref)')

axs[0].set_title('Señal antes y después del filtrado')
axs[0].set_xlabel('Tiempo (s)')
axs[0].set_ylabel('Amplitud')
axs[0].grid(True, linestyle='--', alpha=0.4)
axs[0].legend(loc='upper right')

# ====================================================
# SUBPLOT DERECHA → RESPUESTA EN FRECUENCIA
# ====================================================
axs[1].plot(w, abs(h), color='black', linewidth=2)

# Línea de corte
axs[1].axvline(fcorte, color='red', linestyle='--', label='Frecuencia de corte')

# Componentes importantes
axs[1].axvline(fm, color='green', linestyle='--', label='Mensaje (fm)')
axs[1].axvline(2*fc, color='blue', linestyle='--', label='Alta frecuencia (2fc)')

# Etiquetas visuales
axs[1].text(fm, 0.9, 'mensaje', color='green')
axs[1].text(2*fc, 0.3, '2fc', color='blue')

axs[1].set_title('Respuesta en frecuencia del filtro pasa bajas')
axs[1].set_xlabel('Frecuencia (Hz)')
axs[1].set_ylabel('|H(f)|')
axs[1].set_xlim(0, 250)
axs[1].grid(True, linestyle='--', alpha=0.4)
axs[1].legend(loc='upper right')

# -----------------------------
# Ajuste de espacios
# -----------------------------
plt.suptitle('Filtrado en demodulación coherente')
plt.subplots_adjust(wspace=0.25)
plt.tight_layout()

# Guardar
plt.savefig('demod_filtrado.png', dpi=300)
plt.show()