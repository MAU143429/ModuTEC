import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Parámetros
# -----------------------------
bits = np.array([1, 0, 1, 1, 0, 0, 1])
Tb = 0.1
fc = 50
fs = 5000

samples_per_bit = int(Tb * fs)

# Tiempo
t = np.arange(0, len(bits)*Tb, 1/fs)

# -----------------------------
# Señal binaria (expandida)
# -----------------------------
binary_signal = np.repeat(bits, samples_per_bit)
binary_signal = binary_signal[:len(t)]

# Escalar para que quede arriba (visual)
binary_visual = binary_signal * 1.5

# -----------------------------
# Portadora y OOK
# -----------------------------
carrier = np.cos(2 * np.pi * fc * t)
ook_signal = binary_signal * carrier

# -----------------------------
# Gráfica única
# -----------------------------
plt.figure(figsize=(12, 5))

# Señal OOK
plt.plot(t, ook_signal, color='black', linewidth=1.2, label='Señal OOK')

# Señal binaria (arriba)
plt.step(t, binary_visual, where='post', color='blue', linewidth=2, label='Señal binaria')

# -----------------------------
# Regiones de bits (colores)
# -----------------------------
for i, bit in enumerate(bits):
    if bit == 1:
        plt.axvspan(i*Tb, (i+1)*Tb, color='green', alpha=0.1)
    else:
        plt.axvspan(i*Tb, (i+1)*Tb, color='red', alpha=0.05)

# -----------------------------
# Etiquetas de bits
# -----------------------------
for i, bit in enumerate(bits):
    plt.text(i*Tb + Tb/2, 1.7, str(bit), ha='center', fontsize=10)

# -----------------------------
# Ejes
# -----------------------------
plt.axhline(0, color='black', linewidth=1)
plt.axvline(0, color='black', linewidth=1)

# -----------------------------
# Estética
# -----------------------------
plt.title('Modulación ASK tipo OOK en el dominio del tiempo')
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud / Nivel lógico')
plt.ylim(-1.5, 2)

plt.grid(True, linestyle='--', alpha=0.4)

# Leyenda
plt.legend(loc='upper right')

# -----------------------------
# Guardar
# -----------------------------
plt.tight_layout()
plt.savefig('ook_unificado.png', dpi=300)
plt.show()