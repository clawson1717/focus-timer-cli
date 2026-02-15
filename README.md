# Focus Timer CLI

A simple yet powerful CLI Pomodoro-style focus timer with session logging and productivity statistics.

## Features

- 🍅 **Customizable focus timer** (default: 25 minutes)
- ⏱️ **Live countdown** with minutes:seconds display
- 🔊 **Audio notification** when timer completes
- 📝 **Session logging** with timestamps and optional notes
- 📊 **Productivity statistics** - track your focus hours
- 🔥 **Streak tracking** - build consistent habits
- 🎨 **Colorful terminal UI** for better experience

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

# Set default timer duration
python src/focus_timer.py config --duration 30

# Enable/disable sound
python src/focus_timer.py config --sound on
```

## Project Structure

```
focus-timer-cli/
├── src/
│   ├── focus_timer.py    # Main timer application
│   └── stats.py          # Statistics and analytics
├── data/                 # Session logs (gitignored)
├── examples/             # Sample outputs
├── requirements.txt      # Python dependencies
└── config.json          # User configuration
```

## Data Storage

Session logs are stored in `data/sessions.json`. This directory is gitignored to keep your personal data private.

## License

MIT
