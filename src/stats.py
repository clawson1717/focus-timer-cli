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
    today_focus_sessions = [s for s in today_sessions if s.get("type", "focus") == "focus"]
    today_break_sessions = [s for s in today_sessions if s.get("type") == "break"]
    
    today_focus_minutes = sum(s["duration"] for s in today_focus_sessions)
    today_break_minutes = sum(s["duration"] for s in today_break_sessions)
    
    streak = calculate_streak(sessions)
    
    print(f"{Fore.CYAN}📊 Today's Stats:{Style.RESET_ALL}")
    print(f"   Focus sessions: {len(today_focus_sessions)}")
    print(f"   Focus time: {format_duration(today_focus_minutes)}")
    if today_break_sessions:
        print(f"   Break time: {format_duration(today_break_minutes)}")
    if streak > 0:
        print(f"   🔥 Streak: {streak} day{'s' if streak != 1 else ''}")
    print()


def show_full_stats():
    """Show detailed statistics."""
    sessions = load_sessions()
    
    if not sessions:
        print(f"{Fore.YELLOW}No sessions recorded yet. Start your first focus session!{Style.RESET_ALL}")
        return
    
    # Separate focus and break sessions
    focus_sessions = [s for s in sessions if s.get("type", "focus") == "focus"]
    break_sessions_list = [s for s in sessions if s.get("type") == "break"]
    
    # Calculate stats for focus sessions
    today_focus = [s for s in get_sessions_in_range(focus_sessions, days=1)]
    week_focus = [s for s in get_sessions_in_range(focus_sessions, days=7)]
    month_focus = [s for s in get_sessions_in_range(focus_sessions, days=30)]
    
    today_break = [s for s in get_sessions_in_range(break_sessions_list, days=1)]
    week_break = [s for s in get_sessions_in_range(break_sessions_list, days=7)]
    month_break = [s for s in get_sessions_in_range(break_sessions_list, days=30)]
    
    today_focus_minutes = sum(s["duration"] for s in today_focus)
    week_focus_minutes = sum(s["duration"] for s in week_focus)
    month_focus_minutes = sum(s["duration"] for s in month_focus)
    total_focus_minutes = sum(s["duration"] for s in focus_sessions)
    
    today_break_minutes = sum(s["duration"] for s in today_break)
    week_break_minutes = sum(s["duration"] for s in week_break)
    month_break_minutes = sum(s["duration"] for s in month_break)
    total_break_minutes = sum(s["duration"] for s in break_sessions_list)
    
    streak = calculate_streak(focus_sessions)
    
    # Calculate averages
    avg_focus_session = total_focus_minutes // len(focus_sessions) if focus_sessions else 0
    
    # Display stats
    print(f"\n{Fore.CYAN}{'=' * 50}")
    print(f"{Fore.CYAN}📊  Productivity Statistics")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n")
    
    # Streak
    if streak > 0:
        fire = "🔥" * min(streak, 5)
        print(f"{Fore.YELLOW}{fire}  Current Streak: {streak} day{'s' if streak != 1 else ''}{Style.RESET_ALL}\n")
    
    # Focus Time stats
    print(f"{Fore.GREEN}🍅  Focus Time:{Style.RESET_ALL}")
    print(f"   Today:     {format_duration(today_focus_minutes):>10}")
    print(f"   This Week: {format_duration(week_focus_minutes):>10}")
    print(f"   This Month:{format_duration(month_focus_minutes):>10}")
    print(f"   All Time:  {format_duration(total_focus_minutes):>10}")
    print()
    
    # Focus Session stats
    print(f"{Fore.GREEN}📈  Focus Sessions:{Style.RESET_ALL}")
    print(f"   Today:     {len(today_focus):>10}")
    print(f"   This Week: {len(week_focus):>10}")
    print(f"   This Month:{len(month_focus):>10}")
    print(f"   All Time:  {len(focus_sessions):>10}")
    print()
    
    # Break stats (if any exist)
    if break_sessions_list:
        print(f"{Fore.BLUE}☕  Break Time:{Style.RESET_ALL}")
        print(f"   Today:     {format_duration(today_break_minutes):>10}")
        print(f"   This Week: {format_duration(week_break_minutes):>10}")
        print(f"   This Month:{format_duration(month_break_minutes):>10}")
        print(f"   All Time:  {format_duration(total_break_minutes):>10}")
        print()
        
        print(f"{Fore.BLUE}☕  Break Sessions:{Style.RESET_ALL}")
        print(f"   Today:     {len(today_break):>10}")
        print(f"   This Week: {len(week_break):>10}")
        print(f"   This Month:{len(month_break):>10}")
        print(f"   All Time:  {len(break_sessions_list):>10}")
        print()
    
    # Average
    print(f"{Fore.MAGENTA}📏  Average Focus Session: {format_duration(avg_focus_session)}{Style.RESET_ALL}")
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
    
    print(f"\n{Fore.CYAN}{'=' * 65}")
    print(f"{Fore.CYAN}📝  Recent Sessions (last {len(recent)})")
    print(f"{Fore.CYAN}{'=' * 65}{Style.RESET_ALL}\n")
    
    for i, session in enumerate(recent, 1):
        timestamp = datetime.fromisoformat(session["timestamp"])
        date_str = timestamp.strftime("%Y-%m-%d %H:%M")
        duration = session["duration"]
        note = session.get("note", "")
        session_type = session.get("type", "focus")
        
        # Use different colors for focus vs break
        type_color = Fore.GREEN if session_type == "focus" else Fore.BLUE
        type_icon = "🍅" if session_type == "focus" else "☕"
        
        print(f"{Fore.WHITE}{i:2d}. {type_icon} {type_color}{date_str}{Fore.WHITE} | {Fore.YELLOW}{duration} min{Style.RESET_ALL}", end="")
        if note:
            print(f" | {Fore.CYAN}{note}{Style.RESET_ALL}")
        else:
            print()
    
    print()


if __name__ == "__main__":
    show_full_stats()
