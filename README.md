Downloadify 🎵

Downloadify is a Python-based GUI application that downloads music from YouTube using a Spotify playlist exported via *Exportify* (CSV format) and automatically organizes the songs into a local MP3 library.

It is designed to be *simple, reliable, and beginner-friendly*, with all required tools bundled directly in the repository.

✨ Features
- 🎧 Import Spotify playlists using Exportify CSV files
- 🔍 Smart YouTube search strategy:
  - Official audio
  - Lyrics videos
  - Topic uploads
- ⏱️ Duration matching to avoid incorrect songs
- 🌙 Dark / ☀️ Light mode toggle (saved automatically)
- ⏹️ Stop button to cancel downloads safely
- 🔁 Retry failed downloads only
- 📁 Single-folder music library (no nested folders)
- 🧾 Detailed log file for every run

📂 Project Structure

Downloadify/
├── downloadify.py

├── README.md

├── LICENSE

├── tools/

│ ├── yt-dlp.exe

│ ├── ffmpeg.exe

│ └── ffprobe.exe

All required tools are included in the `tools/` folder.

🖥️ Requirements
- Windows
- Python 3.9 or newer
No additional installations are required:
- yt-dlp ✅ bundled
- ffmpeg / ffprobe ✅ bundled

🚀 How to Run
1. Clone the repository:

git clone https://github.com/Bhaskarpoonia/Downloadify.git

Navigate into the folder:
cd Downloadify

Run the app:
python downloadify.py

The GUI will open automatically.

📄 Preparing Your CSV (Exportify)
Go to https://exportify.app

Log in with Spotify

Export your playlist as a CSV

Use that CSV file in Downloadify

Supported columns include (others are ignored safely):

Track Name

Artist Name(s)

Duration (ms)

📁 Output
All downloaded songs are saved as MP3 files in your chosen library folder

A log file is created:

Copy code
downloadify_log.txt
This file records:
downloaded tracks
skipped tracks
failed tracks
stopped runs

🔁 Retry Failed Downloads
If some tracks fail:
Fix your network / wait a while
Reopen Downloadify
Click “Retry Failed Only”
Only the failed tracks will be retried.

⚠️ Antivirus Notice
Some antivirus software may flag:
yt-dlp.exe
ffmpeg.exe
This is a false positive due to their downloading and media-processing behavior.

If downloads do not start:
Add the project folder to antivirus exclusions
📜 Legal & Ethical Notes
This tool does not bypass DRM
Content availability depends on YouTube and your region
Intended for personal and educational use only
Respect local copyright laws
🧾 Licenses
Downloadify: MIT License
yt-dlp: Unlicense
ffmpeg / ffprobe: LGPL/GPL (as provided by the FFmpeg project)
All third-party tools are included unmodified and credited to their respective authors.

🤝 Contributing
Contributions are welcome:
Bug reports
Feature requests
Pull requests

Please open an issue first for major changes.
📌 Roadmap (Future Ideas)
Album art preview
Per-track status icons
Cross-platform support (Linux/macOS)
CLI-only mode
Auto-update for yt-dlp
❤️ Acknowledgements
Exportify
yt-dlp developers
FFmpeg project
Open-source community

Enjoy your music library! 🎶
