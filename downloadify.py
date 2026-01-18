import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import subprocess
import re
import json
import threading
from pathlib import Path
from datetime import datetime

# ================= BASIC CONFIG =================

APP_NAME = "Downloadify"
TAGLINE = "Exportify CSV → MP3 Downloader"
CONFIG_FILE = "downloadify.json"
DURATION_TOLERANCE = 3

APP_DIR = Path(__file__).parent

# ================= CONFIG =================

def load_config():
    p = APP_DIR / CONFIG_FILE
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_config(cfg):
    (APP_DIR / CONFIG_FILE).write_text(
        json.dumps(cfg, indent=2),
        encoding="utf-8"
    )

config = load_config()
LIBRARY_DEFAULT = config.get("library_path", str(APP_DIR / "library"))
DARK_MODE = config.get("dark_mode", True)

# ================= THEMES =================

DARK = {
    "bg": "#0f172a",
    "fg": "#e5e7eb",
    "entry": "#020617",
    "log": "#020617",
    "btn": "#2563eb",
    "danger": "#dc2626"
}

LIGHT = {
    "bg": "#ffffff",
    "fg": "#000000",
    "entry": "#ffffff",
    "log": "#ffffff",
    "btn": "#2563eb",
    "danger": "#dc2626"
}

# ================= HELPERS =================

def clean(text):
    return re.sub(r'[\\/*?:"<>|]', "", text.strip()) if text else ""

def get(row, *keys):
    for k in keys:
        if row.get(k):
            return clean(row[k])
    return ""

def expected_duration(row):
    if row.get("Duration (ms)", "").isdigit():
        return int(row["Duration (ms)"]) / 1000
    return None

def audio_duration(path):
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=nokey=1:noprint_wrappers=1",
                str(path)
            ],
            capture_output=True,
            text=True
        )
        return float(r.stdout.strip())
    except Exception:
        return None

def get_failed_tracks(log_path):
    failed = set()
    if not log_path.exists():
        return failed
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("FAILED:"):
            failed.add(line.replace("FAILED:", "").strip())
    return failed

# ================= SEARCH STRATEGY =================

SEARCHES = [
    "ytsearch1:{title} {artist} official audio",
    "ytsearch1:{title} {artist} lyrics",
    "ytsearch1:{title} {artist} topic",
]

# ================= PIPELINE =================

def run_pipeline(csv_path, library, log_box, progress, stop_flag, retry_failed=False):
    library = Path(library)
    library.mkdir(parents=True, exist_ok=True)

    log_file = library / "downloadify_log.txt"
    log = open(log_file, "a", encoding="utf-8")

    log.write("\n" + "=" * 60 + "\n")
    log.write(f"Run started: {datetime.now()}\n")
    log.write(f"CSV: {csv_path}\n")
    if retry_failed:
        log.write("MODE: RETRY FAILED ONLY\n")

    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    failed_only = get_failed_tracks(log_file) if retry_failed else set()

    progress["maximum"] = len(rows)

    for index, row in enumerate(rows, start=1):
        if stop_flag["stop"]:
            log.write("STOPPED BY USER\n")
            break

        title = get(row, "Track Name")
        artist = get(row, "Artist Name(s)")
        album = get(row, "Album Name")
        date = get(row, "Release Date")
        genre = get(row, "Genres")
        label = get(row, "Record Label")
        dur = expected_duration(row)

        if not title or not artist:
            continue

        if retry_failed and title not in failed_only:
            progress["value"] = index
            continue

        output = library / f"{title}.mp3"
        if output.exists() and not retry_failed:
            progress["value"] = index
            continue

        success = False

        for template in SEARCHES:
            if stop_flag["stop"]:
                break

            query = template.format(title=title, artist=artist)
            temp = library / f".tmp_{index}.mp3"

            log_box.insert(tk.END, f"Searching: {query}\n")
            log_box.see(tk.END)

            subprocess.run([
                "yt-dlp", query,
                "--no-cache-dir",
                "--force-ipv4",
                "--match-filter", "duration > 60 & duration < 900",

                "--add-metadata",
                "--embed-thumbnail",
                "--convert-thumbnails", "jpg",

                "--parse-metadata", f"title:{title}",
                "--parse-metadata", f"artist:{artist}",
                "--parse-metadata", f"album:{album}",
                "--parse-metadata", f"date:{date}",
                "--parse-metadata", f"genre:{genre}",
                "--parse-metadata", f"label:{label}",

                "-f", "bestaudio",
                "-x", "--audio-format", "mp3",
                "--audio-quality", "0",
                "--no-playlist",
                "-o", str(temp)
            ])

            if not temp.exists():
                continue

            if dur:
                actual = audio_duration(temp)
                if actual is None or abs(actual - dur) > DURATION_TOLERANCE:
                    temp.unlink(missing_ok=True)
                    continue

            temp.rename(output)
            log.write(f"DOWNLOADED: {title}\n")
            success = True
            break

        if not success:
            log.write(f"FAILED: {title}\n")

        progress["value"] = index

    log.write(f"Finished: {datetime.now()}\n")
    log.close()
    messagebox.showinfo("Done", "Download complete. Check log file.")

