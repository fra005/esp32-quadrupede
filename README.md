# Fractals Visualizer

An interactive fractal visualizer built with **Python**, **Tkinter**, **NumPy** and **Matplotlib**.

Un'applicazione per esplorare diversi frattali, modificando zoom, posizione, colori e numero di iterazioni.

## Features / Funzionalità

- Mandelbrot, Julia, Burning Ship and Tricorn sets.
- Interactive controls for zoom and center position.
- Adjustable iteration count and color maps.
- Custom real and imaginary parameters for the Julia set.
- Dark interface built with Tkinter.

## Requirements / Requisiti

- Python 3.9+
- Tkinter (usually included with Python; on some Linux systems install `python3-tk`)
- NumPy
- Matplotlib

## Installation / Installazione

1. Download or clone this repository.
2. Open a terminal in the project folder.
3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the program:

   ```bash
   python main.py
   ```

On Windows, you can use `py` instead of `python`.

## How to use / Come si usa

Choose a fractal from the menu, adjust the sliders, then click **Update / Aggiorna**. Use **Reset / Ripristina** to return to the initial settings. Julia parameters appear when Julia is selected.

The interface needs a desktop environment: it does not run directly inside GitHub's website.
