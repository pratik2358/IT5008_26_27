"""
Manim Community animation explaining DEFERRABLE constraints -- built to
accompany IT5008 Tutorial 2 (the NUN Book Exchange schema, intern's
alternative relational design).

Source material: tut_02.tex "What Does DEFERRABLE Mean?" / "A Motivating
Example" / "Transaction 1 -- ALL IMMEDIATE" / "Transaction 2 -- ALL
DEFERRED" frames, which in turn come straight from T02-comments.pdf
Q3(a)-(b): the book/copy foreign key, and the two transactions that
delete a book and its copy together.

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_02_deferrable_constraints.mp4 for the
site.
"""

from manim import *

# ---------------------------------------------------------------------------
# Shared styling (mirrors the other IT5008 videos for a consistent look)
# ---------------------------------------------------------------------------

ACCENT = "#6fa8dc"
ACCENT_SOFT = "#1b2733"
HL = "#f2c14e"
GOOD = "#89ca78"
BAD = "#e06c75"
MONO_FONT = "Menlo"

SQL_KEYWORDS = [
    "SELECT", "DISTINCT", "FROM", "WHERE", "AND",
    "BEGIN", "TRANSACTION", "END", "COMMIT", "ROLLBACK",
    "SET", "CONSTRAINTS", "ALL", "IMMEDIATE", "DEFERRED",
    "DELETE", "INSERT", "INTO", "VALUES",
    "CREATE", "TABLE", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
    "NOT", "NULL", "CHECK", "DEFERRABLE", "INITIALLY",
]

config.background_color = "#101114"


def sql_block(lines, font_size=22, highlight_lines=None):
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


