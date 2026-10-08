import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libx import Exam  # noqa: F401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats_hard_common import start, load, shown, hidden_setup, PM

# Day 22 stats. Focus: metric-drop. Review: product-metrics.

SETUP = load("taxis", "taxis.csv", parse_dates=["pickup", "dropoff"]) + '''

# Q2: weekly sign-up funnel by traffic source (small made-up table)
signup = pd.DataFrame({
    "week":    ["prev", "prev", "prev", "last", "last", "last"],
    "source":  ["organic", "referral", "paid_social"] * 2,
    "visits":  [500_000, 100_000, 50_000, 505_000, 98_000, 250_000],
    "signups": [75_000, 20_000, 2_500, 75_245, 19_796, 12_000]})
print(signup)'''

HIDDEN = '''rng = np.random.default_rng(22)
_base = {("iOS", "US"): 400, ("Android", "US"): 300, ("Web", "US"): 100, ("iOS", "BR"): 80, ("Android", "BR"): 320,
         ("Web", "BR"): 40, ("iOS", "IN"): 30, ("Android", "IN"): 500, ("Web", "IN"): 30, ("iOS", "DE"): 90,
         ("Android", "DE"): 80, ("Web", "DE"): 30}
_mpd = {"iOS": 52, "Android": 46, "Web": 31}
_cf = {"US": 1.0, "BR": 1.12, "IN": 0.9, "DE": 0.95}
_rel, _hol = pd.Timestamp("2026-09-01"), pd.Timestamp("2026-09-07")
_rows = []
for _d in pd.date_range("2026-08-10", "2026-09-13"):
    _wk, _k = _d.dayofweek >= 5, (_d - _rel).days
    _s = 0 if _k < 0 else min(0.85, 0.10 + 0.15 * _k)
    for (_p, _c), _b in _base.items():
        _dau = _b * 1000 * (1.07 if _wk else 1) * (1.12 if (_c == "BR" and _d == _hol) else 1) * rng.normal(1, 0.015)
        _m = _mpd[_p] * _cf[_c] * (1.08 if _wk else 1) * (1.05 if (_c == "US" and _d == _hol) else 1)
        _parts = [("7.3", 1 - _s), ("7.4", _s)] if _p == "Android" else [("18.2" if _p == "iOS" else "web", 1)]
        for _v, _sh in _parts:
            if _sh <= 0:
                continue
            _u = round(_dau * _sh)
            _mm = _m * (0.70 if _v == "7.4" else 1) * rng.normal(1, 0.01)
            _rows.append((_d, _p, _c, _v, _u, round(_u * rng.normal(2.9, 0.03)), round(_u * _mm)))
daily = pd.DataFrame(_rows, columns=["date", "platform", "country", "app_version", "dau", "sessions", "watch_min"])
print(daily.shape)'''

DATA = """| Table | One row = | Columns | Real or simulated |
|---|---|---|---|
| `daily` | one day x platform x country x app version of a short-video app | `date`, `platform` (iOS/Android/Web), `country` (US/BR/IN/DE), `app_version`, `dau`, `sessions`, `watch_min` (total minutes) | made up, built by the hidden cell (do not read it) |
| `signup` | one week x traffic source | `week` (prev/last), `source`, `visits`, `signups` | made up |
| `taxis` | one NYC taxi ride, March 2019 | `pickup`, `fare`, `tip`, `payment` (cash/credit card) and more | real (seaborn-data) |

Notes: `daily` covers 2026-08-10 to 2026-09-13. Weekends have more users and more minutes per user.
2026-09-07 is Labor Day in the US and Independence Day in Brazil."""

ex = start(22, extra=SETUP, data_doc=DATA)
hidden_setup(ex, "Build the daily metrics table (hidden)", HIDDEN)

