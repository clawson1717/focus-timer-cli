#!/usr/bin/env python3
"""
Focus Timer CLI - A Pomodoro-style focus timer with session logging.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"

DEFAULT_CONFIG = {
    "default_duration": 25,
    "sound_enabled": True,
    "sound_file": None,
}


def ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    """Load configuration or create default."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def load_sessions():
    """Load all sessions from file."""
    if SESSIONS_FILE.exists():
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    return []


def save_session(duration, note=""):
    """Save a completed session."""
    ensure_data_dir()
    sessions = load_sessions()
    
    session = {
        "timestamp": datetime.now().isoformat(),
        "duration": duration,
        "note": note,
    }
    sessions.append(session)
    
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)


def play_notification():
    """Play notification sound or show alert."""
    config = load_config()
    
    if config.get("sound_enabled"):
        try:
            from playsound import playsound
            # Try to play a system sound or beep
            print("\a", end="", flush=True)  # Terminal bell
        except ImportError:
            pass
    
    # Print visual notification
    print(f"\n{Fore.GREEN}{'=' * 50}")
    print(f"{Fore.GREEN}🎉  Focus session complete! Great job!")
    print(f"{Fore.GREEN}{'=' * 50}{Style.RESET_ALL}\n")


def format_time(seconds):
    """Format seconds as MM:SS."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


def countdown(duration_minutes, note=""):
    """Run the focus timer countdown."""
    duration_seconds = duration_minutes * 60
    
    print(f"\n{Fore.CYAN}🍅  Focus Timer Started!")
    print(f"{Fore.CYAN}Duration: {duration_minutes} minutes")
    if note:
        print(f"{Fore.CYAN}Note: {note}")
    print(f"{Fore.YELLOW}Press Ctrl+C to cancel{Style.RESET_ALL}\n")
    
    try:
        for remaining in range(duration_seconds, 0, -1):
            # Clear line and print countdown
            sys.stdout.write(f"\r{Fore.WHITE}⏱️  Time remaining: {Fore.YELLOW}{format_time(remaining)}{Style.RESET_ALL}  ")
            sys.stdout.flush()
            time.sleep(1)
        
        # Timer complete
        sys.stdout.write(f"\r{Fore.GREEN}⏱️  Time remaining: 00:00{' ' * 20}{Style.RESET_ALL}\n")
        sys.stdout.flush()
        
        play_notification()
        save_session(duration_minutes, note)
        
        # Show stats after session
        from stats import show_quick_stats
        show_quick_stats()
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}⚠️  Timer cancelled. Session not saved.{Style.RESET_ALL}")
        sys.exit(0)


def cmd_start(args):
    """Handle start command."""
    config = load_config()
    duration = args.duration or config.get("default_duration", 25)
    note = args.note or ""
    
    countdown(duration, note)


def cmd_stats(args):
    """Handle stats command."""
    from stats import show_full_stats
    show_full_stats()


def cmd_history(args):
    """Handle history command."""
    from stats import show_history
    show_history(limit=args.limit)


def cmd_config(args):
    """Handle config command."""
    config = load_config()
    
    if args.duration is not None:
        config["default_duration"] = args.duration
        save_config(config)
        print(f"{Fore.GREEN}✓ Default duration set to {args.duration} minutes{Style.RESET_ALL}")
    
    if args.sound is not None:
        config["sound_enabled"] = args.sound.lower() in ("on", "true", "yes", "1")
        save_config(config)
        status = "enabled" if config["sound_enabled"] else "disabled"
        print(f"{Fore.GREEN}✓ Sound notifications {status}{Style.RESET_ALL}")
    
    # Show current config
    print(f"\n{Fore.CYAN}Current Configuration:{Style.RESET_ALL}")
    print(f"  Default duration: {config['default_duration']} minutes")
    print(f"  Sound enabled: {config['sound_enabled']}")


def main():
    parser = argparse.ArgumentParser(
        description="Focus Timer CLI - Pomodoro-style focus timer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a focus session")
    start_parser.add_argument("-d", "--duration", type=int, help="Session duration in minutes")
    start_parser.add_argument("-n", "--note", type=str, help="Note about the session")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="View productivity statistics")
    
    # History command
    history_parser = subparsers.add_parser("history", help="View session history")
    history_parser.add_argument("-l", "--limit", type=int, default=10, help="Number of sessions to show")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configure settings")
    config_parser.add_argument("--duration", type=int, help="Set default duration in minutes")
    config_parser.add_argument("--sound", type=str, choices=["on", "off"], help="Enable/disable sound")
    
    args = parser.parse_args()
    
    if args.command == "start":
        cmd_start(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "history":
        cmd_history(args)
    elif args.command == "config":
        cmd_config(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
