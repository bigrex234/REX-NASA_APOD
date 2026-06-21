"""
NASA APOD Viewer — by REX
Fetches the Astronomy Picture of the Day from NASA's API
and displays it in a beautiful terminal UI.

Requirements:
    pip install requests rich

Get a free API key at: https://api.nasa.gov/
"""

import requests
import webbrowser
import sys
from datetime import datetime, timedelta

# ── Try importing rich, fallback to plain print ──────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.prompt import Prompt
    from rich import box
    RICH = True
    console = Console()
except ImportError:
    RICH = False
    print("[!] Install 'rich' for a better experience: pip install rich\n")

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY = "DEMO_KEY"   # Replace with your key from https://api.nasa.gov/
BASE_URL = "https://api.nasa.gov/planetary/apod"

# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch_apod(date: str = None, count: int = None) -> dict | list:
    """Fetch APOD data from NASA API."""
    params = {"api_key": API_KEY, "thumbs": True}
    if date:
        params["date"] = date
    if count:
        params["count"] = count

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        error("No internet connection. Check your network.")
    except requests.exceptions.HTTPError as e:
        error(f"API error: {e}")
    except Exception as e:
        error(f"Unexpected error: {e}")


def error(msg: str):
    if RICH:
        console.print(f"\n[bold red]ERROR:[/bold red] {msg}\n")
    else:
        print(f"\nERROR: {msg}\n")
    sys.exit(1)


def display_apod(data: dict):
    """Display a single APOD entry beautifully."""
    title     = data.get("title", "Unknown")
    date      = data.get("date", "Unknown")
    media     = data.get("media_type", "image")
    url       = data.get("url", "")
    hdurl     = data.get("hdurl", url)
    copyright = data.get("copyright", "NASA / Public Domain").strip()
    explanation = data.get("explanation", "No description available.")

    if RICH:
        # ── Header ──
        console.print()
        console.rule("[bold yellow]✦ NASA APOD VIEWER ✦[/bold yellow]")
        console.print()

        # ── Title panel ──
        title_text = Text()
        title_text.append(f"  {title}\n", style="bold white")
        title_text.append(f"  {date}  •  ", style="dim white")
        title_text.append(f"© {copyright}", style="italic dim cyan")
        console.print(Panel(title_text, border_style="yellow", padding=(0, 1)))

        # ── Media type badge ──
        badge = "[bold green]📷 IMAGE[/bold green]" if media == "image" else "[bold magenta]🎬 VIDEO[/bold magenta]"
        console.print(f"  Type: {badge}\n")

        # ── Explanation ──
        console.print(Panel(
            explanation,
            title="[bold cyan]Description[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        ))

        # ── Links ──
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column(style="bold yellow")
        table.add_column(style="blue underline")
        if media == "image":
            table.add_row("HD Image:", hdurl)
        table.add_row("Standard:", url)
        console.print(table)

    else:
        # Plain fallback
        print(f"\n{'='*60}")
        print(f"  NASA APOD — {date}")
        print(f"  {title}")
        print(f"  © {copyright}")
        print(f"{'='*60}")
        print(f"\n{explanation}\n")
        print(f"URL: {url}")

    return hdurl if media == "image" else url


def open_in_browser(url: str):
    """Open the image/video in the default browser."""
    if RICH:
        console.print("\n[dim]Opening in browser...[/dim]")
    else:
        print("\nOpening in browser...")
    webbrowser.open(url)


def show_menu():
    """Main interactive menu."""
    if RICH:
        console.print()
        console.rule("[bold yellow]MENU[/bold yellow]")
        options = Table(box=box.SIMPLE, show_header=False)
        options.add_column(style="bold yellow", width=4)
        options.add_column(style="white")
        options.add_row("1", "Today's APOD")
        options.add_row("2", "APOD for a specific date")
        options.add_row("3", "5 random APODs")
        options.add_row("4", "Yesterday's APOD")
        options.add_row("0", "Exit")
        console.print(options)
        choice = Prompt.ask("\n[bold yellow]Choose[/bold yellow]", choices=["0","1","2","3","4"], default="1")
    else:
        print("\n--- MENU ---")
        print("1. Today's APOD")
        print("2. APOD for a specific date")
        print("3. 5 random APODs")
        print("4. Yesterday's APOD")
        print("0. Exit")
        choice = input("\nChoose: ").strip()

    return choice


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if RICH:
        console.print("\n[bold yellow]  ✦ NASA Astronomy Picture of the Day[/bold yellow]")
        console.print("[dim]  Powered by NASA Open APIs — api.nasa.gov[/dim]")

    while True:
        choice = show_menu()

        if choice == "0":
            if RICH:
                console.print("\n[bold yellow]Later, space explorer. 🚀[/bold yellow]\n")
            else:
                print("\nBye!\n")
            break

        elif choice == "1":
            data = fetch_apod()
            url = display_apod(data)
            if RICH:
                ans = Prompt.ask("\n[yellow]Open in browser?[/yellow]", choices=["y","n"], default="y")
            else:
                ans = input("\nOpen in browser? (y/n): ").strip().lower()
            if ans == "y":
                open_in_browser(url)

        elif choice == "2":
            if RICH:
                date_str = Prompt.ask("[yellow]Enter date[/yellow] [dim](YYYY-MM-DD)[/dim]")
            else:
                date_str = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                if RICH:
                    console.print("[red]Invalid date format.[/red]")
                else:
                    print("Invalid date format.")
                continue
            data = fetch_apod(date=date_str)
            url = display_apod(data)
            if RICH:
                ans = Prompt.ask("\n[yellow]Open in browser?[/yellow]", choices=["y","n"], default="y")
            else:
                ans = input("\nOpen in browser? (y/n): ").strip().lower()
            if ans == "y":
                open_in_browser(url)

        elif choice == "3":
            if RICH:
                console.print("\n[dim]Fetching 5 random APODs...[/dim]")
            else:
                print("\nFetching 5 random APODs...")
            items = fetch_apod(count=5)
            for i, item in enumerate(items, 1):
                if RICH:
                    console.print(f"\n[bold yellow]── APOD {i}/5 ──[/bold yellow]")
                else:
                    print(f"\n--- APOD {i}/5 ---")
                display_apod(item)
                if i < len(items):
                    if RICH:
                        Prompt.ask("\n[dim]Press Enter for next[/dim]", default="")
                    else:
                        input("\nPress Enter for next...")

        elif choice == "4":
            yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
            data = fetch_apod(date=yesterday)
            url = display_apod(data)
            if RICH:
                ans = Prompt.ask("\n[yellow]Open in browser?[/yellow]", choices=["y","n"], default="y")
            else:
                ans = input("\nOpen in browser? (y/n): ").strip().lower()
            if ans == "y":
                open_in_browser(url)

        else:
            if RICH:
                console.print("[red]Invalid choice.[/red]")
            else:
                print("Invalid choice.")


if __name__ == "__main__":
    main()