# ---------------------------------------------------------------- Q1 planted drop
q1 = '''o = daily.groupby("date")[["dau", "watch_min"]].sum()
o["mpd"] = o.watch_min / o.dau
print(o.mpd.loc["2026-08-29":"2026-09-04"].round(1).rename(lambda x: x.strftime("%b %d")).to_dict())  # start?

w0 = daily[daily.date.between("2026-08-24", "2026-08-30")]
w1 = daily[daily.date.between("2026-09-07", "2026-09-13")]
m0, m1 = w0.watch_min.sum() / w0.dau.sum(), w1.watch_min.sum() / w1.dau.sum()
print(f"minutes per DAU {m0:.2f} -> {m1:.2f} ({m1 / m0 - 1:+.1%}), change {m1 - m0:.2f}")

def cut(dim):
    a = w0.groupby(dim)[["dau", "watch_min"]].sum()
    b = w1.groupby(dim)[["dau", "watch_min"]].sum()
    t = pd.DataFrame({"mpd_before": a.watch_min / a.dau, "mpd_after": b.watch_min / b.dau,
                      "dau_share": b.dau / b.dau.sum()})
    t["change"] = t.mpd_after / t.mpd_before - 1
    t["contribution"] = b.watch_min / b.dau.sum() - a.watch_min / a.dau.sum()   # sums to the total change
    return t.round(3)

print(cut("platform"))
print(cut("country"))

andr = w1[w1.platform == "Android"].groupby(["country", "app_version"])[["dau", "watch_min"]].sum()
andr = (andr.watch_min / andr.dau).unstack()
print((andr["7.4"] / andr["7.3"]).round(2).to_dict())                    # same days, same country
s = daily[daily.platform == "Android"].groupby(["date", "app_version"]).dau.sum().unstack().fillna(0)
print((s["7.4"] / s.sum(axis=1)).loc["2026-08-31":"2026-09-07"].round(2).rename(lambda x: x.strftime("%b %d")).to_dict())
# {'Aug 29': 50.0, 'Aug 30': 49.7, 'Aug 31': 45.9, 'Sep 01': 45.3, 'Sep 02': 44.0, 'Sep 03': 42.8, 'Sep 04': 41.5}
# minutes per DAU 47.16 -> 40.16 (-14.8%), change -7.00
#           mpd_before  mpd_after  dau_share  change  contribution
# Android       46.399     34.695      0.599  -0.252        -6.983
# Web           31.755     32.142      0.101   0.012         0.065
# iOS           53.794     53.799      0.300   0.000        -0.081
# country change: BR -18.5%, DE -10.7%, IN -22.8%, US -8.9% (contributions -1.988, -0.501, -2.726, -1.784)
# {'BR': 0.7, 'DE': 0.7, 'IN': 0.7, 'US': 0.7}   7.4 / 7.3 minutes per DAU, same days
# 7.4 share of Android DAU: Aug 31 0.0, Sep 01 0.1, Sep 02 0.25, Sep 03 0.4, Sep 04 0.55, Sep 05 0.7, Sep 06 0.85, Sep 07 0.85'''
ex.q("Where did the watch time go?", minutes=9, kind="python",
     prompt="The weekly business review says: **watch minutes per daily active user fell about 15%** in the week "
            "of Sep 7 to 13 compared with the week of Aug 24 to 30. DAU itself looks flat. Nobody knows why. "
            "Use the `daily` table (made up, do not read the hidden cell).\n\n"
            "1. Find the day the decline starts and describe its shape (sudden step or gradual?).\n"
            "2. Cut the change by platform and by country. For each segment give the before and after minutes per "
            "DAU and its **contribution** to the total change, so that contributions add up to the total.\n"
            "3. Name the most likely cause and give one piece of evidence that is not just a before/after "
            "comparison.\n\n"
            "Example of a contribution: if Web has 10% of DAU at 30 min before and 10% at 27 min after, it "
            "contributes `0.10 x 27 - 0.10 x 30 = -0.3` minutes to the overall change." +
            PM + "what happened, how big it is, and what you recommend.",
     hint1="Signal: a ratio metric drops, nothing obvious launched, several dimensions available. Method: "
           "metric-drop investigation: timing, then segment cuts with a contribution table, then a within-time "
           "comparison that isolates the cause.",
     hint2="1. Daily `sum(watch_min) / sum(dau)`. 2. For each segment: `contribution = minutes_after / total_dau_after "
           "- minutes_before / total_dau_before`. 3. The platform cut finds the segment; the country cut is spread "
           "evenly (why?). 4. Inside Android, compare app versions on the same days; check how the version share "
           "grows day by day.",
     solution=q1,
     why="The fall from Aug 30 to Aug 31 is only the weekend ending (Monday Aug 31 at 45.9 matches Monday Aug 24 "
         "at 46.1). The real decline starts on Sep 1 and deepens day by day until about Sep 6, which looks like a staged rollout, "
         "not an outage (a step) or seasonality (it would repeat weekly). Android explains almost all of the "
         "-7.00 minutes (-6.98); iOS and Web are flat. Every country drops, in proportion to its Android share "
         "(India, mostly Android, drops most), so the country cut is a symptom, not the cause. Inside Android, "
         "version 7.4 users watch 30% less than 7.3 users **on the same days in the same countries**, and the 7.4 "
         "share grows from 10% on Sep 1 to 85%. The same-day comparison removes seasonality and holidays. "
         "Caveat: early updaters can differ from late ones, but a 30% gap that is identical in every country is far "
         "too large for that. Sessions per DAU did not move, so users still open the app: the loss is inside the "
         "session (for example autoplay or the feed loading), or it is a logging bug in 7.4. Next step: compare "
         "client-side minutes with server-side video delivery logs to tell a real behaviour change from broken "
         "logging." + PM + "\"Watch time per user is down 15% because of Android app 7.4, released on Sep 1: its "
         "users watch 30% less on the same days in every country, and DAU is unaffected; I recommend pausing the "
         "7.4 rollout and checking with engineering whether it is a playback bug or a logging bug.\"",
     mistakes="Comparing a week that contains the US/BR holiday with a normal week without saying so. Stopping at "
              "the country cut and blaming India. Averaging segment ratios instead of using sums. Comparing "
              "versions across different days (version adoption is confounded with time).",
     learn=["stats-metric-drop", "stats-ratio-metrics"])
