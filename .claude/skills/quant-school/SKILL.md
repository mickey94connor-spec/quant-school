---
name: quant-school
description: Michael's Plan v3 MNQ rules, log formats and file locations. Use for any v3 logging, stats, backtest or checklist task in this repo.
---
# Quant School skill

## Plan v3 (never change it here)
1. 8-9 AM move: Up or Down (close at 9:00 vs open at 8:00).
2. 9:30-9:45 open: Up or Down. Must agree with #1 or no trade today.
3. Entry: first pullback to the 20 EMA between 9:45 and 10:30, trend direction only.
4. 1 contract. Stop 25 points (100 ticks). Target 62 points (248 ticks). ATM: mikesclaudatm.
5. Flat by 11:00. Two losses = done for the day.
Break-even win rate = 25 / (25 + 62) = 29%. MNQ = $2 a point.

## Logs (markdown tables, one row per day, no-trade days included)
`../miketrades/2 DAY TRADING/v3 Replay Log.md` (replay) and `v3 Lucid Log.md` (Lucid).
Columns: Date | 8-9 move | Open 9:30-9:45 | Trade | Entry time | Result | Points | Rules followed | Notes
Result is Win, Loss, Flat11 or None. Points only for Flat11 or odd fills. Rules followed is Y or N.
Append rows above the blank last row. Never edit old rows without being asked.

## Stats
`python replay_stats.py` (replay log) or `python replay_stats.py "../miketrades/2 DAY TRADING/v3 Lucid Log.md"`.
Report: trades, wins/losses, win rate vs 29%, EV per trade in points and dollars, rules-followed count.
Under 30 trades: say the sample is too small. Never add lessons unless asked.

## Backtest
`python backtest_v3.py` reads `mnq_1min.txt` (NinjaTrader minute export). If the file is missing,
give the export steps from the top of backtest_v3.py. Never tune the rules to fit the data.
