import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ---------------- 1. DATASET & ML MODEL ----------------

df = pd.read_csv("Crop_recommendation.csv")

X = df.drop("label", axis=1)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred) * 100

# ---------------- 2. PRESETS DATA ----------------

PRESETS = {
    "Select Soil Preset...": None,
    "🌾 Rice Paddy Field": {"N": 90, "P": 42, "K": 43, "temp": 23.6, "hum": 82, "ph": 6.5, "rain": 236},
    "☁️ Cotton Alluvial Belt": {"N": 118, "P": 46, "K": 19, "temp": 24.0, "hum": 80, "ph": 6.9, "rain": 80},
    "☀️ Arid Fruit Zone": {"N": 20, "P": 25, "K": 50, "temp": 31.0, "hum": 50, "ph": 7.2, "rain": 45},
    "🍎 Highland Orchard": {"N": 20, "P": 135, "K": 200, "temp": 22.0, "hum": 92, "ph": 6.0, "rain": 110},
    "🥥 Coastal Tropical": {"N": 22, "P": 17, "K": 31, "temp": 27.5, "hum": 95, "ph": 6.0, "rain": 175}
}

# ---------------- 3. GUI ACTIONS ----------------

def recommend_crop():
    try:
        values = [
            float(entries["N"].get()),
            float(entries["P"].get()),
            float(entries["K"].get()),
            float(entries["temperature"].get()),
            float(entries["humidity"].get()),
            float(entries["ph"].get()),
            float(entries["rainfall"].get())
        ]

        user_data = pd.DataFrame([values], columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])
        
        probs = model.predict_proba(user_data)[0]
        classes = model.classes_
        
        prob_list = []
        for idx, c in enumerate(classes):
            prob_list.append((c, probs[idx] * 100))
        prob_list.sort(key=lambda x: x[1], reverse=True)

        top_crop, top_conf = prob_list[0]
        
        result_title_var.set(f"🌾 Recommended: {top_crop.upper()}")
        result_sub_var.set(f"Match Confidence: {top_conf:.1f}%\nAlt: {prob_list[1][0]} ({prob_list[1][1]:.1f}%) | {prob_list[2][0]} ({prob_list[2][1]:.1f}%)")
        result_card.config(bg="#d1fae5")
        result_title_label.config(fg="#065f46", bg="#d1fae5")
        result_sub_label.config(fg="#047857", bg="#d1fae5")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values for all parameters.")

def clear_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)
    preset_combobox.set("Select Soil Preset...")
    result_title_var.set("🌱 Ready for Analysis")
    result_sub_var.set("Enter values above or select a preset to analyze.")
    result_card.config(bg="#f3f4f6")
    result_title_label.config(fg="#374151", bg="#f3f4f6")
    result_sub_label.config(fg="#6b7280", bg="#f3f4f6")

def load_preset(event=None):
    selected = preset_combobox.get()
    data = PRESETS.get(selected)
    if data:
        entries["N"].delete(0, tk.END); entries["N"].insert(0, data["N"])
        entries["P"].delete(0, tk.END); entries["P"].insert(0, data["P"])
        entries["K"].delete(0, tk.END); entries["K"].insert(0, data["K"])
        entries["temperature"].delete(0, tk.END); entries["temperature"].insert(0, data["temp"])
        entries["humidity"].delete(0, tk.END); entries["humidity"].insert(0, data["hum"])
        entries["ph"].delete(0, tk.END); entries["ph"].insert(0, data["ph"])
        entries["rainfall"].delete(0, tk.END); entries["rainfall"].insert(0, data["rain"])

# ---------------- 4. TKINTER INTERFACE SETUP ----------------

root = tk.Tk()
root.title("Smart Crop Recommendation AI")
root.geometry("640x760")
root.configure(bg="#f8fafc")
root.resizable(False, False)

# Main Container
main_frame = tk.Frame(root, bg="#f8fafc", padx=25, pady=20)
main_frame.pack(fill="both", expand=True)

# Header Section
header_frame = tk.Frame(main_frame, bg="#064e3b", padx=20, pady=15)
header_frame.pack(fill="x", pady=(0, 15))

title_label = tk.Label(
    header_frame,
    text="🌱 CropAI Recommendation System",
    font=("Helvetica", 18, "bold"),
    fg="#ffffff",
    bg="#064e3b"
)
title_label.pack(anchor="w")

