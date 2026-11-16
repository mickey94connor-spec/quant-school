# quant-school: rules for any AI working in this folder

This is Michael's Quant School code. Read this before touching anything.

## The plan is fixed
Plan v3 (MNQ, Eastern time): the 8-9 AM move must agree with the 9:30-9:45 open; then one
pullback to the 20 EMA between 9:45 and 10:30; 1 contract, 25-point stop, 62-point target,
flat by 11:00. Chart: 9000-tick, VWAP (no bands), 20 EMA, cumulative delta. Nothing else.

- Do NOT change the rules, add indicators, add filters, or "improve" the strategy.
  Suggestions go in a note titled "Ideas for v4", never into v3.
- Do NOT create another journal, sheet, dashboard or vault structure. The only journals are
  `../miketrades/2 DAY TRADING/v3 Replay Log.md` and `v3 Lucid Log.md`.
- Do NOT write code that places, modifies or cancels orders. No trading bots until v3 has
  30+ rule-following trades logged with positive EV. Michael clicks every order himself.
- Do NOT rebuild this project. Fix the file that's broken.

## Files
- `replay_stats.py`  win rate / EV from a log. `Run v3 Stats.bat`, `Run Lucid Stats.bat`.
- `backtest_v3.py`   v3 on NinjaTrader 1-minute exports (`mnq_1min.txt`). Fake-data tested;
                     real test needs Michael's export (steps in the file).
- Obsidian vault: `../miketrades/`. Plan: `2 DAY TRADING/Plan v3.md`.

## Style
Plain words. Michael reads on his phone. Short answers, one next step at the end.
Pure Python (no pandas) so it runs anywhere. Say "fake data" when it was fake data.
