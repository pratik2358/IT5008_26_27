"""
Manim Community animation explaining DEFERRABLE constraints and
concurrency -- built to accompany IT5008 Tutorial 2 (the NUN Book
Exchange schema). Continues directly from the DEFERRABLE constraints
video, reusing its own schema and BEGIN TRANSACTION; ... END
TRANSACTION; block style -- no new tables or constraints invented.

The scenario: only one copy of a book is left, owned by one student
(Dave). Two other students, Alice and Bob, walk up to two different
circulation desks on the same day, both wanting to borrow it. The key
observation is entirely schema-native: loan(borrower, owner, book,
copy, borrowed, returned) already has a natural primary key --
(owner, book, copy, borrowed), since a given physical copy can't be
marked "checked out starting today" twice. Crucially, `borrower` is
NOT part of that key -- so Alice's INSERT and Bob's INSERT carry an
IDENTICAL key regardless of who ends up borrowing it, simply because
there's only one copy, one owner, and one calendar day.

The technical story stays honest: the PRIMARY KEY (extended here to be
DEFERRABLE, exactly the way copy's FK to book already was) is what
actually prevents the double-booking, via Postgres's own row-level
locking -- that happens the same way whether the key is deferred or
not. DEFERRABLE only changes WHEN the losing desk is told: right after
its INSERT, or only at END TRANSACTION.

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
# and verified pairwise substring-free (manim's Text raises "Ambiguous
# style" when two different t2c keys match overlapping characters on
# the same line -- e.g. a short keyword that's a substring of a longer
# one used in that same line).
SQL_KEYWORDS = [
    "CREATE", "TABLE", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
    "DEFERRABLE",
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
    suffix, each its own Text mobject (deliberately no t2c keyword
    matching here, to sidestep the ambiguous-style class of bug for
    this free-form trace)."""
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
            "Two desks, one last copy — using the schema we already"
            " built",
            font_size=23, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- The schema we already have
# ---------------------------------------------------------------------------

