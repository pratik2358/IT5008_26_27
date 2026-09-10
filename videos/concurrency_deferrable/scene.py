"""
Manim Community animation explaining DEFERRABLE constraints and
concurrency -- built to accompany IT5008 Tutorial 2 (the NUN Book
Exchange schema). Continues from the DEFERRABLE constraints video
(same book/copy scenario), now with a second, CONCURRENT transaction
in the picture: two students trying to borrow the last copy of a book
from two different circulation desks at once.

The honest technical story (verified against real PostgreSQL unique
-index behaviour) is NOT "DEFERRABLE prevents the race" -- a UNIQUE
constraint plus Postgres's own row-level locking is what prevents it,
whether the constraint is deferred or not. What DEFERRABLE changes is
*when* the losing desk finds out: immediately after its INSERT, or
only at COMMIT (possibly after doing more work in between). The video
also flags a genuine PostgreSQL limitation: the *general* version of
this constraint (allow re-lending a copy once it's returned) needs a
partial unique index, and partial indexes cannot be declared
DEFERRABLE -- which is why the demo scopes itself to a copy's very
first loan.

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_02_concurrency_deferrable.mp4 for the
site.
"""

from manim import *

# ---------------------------------------------------------------------------
# Shared styling (mirrors the other IT5008 videos for a consistent look)
# ---------------------------------------------------------------------------

ACCENT = "#6fa8dc"      # Alice / Desk A
BOB = "#e0a458"          # Bob / Desk B
ACCENT_SOFT = "#1b2733"
HL = "#f2c14e"
GOOD = "#89ca78"
BAD = "#e06c75"
MONO_FONT = "Menlo"

# Curated to exactly the keywords used in this file's sql_block() calls,
# and verified pairwise substring-free (a lesson learned the hard way in
# the other two Tutorial 2/3 videos: manim's Text raises "Ambiguous
# style" if two different t2c keys match overlapping characters -- e.g.
# a short keyword that happens to be a substring of a longer one used on
# the same line). Notably "ON" is deliberately absent: it's a substring
# of "CONSTRAINT" (as in "ADD C-ON-STRAINT"), which this file also uses.
SQL_KEYWORDS = [
    "ALTER", "TABLE", "ADD", "CONSTRAINT", "UNIQUE",
    "CREATE", "INDEX", "WHERE",
]

config.background_color = "#101114"


def sql_block(lines, font_size=20, highlight_lines=None):
    highlight_lines = highlight_lines or {}
    t2c = {kw: "#c586c0" for kw in SQL_KEYWORDS}
    rows = VGroup()
    for i, line in enumerate(lines):
        t2c_line = dict(t2c)
        if i in highlight_lines:
            for token in highlight_lines[i]:
                t2c_line[token] = HL
        txt = Text(line, font=MONO_FONT, font_size=font_size, t2c=t2c_line)
        rows.add(txt)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    return rows


def record_card(title, fields, color=ACCENT, font_size=17):
    lines = VGroup(*[
        Text(f"{k}: {v}", font=MONO_FONT, font_size=font_size, color=WHITE)
        for k, v in fields
    ])
    lines.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    box = SurroundingRectangle(lines, color=color, buff=0.22,
                                corner_radius=0.08, stroke_width=2.2)
    box.set_fill(ACCENT_SOFT, opacity=1)
    label = Text(title, font_size=17, color=color, weight=BOLD)
    label.next_to(box, UP, buff=0.12).align_to(box, LEFT)
    group = VGroup(box, lines, label)
    group.box = box
    return group


def trace_line(actor, text, color, status="", status_color=None,
                font_size=19):
    """One line of an interleaved concurrency trace: a colored actor
    tag, plain monospace SQL/action text, and an optional status
    suffix (e.g. a block/commit/error marker) in its own color. No
    t2c keyword matching here -- deliberately, to sidestep the
    ambiguous-style class of bug entirely for this free-form trace."""
    tag = Text(actor, font=MONO_FONT, font_size=font_size, color=color,
               weight=BOLD)
    body = Text(text, font=MONO_FONT, font_size=font_size, color=WHITE)
    parts = [tag, body]
    if status:
        parts.append(Text(status, font_size=font_size,
                           color=status_color or color, weight=BOLD))
    row = VGroup(*parts).arrange(RIGHT, buff=0.25)
    return row


