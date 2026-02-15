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
    "break_duration": 5,
    "auto_break": True,
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


def save_session(duration, note="", session_type="focus"):
    """Save a completed session."""
    ensure_data_dir()
    sessions = load_sessions()
    
    session = {
        "timestamp": datetime.now().isoformat(),
        "duration": duration,
        "note": note,
        "type": session_type,
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


def play_break_notification():
    """Play break notification sound or show alert."""
    config = load_config()
    
    if config.get("sound_enabled"):
        try:
            from playsound import playsound
            # Try to play a system sound or beep (different pattern for break)
            print("\a\a", end="", flush=True)  # Double terminal bell for break
        except ImportError:
            pass
    
    # Print visual notification
    print(f"\n{Fore.BLUE}{'=' * 50}")
    print(f"{Fore.BLUE}☕  Break time is over! Ready to focus?")
    print(f"{Fore.BLUE}{'=' * 50}{Style.RESET_ALL}\n")


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
        save_session(duration_minutes, note, session_type="focus")
        
        # Show stats after session
        from stats import show_quick_stats
        show_quick_stats()
        
        # Offer break after focus session
        config = load_config()
        if config.get("auto_break", True):
            offer_break()
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}⚠️  Timer cancelled. Session not saved.{Style.RESET_ALL}")
        sys.exit(0)


def break_countdown(duration_minutes):
    """Run the break timer countdown."""
    duration_seconds = duration_minutes * 60
    
    print(f"\n{Fore.BLUE}☕  Break Timer Started!")
    print(f"{Fore.BLUE}Duration: {duration_minutes} minutes")
    print(f"{Fore.YELLOW}Press Ctrl+C to skip remaining break{Style.RESET_ALL}\n")
    
    try:
        for remaining in range(duration_seconds, 0, -1):
            # Clear line and print countdown
            sys.stdout.write(f"\r{Fore.WHITE}⏱️  Break time remaining: {Fore.BLUE}{format_time(remaining)}{Style.RESET_ALL}  ")
            sys.stdout.flush()
            time.sleep(1)
        
        # Timer complete
        sys.stdout.write(f"\r{Fore.GREEN}⏱️  Break time remaining: 00:00{' ' * 20}{Style.RESET_ALL}\n")
        sys.stdout.flush()
        
        play_break_notification()
        save_session(duration_minutes, note="Break session", session_type="break")
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Break skipped early.{Style.RESET_ALL}")
        # Still save partial break
        elapsed = duration_seconds - remaining if 'remaining' in locals() else 0
        if elapsed > 60:  # Only save if at least 1 minute elapsed
            save_session(elapsed // 60, note="Partial break session", session_type="break")
        return False
    return True


def offer_break():
    """Offer to start a break after focus session."""
    config = load_config()
    break_duration = config.get("break_duration", 5)
    
    print(f"\n{Fore.CYAN}{'=' * 50}")
    print(f"{Fore.CYAN}☕  Break Time Options:")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  [b]{Fore.GREEN} Start break ({break_duration} min)")
    print(f"{Fore.WHITE}  [e]{Fore.YELLOW} Extend break (+5 min)")
    print(f"{Fore.WHITE}  [s]{Fore.MAGENTA} Skip break")
    print(f"{Fore.WHITE}  [f]{Fore.CYAN} Start next focus session")
    print()
    
    while True:
        try:
            choice = input(f"{Fore.CYAN}Choose an option [b/e/s/f]: {Style.RESET_ALL}").strip().lower()
            
            if choice == 'b' or choice == '':
                # Start break with default duration
                break_countdown(break_duration)
                break
            elif choice == 'e':
                # Extended break
                extended_duration = break_duration + 5
                print(f"{Fore.YELLOW}Extended break: {extended_duration} minutes{Style.RESET_ALL}")
                break_countdown(extended_duration)
                break
            elif choice == 's':
                print(f"{Fore.YELLOW}Break skipped.{Style.RESET_ALL}")
                break
            elif choice == 'f':
                # Start next focus session immediately
                print(f"{Fore.GREEN}Starting next focus session...{Style.RESET_ALL}")
                config = load_config()
                default_duration = config.get("default_duration", 25)
                countdown(default_duration)
                break
            else:
                print(f"{Fore.RED}Invalid option. Please choose b, e, s, or f.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Break options cancelled.{Style.RESET_ALL}")
            break


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


def cmd_break(args):
    """Handle break command."""
    config = load_config()
    duration = args.duration or config.get("break_duration", 5)
    
    break_countdown(duration)


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
    
    if args.break_duration is not None:
        config["break_duration"] = args.break_duration
        save_config(config)
        print(f"{Fore.GREEN}✓ Break duration set to {args.break_duration} minutes{Style.RESET_ALL}")
    
    if args.auto_break is not None:
        config["auto_break"] = args.auto_break.lower() in ("on", "true", "yes", "1")
        save_config(config)
        status = "enabled" if config["auto_break"] else "disabled"
        print(f"{Fore.GREEN}✓ Auto-break after focus {status}{Style.RESET_ALL}")
    
    # Show current config
    print(f"\n{Fore.CYAN}Current Configuration:{Style.RESET_ALL}")
    print(f"  Default duration: {config['default_duration']} minutes")
    print(f"  Sound enabled: {config['sound_enabled']}")
    print(f"  Break duration: {config.get('break_duration', 5)} minutes")
    print(f"  Auto-break enabled: {config.get('auto_break', True)}")


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
    
    # Break command
    break_parser = subparsers.add_parser("break", help="Start a break timer")
    break_parser.add_argument("-d", "--duration", type=int, help="Break duration in minutes")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="View productivity statistics")
    
    # History command
    history_parser = subparsers.add_parser("history", help="View session history")
    history_parser.add_argument("-l", "--limit", type=int, default=10, help="Number of sessions to show")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configure settings")
    config_parser.add_argument("--duration", type=int, help="Set default focus duration in minutes")
    config_parser.add_argument("--sound", type=str, choices=["on", "off"], help="Enable/disable sound")
    config_parser.add_argument("--break-duration", type=int, help="Set default break duration in minutes")
    config_parser.add_argument("--auto-break", type=str, choices=["on", "off"], help="Enable/disable auto-break after focus")
    
    args = parser.parse_args()
    
    if args.command == "start":
        cmd_start(args)
    elif args.command == "break":
        cmd_break(args)
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
