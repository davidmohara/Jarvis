import subprocess

tasks = [
    {
        "name": "Send fixed-bid proposal to Jerry Pender at Specialty Capital",
        "note": "From call 4/2. Fixed-bid 6-week discovery to reverse-engineer legacy PHP SaaS via Code Explorer. Deliverables: PRD, TRD, replatforming roadmap. Jerry Pender is Fractional CTO. Source: zzPlaud/Client/2026-04-02 Specialty Capital",
        "project": "Sales",
        "tag": "Email",
        "due": "Friday, April 10, 2026 at 5:00 PM",
    },
    {
        "name": "Send Birgo AI Deep Learning Program pricing to Melvin Novak",
        "note": "From Birgo call 4/6. Melvin asked for pamphlet and pricing on AI DLP. mnovak@birgo.com. Source: zzPlaud/Client/2026-04-06 Birgo",
        "project": "Sales",
        "tag": "Email",
        "due": "Friday, April 10, 2026 at 5:00 PM",
    },
    {
        "name": "Schedule follow-up with Melvin Novak and Tanya at Birgo re pilot",
        "note": "From Birgo call 4/6. Review their Claude pain point Google Doc, then schedule call with Melvin, Tanya, and a maintenance supervisor to scope pilot. Source: zzPlaud/Client/2026-04-06 Birgo",
        "project": "Sales",
        "tag": "Phone",
        "due": "Friday, April 10, 2026 at 5:00 PM",
    },
    {
        "name": "Add Andrew Reichert and Melvin Novak to Clay",
        "note": "From Birgo call 4/6. Andrew Reichert CEO areichert@birgo.com, Melvin Novak IT Manager mnovak@birgo.com. Source: zzPlaud/Client/2026-04-06 Birgo",
        "project": "Reachout",
        "tag": "Improving",
        "due": "Friday, April 10, 2026 at 5:00 PM",
    },
    {
        "name": "Ask Google VP if Live Nation falls under their purview",
        "note": "From One Texas campfire 4/2. Live Nation is a new 4M+ opportunity. Google was at AI workshop and interested in co-funding. Source: zzPlaud/Improving/2026-04-02 One Texas Key Account Review",
        "project": "Sales",
        "tag": "Improving",
        "due": "Friday, April 10, 2026 at 5:00 PM",
    },
    {
        "name": "Ask Thad Martin for insights and connections at McLane",
        "note": "From McLane weekly 4/2. New CIO Murat Chen is unresponsive. Thad may have useful intel or contacts. Source: zzPlaud/Improving/2026-04-02 McLane Account Strategy",
        "project": "Networking",
        "tag": "Improving",
        "due": "Friday, April 10, 2026 at 5:00 PM",
    },
    {
        "name": "Consider reaching out to Jack Nelson and Gavin Turner at Mainsail via YPO",
        "note": "From McLane weekly 4/2. Mainsail Partners PE play via Skimmer. Nick Olson heads their AI practice. David connected to Jack Nelson and Gavin Turner via YPO Gold Austin. Goal: partner to scale AI across 30+ portfolio companies. Source: zzPlaud/Improving/2026-04-02 McLane Account Strategy",
        "project": "Networking",
        "tag": "Improving",
        "due": "Friday, April 10, 2026 at 5:00 PM",
    },
]

results = []
for task in tasks:
    # Build script using heredoc-style — pass via stdin to avoid shell quoting entirely
    script = '''tell application "OmniFocus"
    tell default document
        set p to first flattened project whose name is "''' + task['project'] + '''"
        set tg to first flattened tag whose name is "''' + task['tag'] + '''"
        set t to make new task with properties {name:"''' + task['name'] + '''", note:"''' + task['note'] + '''", due date:date "''' + task['due'] + '''"} in p
        add tg to tags of t
        return "OK"
    end tell
end tell'''

    result = subprocess.run(
        ['osascript'],
        input=script,
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and 'OK' in result.stdout:
        results.append(f"OK  {task['name'][:65]}")
    else:
        results.append(f"ERR {task['name'][:65]}: {result.stderr.strip()[:100]}")

for r in results:
    print(r)