class WatermarkedScene(Scene):
    def setup(self):
        super().setup()
        self.watermark = Text("Pratik Karmakar", font_size=16, color=GREY_C)
        self.watermark.set_opacity(0.45)
        self.watermark.to_corner(DR, buff=0.2)
        self.add(self.watermark)

    def clear_scene(self):
        self.play(*[
            FadeOut(m) for m in self.mobjects if m is not self.watermark
        ])


# ---------------------------------------------------------------------------
# Scene 1 -- Title
# ---------------------------------------------------------------------------

class S01_Title(WatermarkedScene):
    def construct(self):
        kicker = Text("IT5008 · Tutorial 2", font_size=28, color=ACCENT)
        title = Text("DEFERRABLE Constraints & Concurrency",
                      font_size=40, weight=BOLD)
        sub = Text(
            "Two desks, one last copy — who wins?",
            font_size=26, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- The scenario
# ---------------------------------------------------------------------------

class S02_Scenario(WatermarkedScene):
    def construct(self):
        heading = Text("The last copy", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        book_card = record_card("book 111", [
            ("title", "Intro DB"),
            ("copies left", "1"),
        ], color=HL)
        book_card.move_to(ORIGIN)
        self.play(FadeIn(book_card))
        self.wait(0.4)

        desk_a = Text("Desk A — Alice", font_size=24, color=ACCENT,
                       weight=BOLD)
        desk_b = Text("Desk B — Bob", font_size=24, color=BOB, weight=BOLD)
        desk_a.to_edge(LEFT, buff=1.3).align_to(book_card, UP)
        desk_b.to_edge(RIGHT, buff=1.3).align_to(book_card, UP)
        arrow_a = Arrow(desk_a.get_right(), book_card.get_left(),
                         color=ACCENT, buff=0.2, stroke_width=3)
        arrow_b = Arrow(desk_b.get_left(), book_card.get_right(),
                         color=BOB, buff=0.2, stroke_width=3)
        self.play(FadeIn(desk_a), FadeIn(desk_b))
        self.play(Create(arrow_a), Create(arrow_b))
        self.wait(0.8)

        caption = Text(
            "Both students reach for the SAME last copy,\n"
            "at the SAME moment, at two different desks.",
            font_size=24, color=WHITE, line_spacing=1.3,
        )
        caption.next_to(book_card, DOWN, buff=1.0)
        self.play(FadeIn(caption, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- The naive approach has a race condition
# ---------------------------------------------------------------------------

class S03_NaiveRace(WatermarkedScene):
    def construct(self):
        heading = Text("Why \"check, then insert\" isn't enough",
                        font_size=28, weight=BOLD, color=BAD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        rows = VGroup(
            trace_line("Alice ", "SELECT * FROM loan WHERE book=111 AND copy=1;",
                       ACCENT, "→ 0 rows: looks free", GOOD),
            trace_line("Bob   ", "SELECT * FROM loan WHERE book=111 AND copy=1;",
                       BOB, "→ 0 rows: looks free too!", GOOD),
            trace_line("Alice ", "INSERT INTO loan VALUES ('alice',...);",
                       ACCENT, "✓ inserted", GOOD),
            trace_line("Bob   ", "INSERT INTO loan VALUES ('bob',...);",
                       BOB, "✓ inserted  ← same copy!", BAD),
        )
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        rows.next_to(heading, DOWN, buff=0.7)
        for r in rows:
            self.play(FadeIn(r, shift=UP * 0.15))
            self.wait(0.5)
        self.wait(0.6)

        banner = Text(
            "Nothing in the schema stopped this — two students now both"
            " hold copy #1.",
            font_size=21, color=BAD, weight=BOLD,
        )
        banner.next_to(rows, DOWN, buff=0.55)
        self.play(FadeIn(banner, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- The constraint that actually prevents it
# ---------------------------------------------------------------------------

class S04_TheConstraint(WatermarkedScene):
    def construct(self):
        heading = Text("A UNIQUE constraint is the real guard",
                        font_size=30, weight=BOLD, color=GOOD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        sql = sql_block([
            "ALTER TABLE loan",
            "ADD CONSTRAINT one_loan_per_copy",
            "  UNIQUE (owner, book, copy)",
            "  DEFERRABLE;",
        ], font_size=24, highlight_lines={2: ["UNIQUE"]})
        sql.next_to(heading, DOWN, buff=0.7)
        self.play(FadeIn(sql, shift=UP * 0.2))
        self.wait(1)

        note = Text(
            "Scoped to this copy's very first loan ever — no earlier row"
            " to collide with.\nTwo INSERTs for the same (owner, book,"
            " copy) can't both succeed.",
            font_size=20, color=WHITE, line_spacing=1.3,
        )
        note.next_to(sql, DOWN, buff=0.6)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.4)

        note2 = Text(
            "Same idea as before — but now the second statement belongs"
            " to a DIFFERENT transaction.",
            font_size=20, color=HL,
        )
        note2.next_to(note, DOWN, buff=0.4)
        self.play(FadeIn(note2, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- Race #1: checked immediately
# ---------------------------------------------------------------------------

class S05_RaceImmediate(WatermarkedScene):
    def construct(self):
        heading = Text("Race #1 — checked immediately (the default)",
                        font_size=27, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        rows = VGroup(
            trace_line("Alice ", "BEGIN;", ACCENT),
            trace_line("Alice ", "INSERT INTO loan VALUES ('alice',...);",
                       ACCENT, "✓ not yet committed", GOOD),
            trace_line("Bob   ", "BEGIN;", BOB),
            trace_line("Bob   ", "INSERT INTO loan VALUES ('bob',...);",
                       BOB, "blocks — waits on Alice's row", HL),
            trace_line("Alice ", "COMMIT;", ACCENT,
                       "✓ Alice gets the book", GOOD),
            trace_line("Bob   ", "  ⋮ unblocks now  ⋮", BOB,
                       "✗ ERROR: duplicate key", BAD),
        )
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        rows.next_to(heading, DOWN, buff=0.55)
        for r in rows:
            self.play(FadeIn(r, shift=UP * 0.15))
            self.wait(0.5)
        self.wait(0.5)

        note = Text(
            "Bob's desk finds out immediately — right at the INSERT,"
            " before doing anything else.",
            font_size=21, color=HL,
        )
        note.next_to(rows, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- Race #2: the same constraint, deferred
# ---------------------------------------------------------------------------

class S06_RaceDeferred(WatermarkedScene):
    def construct(self):
        heading = Text("Race #2 — the SAME constraint, deferred",
                        font_size=27, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        rows = VGroup(
            trace_line("Alice ", "BEGIN;", ACCENT),
            trace_line("Alice ", "INSERT INTO loan VALUES ('alice',...);",
                       ACCENT, "✓ not yet committed", GOOD),
            trace_line("Bob   ", "BEGIN;", BOB),
            trace_line("Bob   ", "SET CONSTRAINTS one_loan_per_copy"
                       " DEFERRED;", BOB),
            trace_line("Bob   ", "INSERT INTO loan VALUES ('bob',...);",
                       BOB, "blocks — waits on Alice's row", HL),
            trace_line("Alice ", "COMMIT;", ACCENT,
                       "✓ Alice gets the book", GOOD),
            trace_line("Bob   ", "  ⋮ unblocks now  ⋮", BOB,
                       "(no error yet — check deferred)", HL),
            trace_line("Bob   ", "-- prints a receipt, logs the"
                       " register...", BOB),
            trace_line("Bob   ", "COMMIT;", BOB,
                       "✗ ERROR at commit — rolled back", BAD),
        )
        rows.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        rows.next_to(heading, DOWN, buff=0.45)
        for r in rows:
            self.play(FadeIn(r, shift=UP * 0.12))
            self.wait(0.4)
        self.wait(0.5)

        note = Text(
            "Bob's desk only finds out at COMMIT — after printing a"
            " receipt that now has to be voided.",
            font_size=19, color=HL,
        )
        note.next_to(rows, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.4)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 7 -- What DEFERRABLE actually changed here
# ---------------------------------------------------------------------------

class S07_WhatChanged(WatermarkedScene):
    def construct(self):
        heading = Text("What DEFERRABLE actually changed",
                        font_size=30, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        b1 = Text(
            "The BLOCK — Bob's INSERT, stalling on Alice's row, happens"
            " either way.",
            font_size=22, color=WHITE,
        )
        b1b = Text(
            "That's Postgres's ordinary unique-index locking, nothing to"
            " do with DEFERRABLE.",
            font_size=20, color=GREY_B,
        )
        b2 = Text(
            "DEFERRABLE only moves WHEN the loser is told: right after"
            " the INSERT, or only at COMMIT.",
            font_size=22, color=WHITE,
        )
        b3 = Text(
            "Same conflict, same eventual loser — just a different"
            " moment of finding out.",
            font_size=22, color=HL, weight=BOLD,
        )
        bullets = VGroup(
            VGroup(b1, b1b).arrange(DOWN, buff=0.1, aligned_edge=LEFT),
            b2, b3,
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        bullets.next_to(heading, DOWN, buff=0.7)
        for b in bullets:
            self.play(FadeIn(b, shift=UP * 0.2))
            self.wait(0.5)
        self.wait(1.8)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 8 -- The gotcha: re-lending after a return
# ---------------------------------------------------------------------------

class S08_Gotcha(WatermarkedScene):
    def construct(self):
        heading = Text("One more wrinkle: re-lending after a return",
                        font_size=27, weight=BOLD, color=BAD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        note = Text(
            "Our UNIQUE(owner, book, copy) only worked because this copy"
            " had\nnever been loaned before. Normally the SAME copy IS"
            " re-lent\nafter it comes back — so real systems guard with"
            " a PARTIAL\nunique index instead:",
            font_size=21, color=WHITE, line_spacing=1.3,
        )
        note.next_to(heading, DOWN, buff=0.55)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1)

        sql = sql_block([
            "CREATE UNIQUE INDEX one_open_loan",
            "  ON loan (owner, book, copy)",
            "  WHERE returned IS NULL;",
        ], font_size=22)
        sql.next_to(note, DOWN, buff=0.5)
        self.play(FadeIn(sql, shift=UP * 0.2))
        self.wait(1)

        gotcha = Text(
            "✗ Partial indexes cannot be declared DEFERRABLE in"
            " PostgreSQL.",
            font_size=22, color=BAD, weight=BOLD,
        )
        gotcha.next_to(sql, DOWN, buff=0.45)
        self.play(FadeIn(gotcha, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 9 -- Takeaways
# ---------------------------------------------------------------------------

class S09_Takeaway(WatermarkedScene):
    def construct(self):
        heading = Text("Takeaways", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        pts = [
            "Mutual exclusion between two desks comes from the"
            " UNIQUE/PRIMARY KEY constraint\nplus Postgres's row-level"
            " locking — that part is automatic, deferred or not.",
            "DEFERRABLE only changes WHEN the constraint is checked:"
            " right after the\nstatement, or at COMMIT.",
            "For \"last item, first come first served\" scenarios,"
            " IMMEDIATE usually serves\nusers better — fail fast, before"
            " doing more work.",
            "DEFERRED still shines for a single transaction's own"
            " multi-step consistency\n(our earlier own-book-and-copy"
            " example) — it isn't a concurrency-coordination\ntool by"
            " itself.",
        ]
        colors = [WHITE, WHITE, WHITE, HL]
        bullets = VGroup(*[
            Text(p, font_size=20, color=c, line_spacing=1.3)
            for p, c in zip(pts, colors)
        ])
        bullets.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        bullets.next_to(heading, DOWN, buff=0.6)
        for b in bullets:
            self.play(FadeIn(b, shift=UP * 0.2))
            self.wait(0.5)
        self.wait(2)

        self.clear_scene()
