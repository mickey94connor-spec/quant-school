# quant-school

My Quant School code. First build: **replay_stats.py**.

## What it does

Reads my v3 replay log in Obsidian (`miketrades/2 DAY TRADING/v3 Replay Log.md`) and prints my win rate, EV per trade and total points for plan v3.

## How to run it

Double-click **Run v3 Stats.bat** for replay days, or **Run Lucid Stats.bat** for Lucid trades.

If Windows says Python isn't found, install Python 3 from python.org (tick "Add python.exe to PATH"), then try again.

## Put it on GitHub (first push)

1. On github.com, make a new **empty** repo called `quant-school` (no README).
2. Right-click inside this folder → **Open Git Bash here** (on Windows 11 it's under "Show more options").
3. Run these one line at a time. The first two only need doing once, ever:

```
git config --global user.name "Your Name"
git config --global user.email "the-email-on-your-github"
git init
git add .
git commit -m "First build: v3 replay stats"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/quant-school.git
git push -u origin main
```

The first push opens a GitHub sign-in window. Sign in there yourself.
