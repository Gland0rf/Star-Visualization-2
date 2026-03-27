
## About the Project

This project is a physics-based space simulation that models the motion of celestial bodies such as stars and planets using gravitational interactions.

---

## Notes

Everything in this Simulation is accurate, **except** the size of the planets and stars. Realistically they would be a lot smaller,
but for viewing purposes, they are much bigger than they should be (otherwise you would have to zoom for a while).
The "Open Menu" button is disabled right now.
There still are some errors that lead to the program crashing.

---

# Project Setup

## Prerequisites

* Python 3.13.12 or higher installed

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/SPG-NASA/Space-Simulation.git
cd Space-Simulation
```

---

## Create & Activate Virtual Environment

### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

If you get a permission error:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

Install everything from the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## ▶Run the Project

```bash
python main.py
# or
python3 main.py
```
