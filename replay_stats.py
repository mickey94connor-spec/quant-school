"""
v3 Replay Stats - Quant School, first build.

Reads the table in "v3 Replay Log.md" (in my Obsidian vault) and prints
my win rate and expected value (EV) per trade for plan v3.

Run it:   double-click "Run v3 Stats.bat"
   or:    python replay_stats.py
   or:    python replay_stats.py "C:/path/to/v3 Replay Log.md"
"""
import sys
from pathlib import Path

# Plan v3 numbers
STOP_POINTS = 25          # stop loss, in points
TARGET_POINTS = 62        # profit target, in points
DOLLARS_PER_POINT = 2     # MNQ pays $2 per point, per contract
MIN_TRADES_TO_TRUST = 30  # fewer trades than this = sample too small

# The log lives in the miketrades vault, next to this quant-school folder
DEFAULT_LOG = (Path(__file__).resolve().parent.parent
               / "miketrades" / "2 DAY TRADING" / "v3 Replay Log.md")

NO_TRADE = ("", "none", "no trade", "-")


def read_table(path):
    """Turn the markdown table into a list of rows (dicts). Skips blank rows."""
    rows, header = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):  # the |---|---| line
            continue
        row = dict(zip(header, cells))
        if row.get("date"):
            rows.append(row)
    return rows


def trade_points(row):
    """Points for one row. None for no-trade days or when points are missing."""
    result = row.get("result", "").lower()
    if result in NO_TRADE:
        return None
    written = row.get("points", "").replace("+", "").replace(" ", "")
    if written:
        try:
            return float(written)
        except ValueError:
            pass
    if result.startswith("win"):
        return float(TARGET_POINTS)
    if result.startswith("loss"):
        return float(-STOP_POINTS)
    return None  # e.g. Flat11 with no points written yet


def money(x):
    sign = "+" if x >= 0 else "-"
    return f"{sign}${abs(x):,.2f}"


def main():
    log = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LOG
    if not log.exists():
        print("Can't find the log file:")
        print("   ", log)
        return

    rows = read_table(log)
    trades, need_points, trade_days = [], [], set()
    for row in rows:
        pts = trade_points(row)
        if pts is not None:
            trades.append((row, pts))
            trade_days.add(row["date"])
        elif row.get("result", "").lower() not in NO_TRADE:
            need_points.append(row["date"])
            trade_days.add(row["date"])
    days = {row["date"] for row in rows}

    breakeven = STOP_POINTS / (STOP_POINTS + TARGET_POINTS)

    print()
    print(f"v3 STATS: {log.stem}")
    print("=" * 40)
    print(f"Days logged:      {len(days)}")
    print(f"No-trade days:    {len(days - trade_days)}")
    print(f"Trades:           {len(trades)}")
    if need_points:
        print(f"Missing points:   {', '.join(need_points)}  (fill in the Points column)")

    if not trades:
        print()
        print("No trades logged yet. Fill in the log and run this again.")
        print(f"Break-even win rate for v3: {breakeven:.0%}")
        return

    points = [p for _, p in trades]
    wins = [p for p in points if p > 0]
    losses = [p for p in points if p < 0]
    n = len(points)
    p_win, p_loss = len(wins) / n, len(losses) / n
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    ev = sum(points) / n
    followed = sum(1 for r, _ in trades
                   if r.get("rules followed", "").lower().startswith("y"))

    print(f"Wins / losses:    {len(wins)} / {len(losses)}")
    print(f"Win rate:         {p_win:.0%}   (break-even is {breakeven:.0%})")
    print()
    print("EV = P(win) x avg win + P(loss) x avg loss")
    print(f"EV = {p_win:.2f} x {avg_win:+.1f} + {p_loss:.2f} x {avg_loss:+.1f}")
    print(f"EV = {ev:+.2f} points per trade  ({money(ev * DOLLARS_PER_POINT)})")
    print()
    print(f"Total:            {sum(points):+.1f} points  ({money(sum(points) * DOLLARS_PER_POINT)})")
    print(f"Rules followed:   {followed} of {n} trades")
    print()
    if n < MIN_TRADES_TO_TRUST:
        print(f"Only {n} trades. Too few to trust yet; aim for {MIN_TRADES_TO_TRUST}+.")
    elif ev > 0:
        print("Positive EV over a real sample. Keep logging.")
    else:
        print("EV is zero or negative over a real sample. The edge isn't there yet.")


if __name__ == "__main__":
    main()
