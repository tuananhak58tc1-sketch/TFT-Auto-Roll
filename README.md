# TFT Auto Roll

A learning project on Computer Vision, OCR, image processing, and automation for TFT.

## Prerequisites
- Python 3.13+

## Setup Instructions

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Entry point of the application.
- `requirements.txt`: Python dependencies.
- `config.json`: Application configuration.
- `data/`: Contains static data like champion information.
- `plan/`: Logic for managing and parsing user plans.
- `vision/`: Modules for screen capture and image recognition (Phase 2+).
- `logic/`: Decision engine to process vision output against the plan.
- `ui/`: PySide6 graphical user interface.
- `screenshots/`: Directory to store mock or captured screenshots.
- `tests/`: Unit and integration tests.

