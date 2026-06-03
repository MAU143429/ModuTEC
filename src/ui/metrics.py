import numpy as np


def analog_ncc(signal_original: np.ndarray, signal_demod: np.ndarray) -> float:
    """
    Normalized Cross-Correlation para señales analógicas (AM, FM, etc).
    Usa correlación de Pearson entre la señal original y la demodulada.
    Retorna un valor entre 0.0 y 100.0 (porcentaje).
    """
    if len(signal_original) != len(signal_demod):
        return 0.0

    # Centrar señales
    a = signal_original - np.mean(signal_original)
    b = signal_demod    - np.mean(signal_demod)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a < 1e-9 or norm_b < 1e-9:
        return 0.0

    correlation = np.dot(a, b) / (norm_a * norm_b)

    # Clamp a [0, 1] y convertir a porcentaje
    correlation = float(np.clip(correlation, 0.0, 1.0))
    return round(correlation * 100.0, 1)


def digital_ncc(signal_original: np.ndarray, signal_demod: np.ndarray) -> float:
    """
    NCC para señales digitales (ASK/OOK, FSK, etc).
    Compara bits recuperados vs bits originales como porcentaje de aciertos.
    Ambas señales deben estar en formato NRZ (-1/+1).
    Retorna un valor entre 0.0 y 100.0 (porcentaje).
    """
    if len(signal_original) != len(signal_demod):
        return 0.0

    # Convertir NRZ a bits: positivo = 1, negativo = 0
    bits_orig  = (signal_original >= 0).astype(np.int8)
    bits_demod = (signal_demod    >= 0).astype(np.int8)

    matches = np.sum(bits_orig == bits_demod)
    return round((matches / len(bits_orig)) * 100.0, 1)


def ncc_color(value: float) -> str:
    """
    Retorna el color correspondiente al valor NCC.
    < 65%  → rojo
    65-70% → amarillo
    > 70%  → verde
    """
    if value >= 70.0:
        return "#2ecc71"   # verde
    elif value >= 65.0:
        return "#f39c12"   # amarillo
    else:
        return "#e74c3c"   # rojo
    
    
def nrmse(signal_original: np.ndarray,
                  signal_demod: np.ndarray,
                  max_lag: int = 20) -> float:
    """
    NRMSE con compensación de desfase y ganancia.
    Útil para comparar señal original vs demodulada cuando existe
    retardo por filtrado LPF o diferencias de amplitud.
    """

    if len(signal_original) != len(signal_demod):
        return 0.0

    x = np.asarray(signal_original, dtype=np.float32)
    y = np.asarray(signal_demod, dtype=np.float32)

    x = x - np.mean(x)
    y = y - np.mean(y)

    best_error = None

    for lag in range(-max_lag, max_lag + 1):

        if lag < 0:
            x_lag = x[-lag:]
            y_lag = y[:len(y) + lag]

        elif lag > 0:
            x_lag = x[:-lag]
            y_lag = y[lag:]

        else:
            x_lag = x
            y_lag = y

        if len(x_lag) < 5:
            continue

        denom = np.dot(y_lag, y_lag)

        if denom < 1e-9:
            continue

        gain = np.dot(x_lag, y_lag) / denom
        y_fit = gain * y_lag

        dynamic_range = np.max(x_lag) - np.min(x_lag)

        if dynamic_range < 1e-9:
            continue

        rmse = np.sqrt(np.mean((x_lag - y_fit) ** 2))
        err = rmse / dynamic_range

        if best_error is None or err < best_error:
            best_error = err

    if best_error is None:
        return 0.0

    return round(float(best_error), 4)


def ncc_std(history: list) -> float:
    """
    Desviación estándar del historial NCC.
    """

    if len(history) < 2:
        return 0.0

    return round(float(np.std(history)), 2)


def nrmse_color(value: float) -> str:

    if value < 0.10:
        return "#2ecc71"

    elif value < 0.20:
        return "#f39c12"

    else:
        return "#e74c3c"


def std_color(value: float) -> str:

    if value < 2.0:
        return "#2ecc71"

    elif value < 5.0:
        return "#f39c12"

    else:
        return "#e74c3c"
    