shown(ex)

# ---------------------------------------------------------------- Q2 mix shift
q2 = '''p = signup.pivot(index="source", columns="week", values=["visits", "signups"])
r0 = p.signups.prev / p.visits.prev
r1 = p.signups["last"] / p.visits["last"]
w0 = p.visits.prev / p.visits.prev.sum()
w1 = p.visits["last"] / p.visits["last"].sum()
R0, R1 = (w0 * r0).sum(), (w1 * r1).sum()
mix = ((w1 - w0) * r0).sum()
rate = (w1 * (r1 - r0)).sum()
print(f"overall conversion {R0:.4f} -> {R1:.4f}, change {R1 - R0:+.4f}")
print(f"mix effect {mix:+.4f}, rate effect {rate:+.4f}, sum {mix + rate:+.4f}")
print(f"conversion with the old mix: {(w0 * r1).sum():.4f}")
print(f"signups {p.signups.prev.sum():,} -> {p.signups['last'].sum():,}")
from statsmodels.stats.proportion import proportions_ztest
z, pv = proportions_ztest([75_245, 75_000], [505_000, 500_000])
print(f"organic rate change: z = {z:.2f}, p = {pv:.2f}")
# overall conversion 0.1500 -> 0.1255, change -0.0245
# mix effect -0.0236, rate effect -0.0009, sum -0.0245
# conversion with the old mix: 0.1494
# signups 97,500 -> 107,041
# organic rate change: z = -1.41, p = 0.16'''
ex.q("Conversion fell, sign-ups rose", minutes=6, kind="python",
     prompt="The growth dashboard alarms: **visit-to-sign-up conversion fell from 15.0% to 12.5%** week over week. "
            "Use the `signup` table (made up).\n\n"
            "1. Split the change in overall conversion into a **mix effect** (the traffic moved between sources) "
            "and a **rate effect** (conversion changed inside sources). The two parts must add up to the total.\n"
            "2. What would conversion be last week with the previous week's traffic mix?\n"
            "3. Is the small change inside organic traffic real?" +
            PM + "should the growth team panic?",
     hint1="Signal: an overall rate falls while the segments have very different rates and sizes. Method: mix "
           "versus rate decomposition (the same arithmetic as Simpson's paradox).",
     hint2="1. `overall = sum(w_i * r_i)` with `w_i` = share of visits. 2. `mix = sum((w1 - w0) * r0)`, "
           "`rate = sum(w1 * (r1 - r0))`. 3. Standardised rate: `sum(w0 * r1)`. 4. Two-proportion z-test on "
           "organic.",
     solution=q2,
     why="Paid social traffic went from 50k to 250k visits and converts at about 5%, so it pulls the average down. "
         "Almost all of the 2.45-point drop (2.36 points) is mix; inside the sources conversion barely moved "
         "(rate effect -0.09 points; with the old mix, conversion would be 14.94% instead of 15.00%), and the organic change of 0.1 point is "
         "within noise (p = 0.16). Absolute sign-ups grew by about 9,500. This decomposition is exact because "
         "`R1 - R0 = sum(w1 r1) - sum(w0 r0)` splits into the two sums." + PM +
         "\"Conversion fell only because the new paid campaign brings many low-intent visitors; every channel "
         "converts as before and we got about 9,500 more sign-ups, so the real questions are the cost per sign-up "
         "of the campaign and whether those users stay.\"",
     mistakes="Reporting the drop without segmenting by source. Using a decomposition whose parts do not add up "
              "(mixing old and new weights in both terms). Celebrating more sign-ups without asking about their "
              "quality (retention) and cost.",
     learn=["stats-metric-drop", "stats-heterogeneous-effects"])