sub_title_label = tk.Label(
    header_frame,
    text=f"Random Forest ML • Model Accuracy: {accuracy:.2f}%",
    font=("Helvetica", 10),
    fg="#a7f3d0",
    bg="#064e3b"
)
sub_title_label.pack(anchor="w", pady=(3, 0))

# Preset Selection Dropdown
preset_frame = tk.Frame(main_frame, bg="#f8fafc")
preset_frame.pack(fill="x", pady=(0, 15))

tk.Label(preset_frame, text="⚡ Quick Presets:", font=("Helvetica", 10, "bold"), fg="#475569", bg="#f8fafc").pack(side="left", padx=(0, 10))
preset_combobox = ttk.Combobox(preset_frame, values=list(PRESETS.keys()), state="readonly", width=35, font=("Helvetica", 10))
preset_combobox.set("Select Soil Preset...")
preset_combobox.pack(side="left", fill="x", expand=True)
preset_combobox.bind("<<ComboboxSelected>>", load_preset)

# Form Grid Container
form_card = tk.Frame(main_frame, bg="#ffffff", bd=1, relief="solid", highlightthickness=0, padx=20, pady=15)
form_card.config(highlightbackground="#e2e8f0")
form_card.pack(fill="x", pady=(0, 15))

entries = {}
fields_data = [
    ("Nitrogen (N):", "N", "0 - 140 kg/ha"),
    ("Phosphorus (P):", "P", "5 - 145 kg/ha"),
    ("Potassium (K):", "K", "5 - 205 kg/ha"),
    ("Temperature (°C):", "temperature", "8 - 45 °C"),
    ("Humidity (%):", "humidity", "10 - 100 %"),
    ("Soil pH:", "ph", "3.5 - 10.0"),
    ("Rainfall (mm):", "rainfall", "20 - 300 mm")
]

for idx, (label_text, key, unit) in enumerate(fields_data):
    row_frame = tk.Frame(form_card, bg="#ffffff")
    row_frame.pack(fill="x", pady=6)

    tk.Label(row_frame, text=label_text, width=18, anchor="w", font=("Helvetica", 10, "bold"), fg="#1e293b", bg="#ffffff").pack(side="left")
    
    entry = tk.Entry(row_frame, font=("Helvetica", 10), bd=1, relief="solid", width=18)
    entry.pack(side="left", padx=(0, 10))
    entries[key] = entry

    tk.Label(row_frame, text=unit, font=("Helvetica", 9), fg="#94a3b8", bg="#ffffff").pack(side="left")

# Action Buttons
btn_frame = tk.Frame(main_frame, bg="#f8fafc")
btn_frame.pack(fill="x", pady=(0, 15))

rec_btn = tk.Button(
    btn_frame,
    text="🌾 Recommend Optimal Crop",
    command=recommend_crop,
    font=("Helvetica", 11, "bold"),
    bg="#10b981",
    fg="#ffffff",
    activebackground="#059669",
    activeforeground="#ffffff",
    bd=0,
    padx=15,
    pady=10,
    cursor="hand2"
)
rec_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

clr_btn = tk.Button(
    btn_frame,
    text="🔄 Reset",
    command=clear_fields,
    font=("Helvetica", 11),
    bg="#e2e8f0",
    fg="#475569",
    activebackground="#cbd5e1",
    bd=0,
    padx=15,
    pady=10,
    cursor="hand2"
)
clr_btn.pack(side="right", width=10)

# Result Card
result_card = tk.Frame(main_frame, bg="#f3f4f6", padx=20, pady=15)
result_card.pack(fill="x")

result_title_var = tk.StringVar(value="🌱 Ready for Analysis")
result_sub_var = tk.StringVar(value="Enter values above or select a preset to analyze.")

result_title_label = tk.Label(
    result_card,
    textvariable=result_title_var,
    font=("Helvetica", 14, "bold"),
    fg="#374151",
    bg="#f3f4f6"
)
result_title_label.pack(anchor="w")

result_sub_label = tk.Label(
    result_card,
    textvariable=result_sub_var,
    font=("Helvetica", 10),
    fg="#6b7280",
    bg="#f3f4f6",
    justify="left"
)
result_sub_label.pack(anchor="w", pady=(5, 0))

root.mainloop()