"""
v3 Backtest - Quant School, build 2.

Tests Plan v3 on real MNQ 1-minute bars exported from NinjaTrader, one trade a
day, and prints the same stats as replay_stats.py.

Get the data (NinjaTrader):
  Control Center > Tools > Historical Data > Export
  Instrument MNQ 12-26, Interval: Minute, Value: 1, Format: NinjaTrader.
  Pick the dates, click Export, and save it as mnq_1min.txt in this folder.

Run it:   python backtest_v3.py              (reads mnq_1min.txt)
    or:   python backtest_v3.py other_file.txt

Plan v3 as code (1-minute bars, Eastern time):
  1. 8-9 move  = close at 9:00 minus open at 8:00. Up or Down.
  2. Open move = close at 9:45 minus open at 9:30. Up or Down.
  3. Both must agree, or no trade that day.
  4. First bar between 9:45 and 10:30 whose range touches the 20 EMA and
     closes on the trend side of it = the pullback. Enter at that bar's close.
  5. Stop 25 points, target 62 points. A bar that hits both counts as a loss.
  6. Still open at 11:00 = closed at the 11:00 bar ("Flat11").

My chart uses 9000-tick bars, so its 20 EMA is not identical to a 1-minute
20 EMA. This tests the idea, not the exact fills.
"""
import csv
import sys
from datetime import datetime, timedelta, time
from pathlib import Path

STOP_POINTS = 25.0
TARGET_POINTS = 62.0
DOLLARS_PER_POINT = 2
EMA_LEN = 20
MIN_TRADES_TO_TRUST = 30
TIMESTAMP_IS_BAR_END = True      # NinjaTrader stamps each bar with its END time

PRE = (time(8, 0), time(9, 0))        # the 8-9 move
OPEN = (time(9, 30), time(9, 45))     # the open
WINDOW = (time(9, 45), time(10, 30))  # entry window
FLAT = time(11, 0)

DEFAULT_FILE = Path(__file__).resolve().parent / "mnq_1min.txt"


def read_bars(path):
    """NinjaTrader export: yyyyMMdd HHmmss;open;high;low;close;volume"""
    bars = []
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            parts = line.strip().replace(",", ";").split(";")
            if len(parts) < 5:
                continue
            stamp = parts[0].strip()
            try:
                ts = datetime.strptime(stamp, "%Y%m%d %H%M%S")
            except ValueError:
                try:
                    ts = datetime.fromisoformat(stamp)
                except ValueError:
                    continue  # header line or junk
            try:
                o, h, l, c = (float(x) for x in parts[1:5])
            except ValueError:
                continue
            if TIMESTAMP_IS_BAR_END:
                ts -= timedelta(minutes=1)  # ts is now the bar's start time
            bars.append((ts, o, h, l, c))
    bars.sort()
    return bars


def by_day(bars):
    days = {}
    for b in bars:
        days.setdefault(b[0].date(), []).append(b)
    return days


def ema_series(day_bars):
    k = 2 / (EMA_LEN + 1)
    out, e = [], None
    for _, _, _, _, c in day_bars:
        e = c if e is None else c * k + e * (1 - k)
        out.append(e)
    return out


def move(day_bars, span):
    seg = [b for b in day_bars if span[0] <= b[0].time() < span[1]]
    if not seg:
        return 0, 0.0
    m = seg[-1][4] - seg[0][1]      # last close minus first open
    return (1 if m > 0 else -1 if m < 0 else 0), m


