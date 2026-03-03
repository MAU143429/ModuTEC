# 📡 ModuTEC – Embedded Signal Modulation & Demodulation

Real-time AM and ASK/OOK modulation/demodulation on low-cost embedded hardware.

---

## 🚀 Overview

**ModuTEC** is an embedded systems project focused on implementing real-time signal modulation and demodulation techniques — specifically **AM** and **ASK/OOK** — on resource-constrained hardware such as the Raspberry Pi Pico.

The project adapts signal processing algorithms originally developed in a simulation environment and deploys them into a microcontroller, enabling real-time signal generation, processing, and transmission for external visualization and performance evaluation.

---

## 🎯 Project Goals

- 🔹 Implement **analog (AM)** and **digital (ASK/OOK)** modulation techniques in an embedded system  
- 🔹 Execute demodulation directly on the microcontroller  
- 🔹 Optimize processing under **limited CPU and memory resources**  
- 🔹 Stream structured signal blocks via **USB Serial** to a PC  
- 🔹 Visualize and evaluate performance in real time  

---

## 🏗️ System Architecture

### 🔌 Embedded Side
- Microcontroller (Raspberry Pi Pico)
- Real-time signal generation
- AM / ASK modulation
- Coherent and envelope demodulation
- Optimized data buffering
- Structured serial communication protocol

### 🖥️ PC Side
- Serial data reception
- Signal visualization
- Performance metrics evaluation
- Comparative signal analysis

---

## ⚙️ Technologies & Tools

- 🐍 MicroPython / C (firmware)
- 🧮 NumPy / SciPy (signal analysis)
- 🖼️ PyQt (GUI & visualization)
- 🔗 USB Serial Communication
- 📊 Correlation & performance metrics

---

## 📈 Performance Evaluation

The system evaluates:

- 📉 Signal stability
- 🔄 Correlation between original and demodulated signals
- ⏱️ Processing latency
- 🧠 CPU and memory usage
- 📶 Signal integrity during transmission

---

## ⚠️ Limitations

- Limited to **AM and ASK/OOK**
- Designed for academic validation
- Visualization handled externally (no local GUI on MCU)
- Digital internal signal generation (no external analog sensor input at this stage)

---

## 👨‍💻 Author

**Mauricio Antonio Calderón Chavarría**<br>
Computer Engineering – Final Graduation Project<br>
Instituto Tecnológico de Costa Rica  

---
