# LeadGen AI — Installation Guide

This guide provides step-by-step instructions for installing and setting up the complete LeadGen AI application on Windows.

---

## 📋 Prerequisites

Ensure the following tools are installed on your Windows machine:
1. **Node.js**: v20+ or v24+ (tested on `v24.20.0`).
2. **npm**: v10+ or v11+ (tested on `11.19.0`).
3. **Python**: 3.11+ (verified on `Python 3.11.9`).
4. **Git**: (verified on `git version 2.56.0`).
5. **PowerShell**: Standard Windows PowerShell 5.1 or PowerShell Core 7+.

---

## 🛠️ Step 1: Clone or Open the Repository

```powershell
# Open project directory in PowerShell
cd "C:\Users\R\OneDrive\Desktop\Lead Gen Ai"
```

---

## 🐍 Step 2: Backend Setup (FastAPI & SQLite)

1. Navigate to the `backend` folder:
   ```powershell
   cd backend
   ```

2. Create a virtual environment using Python 3.11:
   ```powershell
   & "C:\Users\R\AppData\Local\Programs\Python\Python311\python.exe" -m venv venv
   ```

3. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. Upgrade `pip` and install required dependencies:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Create your local environment file:
   ```powershell
   Copy-Item .env.example .env
   ```

6. Return to root:
   ```powershell
   cd ..
   ```

---

## ⚛️ Step 3: Frontend Setup (React + Vite + Tailwind CSS)

1. Navigate to the `frontend` directory:
   ```powershell
   cd frontend
   ```

2. Install npm packages:
   ```powershell
   npm install
   ```

3. Create the frontend environment file:
   ```powershell
   Copy-Item .env.example .env
   ```

4. Return to root:
   ```powershell
   cd ..
   ```

---

## 🚀 Step 4: Starting the Applications

Open two separate PowerShell terminal windows:

### Terminal 1 — Backend API
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base: `http://127.0.0.1:8000`
- Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### Terminal 2 — Frontend CRM Dashboard
```powershell
cd frontend
npm run dev
```
- Frontend UI: `http://localhost:5173`
