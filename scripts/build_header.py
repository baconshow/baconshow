"""Generate the animated profile header, one SVG per GitHub theme.

Edit ERAS and run:  python scripts/build_header.py
"""
from html import escape
from itertools import groupby
from pathlib import Path

ERAS = [
    # (era, code, note)
    ("2012 · C++", 'std::cout << "hello\\n";', "where it started"),
    ("2012 · C#", 'Console.WriteLine("hello");', "then objects"),
    ("2013 · GeneXus", 'msg("hello")', "nobody said low-code yet"),
    ("2015 · Power BI", 'Hello = "hello"', "ten long years at a mining company"),
    ("2019 · SQL", "SELECT 'hello' FROM dual;", "moved to data for good"),
    ("2025 · Python", 'print("hello")', "less ceremony"),
    ("2026 · Spark", "spark.sql(\"select 'hello'\").show()", "same hello, more machines"),
    ("2026 · Claude Code", "&gt; say hello", "now it has a name: vibe coding"),
]

THEMES = {
    "dark": {"text": "#e6edf3", "dim": "#7d8590", "faint": "#30363d"},
    "light": {"text": "#1f2328", "dim": "#656d76", "faint": "#d0d7de"},
}

WIDTH, HEIGHT = 720, 190
MARGIN = 2
TRACK_Y = 172
SLOT_SECONDS = 3.2
LAST_SLOT_SECONDS = 6.0
FADE_SECONDS = 0.5
PIG_SCALE = 2
PIG_LIFT = 4
PIG_COLORS = {"p": "#e8a3ae", "d": "#c97f8c", "t": "#c97f8c", "n": "#c97f8c", "k": "#1f2328"}
FIRST_TICK_INSET = 16
LAST_TICK_INSET = 30


def pig_pixels(level):
    """Pixel grid of the pig at one era: longer, taller, shorter legs as it fattens."""
    last_level = len(ERAS) - 1
    body_w = 11 + 2 * level
    body_h = 4 + round(level * 5 / last_level)
    head_rise = 2 if level < 3 else 1 if level < 6 else 0
    legs = 2 if level < 5 else 1
    grid = [["."] * (body_w + 3) for _ in range(head_rise + body_h + legs)]

    for row in range(head_rise):
        for col in range(body_w - 3, body_w + 1):
            grid[row][col] = "p"
    for row in range(body_h):
        rounded = body_h >= 6 and row in (0, body_h - 1)
        for col in range(2 if rounded else 1, body_w + 1 - (1 if rounded and not head_rise else 0)):
            grid[head_rise + row][col] = "p"
    for row in range(head_rise + body_h, len(grid)):
        for col in (2, 3, body_w - 2, body_w - 1):
            grid[row][col] = "d"

    grid[1][body_w - 1] = "k"
    for row in (2, 3):
        grid[row][body_w + 1] = grid[row][body_w + 2] = "n"
    grid[head_rise + 1][0] = "t"
    return grid


def slot_starts():
    """Start time of each era, plus the total loop length, in seconds."""
    starts = [i * SLOT_SECONDS for i in range(len(ERAS))]
    return starts, starts[-1] + LAST_SLOT_SECONDS


def pct(seconds, total):
    return f"{seconds / total * 100:.2f}%"


def tick_x(index):
    first = MARGIN + FIRST_TICK_INSET
    last = WIDTH - MARGIN - LAST_TICK_INSET
    return first + (last - first) * index / (len(ERAS) - 1)


def frame_keyframes(index, starts, total):
    start = starts[index]
    end = starts[index + 1] if index + 1 < len(starts) else total
    return (
        f"@keyframes f{index}{{"
        f"0%,{pct(start, total)}{{opacity:0}}"
        f"{pct(start + FADE_SECONDS, total)},{pct(end - FADE_SECONDS, total)}{{opacity:1}}"
        f"{pct(end, total)},100%{{opacity:0}}}}"
    )


def tick_keyframes(index, starts, total):
    lit = starts[index] + FADE_SECONDS
    return (
        f"@keyframes t{index}{{"
        f"0%,{pct(starts[index], total)}{{opacity:0}}"
        f"{pct(lit, total)},{pct(total - FADE_SECONDS, total)}{{opacity:1}}"
        f"100%{{opacity:0}}}}"
    )


def sprite_keyframes(index, starts, total):
    """Hard swap, no fade: the pig gains weight mid-hop, at the start of each era."""
    start = starts[index]
    end = starts[index + 1] if index + 1 < len(starts) else total
    before = f"0%,{pct(start - 0.01, total)}{{opacity:0}}" if index else ""
    after = f"{pct(end, total)},100%{{opacity:0}}" if index + 1 < len(starts) else ""
    return (
        f"@keyframes s{index}{{{before}"
        f"{pct(start, total)},{pct(end - 0.01, total)}{{opacity:1}}{after}}}"
    )


