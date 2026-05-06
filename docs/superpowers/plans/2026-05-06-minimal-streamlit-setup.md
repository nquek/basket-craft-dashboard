# Minimal Streamlit Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap a runnable Streamlit app with a venv and a single title as the foundation for the Basket Craft Dashboard.

**Architecture:** A Python venv isolates dependencies. A `requirements.txt` pins `streamlit`. A single `app.py` renders one title and nothing else.

**Tech Stack:** Python 3.14, venv, Streamlit

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `.venv/` | Create (not committed) | Isolated Python environment |
| `requirements.txt` | Create | Pin `streamlit` dependency |
| `app.py` | Create | Streamlit entrypoint with title |
| `.gitignore` | Verify | Ensure `.venv/` is ignored |

---

### Task 1: Create the virtual environment

**Files:**
- Create: `.venv/` (directory, managed by venv — not committed)

- [ ] **Step 1: Create the venv**

```bash
python3 -m venv .venv
```

Expected: `.venv/` directory appears at project root with `bin/`, `lib/`, `pyvenv.cfg`.

- [ ] **Step 2: Verify `.venv` is gitignored**

```bash
grep -n '\.venv' .gitignore
```

Expected: a line matching `.venv` or `.venv/`. If missing, add it:

```bash
echo '.venv/' >> .gitignore
git add .gitignore
git commit -m "chore: ignore .venv"
```

---

### Task 2: Pin Streamlit in requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Install Streamlit into the venv**

```bash
.venv/bin/pip install streamlit
```

Expected: output ends with `Successfully installed streamlit-...`

- [ ] **Step 2: Pin the installed version**

```bash
.venv/bin/pip freeze | grep -i streamlit > requirements.txt
```

Expected: `requirements.txt` contains exactly one line like `streamlit==1.x.x`.

- [ ] **Step 3: Verify the file looks right**

```bash
cat requirements.txt
```

Expected: a single `streamlit==<version>` line.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: add streamlit dependency"
```

---

### Task 3: Create the minimal app

**Files:**
- Create: `app.py`

- [ ] **Step 1: Write app.py**

Create `app.py` at the project root with this exact content:

```python
import streamlit as st

st.title("Basket Craft Dashboard")
```

- [ ] **Step 2: Commit**

```bash
git add app.py
git commit -m "feat: add minimal Streamlit app with title"
```

---

### Task 4: Run the app and verify it works

**Files:** none modified

- [ ] **Step 1: Launch Streamlit**

```bash
.venv/bin/streamlit run app.py
```

Expected: terminal output similar to:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

- [ ] **Step 2: Open the browser**

Navigate to `http://localhost:8501`.

Expected: a white page with the heading **"Basket Craft Dashboard"** and nothing else.

- [ ] **Step 3: Stop the server**

Press `Ctrl+C` in the terminal.
