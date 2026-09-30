import os
import json
import urllib.request
from datetime import datetime, timezone, date

USERNAME = "Rashad-omran"
TOKEN = os.environ["PROFILE_TOKEN"]
OUTPUT = "assets/streak.svg"

now = datetime.now(timezone.utc)
year = now.year

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

variables = {
    "login": USERNAME,
    "from": f"{year}-01-01T00:00:00Z",
    "to": now.isoformat().replace("+00:00", "Z")
}

payload = json.dumps({
    "query": query,
    "variables": variables
}).encode()

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    method="POST",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Rashad-Profile-Metrics"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode())

if result.get("errors"):
    raise RuntimeError(json.dumps(result["errors"], indent=2))

calendar = (
    result["data"]["user"]
    ["contributionsCollection"]
    ["contributionCalendar"]
)

total = calendar["totalContributions"]

days = []

for week in calendar["weeks"]:
    for item in week["contributionDays"]:
        day_date = date.fromisoformat(item["date"])

        if day_date <= date.today():
            days.append({
                "date": day_date,
                "count": item["contributionCount"]
            })

days.sort(key=lambda x: x["date"])

# -------------------------
# LONGEST STREAK
# -------------------------

longest = 0
running = 0

for item in days:
    if item["count"] > 0:
        running += 1
        longest = max(longest, running)
    else:
        running = 0

# -------------------------
# CURRENT STREAK
# -------------------------

current = 0

if days:
    index = len(days) - 1

    # If today is still empty, calculate from yesterday.
    if days[index]["date"] == date.today() and days[index]["count"] == 0:
        index -= 1

    while index >= 0 and days[index]["count"] > 0:
        current += 1
        index -= 1

# -------------------------
# SVG
# -------------------------

svg = f"""
<svg
  width="900"
  height="220"
  viewBox="0 0 900 220"
  xmlns="http://www.w3.org/2000/svg"
  role="img"
  aria-label="GitHub contribution statistics"
>

<defs>

  <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#38BDF8"/>
    <stop offset="50%" stop-color="#6366F1"/>
    <stop offset="100%" stop-color="#7C3AED"/>
  </linearGradient>

</defs>

<style>

.title {{
  font: 600 18px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  fill: #F8FAFC;
}}

.number {{
  font: 700 36px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  fill: #F8FAFC;
}}

.current {{
  font: 700 36px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  fill: #818CF8;
}}

.label {{
  font: 500 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  fill: #94A3B8;
}}

.small {{
  font: 400 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  fill: #64748B;
}}

.divider {{
  stroke: #1E293B;
  stroke-width: 1;
}}

</style>

<!-- Background -->

<rect
  x="1"
  y="1"
  width="898"
  height="218"
  rx="12"
  fill="#020617"
  stroke="#1E293B"
/>

<!-- Accent -->

<rect
  x="0"
  y="0"
  width="900"
  height="3"
  rx="2"
  fill="url(#accent)"
/>

<!-- Title -->

<text
  x="450"
  y="39"
  text-anchor="middle"
  class="title"
>
Contribution Streak
</text>

<!-- Dividers -->

<line
  x1="300"
  y1="70"
  x2="300"
  y2="185"
  class="divider"
/>

<line
  x1="600"
  y1="70"
  x2="600"
  y2="185"
  class="divider"
/>

<!-- TOTAL -->

<text
  x="150"
  y="118"
  text-anchor="middle"
  class="number"
>
{total:,}
</text>

<text
  x="150"
  y="151"
  text-anchor="middle"
  class="label"
>
TOTAL CONTRIBUTIONS
</text>

<text
  x="150"
  y="176"
  text-anchor="middle"
  class="small"
>
{year}
</text>

<!-- CURRENT -->

<text
  x="450"
  y="118"
  text-anchor="middle"
  class="current"
>
{current}
</text>

<text
  x="450"
  y="151"
  text-anchor="middle"
  class="label"
>
CURRENT STREAK
</text>

<text
  x="450"
  y="176"
  text-anchor="middle"
  class="small"
>
days
</text>

<!-- LONGEST -->

<text
  x="750"
  y="118"
  text-anchor="middle"
  class="number"
>
{longest}
</text>

<text
  x="750"
  y="151"
  text-anchor="middle"
  class="label"
>
LONGEST STREAK
</text>

<text
  x="750"
  y="176"
  text-anchor="middle"
  class="small"
>
days
</text>

</svg>
"""

os.makedirs("assets", exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as file:
    file.write(svg)

print("=" * 50)
print("PROFILE CONTRIBUTION METRICS")
print("=" * 50)
print(f"Total Contributions : {total}")
print(f"Current Streak      : {current}")
print(f"Longest Streak      : {longest}")
print(f"Output              : {OUTPUT}")
print("=" * 50)
