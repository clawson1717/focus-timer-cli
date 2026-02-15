#!/usr/bin/env python3
"""
Statistics module for Focus Timer CLI.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from colorama import Fore, Style

DATA_DIR = Path(__file__).parent.parent / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"


def load_sessions():
    """Load all sessions from file."""
    if SESSIONS_FILE.exists():
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    return []


def parse_session_time(session):
    """Parse session timestamp to datetime."""
    return datetime.fromisoformat(session["timestamp"])


def get_sessions_in_range(sessions, days=1):
    """Get sessions from the last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    return [s for s in sessions if parse_session_time(s) >= cutoff]


def calculate_streak(sessions):
    """Calculate current streak of days with at least one session."""
    if not sessions:
        return 0
    
    # Group sessions by date
    dates_with_sessions = set()
    for session in sessions:
        session_date = parse_session_time(session).date()
        dates_with_sessions.add(session_date)
    
    # Calculate streak
    streak = 0
    today = datetime.now().date()
    
    # Check if there's a session today
    if today in dates_with_sessions:
        streak += 1
    elif today - timedelta(days=1) not in dates_with_sessions:
        # If no session yesterday and none today, streak is 0
        return 0
    
    # Count backwards
    check_date = today - timedelta(days=1)
    while check_date in dates_with_sessions:
        streak += 1
        check_date -= timedelta(days=1)
    
    return streak


def format_duration(minutes):
    """Format minutes as hours and minutes."""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def show_quick_stats():
    """Show brief stats after a session."""
    sessions = load_sessions()
    
    today_sessions = get_sessions_in_range(sessions, days=1)
    today_minutes = sum(s["duration"] for s in today_sessions)
    
    streak = calculate_streak(sessions)
    
    print(f"{Fore.CYAN}📊 Today's Stats:{Style.RESET_ALL}")
    print(f"   Sessions: {len(today_sessions)}")
    print(f"   Focus time: {format_duration(today_minutes)}")
    if streak > 0:
        print(f"   🔥 Streak: {streak} day{'s' if streak != 1 else ''}")
    print()


def show_full_stats():
    """Show detailed statistics."""
    sessions = load_sessions()
    
    if not sessions:
        print(f"{Fore.YELLOW}No sessions recorded yet. Start your first focus session!{Style.RESET_ALL}")
        return
    
    # Calculate stats
    today_sessions = get_sessions_in_range(sessions, days=1)
    week_sessions = get_sessions_in_range(sessions, days=7)
    month_sessions = get_sessions_in_range(sessions, days=30)
    
    today_minutes = sum(s["duration"] for s in today_sessions)
    week_minutes = sum(s["duration"] for s in week_sessions)
    month_minutes = sum(s["duration"] for s in month_sessions)
    total_minutes = sum(s["duration"] for s in sessions)
    
    streak = calculate_streak(sessions)
    
    # Calculate averages
    avg_session = total_minutes // len(sessions) if sessions else 0
    
    # Display stats
    print(f"\n{Fore.CYAN}{'=' * 50}")
    print(f"{Fore.CYAN}📊  Productivity Statistics")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n")
    
    # Streak
    if streak > 0:
        fire = "🔥" * min(streak, 5)
        print(f"{Fore.YELLOW}{fire}  Current Streak: {streak} day{'s' if streak != 1 else ''}{Style.RESET_ALL}\n")
    
    # Time stats
    print(f"{Fore.GREEN}⏱️  Focus Time:{Style.RESET_ALL}")
    print(f"   Today:     {format_duration(today_minutes):>10}")
    print(f"   This Week: {format_duration(week_minutes):>10}")
    print(f"   This Month:{format_duration(month_minutes):>10}")
    print(f"   All Time:  {format_duration(total_minutes):>10}")
    print()
    
    # Session stats
    print(f"{Fore.BLUE}📈  Sessions:{Style.RESET_ALL}")
    print(f"   Today:     {len(today_sessions):>10}")
    print(f"   This Week: {len(week_sessions):>10}")
    print(f"   This Month:{len(month_sessions):>10}")
    print(f"   All Time:  {len(sessions):>10}")
    print()
    
    # Average
    print(f"{Fore.MAGENTA}📏  Average Session: {format_duration(avg_session)}{Style.RESET_ALL}")
    print()


def show_history(limit=10):
    """Show recent session history."""
    sessions = load_sessions()
    
    if not sessions:
        print(f"{Fore.YELLOW}No sessions recorded yet.{Style.RESET_ALL}")
        return
    
    # Sort by timestamp (newest first)
    sorted_sessions = sorted(sessions, key=lambda s: s["timestamp"], reverse=True)
    recent = sorted_sessions[:limit]
    
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}📝  Recent Sessions (last {len(recent)})")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")
    
    for i, session in enumerate(recent, 1):
        timestamp = datetime.fromisoformat(session["timestamp"])
        date_str = timestamp.strftime("%Y-%m-%d %H:%M")
        duration = session["duration"]
        note = session.get("note", "")
        
        print(f"{Fore.WHITE}{i:2d}. {Fore.GREEN}{date_str}{Fore.WHITE} | {Fore.YELLOW}{duration} min{Style.RESET_ALL}", end="")
        if note:
            print(f" | {Fore.CYAN}{note}{Style.RESET_ALL}")
        else:
            print()
    
    print()


if __name__ == "__main__":
    show_full_stats()
