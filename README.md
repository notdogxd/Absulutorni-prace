## Installation & Requirements

The application is written in **Python 3.12.3** and does not require a database server—all data is stored locally in the `data/` folder using the pandas library.

### Prerequisites
* **Python 3.10+** (Tested on Python 3.12.3)
* `pip` package manager installed

### Installation Steps

### 1. Install Python
If you don't have Python installed on your computer, you need to download and install it first.

* **Windows / macOS:**
  1. Go to the official Python website: [python.org/downloads](https://www.python.org/downloads/)
  2. Download the installer for your operating system.
  3. **Crucial for Windows:** During the installation, make sure to check the box that says **"Add Python to PATH"** (or "Add python.exe to PATH") at the bottom of the installation window before clicking "Install Now".
* **Linux (Ubuntu/Debian):**
  Open your terminal and run the following command:
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip python3-venv
  ```

2. **Clone the repository to your local machine:**
   ```bash
   git clone <YOUR_REPOSITORY_URL>
   cd <FOLDER_NAME>
   ```

3. **Create and activate a virtual environment (recommended):**
   * **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

4. **Install dependencies:**
   The application uses the PyQt5 framework for the GUI and the pandas library for data storage. 
   
   Install the packages using the following command:
   ```bash
   pip install PyQt5 pandas 
   ```
   *(Alternatively, run `pip install -r requirements.txt` if you decide to add the file).*

4. **Run the application:**
   Once everything is installed, you can start the application by running the `main.py` file:
   ```bash
   python main.py
   ```
