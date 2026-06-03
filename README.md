# 📡 ModuTEC – Modular Embedded Modulation Analysis Platform

Real-time generation, modulation, demodulation, visualization, and evaluation of analog and digital communication techniques on low-cost embedded hardware.

---

# 🚀 Overview

**ModuTEC** is a modular educational and experimental platform designed to study communication systems through real-time signal processing.

The system combines a **Raspberry Pi Pico (RP2040)** running embedded firmware with a desktop monitoring application developed in Python. Signal processing techniques can be dynamically configured, executed on the embedded device, and visualized in real time on the PC.

Unlike traditional simulators, ModuTEC executes the modulation and demodulation algorithms directly on embedded hardware, allowing students and researchers to evaluate performance under realistic processing and resource constraints.

---

# 📥 Download

The latest standalone Windows executable can be downloaded from the project's Releases page:

[Download the lastest version of ModuTEC here!](https://github.com/MAU143429/ModuTEC/releases/tag/v1.0.0)

---

# 🎯 Main Features

* Real-time signal generation and processing
* Support for analog and digital modulation techniques
* Embedded execution on Raspberry Pi Pico (RP2040)
* Real-time visualization of:

  * Original signal
  * Modulated signal
  * Demodulated signal
* USB Serial communication using a structured binary protocol
* Signal quality evaluation through quantitative metrics
* Dynamic technique configuration through a dedicated Configuration Tool
* Modular architecture for adding new techniques without modifying the core system

---

# 🏗️ System Architecture

## Embedded Layer

The embedded firmware executes directly on the Raspberry Pi Pico and is responsible for:

* Signal generation
* Modulation
* Demodulation
* Parameter acquisition
* Data packet generation
* USB Serial communication

The firmware processes signals in blocks to maintain real-time performance while operating within the memory and processing limitations of the RP2040.

---

## Desktop Layer

The desktop application provides:

* Device communication management
* Real-time signal visualization
* Performance metric calculation
* Technique configuration
* Firmware deployment utilities
* Signal monitoring and analysis

The graphical interface is implemented using PyQt and PyQtGraph to achieve high refresh rates during visualization.

---

# 🔧 Supported Techniques

Current implementations include:

## Analog Techniques

* AM (Amplitude Modulation)

## Digital Techniques

* ASK / OOK (Amplitude Shift Keying / On-Off Keying)

The platform architecture allows additional techniques to be integrated by registering new modules that comply with the ModuTEC interface requirements.

---

# 📊 Performance Metrics

ModuTEC evaluates the quality of the communication process using metrics such as:

* NCC (Normalized Cross-Correlation)
* NRMSE (Normalized Root Mean Square Error)
* **NCC Standard Deviation** – Evaluates the stability and consistency of the correlation over time.

These metrics enable quantitative comparison between the original and demodulated signals.

---

# 🧪 Educational Purpose

ModuTEC was developed as an academic platform to support learning, experimentation, and validation of communication system concepts in embedded environments.

The project focuses on demonstrating practical implementations of modulation and demodulation techniques while providing a reusable framework for future extensions.

---

# 👨‍💻 Author

**Mauricio Antonio Calderón Chavarría**

Computer Engineering

Tecnológico de Costa Rica

Final Graduation Project (TFG)