def run_day(day_bars):
    """Returns a dict for the log row."""
    d1, m1 = move(day_bars, PRE)
    d2, m2 = move(day_bars, OPEN)
    row = {"8-9": fmt_dir(d1, m1), "open": fmt_dir(d2, m2),
           "trade": "None", "entry_time": "", "entry": "", "exit_time": "",
           "result": "None", "points": ""}
    if d1 == 0 or d2 == 0 or d1 != d2:
        row["note"] = "no agree" if d1 and d2 else "no data"
        return row
    side = d1
    ema = ema_series(day_bars)
    for i, (ts, o, h, l, c) in enumerate(day_bars):
        if not (WINDOW[0] <= ts.time() < WINDOW[1]):
            continue
        touched = l <= ema[i] <= h
        held = c >= ema[i] if side == 1 else c <= ema[i]
        if touched and held:
            result, pts, exit_ts = simulate(day_bars, i, side, c)
            row.update({"trade": "Long" if side == 1 else "Short",
                        "entry_time": ts.strftime("%H:%M"), "entry": f"{c:.2f}",
                        "exit_time": exit_ts.strftime("%H:%M"),
                        "result": result, "points": f"{pts:+.2f}", "note": ""})
            return row
    row["note"] = "agreed, no pullback"
    return row


def simulate(day_bars, i_entry, side, entry):
    stop = entry - side * STOP_POINTS
    target = entry + side * TARGET_POINTS
    for ts, o, h, l, c in day_bars[i_entry + 1:]:
        if ts.time() >= FLAT:
            return "Flat11", side * (o - entry), ts
        hit_stop = l <= stop if side == 1 else h >= stop
        hit_target = h >= target if side == 1 else l <= target
        if hit_stop:                      # stop checked first = conservative
            return "Loss", -STOP_POINTS, ts
        if hit_target:
            return "Win", TARGET_POINTS, ts
    last = day_bars[-1]
    return "Flat11", side * (last[4] - entry), last[0]


def fmt_dir(d, m):
    return {1: "Up", -1: "Down"}.get(d, "Flat") + f" ({m:+.0f})"


def money(x):
    return ("+" if x >= 0 else "-") + f"${abs(x):,.2f}"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    if not path.exists():
        print("Can't find the data file:", path)
        print("Export MNQ 1-minute bars from NinjaTrader and save them as mnq_1min.txt here.")
        return
    bars = read_bars(path)
    days = by_day(bars)
    if not days:
        print("No bars read. Is the file a NinjaTrader minute export?")
        return

    rows = []
    for day in sorted(days):
        r = run_day(days[day])
        r["date"] = day.strftime("%m/%d/%Y")
        rows.append(r)

    out = path.parent / "backtest_v3_results.csv"
    cols = ["date", "8-9", "open", "trade", "entry_time", "entry", "exit_time", "result", "points", "note"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    trades = [r for r in rows if r["trade"] != "None"]
    pts = [float(r["points"]) for r in trades]
    wins = [p for p in pts if p > 0]
    losses = [p for p in pts if p < 0]
    flat = [r for r in trades if r["result"] == "Flat11"]
    breakeven = STOP_POINTS / (STOP_POINTS + TARGET_POINTS)

    print()
    print(f"v3 BACKTEST: {path.name}")
    print("=" * 44)
    print(f"Days tested:      {len(rows)}  ({rows[0]['date']} to {rows[-1]['date']})")
    print(f"No-trade days:    {len(rows) - len(trades)}")
    print(f"Trades:           {len(trades)}")
    if not trades:
        print("No trades. Either the filter never agreed, or the file doesn't cover 8:00-11:00.")
        return
    n = len(pts)
    p_win = len(wins) / n
    ev = sum(pts) / n
    print(f"Wins / losses:    {len(wins)} / {len(losses)}   (flat at 11:00: {len(flat)})")
    print(f"Win rate:         {p_win:.0%}   (break-even is {breakeven:.0%})")
    print(f"EV per trade:     {ev:+.2f} points  ({money(ev * DOLLARS_PER_POINT)})")
    print(f"Total:            {sum(pts):+.1f} points  ({money(sum(pts) * DOLLARS_PER_POINT)})")
    print()
    if n < MIN_TRADES_TO_TRUST:
        print(f"Only {n} trades. Export more months; aim for {MIN_TRADES_TO_TRUST}+.")
    elif ev > 0:
        print("Positive EV over a real sample.")
    else:
        print("EV is zero or negative over a real sample. The edge isn't there on 1-minute bars.")
    print(f"Every day is in {out.name}.")


if __name__ == "__main__":
    main()
