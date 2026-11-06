"""Generate README.md. Edit PROJECTS and PATH_ERAS and run:  python scripts/build_readme.py"""
from pathlib import Path
from urllib.parse import quote

BADGE_COLOR = "30363d"

PROJECTS = [
    ("Cody", "https://github.com/baconshow/cody",
     "A desk mascot for Claude Code. It watches what Claude does, and you can talk to it.",
     ["Python", "JavaScript", "three.js"]),
    ("Voxel OS", None,
     "Your agents, projects and memory as a small block world. Coming soon.",
     ["Python", "JavaScript", "three.js"]),
    ("nexaya-os", "https://github.com/baconshow/nexaya-os",
     "Free core of an agentic system for Claude Code. Markdown routers, memory, routines. All local.",
     ["Python", "Markdown"]),
    ("text2sql-ptbr-lora", "https://github.com/baconshow/text2sql-ptbr-lora",
     "QLoRA fine-tune of a 0.5B model for Portuguese Text-to-SQL.",
     ["Python", "PyTorch", "PEFT"]),
]

PATH_ERAS = [
    ("2009", "Before any code. Project coordinator at a US consulting firm, in the room with "
             "city officials for a US$ 560M metro rail proposal.", []),
    ("2011", "Opened my first company.", []),
    ("2012", "C++ and C#. Memory by hand, then objects.", ["C++", "C#", ".NET"]),
    ("2013", "GeneXus. You described the model and it wrote the app. "
             "Nobody said low-code yet, let alone vibe code.", ["GeneXus"]),
    ("2015 to 2025", "Ten long years at a mining company. Ran the support team, then IT "
                     "governance, studied data on the side when Power BI showed up, and moved "
                     "there for good. When buying a tool was not an option, I built one.",
     ["Azure", "Power Automate", "SharePoint", "Power BI", "SQL"]),
    ("2025", "Back on my own. Data pipelines with an LLM in the middle, web and mobile for clients.",
     ["Python", "Selenium", "BigQuery", "Vertex AI", "Gemini", "GCP", "Firebase", "React",
      "Flutter", "Tailwind"]),
    ("2026", "Data platforms by day, agents by night.",
     ["Airflow", "Spark", "Impala", "Oracle", "DuckDB", "FastAPI", "Claude Code"]),
]


def badge(label):
    safe = quote(label.replace("-", "--").replace("_", "__"), safe="")
    return (f'<img src="https://img.shields.io/badge/{safe}-{BADGE_COLOR}?style=flat-square" '
            f'alt="{label}" height="20"/>')


def badges(labels):
    return " ".join(badge(label) for label in labels)


def project_block(name, url, text, stack):
    title = f"[{name}]({url})" if url else name
    return f"**{title}**<br/>\n{text}<br/>\n{badges(stack)}\n"


def era_block(when, text, stack):
    if not stack:
        return f"**{when}**<br/>\n{text}\n"
    return f"**{when}**<br/>\n{text}<br/>\n{badges(stack)}\n"


def main():
    parts = [
        '<picture>\n'
        '  <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg"/>\n'
        '  <source media="(prefers-color-scheme: light)" srcset="assets/header-light.svg"/>\n'
        '  <img src="assets/header-dark.svg" width="100%" '
        'alt="The same hello world written in each language of a career, from C to plain English"/>\n'
        '</picture>\n',
        "I make small tools, mostly around data and agents.\n",
        "### Now\n",
        *[project_block(*p) for p in PROJECTS],
        "### The long way here\n",
        *[era_block(*e) for e in PATH_ERAS],
        "---\n",
        "<sub>Best way to reach me is an issue on the repo in question.</sub>\n",
    ]
    readme = Path(__file__).resolve().parent.parent / "README.md"
    readme.write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    main()
