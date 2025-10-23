# 🎓 University Chatbot Demo

This is a **demo project** of a university chatbot application built with Python.

> ⚠️ **Note:** This is a prototype and **not a finished product**.

---

## 🧩 Features

* Interactive chatbot interface
* Uses **Ollama** models: `llama3` and `qwen`
* Simple web interface served via Flask
* Designed for educational and testing purposes

---

## 🛠️ Requirements

* **Python 3.10+**
* **Ollama** installed and configured
* Internet connection for model downloads

---

## 📦 Installation Guide

### 1. Install Python

#### **Windows**

1. Download Python from the [official website](https://www.python.org/downloads/).
2. During installation, **check the box** that says “Add Python to PATH”.
3. Verify installation by opening **Command Prompt** and running:

   ```bash
   python --version
   ```

#### **Linux (Debian/Ubuntu-based)**

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
python3 --version
```

---

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

---

### 3. Create and Activate a Virtual Environment

#### **Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

#### **Linux/macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install Required Libraries

Make sure you are inside your virtual environment, then run:

```bash
pip install -r requirements.txt
```

---

## 🧠 Ollama Setup

This project uses **Ollama** to run large language models locally.

1. Install Ollama by following the instructions on [ollama.com/download](https://ollama.com/download).
2. Pull the required models:

   ```bash
   ollama pull llama3
   ollama pull qwen
   ```
3. Verify installation:

   ```bash
   ollama list
   ```

---

## 🚀 Running the Application

Start the demo by running:

```bash
python app.py
```

After launching, check your terminal output — it should display a link similar to:

```
 * Running on http://127.0.0.1:5000
```

Click the link or copy it into your browser to use the chatbot.

---

## ⚠️ Disclaimer

This chatbot is a **work-in-progress demo** for educational purposes.
Expect incomplete features, limited responses, and possible bugs.

---

## 📚 License

This project is for **university and personal learning use only**.
Please do not use it in production environments.
