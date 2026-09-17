"""
Manim Community animation explaining EXISTS/NOT EXISTS, and how they
compose to implement universal quantification and logical implication
-- built to accompany IT5008 Tutorial 4 (Aggregate and Nested
Queries). Continues directly from tut_04.tex's 2(b) question
("students who borrowed all books by Adam Smith") and the two
diagrams already in that deck (tut_04_images/tut_04_01.pdf,
tut_04_02.pdf), which show the truth table and the annotated SQL. This
video fills in the mechanics those static images assume: what EXISTS
actually checks, why "for all" has to be rewritten as "no
counterexample", and why an implication is "no case where P holds and
Q fails" -- then walks concrete rows through the resulting
double-NOT-EXISTS query.

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_04_exists_implication.mp4 for the site.
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

# Curated to exactly the keywords used in this file's sql_block() calls,
# and verified pairwise substring-free (manim's Text raises "Ambiguous
# style" when two different t2c keys match overlapping characters on
# the same line).
SQL_KEYWORDS = ["SELECT", "FROM", "WHERE", "AND", "EXISTS", "NOT"]

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


def relation_table(data, col_labels, name=None, scale=0.55,
                    cell_highlight=None, row_highlight=None,
                    name_color=ACCENT):
    cell_highlight = cell_highlight or {}
    row_highlight = row_highlight or []
    table = Table(
        data,
        col_labels=[Text(c, font=MONO_FONT, weight=BOLD) for c in col_labels],
        include_outer_lines=True,
        line_config={"stroke_width": 1.5, "color": GREY_B},
    ).scale(scale)
    table.get_horizontal_lines().set_color(GREY_B)
    table.get_vertical_lines().set_color(GREY_B)
    for r in row_highlight:
        for c in range(1, len(col_labels) + 1):
            table.add_highlighted_cell((r + 2, c), color=ACCENT_SOFT)
    for (r, c), color in cell_highlight.items():
        table.add_highlighted_cell((r + 2, c + 1), color=color)
    group = table
    if name:
        cap = Text(name, font_size=26, color=name_color, weight=BOLD)
        cap.next_to(table, UP, buff=0.28)
        group = VGroup(table, cap)
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
        kicker = Text("IT5008 · Tutorial 4", font_size=28, color=ACCENT)
        title = Text("EXISTS, and Implementing P ⟹ Q", font_size=38,
                      weight=BOLD)
        sub = Text(
            "From subquery semantics to universal quantification",
            font_size=24, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- What EXISTS actually checks
# ---------------------------------------------------------------------------

class S02_WhatExistsMeans(WatermarkedScene):
    def construct(self):
        heading = Text("What EXISTS Actually Checks", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        loan_t = relation_table(
            [["111", "alice"], ["222", "alice"], ["111", "bob"]],
            ["book", "borrower"], name="loan", scale=0.55,
        )
        loan_t.next_to(heading, DOWN, buff=0.5)
        self.play(Create(loan_t))
        self.wait(0.5)

        q1 = sql_block([
            "EXISTS (SELECT * FROM loan",
            "  WHERE book='111' AND borrower='bob')",
        ], font_size=19)
        q1.next_to(loan_t, DOWN, buff=0.5).align_to(loan_t, LEFT)
        self.play(FadeIn(q1, shift=UP * 0.2))

        table = loan_t[0]
        match_box = SurroundingRectangle(
            VGroup(*[table.get_entries((4, c)) for c in range(1, 3)]),
            color=GOOD, buff=0.08,
        )
        self.play(Create(match_box))
        r1 = Text("→ TRUE  (row 3 matches)", font_size=20, color=GOOD,
                   weight=BOLD)
        r1.next_to(q1, RIGHT, buff=0.5)
        self.play(FadeIn(r1, shift=LEFT * 0.2))
        self.wait(1.2)
        self.play(FadeOut(q1), FadeOut(r1), FadeOut(match_box))

        q2 = sql_block([
            "EXISTS (SELECT * FROM loan",
            "  WHERE book='222' AND borrower='bob')",
        ], font_size=19)
        q2.next_to(loan_t, DOWN, buff=0.5).align_to(loan_t, LEFT)
        self.play(FadeIn(q2, shift=UP * 0.2))
        r2 = Text("→ FALSE  (no such row)", font_size=20, color=BAD,
                   weight=BOLD)
        r2.next_to(q2, RIGHT, buff=0.5)
        self.play(FadeIn(r2, shift=LEFT * 0.2))
        self.wait(1.2)

        note = Text(
            "EXISTS ignores the VALUES returned — only whether at least"
            " one row comes back.",
            font_size=20, color=HL,
        )
        note.next_to(q2, DOWN, buff=0.7).set_x(0)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1)

        note2 = Text(
            "NOT EXISTS is the mirror image: true exactly when ZERO rows"
            " come back.",
            font_size=20, color=WHITE,
        )
        note2.next_to(note, DOWN, buff=0.3).set_x(0)
        self.play(FadeIn(note2, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- SQL has no FORALL
# ---------------------------------------------------------------------------

class S03_NeedForAll(WatermarkedScene):
    def construct(self):
        heading = Text("SQL Gives Us ∃, Not ∀", font_size=34,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        goal = Text(
            '"Print students who borrowed ALL books by Adam Smith."',
            font_size=23, color=WHITE,
        )
        goal.next_to(heading, DOWN, buff=0.6)
        self.play(FadeIn(goal, shift=UP * 0.2))
        self.wait(0.6)

        forall = MathTex(r"\forall x,\ P(x)", font_size=44, color=ACCENT)
        forall.next_to(goal, DOWN, buff=0.6)
        self.play(Write(forall))
        self.wait(0.6)

        no_keyword = Text(
            "...but SQL has no FORALL keyword. Only EXISTS.",
            font_size=22, color=BAD,
        )
        no_keyword.next_to(forall, DOWN, buff=0.5)
        self.play(FadeIn(no_keyword, shift=UP * 0.2))
        self.wait(1)

        key = MathTex(
            r"\forall x,\ P(x)\ \equiv\ \neg\exists x,\ \neg P(x)",
            font_size=40, color=HL,
        )
        key.next_to(no_keyword, DOWN, buff=0.6)
        self.play(Write(key))
        self.wait(1)

        note = Text(
            '"true for every x" is the same as "no x is a counterexample"',
            font_size=21, color=WHITE,
        )
        note.next_to(key, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- The per-book condition is an implication
# ---------------------------------------------------------------------------

class S04_ImplicationSetup(WatermarkedScene):
    def construct(self):
        heading = Text("The Per-Book Condition Is an Implication",
                        font_size=30, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        defs = VGroup(
            Text('A(x):  "x is a book by Adam Smith"', font_size=23,
                 color=ACCENT),
            Text('B(x):  "student s borrowed x"', font_size=23,
                 color=ACCENT),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        defs.next_to(heading, DOWN, buff=0.6)
        self.play(FadeIn(defs, lag_ratio=0.2))
        self.wait(0.8)

        imp = MathTex(r"A(x) \rightarrow B(x)", font_size=44, color=HL)
        imp.next_to(defs, DOWN, buff=0.6)
        self.play(Write(imp))
        self.wait(0.6)

        note = Text(
            '"IF x is by Adam Smith, THEN s borrowed x" — vacuously'
            ' true when x isn\'t.',
            font_size=21, color=WHITE,
        )
        note.next_to(imp, DOWN, buff=0.45)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1)

        full = MathTex(
            r"\forall x,\ A(x) \rightarrow B(x)", font_size=36, color=ACCENT,
        )
        full.next_to(note, DOWN, buff=0.5)
        self.play(Write(full))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- Implication, rewritten without ->
# ---------------------------------------------------------------------------

class S05_ImplicationTruthTable(WatermarkedScene):
    def construct(self):
        heading = Text("Implication, Rewritten Without →",
                        font_size=32, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        identity = MathTex(
            r"P \rightarrow Q \ \equiv\ \neg P \lor Q\ \equiv\ "
            r"\neg(P \land \neg Q)",
            font_size=32, color=HL,
        )
        identity.next_to(heading, DOWN, buff=0.5)
        self.play(Write(identity))
        self.wait(0.8)

        data = [["F", "F", "T", "T"], ["F", "T", "T", "T"],
                ["T", "F", "F", "F"], ["T", "T", "T", "T"]]
        cols = ["P", "Q", "P→Q", "¬P∨Q"]
        table = relation_table(data, cols, scale=0.62)
        table.next_to(identity, DOWN, buff=0.5)
        self.play(Create(table))
        self.wait(0.6)

        t = table
        bad_row = SurroundingRectangle(
            VGroup(*[t.get_entries((4, c)) for c in range(1, 5)]),
            color=BAD, buff=0.08,
        )
        self.play(Create(bad_row))
        note = Text(
            "P→Q fails in exactly ONE case: P true, Q false — a"
            " counterexample.",
            font_size=21, color=BAD, weight=BOLD,
        )
        note.next_to(table, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- Putting it together: the double NOT EXISTS
# ---------------------------------------------------------------------------

class S06_DoubleNotExists(WatermarkedScene):
    def construct(self):
        heading = Text("Putting It Together", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        steps = VGroup(
            MathTex(r"\forall x,\ A(x) \rightarrow B(x)", font_size=26),
            MathTex(r"\equiv\ \neg\exists x,\ \neg(A(x) \rightarrow B(x))",
                     font_size=26, color=ACCENT),
            MathTex(r"\equiv\ \neg\exists x,\ \big(A(x) \land \neg B(x)\big)",
                     font_size=26, color=HL),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        steps.next_to(heading, DOWN, buff=0.35)
        for s in steps:
            self.play(Write(s))
            self.wait(0.3)
        self.wait(0.3)

        note = Text(
            '"no book x such that x is by Adam Smith AND s did NOT'
            ' borrow x"',
            font_size=18, color=WHITE,
        )
        note.next_to(steps, DOWN, buff=0.3)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(0.6)

        code = sql_block([
            "SELECT s.email, s.name",
            "FROM student s",
            "WHERE NOT EXISTS (",
            "  SELECT * FROM book b",
            "  WHERE b.authors = 'Adam Smith'",
            "    AND NOT EXISTS (",
            "      SELECT * FROM loan l",
            "      WHERE l.book = b.ISBN13 AND l.borrower = s.email",
            "    )",
            ");",
        ], font_size=15)
        code.next_to(note, DOWN, buff=0.25)
        self.play(FadeIn(code, shift=UP * 0.2))
        self.wait(0.6)

        outer = SurroundingRectangle(code[2], color=ACCENT, buff=0.05)
        inner = SurroundingRectangle(code[5], color=HL, buff=0.05)
        self.play(Create(outer))
        self.play(Create(inner))
        self.wait(0.4)

        legend = VGroup(
            Text("blue box = ¬∃x (...)", font_size=17, color=ACCENT,
                 weight=BOLD),
            Text("gold box = ¬B(x)", font_size=17, color=HL, weight=BOLD),
        ).arrange(RIGHT, buff=0.7)
        legend.next_to(code, DOWN, buff=0.22).set_x(0)
        self.play(FadeIn(legend, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 7 -- Walking through real data
# ---------------------------------------------------------------------------

class S07_Walkthrough(WatermarkedScene):
    def construct(self):
        heading = Text("Trying It on Real Data", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        book_t = relation_table(
            [["111", "Adam Smith"], ["222", "Adam Smith"],
             ["333", "Newton"]],
            ["book", "authors"], name="book", scale=0.42,
        )
        loan_t = relation_table(
            [["111", "alice"], ["222", "alice"], ["111", "bob"]],
            ["book", "borrower"], name="loan", scale=0.42,
        )
        both = VGroup(book_t, loan_t).arrange(RIGHT, buff=1.0)
        both.next_to(heading, DOWN, buff=0.35)
        self.play(Create(both))
        self.wait(0.5)

        # --- Alice ---
        alice_hdr = Text("alice", font_size=24, color=GOOD, weight=BOLD)
        alice_hdr.next_to(both, DOWN, buff=0.4).set_x(-3.3)
        self.play(FadeIn(alice_hdr))
        a1 = Text("111 (Adam Smith) — borrowed? yes → fine",
                   font_size=16, color=WHITE)
        a2 = Text("222 (Adam Smith) — borrowed? yes → fine",
                   font_size=16, color=WHITE)
        a_lines = VGroup(a1, a2).arrange(DOWN, buff=0.15)
        a_lines.next_to(alice_hdr, DOWN, buff=0.25).set_x(-3.3)
        self.play(FadeIn(a_lines, lag_ratio=0.3))
        a_res = Text("no counterexample → TRUE", font_size=18,
                      color=GOOD, weight=BOLD)
        a_res.next_to(a_lines, DOWN, buff=0.25).set_x(-3.3)
        self.play(FadeIn(a_res, shift=UP * 0.15))
        self.wait(0.8)

        # --- Bob ---
        bob_hdr = Text("bob", font_size=24, color=BAD, weight=BOLD)
        bob_hdr.next_to(both, DOWN, buff=0.4).set_x(3.3)
        self.play(FadeIn(bob_hdr))
        b1 = Text("111 (Adam Smith) — borrowed? yes → fine",
                   font_size=16, color=WHITE)
        b2 = Text("222 (Adam Smith) — borrowed? NO",
                   font_size=16, color=BAD, weight=BOLD)
        b3 = Text("→ COUNTEREXAMPLE!", font_size=16, color=BAD,
                   weight=BOLD)
        b_lines = VGroup(b1, b2, b3).arrange(DOWN, buff=0.15)
        b_lines.next_to(bob_hdr, DOWN, buff=0.25).set_x(3.3)
        self.play(FadeIn(b_lines, lag_ratio=0.3))
        b_res = Text("counterexample exists → FALSE", font_size=18,
                      color=BAD, weight=BOLD)
        b_res.next_to(b_lines, DOWN, buff=0.25).set_x(3.3)
        self.play(FadeIn(b_res, shift=UP * 0.15))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 8 -- Takeaways
# ---------------------------------------------------------------------------

class S08_Takeaway(WatermarkedScene):
    def construct(self):
        heading = Text("Takeaways", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        pts = [
            "EXISTS asks \"is there at least one row?\" NOT EXISTS asks"
            " \"are there none?\"",
            "∀x, P(x)  ≡  ¬∃x, ¬P(x)  —"
            " \"for all\" means \"no counterexample\".",
            "P→Q  ≡  ¬(P ∧ ¬Q)  — an implication"
            " is \"no case where P holds and Q fails\".",
            "Combine both, and \"borrowed all of an author's books\""
            " becomes exactly two\nnested NOT EXISTS — one for the"
            " ∀, one for the →.",
        ]
        colors = [WHITE, WHITE, WHITE, HL]
        bullets = VGroup(*[
            Text(p, font_size=21, color=c, line_spacing=1.3)
            for p, c in zip(pts, colors)
        ])
        bullets.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        bullets.next_to(heading, DOWN, buff=0.6)
        for b in bullets:
            self.play(FadeIn(b, shift=UP * 0.2))
            self.wait(0.5)
        self.wait(2.2)

        self.clear_scene()