shown(ex)

# ---------------------------------------------------------------- Q3 framework case
ex.q("DAU fell 4% yesterday in one country", minutes=6, kind="text",
     prompt="You are the data scientist on call. Yesterday's DAU in Indonesia is **4% below** the same weekday "
            "last week; other countries look normal. The VP asks for an answer by noon.\n\n"
            "Describe your investigation **in order**, with the exact cuts and checks, how you separate a logging "
            "problem from a real change in behaviour, and when you would escalate. End with what you would send "
            "to the VP at noon if you still do not know the cause." +
            PM + "the noon message.",
     hint1="Signal: a sudden drop localized to one segment. Method: the metric-drop framework: is it real "
           "(data), is it expected (seasonality, events), where is it (segments), why (internal vs external), "
           "what to do.",
     hint2="1. Validate: pipeline delays, logging, definition changes. 2. Context: same weekday, holidays, last "
           "year. 3. Size: is 4% outside normal day-to-day noise? 4. Cuts: platform, app version, new vs returning, "
           "acquisition source, region inside the country, network/ISP. 5. Internal changes (releases, experiments, "
           "ranking) vs external (holiday, outage, competitor, regulation). 6. Escalate with what you know.",
     solution="""**1. Is the number real? (15 minutes)** Check data freshness (did all partitions land, late
events), whether the DAU definition or a filter changed, and compare with an independent source: server-side request
logs or backend session counts. If the client metric dropped but server requests did not, it is logging (for example
an app release that stopped sending an event). If both dropped, users really are missing.

**2. Is it unusual?** Compare with the normal spread of day-over-day changes for Indonesia (for example the last 8
same weekdays). 4% may be within noise for a small country; for a large one it is not. Check the calendar: a
public holiday, Ramadan timing, school exams, or a national event.

**3. Where is it?** Cut by platform and app version, new versus returning users, acquisition channel (a paused
paid campaign removes new users), region or city, mobile carrier or ISP, and device type. Use a contribution
table so the parts add up. A drop in one carrier points to a network or blocking issue; a drop in one app version
points to a release; a drop only in new users points to acquisition.

**4. Why?** Internal: releases, experiments ramped yesterday (check the experiment platform for anything targeting
Indonesia), ranking or notification changes, an expired push campaign. External: an outage of a payment or login
provider, government blocking, a competitor launch, a news event. Check correlated metrics: if sessions per user and
watch time per user are stable, the loss is in reach (users not arriving), not engagement.

**5. Escalate** immediately if there are signs of an outage, blocking, a logging break that feeds billing or
ads, or a release that can be rolled back. Otherwise keep monitoring and recheck after the next day's data.

**Noon message (cause still unknown):** what we know (size, start time, segments), what we ruled out, the current
leading hypothesis, the next check and when the next update comes.

**Say it to a PM:** "Indonesia DAU is 4% below last week, only on Android and starting yesterday 9:00 local time; the
data pipeline is complete and server logs show the same drop, so it is real; we have ruled out holidays and
experiments, we are checking with the Android team about yesterday's release and will update you at 3 pm.\"""",
     why="Examiners grade the order (validate data before hunting causes), the use of a baseline for noise, "
         "segment cuts that can distinguish hypotheses, and a calm, specific update to leadership.",
     learn=["stats-metric-drop", "stats-case-framework"])