def pig_keyframes(starts, total):
    steps = []
    for index, start in enumerate(starts):
        x = tick_x(index)
        steps.append(f"{pct(start + FADE_SECONDS, total)}{{transform:translate({x:.1f}px,0)}}")
        if index + 1 < len(starts):
            nxt = starts[index + 1]
            hop_x = (x + tick_x(index + 1)) / 2
            steps.append(f"{pct(nxt - 0.6, total)}{{transform:translate({x:.1f}px,0)}}")
            steps.append(f"{pct(nxt - 0.3, total)}{{transform:translate({hop_x:.1f}px,-5px)}}")
    last_x = tick_x(len(ERAS) - 1)
    first_x = tick_x(0)
    return (
        "@keyframes pig{"
        f"0%{{transform:translate({first_x:.1f}px,0)}}"
        + "".join(steps)
        + f"100%{{transform:translate({last_x:.1f}px,0)}}}}"
        "@keyframes pigfade{"
        f"0%{{opacity:0}}{pct(FADE_SECONDS, total)},{pct(total - FADE_SECONDS, total)}{{opacity:1}}"
        "100%{opacity:0}}"
    )


def sprite_svg(level):
    """One sprite, centered on x=0 and standing on y=0. Same-color runs share a rect."""
    grid = pig_pixels(level)
    left = -len(grid[0]) * PIG_SCALE / 2
    top = -len(grid) * PIG_SCALE
    rects = []
    for y, row in enumerate(grid):
        for cell, run in groupby(enumerate(row), key=lambda item: item[1]):
            run = list(run)
            if cell in PIG_COLORS:
                rects.append(
                    f'<rect x="{left + run[0][0] * PIG_SCALE:g}" y="{top + y * PIG_SCALE:g}" '
                    f'width="{len(run) * PIG_SCALE}" height="{PIG_SCALE}" fill="{PIG_COLORS[cell]}"/>'
                )
    last = " last" if level == len(ERAS) - 1 else ""
    return f'<g class="s{last}" style="animation-name:s{level}">{"".join(rects)}</g>'


def era_svg(index, era, code, note):
    # code is already escaped where it needs to be; the last era holds a literal &gt;
    safe_code = code if "&gt;" in code else escape(code, quote=False)
    last = " last" if index == len(ERAS) - 1 else ""
    return (
        f'<g class="f{last}" style="animation-name:f{index}">'
        f'<text x="{MARGIN}" y="70" class="mono small dim">{escape(era)}</text>'
        f'<text x="{MARGIN}" y="110" class="mono code">{safe_code}</text>'
        f'<text x="{MARGIN}" y="136" class="small dim">{escape(note)}</text>'
        "</g>"
    )


def tick_svg(index):
    x = tick_x(index)
    return (
        f'<circle cx="{x:.1f}" cy="{TRACK_Y}" r="2.5" class="tick"/>'
        f'<circle cx="{x:.1f}" cy="{TRACK_Y}" r="2.5" fill="{PIG_COLORS["p"]}" '
        f'class="lit" style="animation-name:t{index}"/>'
    )


def build(theme):
    starts, total = slot_starts()
    keyframes = "".join(frame_keyframes(i, starts, total) for i in range(len(ERAS)))
    keyframes += "".join(tick_keyframes(i, starts, total) for i in range(len(ERAS)))
    keyframes += "".join(sprite_keyframes(i, starts, total) for i in range(len(ERAS)))
    keyframes += pig_keyframes(starts, total)
    last_pig_x = tick_x(len(ERAS) - 1)
    style = f"""
      text{{font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;fill:{theme['text']}}}
      .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
      .small{{font-size:15px}}
      .dim{{fill:{theme['dim']}}}
      .code{{font-size:26px}}
      .tick{{fill:{theme['faint']}}}
      .f,.lit,.s{{opacity:0;animation-duration:{total:.1f}s;animation-iteration-count:infinite;animation-timing-function:linear}}
      .f.last,.lit,.s.last{{opacity:1}}
      .pig{{transform:translate({last_pig_x:.1f}px,0);animation:pig {total:.1f}s ease-in-out infinite}}
      .pigwrap{{animation:pigfade {total:.1f}s linear infinite}}
      {keyframes}
      @media (prefers-reduced-motion:reduce){{
        .f,.lit,.s,.pig,.pigwrap{{animation:none}}
      }}
    """
    eras = "".join(era_svg(i, *era) for i, era in enumerate(ERAS))
    ticks = "".join(tick_svg(i) for i in range(len(ERAS)))
    sprites = "".join(sprite_svg(i) for i in range(len(ERAS)))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="The same hello world written in each language of a career, from C to plain English">
  <style>{style}</style>
  <text x="{MARGIN}" y="26" class="mono small dim">baconshow</text>
  <text x="{WIDTH - MARGIN}" y="26" text-anchor="end" class="mono small dim">same line, every era</text>
  {eras}
  <line x1="{MARGIN}" y1="{TRACK_Y}" x2="{WIDTH - MARGIN}" y2="{TRACK_Y}" stroke="{theme['faint']}"/>
  {ticks}
  <g class="pigwrap"><g transform="translate(0 {TRACK_Y - PIG_LIFT})"><g class="pig">{sprites}</g></g></g>
</svg>
"""


def main():
    assets = Path(__file__).resolve().parent.parent / "assets"
    assets.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        (assets / f"header-{name}.svg").write_text(build(theme), encoding="utf-8")


if __name__ == "__main__":
    main()