def labelled_box(mobj, label, color=ACCENT):
    cap = Text(label, font_size=22, color=color, weight=BOLD)
    group = VGroup(cap, mobj).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    return group


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
        title = Text("DEFERRABLE Constraints", font_size=48, weight=BOLD)
        sub = Text(
            "When exactly does a constraint get checked?",
            font_size=26, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- The three qualifiers
# ---------------------------------------------------------------------------

class S02_ThreeQualifiers(WatermarkedScene):
    def construct(self):
        heading = Text("One question: WHEN is a constraint checked?",
                        font_size=30, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        q1 = Text(
            "immediately — right after the statement that could violate it",
            font_size=22, color=WHITE,
        )
        q2 = Text(
            "or deferred — postponed until COMMIT / END TRANSACTION",
            font_size=22, color=WHITE,
        )
        qs = VGroup(q1, q2).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        qs.next_to(heading, DOWN, buff=0.6)
        self.play(FadeIn(q1, shift=UP * 0.2))
        self.wait(0.6)
        self.play(FadeIn(q2, shift=UP * 0.2))
        self.wait(1.4)

        self.clear_scene()

        heading2 = Text("Three qualifiers", font_size=32, weight=BOLD)
        heading2.to_edge(UP)
        self.play(FadeIn(heading2, shift=UP * 0.2))

        def qual_box(label, desc, color):
            box = Rectangle(width=4.1, height=1.5, color=color,
                             stroke_width=2.5)
            tag = Text(label, font_size=22, weight=BOLD, color=color)
            d = Text(desc, font_size=17, color=GREY_B)
            content = VGroup(tag, d).arrange(DOWN, buff=0.18)
            content.move_to(box.get_center())
            return VGroup(box, content)

        b1 = qual_box("NOT DEFERRABLE", "the default — always\nchecked immediately",
                       GREY_B)
        b2 = qual_box("DEFERRABLE\nINITIALLY IMMEDIATE",
                       "deferrable, but checked\nimmediately unless told",
                       ACCENT)
        b3 = qual_box("DEFERRABLE\nINITIALLY DEFERRED",
                       "checked only at\nCOMMIT, unless told",
                       GOOD)
        row = VGroup(b1, b2, b3).arrange(RIGHT, buff=0.45)
        row.next_to(heading2, DOWN, buff=0.7)
        self.play(FadeIn(row, lag_ratio=0.2))
        self.wait(1.6)

        note1 = Text(
            "Only UNIQUE, PRIMARY KEY and FOREIGN KEY can take these"
            " qualifiers.",
            font_size=21, color=HL,
        )
        note2 = Text(
            "CHECK constraints cannot be deferred — always checked"
            " immediately.",
            font_size=21, color=HL,
        )
        notes = VGroup(note1, note2).arrange(DOWN, buff=0.18)
        notes.next_to(row, DOWN, buff=0.6)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- The setup: a book and its copy
# ---------------------------------------------------------------------------

class S03_TheSetup(WatermarkedScene):
    def construct(self):
        heading = Text("The setup", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        book = record_card("book", [
            ("title", "An Intro to DB Systems"),
            ("isbn13", "978-0321197849"),
        ], color=ACCENT)
        copy = record_card("copy", [
            ("owner", "tikki@gmail.com"),
            ("book", "978-0321197849"),
            ("copy", "1"),
        ], color=ACCENT)
        row = VGroup(book, copy).arrange(RIGHT, buff=1.8)
        row.next_to(heading, DOWN, buff=1.0)

        self.play(FadeIn(book))
        self.play(FadeIn(copy))

        arrow = Arrow(copy.box.get_top(), book.box.get_bottom(),
                       color=HL, stroke_width=3, buff=0.15,
                       max_tip_length_to_length_ratio=0.12)
        arrow_label = Text("references (FK)", font_size=18, color=HL)
        arrow_label.next_to(arrow.get_center(), DOWN, buff=0.2)
        self.play(Create(arrow), FadeIn(arrow_label))
        self.wait(0.8)

        cap = Text(
            "copy.book must match some book.isbn13 — that's the"
            " foreign key.",
            font_size=22, color=WHITE,
        )
        cap.next_to(row, DOWN, buff=0.9)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait(1.4)

        cap2 = Text(
            "Now suppose we delete both — the book, and this copy of"
            " it — in one transaction.",
            font_size=22, color=HL,
        )
        cap2.next_to(cap, DOWN, buff=0.4)
        self.play(FadeIn(cap2, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- Transaction 1: ALL IMMEDIATE (the default)
# ---------------------------------------------------------------------------

class S04_Immediate(WatermarkedScene):
    def construct(self):
        heading = Text("SET CONSTRAINTS ALL IMMEDIATE  (the default)",
                        font_size=25, weight=BOLD, color=BAD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        code = sql_block([
            "BEGIN TRANSACTION;",
            "  SET CONSTRAINTS ALL IMMEDIATE;",
            "  DELETE FROM book WHERE isbn13 = '...849';",
            "  DELETE FROM copy WHERE book = '...849';",
            "END TRANSACTION;",
        ], font_size=20, highlight_lines={1: ["IMMEDIATE"]})
        code.to_edge(LEFT, buff=1.0).shift(DOWN * 0.3)
        self.play(FadeIn(code, shift=RIGHT * 0.2))

        book = record_card("book", [("isbn13", "978-...849")], color=ACCENT,
                            font_size=16)
        copy = record_card("copy", [("book", "978-...849")], color=ACCENT,
                            font_size=16)
        cards = VGroup(book, copy).arrange(DOWN, buff=0.9)
        cards.to_edge(RIGHT, buff=1.2).shift(DOWN * 0.2)
        arrow = Arrow(copy.box.get_top(), book.box.get_bottom(), color=HL,
                       stroke_width=3, buff=0.15,
                       max_tip_length_to_length_ratio=0.15)
        self.play(FadeIn(cards), Create(arrow))
        self.wait(0.6)

        # Highlight and "run" line 2: DELETE FROM book.
        box2 = SurroundingRectangle(code[2], color=HL, buff=0.08)
        self.play(Create(box2))
        self.play(FadeOut(book), FadeOut(arrow))
        self.wait(0.3)

        cross = Text("✗", font_size=40, color=BAD, weight=BOLD)
        cross.next_to(copy, UP, buff=0.3)
        err = Text(
            "ERROR: update or delete on table \"book\" violates\n"
            "foreign key constraint on table \"copy\"",
            font_size=17, color=BAD, line_spacing=1.3,
        )
        err.next_to(cards, DOWN, buff=0.5).set_x(0)
        self.play(FadeIn(cross, scale=1.5), FadeIn(err, shift=UP * 0.2))
        self.wait(1)

        rollback = Text("ROLLBACK — nothing in this transaction sticks",
                         font_size=22, color=BAD, weight=BOLD)
        rollback.next_to(err, DOWN, buff=0.4).set_x(0)
        self.play(FadeIn(rollback, shift=UP * 0.2))
        self.wait(0.5)
        self.play(FadeIn(book))
        self.wait(1.6)

        note = Text(
            "Checked right away means right away — even mid-transaction.",
            font_size=20, color=BAD,
        )
        note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.8)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- Transaction 2: ALL DEFERRED
# ---------------------------------------------------------------------------

class S05_Deferred(WatermarkedScene):
    def construct(self):
        heading = Text("SET CONSTRAINTS ALL DEFERRED",
                        font_size=25, weight=BOLD, color=GOOD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        code = sql_block([
            "BEGIN TRANSACTION;",
            "  SET CONSTRAINTS ALL DEFERRED;",
            "  DELETE FROM book WHERE isbn13 = '...849';",
            "  DELETE FROM copy WHERE book = '...849';",
            "END TRANSACTION;",
        ], font_size=20, highlight_lines={1: ["DEFERRED"]})
        code.to_edge(LEFT, buff=1.0).shift(DOWN * 0.3)
        self.play(FadeIn(code, shift=RIGHT * 0.2))

        book = record_card("book", [("isbn13", "978-...849")], color=ACCENT,
                            font_size=16)
        copy = record_card("copy", [("book", "978-...849")], color=ACCENT,
                            font_size=16)
        cards = VGroup(book, copy).arrange(DOWN, buff=0.9)
        cards.to_edge(RIGHT, buff=1.2).shift(DOWN * 0.2)
        arrow = Arrow(copy.box.get_top(), book.box.get_bottom(), color=HL,
                       stroke_width=3, buff=0.15,
                       max_tip_length_to_length_ratio=0.15)
        self.play(FadeIn(cards), Create(arrow))
        self.wait(0.5)

        # Step 1: DELETE FROM book -- check postponed, no error.
        box2 = SurroundingRectangle(code[2], color=HL, buff=0.08)
        self.play(Create(box2))
        dashed_stub = DashedLine(
            copy.box.get_top(), copy.box.get_top() + UP * 1.0,
            color=BAD, stroke_width=3,
        )
        self.play(FadeOut(book), FadeOut(arrow), FadeIn(dashed_stub))
        dangle_box = SurroundingRectangle(copy, color=BAD, buff=0.12,
                                            corner_radius=0.08)
        pending = Text("(check deferred —\nnot verified yet)", font_size=16,
                        color=BAD, line_spacing=1.2)
        pending.next_to(dangle_box, LEFT, buff=0.3)
        self.play(FadeIn(pending), Create(dangle_box))
        self.wait(1.2)

        inconsistent = Text(
            "database is momentarily inconsistent",
            font_size=19, color=BAD, weight=BOLD,
        )
        inconsistent.next_to(cards, DOWN, buff=0.55)
        self.play(FadeIn(inconsistent, shift=UP * 0.2))
        self.wait(1.4)
        self.play(FadeOut(inconsistent))

        # Step 2: DELETE FROM copy -- the dangling row is gone too.
        box3 = SurroundingRectangle(code[3], color=HL, buff=0.08)
        self.play(Transform(box2, box3))
        self.play(FadeOut(copy), FadeOut(dashed_stub), FadeOut(pending),
                   FadeOut(dangle_box))
        self.wait(0.6)

        # Step 3: END TRANSACTION -- checked now, and it holds.
        box4 = SurroundingRectangle(code[4], color=HL, buff=0.08)
        self.play(Transform(box2, box4))
        check = Text("✓", font_size=40, color=GOOD, weight=BOLD)
        check.move_to(cards.get_center())
        commit = Text(
            "COMMIT — no copy references a missing book, so the\n"
            "FOREIGN KEY constraint holds at commit time",
            font_size=18, color=GOOD, line_spacing=1.3,
        )
        commit.next_to(cards, DOWN, buff=0.5).set_x(0)
        self.play(FadeIn(check, scale=1.5), FadeIn(commit, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- Peeking mid-transaction
# ---------------------------------------------------------------------------

class S06_Peek(WatermarkedScene):
    def construct(self):
        heading = Text("Peeking mid-transaction", font_size=32, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        sub = Text(
            "Copy line-by-line through Transaction 2, and pause right"
            " after the book delete:",
            font_size=21, color=GREY_B,
        )
        sub.next_to(heading, DOWN, buff=0.4)
        self.play(FadeIn(sub, shift=UP * 0.2))

        q1 = sql_block([
            "SELECT * FROM book",
            "WHERE isbn13 = '978-0321197849';",
        ], font_size=19)
        q2 = sql_block([
            "SELECT * FROM copy",
            "WHERE book = '978-0321197849';",
        ], font_size=19)
        p1 = labelled_box(q1, "Query book")
        p2 = labelled_box(q2, "Query copy")
        panels = VGroup(p1, p2).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        panels.next_to(sub, DOWN, buff=0.55)
        self.play(FadeIn(p1, shift=RIGHT * 0.2))
        self.play(FadeIn(p2, shift=LEFT * 0.2))
        self.wait(0.8)

        r1 = Text("0 rows", font_size=22, color=BAD, weight=BOLD)
        r1.next_to(p1, DOWN, buff=0.35)
        r2 = record_card("copy (1 row)", [
            ("owner", "tikki@gmail.com"),
            ("book", "978-...849  ← dangling!"),
        ], color=BAD, font_size=15)
        r2.next_to(p2, DOWN, buff=0.35)
        self.play(FadeIn(r1, shift=UP * 0.2))
        self.play(FadeIn(r2, shift=UP * 0.2))
        self.wait(1.4)

        note = Text(
            "The database really is inconsistent right now — PostgreSQL"
            " lets you\nsee it, because the FK check simply hasn't run yet.",
            font_size=20, color=HL, line_spacing=1.3,
        )
        note.next_to(VGroup(r1, r2), DOWN, buff=0.55).set_x(0)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.4)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 7 -- Takeaways
# ---------------------------------------------------------------------------

class S07_Takeaway(WatermarkedScene):
    def construct(self):
        heading = Text("Takeaways", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        b1 = Text(
            "Deferring changes WHEN a constraint is checked — never"
            " WHETHER.",
            font_size=23, color=WHITE,
        )
        b2 = Text(
            "It's useful exactly when a consistent end state can only be"
            " reached\nby passing through an inconsistent intermediate one.",
            font_size=23, color=WHITE, line_spacing=1.3,
        )
        b3 = Text(
            "CHECK constraints don't get this luxury — order those"
            " statements\n(or use temporary NULLs) instead.",
            font_size=23, color=WHITE, line_spacing=1.3,
        )
        b4 = Text(
            "Transaction control: BEGIN, COMMIT, SAVEPOINT s,"
            " ROLLBACK TO s.",
            font_size=23, color=WHITE,
        )
        bullets = VGroup(b1, b2, b3, b4).arrange(DOWN, buff=0.4,
                                                   aligned_edge=LEFT)
        bullets.next_to(heading, DOWN, buff=0.7)
        for b in bullets:
            self.play(FadeIn(b, shift=UP * 0.2))
            self.wait(0.5)
        self.wait(1.8)

        self.clear_scene()