class S02_TheSchema(WatermarkedScene):
    def construct(self):
        heading = Text("Recall: loan's own primary key", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        sql = sql_block([
            "CREATE TABLE loan (",
            "  borrower VARCHAR(256) REFERENCES student(email),",
            "  owner    VARCHAR(256), book CHAR(14), copy INT,",
            "  borrowed DATE, returned DATE,",
            "  PRIMARY KEY (owner, book, copy, borrowed)",
            "    DEFERRABLE,",
            "  FOREIGN KEY (owner, book, copy)",
            "    REFERENCES copy (owner, book, copy)",
            ");",
        ], font_size=19, highlight_lines={5: ["DEFERRABLE"]})
        sql.next_to(heading, DOWN, buff=0.5)
        self.play(FadeIn(sql, shift=UP * 0.2))
        self.wait(1)

        note = Text(
            "borrower is NOT part of the key — a copy's checkout on a"
            " given\nday only has room for one loan record, no matter"
            " who it is.",
            font_size=20, color=HL, line_spacing=1.3,
        )
        note.next_to(sql, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1)

        note2 = Text(
            "We're marking it DEFERRABLE here — same idea as copy's FK"
            " to book earlier.",
            font_size=19, color=GREY_B,
        )
        note2.next_to(note, DOWN, buff=0.35)
        self.play(FadeIn(note2, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- The collision is forced, not incidental
# ---------------------------------------------------------------------------

class S03_TheCollision(WatermarkedScene):
    def construct(self):
        heading = Text("One copy, one day — the collision is forced",
                        font_size=28, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        setup = Text(
            "Dave owns the ONLY copy of \"Intro DB\" (book 111, copy 1)."
            " Today, Alice\nwalks up to Desk A and Bob walks up to Desk"
            " B — both want to borrow it.",
            font_size=20, color=WHITE, line_spacing=1.3,
        )
        setup.next_to(heading, DOWN, buff=0.4)
        self.play(FadeIn(setup, shift=UP * 0.2))
        self.wait(1)

        alice_card = record_card("Desk A — Alice's INSERT", [
            ("owner", "dave@nun.edu"),
            ("book", "111"),
            ("copy", "1"),
            ("borrowed", "today"),
            ("borrower", "alice@nun.edu"),
        ], color=ACCENT, font_size=17)
        bob_card = record_card("Desk B — Bob's INSERT", [
            ("owner", "dave@nun.edu"),
            ("book", "111"),
            ("copy", "1"),
            ("borrowed", "today"),
            ("borrower", "bob@nun.edu"),
        ], color=BOB, font_size=17)
        cards = VGroup(alice_card, bob_card).arrange(RIGHT, buff=1.0)
        cards.next_to(setup, DOWN, buff=0.6)
        self.play(FadeIn(alice_card))
        self.play(FadeIn(bob_card))
        self.wait(0.6)

        for card, n in ((alice_card, 4), (bob_card, 4)):
            box = SurroundingRectangle(card[1][:n], color=HL, buff=0.08)
            self.play(Create(box))
        self.wait(0.4)

        note = Text(
            "Same key, four-for-four — only \"borrower\" differs, and"
            " it isn't part of the key.",
            font_size=20, color=HL, weight=BOLD,
        )
        note.next_to(cards, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- Race #1: checked immediately (the default)
# ---------------------------------------------------------------------------

class S04_RaceImmediate(WatermarkedScene):
    def construct(self):
        heading = Text("Race #1 — checked immediately (the default)",
                        font_size=27, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        rows = VGroup(
            trace_line("Alice ", "BEGIN TRANSACTION;", ACCENT),
            trace_line("Alice ", "INSERT INTO loan VALUES (...,'alice',...);",
                       ACCENT, "✓ not yet committed", GOOD),
            trace_line("Bob   ", "BEGIN TRANSACTION;", BOB),
            trace_line("Bob   ", "INSERT INTO loan VALUES (...,'bob',...);",
                       BOB, "blocks — same key as Alice's row", HL),
            trace_line("Alice ", "END TRANSACTION;", ACCENT,
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
# Scene 5 -- Race #2: the same key, deferred
# ---------------------------------------------------------------------------

class S05_RaceDeferred(WatermarkedScene):
    def construct(self):
        heading = Text("Race #2 — the SAME key, deferred", font_size=27,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        rows = VGroup(
            trace_line("Alice ", "BEGIN TRANSACTION;", ACCENT),
            trace_line("Alice ", "INSERT INTO loan VALUES (...,'alice',...);",
                       ACCENT, "✓ not yet committed", GOOD),
            trace_line("Bob   ", "BEGIN TRANSACTION;", BOB),
            trace_line("Bob   ", "SET CONSTRAINTS ALL DEFERRED;", BOB),
            trace_line("Bob   ", "INSERT INTO loan VALUES (...,'bob',...);",
                       BOB, "blocks — same key as Alice's row", HL),
            trace_line("Alice ", "END TRANSACTION;", ACCENT,
                       "✓ Alice gets the book", GOOD),
            trace_line("Bob   ", "  ⋮ unblocks now  ⋮", BOB,
                       "(no error yet — check deferred)", HL),
            trace_line("Bob   ", "-- prints a receipt, logs the"
                       " register...", BOB),
            trace_line("Bob   ", "END TRANSACTION;", BOB,
                       "✗ ERROR at commit — rolled back", BAD),
        )
        rows.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        rows.next_to(heading, DOWN, buff=0.45)
        for r in rows:
            self.play(FadeIn(r, shift=UP * 0.12))
            self.wait(0.4)
        self.wait(0.5)

        note = Text(
            "Bob's desk only finds out at END TRANSACTION — after"
            " printing a receipt that now has to be voided.",
            font_size=19, color=HL,
        )
        note.next_to(rows, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.4)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- What DEFERRABLE actually changed
# ---------------------------------------------------------------------------

class S06_WhatChanged(WatermarkedScene):
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
            "That's Postgres's ordinary primary-key locking, nothing to"
            " do with DEFERRABLE.",
            font_size=20, color=GREY_B,
        )
        b2 = Text(
            "DEFERRABLE only moves WHEN the loser is told: right after"
            " the INSERT, or only at END TRANSACTION.",
            font_size=21, color=WHITE,
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
# Scene 7 -- Takeaways
# ---------------------------------------------------------------------------

class S07_Takeaway(WatermarkedScene):
    def construct(self):
        heading = Text("Takeaways", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        pts = [
            "The mutual exclusion here comes straight from loan's own"
            " PRIMARY KEY — no new\ntable or constraint needed, just the"
            " key the design already implied.",
            "DEFERRABLE only changes WHEN that key is checked: right"
            " after the\nstatement, or at END TRANSACTION.",
            "For \"last copy, first come first served\", checking"
            " immediately usually serves\nusers better — fail fast,"
            " before doing more work.",
            "One honest limitation: (owner, book, copy, borrowed) also"
            " blocks a SECOND,\ngenuinely different loan of the same"
            " copy later the same day — a narrower\nedge case than the"
            " concurrent race, but worth knowing about.",
        ]
        colors = [WHITE, WHITE, WHITE, GREY_B]
        sizes = [20, 20, 20, 18]
        bullets = VGroup(*[
            Text(p, font_size=s, color=c, line_spacing=1.3)
            for p, c, s in zip(pts, colors, sizes)
        ])
        bullets.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        bullets.next_to(heading, DOWN, buff=0.6)
        for b in bullets:
            self.play(FadeIn(b, shift=UP * 0.2))
            self.wait(0.5)
        self.wait(2)

        self.clear_scene()
