import csv
import pathlib
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")  # embed in Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

CSV_FILE = pathlib.Path(__file__).with_name("bmi_data.csv")

# ---------- BMI helpers ----------
def calculate_bmi(weight, ft):
    metres = ft * 0.3048
    return weight / (metres ** 2)

def categorize(bmi):
    return (
        "Underweight" if bmi < 18.5 else
        "Normal weight" if bmi < 25 else
        "Overweight" if bmi < 30 else
        "Obesity"
    )

# ---------- CSV persistence ----------
def save_row(w, h, age, bmi, cat):
    newfile = not CSV_FILE.exists()
    with CSV_FILE.open("a", newline="") as f:
        writer = csv.writer(f)
        if newfile:
            writer.writerow(["date", "weight", "height_ft", "age", "bmi", "category"])
        writer.writerow([datetime.now().isoformat(), w, h, age, bmi, cat])

def load_bmis():
    """Return a list of BMI floats from the CSV, skipping any header row automatically."""
    if not CSV_FILE.exists():
        return []

    bmis = []
    with CSV_FILE.open() as f:
        reader = csv.reader(f)
        for row in reader:
            # Either header row or bad/empty row
            if not row or row[0].lower() == "date":
                continue
            try:
                # BMI is the 5th column (index 4) in our csv schema
                bmis.append(float(row[4]))
            except (ValueError, IndexError):
                # Skip rows that don't match expected format
                continue
    return bmis

# ---------- UI ----------
app = ttk.Window(themename="litera", title="BMI Calculator", size=(800, 650))
app.place_window_center()

# ---- Form frame ----
frm = ttk.Frame(app, padding=20)
frm.pack(fill=BOTH, expand=True)

header = ttk.Label(frm, text="BMI Calculator", font=("Helvetica", 28, "bold"), anchor=CENTER)
header.grid(row=0, column=0, columnspan=4, pady=(0, 25))

# labels + entries
labels = ["Weight (kg)", "Height (ft)", "Age (yrs)"]
vars_  = [ttk.DoubleVar(), ttk.DoubleVar(), ttk.IntVar()]

for i, (lab, var) in enumerate(zip(labels, vars_)):
    ttk.Label(frm, text=lab + ":", font=("Helvetica", 14)).grid(row=1, column=i, sticky=E, padx=5, pady=10)
    ttk.Entry(frm, textvariable=var, font=("Helvetica", 14), width=12).grid(row=1, column=i+1, sticky=W, padx=5, pady=10)

w_var, h_var, age_var = vars_

# ---- Result & gauge ----
result_lbl = ttk.Label(frm, text="", font=("Helvetica", 16))
result_lbl.grid(row=2, column=0, columnspan=4, pady=10)

gauge = ttk.Progressbar(frm, length=450, bootstyle=SUCCESS, maximum=50)
gauge.grid(row=3, column=0, columnspan=4, pady=(0, 20))

# ---- Trend chart ----
fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=frm)
canvas.get_tk_widget().grid(row=6, column=0, columnspan=4, pady=25)

def refresh_chart():
    bmis = load_bmis()
    ax.clear()
    if bmis:
        ax.plot(range(1, len(bmis)+1), bmis, marker="o", color="#20639B", linewidth=2)
        ax.set_title("BMI Trend Over Time", fontsize=12)
        ax.set_xlabel("Entry #")
        ax.set_ylabel("BMI")
        ax.grid(alpha=0.3)
    canvas.draw()

# ---- Calculate handler ----
def on_calc():
    try:
        w, h, age = w_var.get(), h_var.get(), age_var.get()
    except ttk.TclError:
        ttk.messagebox.showerror("Error", "Fill all fields with numbers.")
        return

    if w<=0 or h<=0 or age<=0:
        ttk.messagebox.showerror("Error", "All numbers must be positive.")
        return

    bmi = round(calculate_bmi(w, h), 1)
    cat = categorize(bmi)

    colors = {"Underweight": INFO, "Normal weight": SUCCESS,
              "Overweight": WARNING, "Obesity": DANGER}
    gauge.configure(value=bmi, bootstyle=colors[cat])

    result_lbl.configure(text=f"BMI: {bmi}  ➔  {cat}")

    save_row(w, h, age, bmi, cat)
    refresh_chart()

# ---- Buttons ----
ttk.Button(frm, text="Calculate BMI", command=on_calc, bootstyle=PRIMARY, width=20).grid(row=4, column=1, columnspan=2, pady=10)

# make columns expand nicely
frm.columnconfigure((0,1,2,3), weight=1)

refresh_chart()
app.mainloop()
