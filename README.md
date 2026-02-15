# Focus Timer CLI

A simple yet powerful CLI Pomodoro-style focus timer with session logging and productivity statistics.

## Features

- 🍅 **Customizable focus timer** (default: 25 minutes)
- ☕ **Break timer** with auto-start after focus sessions
- ⏱️ **Live countdown** with minutes:seconds display
- 🔊 **Audio notification** when timer completes
- 📝 **Session logging** with timestamps and optional notes
- 📊 **Productivity statistics** - track your focus and break hours separately
- 🔥 **Streak tracking** - build consistent habits
- 🎨 **Colorful terminal UI** for better experience
- ⚙️ **Configurable break duration** and auto-break settings
- 📤 **Export session data** to JSON or CSV for external analysis

## Installation

```bash
git clone https://github.com/clawson1717/focus-timer-cli.git
cd focus-timer-cli
pip install -r requirements.txt
```

## Usage

### Start a focus session

```bash
# Start with default 25-minute timer
python src/focus_timer.py start

# Start with custom duration (in minutes)
python src/focus_timer.py start --duration 45

# Start with a note about what you're working on
python src/focus_timer.py start --note "Working on project proposal"
```

After a focus session completes, you'll be automatically prompted to:
- **Start a break** (default: 5 minutes)
- **Extend break** (+5 minutes)
- **Skip break** and continue
- **Start next focus session** immediately

### Take a break

```bash
# Start a break timer with default duration
python src/focus_timer.py break

# Start a break with custom duration
python src/focus_timer.py break --duration 10
```

The break timer runs independently and can be started manually at any time.

### View statistics

```bash
# Show focus stats (today, week, month)
python src/focus_timer.py stats
```

### View session history

```bash
# Show recent sessions
python src/focus_timer.py history

# Show last 20 sessions
python src/focus_timer.py history --limit 20
```

### Configure settings

```bash
# Show current configuration
python src/focus_timer.py config

# Set default focus duration
python src/focus_timer.py config --duration 30

# Set default break duration
python src/focus_timer.py config --break-duration 5

# Enable/disable auto-break after focus sessions
python src/focus_timer.py config --auto-break on

# Enable/disable sound
python src/focus_timer.py config --sound on
```

### Export session data

```bash
# Export all sessions to JSON (default format)
python src/focus_timer.py export

# Export to CSV format
python src/focus_timer.py export --format csv

# Export to specific file
python src/focus_timer.py export --output my_sessions.json

# Export only focus sessions
python src/focus_timer.py export --type focus

# Export only break sessions
python src/focus_timer.py export --type break

# Export sessions from a date range
python src/focus_timer.py export --from 2024-01-01 --to 2024-12-31

# Export with all filters combined
python src/focus_timer.py export --format csv --type focus --from 2024-01-01 --output january_focus.csv
```

## Project Structure

```
focus-timer-cli/
├── src/
│   ├── focus_timer.py    # Main timer application
│   └── stats.py          # Statistics and analytics
├── data/                 # Session logs (gitignored)
│   └── sessions.json     # Session history
├── examples/             # Sample outputs
├── requirements.txt      # Python dependencies
└── config.json           # User configuration (created on first run)
```

### Configuration Options

The `config.json` file stores your preferences:

```json
{
  "default_duration": 25,
  "sound_enabled": true,
  "break_duration": 5,
  "auto_break": true,
  "export_format": "json",
  "export_directory": "."
}
```

**Export Options:**
- `export_format`: Default export format (`"json"` or `"csv"`)
- `export_directory`: Default directory for exported files (defaults to current directory)

## Data Storage

Session logs are stored in `data/sessions.json`. This directory is gitignored to keep your personal data private.

## License

MIT