# ---------------------------------------------------------------- Q4 review: metric definition (real data)
q4 = '''t = taxis[(taxis.pickup >= "2019-03-01") & taxis.payment.notna()].copy()
t["day"] = t.pickup.dt.date.astype(str)
card = t[t.payment == "credit card"]
d = pd.DataFrame({
    "rides": t.groupby("day").size(),
    "cash_share": t.groupby("day").payment.apply(lambda s: (s == "cash").mean()),
    "tip_rate_all": t.groupby("day").tip.sum() / t.groupby("day").fare.sum(),
    "tip_rate_card": card.groupby("day").tip.sum() / card.groupby("day").fare.sum()})
print(d.loc["2019-03-23"].round(3).to_dict())
print("lowest tip_rate_all:", d.tip_rate_all.idxmin(), "| rank of Mar 23 on tip_rate_card (1 = lowest):",
      int(d.tip_rate_card.rank().loc["2019-03-23"]), "of", len(d))
print(f"March mean card tip rate {d.tip_rate_card.mean():.3f}, sd {d.tip_rate_card.std():.3f}")
print("cash tips recorded:", t.loc[t.payment == "cash", "tip"].sum())
# {'rides': 207.0, 'cash_share': 0.357, 'tip_rate_all': 0.131, 'tip_rate_card': 0.2}
# lowest tip_rate_all: 2019-03-23 | rank of Mar 23 on tip_rate_card (1 = lowest): 11 of 31
# March mean card tip rate 0.204, sd 0.014
# cash tips recorded: 0.0'''
ex.q("The worst tipping day of the month?", minutes=5, kind="python", review=True,
     prompt="Real data: `taxis` (NYC rides, March 2019). An ops dashboard tracks **tip rate = total tips / total "
            "fares** per day. Saturday March 23 is the lowest day of the month and the ops lead wants to know why "
            "riders tipped less.\n\n"
            "1. Compute the daily tip rate as on the dashboard and the same rate for card payments only.\n"
            "2. Where does March 23 rank on the card-only rate? What happened that day?\n"
            "3. Propose a better metric definition." +
            PM + "explain why the dashboard was wrong.",
     hint1="Signal: a rate whose numerator is only observed for part of the denominator. Method: metric "
           "definition check (what is measured for whom), then a mix check.",
     hint2="1. Group by day: tips / fares for all rides and for card rides. 2. Look at the cash share that day. "
           "3. Check whether cash rides ever have a tip recorded.",
     solution=q4,
     why="Cash tips are never recorded (the sum is 0), so every cash ride adds fare to the denominator and nothing "
         "to the numerator. March 23 had one of the highest cash shares of the month (36%), which pulls the dashboard rate down to "
         "13.1%, while riders who paid by card tipped 20.0%, an ordinary day (rank 11 of 31, March mean 20.4%). The "
         "dashboard metric mixes behaviour with payment mix. Better: tip rate among card rides (where tips are "
         "observed), with the cash share shown as a separate metric." + PM +
         "\"Riders did not tip less on March 23: more of them paid cash, and cash tips are not recorded, so I "
         "suggest we report tip rate on card rides only (20% that day, a normal level).\"",
     mistakes="Treating unrecorded values as zeros. Looking for a behavioural story before checking the metric "
              "definition. Averaging per-ride tip percentages, which over-weights very short rides.",
     learn=["stats-product-metrics", "stats-metric-drop"])
shown(ex)

ex.save()