# ================= GUI =================

root = tk.Tk()
root.title(APP_NAME)
root.geometry("900x680")

csv_path = tk.StringVar()
library_path = tk.StringVar(value=LIBRARY_DEFAULT)
stop_flag = {"stop": False}

# ================= THEME =================

def apply_theme():
    theme = DARK if config.get("dark_mode", True) else LIGHT
    root.configure(bg=theme["bg"])
    frame.configure(bg=theme["bg"])
    log_box.configure(bg=theme["log"], fg=theme["fg"])
    for w in themed_widgets:
        try:
            w.configure(bg=theme["entry"], fg=theme["fg"])
        except Exception:
            pass

def toggle_theme():
    config["dark_mode"] = not config.get("dark_mode", True)
    save_config(config)
    apply_theme()

# ================= UI =================

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

themed_widgets = []

title_lbl = tk.Label(frame, text=TAGLINE, font=("Segoe UI", 12, "bold"))
title_lbl.grid(row=0, column=0, sticky="w")
themed_widgets.append(title_lbl)

def browse_csv():
    p = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if p:
        csv_path.set(p)

def browse_library():
    p = filedialog.askdirectory()
    if p:
        library_path.set(p)
        config["library_path"] = p
        save_config(config)

def start(retry=False):
    if not csv_path.get():
        messagebox.showerror("Error", "Select a CSV file")
        return
    stop_flag["stop"] = False
    threading.Thread(
        target=run_pipeline,
        args=(csv_path.get(), library_path.get(), log_box, progress, stop_flag, retry),
        daemon=True
    ).start()

def stop_run():
    stop_flag["stop"] = True

csv_entry = tk.Entry(frame, textvariable=csv_path, width=78)
csv_entry.grid(row=1, column=0)
themed_widgets.append(csv_entry)

tk.Button(frame, text="Browse CSV", command=browse_csv).grid(row=1, column=1)

lib_entry = tk.Entry(frame, textvariable=library_path, width=78)
lib_entry.grid(row=2, column=0)
themed_widgets.append(lib_entry)

tk.Button(frame, text="Library", command=browse_library).grid(row=2, column=1)

tk.Button(frame, text="Start", command=lambda: start(False)).grid(row=3, column=0, sticky="w")
tk.Button(frame, text="Retry Failed Only", command=lambda: start(True)).grid(row=3, column=1, sticky="w")
tk.Button(frame, text="Stop", bg="#dc2626", fg="white", command=stop_run).grid(row=3, column=2, sticky="w")
tk.Button(frame, text="Toggle Dark / Light", command=toggle_theme).grid(row=3, column=3, sticky="w")

progress = ttk.Progressbar(frame, length=860)
progress.grid(row=4, column=0, columnspan=4, pady=10)

log_box = tk.Text(frame, height=22)
log_box.grid(row=5, column=0, columnspan=4, sticky="nsew")

frame.rowconfigure(5, weight=1)
frame.columnconfigure(0, weight=1)

apply_theme()
root.mainloop()
