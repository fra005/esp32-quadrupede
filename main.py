import time
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class FractalCalculator:
    """Numerical methods for four fractal sets."""

    @staticmethod
    def _iterate(c, max_iterations, fractal_type, c_parameter=None):
        z = c.copy() if fractal_type == "julia" else np.zeros_like(c, dtype=np.complex128)
        divergence_iter = np.full(c.shape, max_iterations, dtype=np.int32)
        active = np.ones(c.shape, dtype=bool)

        for i in range(max_iterations):
            if not np.any(active):
                break
            if fractal_type == "mandelbrot":
                z[active] = z[active] ** 2 + c[active]
            elif fractal_type == "julia":
                z[active] = z[active] ** 2 + c_parameter
            elif fractal_type == "burning_ship":
                current = z[active]
                z[active] = (np.abs(current.real) + 1j * np.abs(current.imag)) ** 2 + c[active]
            elif fractal_type == "tricorn":
                z[active] = np.conjugate(z[active]) ** 2 + c[active]

            escaped = active & (np.abs(z) > 2.0)
            divergence_iter[escaped] = i
            active[escaped] = False
        return divergence_iter

    @staticmethod
    def mandelbrot(c, max_iterations):
        return FractalCalculator._iterate(c, max_iterations, "mandelbrot")

    @staticmethod
    def julia(c, max_iterations, c_parameter=-0.7 + 0.27015j):
        return FractalCalculator._iterate(c, max_iterations, "julia", c_parameter)

    @staticmethod
    def burning_ship(c, max_iterations):
        return FractalCalculator._iterate(c, max_iterations, "burning_ship")

    @staticmethod
    def tricorn(c, max_iterations):
        return FractalCalculator._iterate(c, max_iterations, "tricorn")


class FractalVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Fractals Visualizer")
        self.root.geometry("1200x850")
        self.root.configure(bg="#2b2b2b")

        # Fractal names and formulas
        self.math_fractals = {
            "mandelbrot": ("Mandelbrot", "Z² + C"),
            "julia": ("Julia", "Z² + C"),
            "burning_ship": ("Burning Ship", "(|Re(Z)| + i|Im(Z)|)² + C"),
            "tricorn": ("Tricorn", "conjugate(Z)² + C"),
        }
        self.color_maps = ["hot", "viridis", "inferno", "magma", "plasma", "cool", "spring", "summer"]
        self.apply_dark_theme()
        self.setup_ui()

    def setup_ui(self):
        """Build the GUI / Crea l'interfaccia grafica."""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        settings_frame = ttk.LabelFrame(main_frame, text="Settings / Impostazioni", padding=10)
        settings_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(settings_frame, text="Fractal type / Tipo:").pack(anchor=tk.W, pady=(0, 5))
        self.fractal_var = tk.StringVar(value="mandelbrot")
        self.fractal_combo = ttk.Combobox(
            settings_frame, textvariable=self.fractal_var,
            values=list(self.math_fractals.keys()), state="readonly"
        )
        self.fractal_combo.pack(fill=tk.X, pady=(0, 10))
        self.fractal_combo.bind("<<ComboboxSelected>>", self.on_fractal_change)

        self.formula_label = tk.Label(
            settings_frame, text="Formula: Z² + C", font=("Courier", 9),
            bg="#3c3c3c", relief="solid", fg="white", padx=5, pady=5,
            wraplength=250, justify="left"
        )
        self.formula_label.pack(fill=tk.X, pady=(0, 10))

        math_frame = ttk.LabelFrame(settings_frame, text="Rendering", padding=5)
        math_frame.pack(fill=tk.X, pady=10)
        ttk.Label(math_frame, text="Max iterations / Iterazioni:").pack(anchor=tk.W, pady=(0, 5))
        self.iter_var = tk.IntVar(value=100)
        iter_scale = ttk.Scale(math_frame, from_=50, to=500, variable=self.iter_var, orient=tk.HORIZONTAL)
        iter_scale.pack(fill=tk.X, pady=(0, 10))
        self.iter_label = ttk.Label(math_frame, text="100 iterations")
        self.iter_label.pack(anchor=tk.W, pady=(0, 10))
        iter_scale.configure(command=self.on_iter_change)

        ttk.Label(math_frame, text="Color map / Colori:").pack(anchor=tk.W, pady=(0, 5))
        self.color_var = tk.StringVar(value="hot")
        color_combo = ttk.Combobox(math_frame, textvariable=self.color_var, values=self.color_maps, state="readonly")
        color_combo.pack(fill=tk.X, pady=(0, 10))

        zoom_frame = ttk.LabelFrame(settings_frame, text="Position & Zoom", padding=5)
        zoom_frame.pack(fill=tk.X, pady=10)
        ttk.Label(zoom_frame, text="Center X:").pack(anchor=tk.W)
        self.center_x_var = tk.DoubleVar(value=-0.75)
        ttk.Scale(zoom_frame, from_=-2.0, to=1.0, variable=self.center_x_var, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 5))
        ttk.Label(zoom_frame, text="Center Y:").pack(anchor=tk.W)
        self.center_y_var = tk.DoubleVar(value=0.0)
        ttk.Scale(zoom_frame, from_=-1.5, to=1.5, variable=self.center_y_var, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 5))
        ttk.Label(zoom_frame, text="Zoom / Ingrandimento:").pack(anchor=tk.W)
        self.zoom_var = tk.DoubleVar(value=1.0)
        ttk.Scale(zoom_frame, from_=0.1, to=10.0, variable=self.zoom_var, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 5))

        self.julia_frame = ttk.LabelFrame(settings_frame, text="Julia parameters", padding=5)
        ttk.Label(self.julia_frame, text="Constant C:").pack(anchor=tk.W, pady=(5, 0))
        param_frame = ttk.Frame(self.julia_frame)
        param_frame.pack(fill=tk.X, pady=5)
        ttk.Label(param_frame, text="Re(C):").pack(side=tk.LEFT, padx=(0, 5))
        self.julia_real = tk.DoubleVar(value=-0.7)
        ttk.Entry(param_frame, textvariable=self.julia_real, width=10).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(param_frame, text="Im(C):").pack(side=tk.LEFT, padx=(0, 5))
        self.julia_imag = tk.DoubleVar(value=0.27015)
        ttk.Entry(param_frame, textvariable=self.julia_imag, width=10).pack(side=tk.LEFT)

        self.spacer = ttk.Frame(settings_frame, height=0)
        self.spacer.pack(fill=tk.X, pady=10)
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Update / Aggiorna", command=self.update_fractal).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="Reset / Ripristina", command=self.reset_settings).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        self.graph_frame = ttk.Frame(main_frame)
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.status_var = tk.StringVar(value="Ready / Pronto")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)
        self.setup_plot()

    def setup_plot(self):
        """Initialize the embedded Matplotlib chart."""
        self.fig, self.ax = plt.subplots(figsize=(9, 7), facecolor="#2b2b2b")
        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax.set_facecolor("#2b2b2b")

    def apply_dark_theme(self):
        """Configure the dark UI theme."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background="#2b2b2b", foreground="white")
        style.configure("TLabel", background="#2b2b2b", foreground="white")
        style.configure("TLabelframe", background="#2b2b2b", foreground="white")
        style.configure("TLabelframe.Label", background="#3c3c3c", foreground="white", font=("Arial", 10, "bold"))
        style.configure("TButton", background="#404040", foreground="white", borderwidth=1)
        style.map("TButton", background=[("active", "#505050")])
        style.configure("TCombobox", fieldbackground="#404040", background="#404040", foreground="white", selectbackground="#606060", selectforeground="white")
        style.map("TCombobox", fieldbackground=[("readonly", "#404040")], background=[("readonly", "#404040")])
        style.configure("TScale", background="#2b2b2b", troughcolor="#404040")
        style.configure("Horizontal.TScale", background="#2b2b2b")
        style.configure("TEntry", fieldbackground="#404040", foreground="white")

    def on_fractal_change(self, event=None):
        """Update the formula and show Julia-specific controls."""
        fractal_type = self.fractal_var.get()
        _, formula = self.math_fractals[fractal_type]
        self.formula_label.config(text=f"Formula:\n{formula}" if len(formula) > 20 else f"Formula: {formula}")
        if fractal_type == "julia":
            self.julia_frame.pack(fill=tk.X, pady=(5, 0), before=self.spacer)
        else:
            self.julia_frame.pack_forget()

    def on_iter_change(self, value=None):
        self.iter_label.config(text=f"{int(self.iter_var.get())} iterations")

    def calculate_fractal(self):
        """Calculate the chosen fractal / Calcola il frattale selezionato."""
        start_time = time.perf_counter()
        fractal_type = self.fractal_var.get()
        max_iter = int(self.iter_var.get())
        zoom = self.zoom_var.get()
        center_x = self.center_x_var.get()
        center_y = self.center_y_var.get()

        size = 3.0 / zoom
        xmin, xmax = center_x - size / 2, center_x + size / 2
        ymin, ymax = center_y - size / 2, center_y + size / 2
        resolution = 800
        x = np.linspace(xmin, xmax, resolution)
        y = np.linspace(ymin, ymax, resolution)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y

        if fractal_type == "julia":
            c_param = complex(self.julia_real.get(), self.julia_imag.get())
            fractal_data = FractalCalculator.julia(C, max_iter, c_param)
        else:
            method = getattr(FractalCalculator, fractal_type)
            fractal_data = method(C, max_iter)

        return fractal_data, xmin, xmax, ymin, ymax, time.perf_counter() - start_time

    def update_fractal(self):
        """Redraw the fractal and update the status bar."""
        try:
            self.status_var.set("Calculating / Calcolo in corso...")
            self.root.update_idletasks()
            fractal_data, xmin, xmax, ymin, ymax, compute_time = self.calculate_fractal()
            self.ax.clear()
            self.ax.imshow(fractal_data, extent=[xmin, xmax, ymin, ymax], cmap=self.color_var.get(), origin="lower", aspect="equal")
            fractal_type = self.fractal_var.get()
            fractal_name = self.math_fractals[fractal_type][0]
            if fractal_type == "julia":
                c_param = complex(self.julia_real.get(), self.julia_imag.get())
                title = f"{fractal_name}\nC = {c_param.real:.3f} {c_param.imag:+.3f}i"
            else:
                title = fractal_name
            title += f"\nZoom: {self.zoom_var.get():.1f}x | Iterations: {int(self.iter_var.get())}"
            self.ax.set_title(title, color="white", pad=20, fontsize=12)
            self.ax.set_xlabel("Re(C)", color="white")
            self.ax.set_ylabel("Im(C)", color="white")
            self.ax.tick_params(colors="white")
            self.fig.tight_layout()
            self.canvas.draw()
            self.status_var.set(f"Done / Completato! Calculation time: {compute_time:.2f} s")
        except Exception as exc:
            messagebox.showerror("Error / Errore", f"Calculation failed / Errore nel calcolo:\n{exc}")
            self.status_var.set("Calculation error / Errore")

    def reset_settings(self):
        """Restore defaults / Ripristina le impostazioni iniziali."""
        self.fractal_var.set("mandelbrot")
        self.iter_var.set(100)
        self.color_var.set("hot")
        self.zoom_var.set(1.0)
        self.center_x_var.set(-0.75)
        self.center_y_var.set(0.0)
        self.julia_real.set(-0.7)
        self.julia_imag.set(0.27015)
        self.on_iter_change()
        self.on_fractal_change()
        self.update_fractal()


def main():
    root = tk.Tk()
    app = FractalVisualizer(root)
    root.after(100, app.update_fractal)
    root.mainloop()


if __name__ == "__main__":
    main()
