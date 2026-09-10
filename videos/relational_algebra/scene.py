"""
Manim Community animation explaining the relational algebra behind
every answer in IT5008 Tutorial 3 (Simple Queries) -- the NUN Book
Exchange, in its Tutorial-2-refactored form (department split out,
copy.available dropped).

Each scene pairs a small, bespoke 2-4 row example (chosen just large
enough to make the operation's effect visible) with the SQL from
tut_03.tex and its relational-algebra reading, so the video reads as
"here is what the query is actually doing to the rows" rather than a
restatement of the SQL. Question 2(a)'s multi-way join keeps this
readable by joining loan+book concretely and then *stating* the two
further joins against student/department (already worked through
mechanically in question 2(a)'s own join step) rather than redrawing
six tables at once. Questions 2(c)/(d)/(e) share one scene, since they
are literally the same two selections combined with a different set
operator -- exactly the point tut_03.tex itself makes.

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_03_relational_algebra.mp4 for the site.
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

# Pruned to exactly the keywords used in this file's sql_block() calls,
# and verified pairwise substring-free (e.g. "AS" is deliberately absent
# because it's a substring of "ASC", which this file does use --
# overlapping t2c keys make manim's Text raise "Ambiguous style").
SQL_KEYWORDS = [
    "SELECT", "FROM", "DISTINCT",
    "COALESCE", "CURRENT_DATE",
    "ORDER", "BY", "ASC", "DESC",
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


def ra_expr(tex, font_size=32, color=WHITE):
    return MathTex(tex, font_size=font_size, color=color)


def labelled_box(mobj, label, color=ACCENT, font_size=20):
    cap = Text(label, font_size=font_size, color=color, weight=BOLD)
    group = VGroup(cap, mobj).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    return group


def relation_table(data, col_labels, name=None, scale=0.55,
                    row_highlight=None, cell_highlight=None,
                    name_color=ACCENT):
    row_highlight = row_highlight or []
    cell_highlight = cell_highlight or {}
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
        kicker = Text("IT5008 · Tutorial 3", font_size=28, color=ACCENT)
        title = Text("Relational Algebra Behind the Queries",
                      font_size=42, weight=BOLD)
        sub = Text(
            "Every answer, seen as algebra on small example tables",
            font_size=24, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- Operator legend
# ---------------------------------------------------------------------------

class S02_Legend(WatermarkedScene):
    def construct(self):
        heading = Text("The operators we'll use", font_size=32, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        rows_data = [
            (r"\sigma", "selection", "keep rows matching a condition", "WHERE"),
            (r"\pi", "projection", "keep only certain columns", "SELECT list"),
            (r"\delta", "dedup", "drop duplicate rows", "DISTINCT"),
            (r"\Join", "join", "stitch two relations on a condition", "JOIN ... ON"),
            (r"\cup\ \ \cap\ \ -", "set ops", "combine two same-shaped results",
             "UNION / INTERSECT / EXCEPT"),
        ]
        lines = VGroup()
        for sym, name, desc, sqlword in rows_data:
            symtex = MathTex(sym, font_size=34, color=HL)
            nm = Text(name, font_size=22, color=WHITE, weight=BOLD)
            ds = Text(desc, font_size=19, color=GREY_B)
            sq = Text(sqlword, font=MONO_FONT, font_size=18, color=ACCENT)
            row = VGroup(symtex, nm, ds, sq).arrange(RIGHT, buff=0.45)
            lines.add(row)
        lines.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        lines.next_to(heading, DOWN, buff=0.6)
        self.play(FadeIn(lines, lag_ratio=0.15))
        self.wait(2.4)

        note = Text(
            "Every \"simple query\" in this tutorial is just these,"
            " composed.",
            font_size=22, color=HL,
        )
        note.next_to(lines, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.8)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- 1(a) + 1(b): Projection, with and without duplicates
# ---------------------------------------------------------------------------

class S03_Projection(WatermarkedScene):
    def construct(self):
        heading = Text("1(a)/(b) — Projection  π", font_size=32, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        dept_cols = ["department", "faculty"]
        dept_rows = [
            ["CS", "Computing"],
            ["Math", "Science"],
            ["Physics", "Science"],
        ]
        dept_table = relation_table(dept_rows, dept_cols, name="department",
                                     scale=0.5)
        dept_table.to_edge(LEFT, buff=0.9).shift(UP * 0.6)
        self.play(Create(dept_table))

        ra1 = ra_expr(r"\pi_{\,\mathit{department}}(\text{department})",
                      font_size=24)
        sql1 = sql_block(["SELECT d.department", "FROM department d;"],
                          font_size=18)
        panel1 = VGroup(labelled_box(ra1, "1(a)"),
                         labelled_box(sql1, "SQL")).arrange(
                             DOWN, aligned_edge=LEFT, buff=0.3)
        panel1.next_to(dept_table, RIGHT, buff=0.8).align_to(dept_table, UP)
        self.play(FadeIn(panel1, shift=LEFT * 0.2))
        note1 = Text("department is a PRIMARY KEY — never duplicates",
                      font_size=18, color=GOOD)
        note1.next_to(panel1, DOWN, buff=0.3).align_to(panel1, LEFT)
        self.play(FadeIn(note1, shift=UP * 0.2))
        self.wait(1.4)
        self.play(FadeOut(panel1), FadeOut(note1), FadeOut(dept_table))

        stu_cols = ["email", "department"]
        stu_rows = [
            ["alice@nun.edu", "CS"],
            ["bob@nun.edu", "CS"],
            ["carol@nun.edu", "Math"],
        ]
        stu_table = relation_table(stu_rows, stu_cols, name="student",
                                    scale=0.5)
        stu_table.to_edge(LEFT, buff=0.9).shift(UP * 0.6)
        self.play(Create(stu_table))

        ra2 = ra_expr(r"\pi_{\,\mathit{department}}(\text{student})",
                      font_size=24)
        sql2 = sql_block(["SELECT DISTINCT s.department", "FROM student s;"],
                          font_size=18, highlight_lines={0: ["DISTINCT"]})
        panel2 = VGroup(labelled_box(ra2, "1(b)"),
                         labelled_box(sql2, "SQL")).arrange(
                             DOWN, aligned_edge=LEFT, buff=0.3)
        panel2.next_to(stu_table, RIGHT, buff=0.8).align_to(stu_table, UP)
        self.play(FadeIn(panel2, shift=LEFT * 0.2))
        self.wait(0.6)

        raw = Text("raw projection:  [CS, CS, Math]  ← CS repeats",
                    font_size=19, color=BAD)
        raw.next_to(panel2, DOWN, buff=0.35).align_to(panel2, LEFT)
        self.play(FadeIn(raw, shift=UP * 0.2))
        self.wait(1)

        dedup = ra_expr(r"\delta(\cdot) \;=\; \{\mathrm{CS},\ \mathrm{Math}\}",
                         font_size=24, color=GOOD)
        dedup.next_to(raw, DOWN, buff=0.3).align_to(panel2, LEFT)
        self.play(FadeIn(dedup, shift=UP * 0.2))
        self.wait(1.6)

        note2 = Text(
            "DISTINCT = π, then δ removes the repeats",
            font_size=19, color=HL,
        )
        note2.next_to(dedup, DOWN, buff=0.35).align_to(panel2, LEFT)
        self.play(FadeIn(note2, shift=UP * 0.2))
        self.wait(1.8)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- 1(c): Extended projection (a computed attribute)
# ---------------------------------------------------------------------------

class S04_ExtendedProjection(WatermarkedScene):
    def construct(self):
        heading = Text("1(c) — Extended Projection", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        loan_cols = ["book", "borrowed", "returned"]
        loan_rows = [
            ["111", "2022-01-01", "2022-01-10"],
            ["222", "2022-02-01", "NULL"],
        ]
        loan_table = relation_table(loan_rows, loan_cols, name="loan",
                                     scale=0.55)
        loan_table.to_edge(LEFT, buff=0.9).shift(UP * 0.6)
        self.play(Create(loan_table))

        ra_line1 = ra_expr(r"\pi_{\,\mathit{book},\ \mathrm{dur}}(\text{loan})",
                            font_size=20)
        ra_line2 = ra_expr(
            r"\mathrm{dur} = \mathrm{COALESCE}(\mathit{returned},"
            r"\mathrm{today}) - \mathit{borrowed} + 1",
            font_size=16, color=GREY_B,
        )
        ra = VGroup(ra_line1, ra_line2).arrange(DOWN, aligned_edge=LEFT,
                                                  buff=0.15)
        sql = sql_block([
            "SELECT l.book,",
            "  (COALESCE(l.returned, CURRENT_DATE)",
            "   - l.borrowed + 1) AS duration",
            "FROM loan l",
            "ORDER BY l.book ASC, duration DESC;",
        ], font_size=17)
        panel = VGroup(labelled_box(ra, "Relational Algebra"),
                        labelled_box(sql, "SQL")).arrange(
                            DOWN, aligned_edge=LEFT, buff=0.35)
        panel.next_to(loan_table, RIGHT, buff=0.7).align_to(loan_table, UP)
        self.play(FadeIn(panel, shift=LEFT * 0.2))
        self.wait(1)

        result_cols = ["book", "duration"]
        result_rows = [
            ["111", "10"],
            ["222", "(today − 2022-02-01 + 1)"],
        ]
        result_table = relation_table(result_rows, result_cols,
                                       name="result", scale=0.5,
                                       name_color=GOOD)
        result_table.next_to(loan_table, DOWN, buff=0.4).align_to(
            loan_table, LEFT)
        self.play(Create(result_table))
        self.wait(0.8)

        note = Text(
            "A row without a return date isn't excluded —\n"
            "it's treated as still running, until today.",
            font_size=19, color=HL, line_spacing=1.3,
        )
        note.next_to(result_table, RIGHT, buff=0.6)
        self.play(FadeIn(note, shift=LEFT * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- 2(a): Join, then selection, then projection
# ---------------------------------------------------------------------------

class S05_JoinSelectProject(WatermarkedScene):
    def construct(self):
        heading = Text("2(a) — Join, then σ, then π", font_size=30,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        loan_cols = ["owner", "borrower", "book", "returned"]
        loan_rows = [
            ["alice", "bob", "111", "NULL"],
            ["alice", "carol", "222", "NULL"],
            ["bob", "alice", "111", "2022-01-01"],
        ]
        book_cols = ["book", "title", "publisher"]
        book_rows = [
            ["111", "Intro DB", "Wiley"],
            ["222", "Algebra", "Pearson"],
        ]
        loan_t = relation_table(loan_rows, loan_cols, name="loan", scale=0.42)
        book_t = relation_table(book_rows, book_cols, name="book", scale=0.42)
        both = VGroup(loan_t, book_t).arrange(RIGHT, buff=0.8)
        both.next_to(heading, DOWN, buff=0.35)
        self.play(Create(both))

        step1 = ra_expr(r"\text{loan} \Join_{\,\mathit{book}}\, \text{book}",
                         font_size=24)
        step1.next_to(both, DOWN, buff=0.3)
        self.play(Write(step1))
        self.wait(0.6)

        step2 = ra_expr(
            r"\sigma_{\,\mathit{publisher}=\mathrm{Wiley}\ \land\ "
            r"\mathit{returned}\ \text{IS NULL}}(\cdot)",
            font_size=20, color=HL,
        )
        step2.next_to(step1, DOWN, buff=0.3)
        self.play(Write(step2))
        self.wait(0.6)

        keep_note = Text(
            "Only row 1 survives: book 111 is Wiley, and still unreturned",
            font_size=18, color=GOOD,
        )
        keep_note.next_to(step2, DOWN, buff=0.3)
        self.play(FadeIn(keep_note, shift=UP * 0.2))
        self.wait(1.4)

        self.clear_scene()

        heading2 = Text("...then join twice more, for names and faculties",
                         font_size=26, weight=BOLD)
        heading2.to_edge(UP)
        self.play(FadeIn(heading2, shift=UP * 0.2))

        note = Text(
            "Same idea, twice: join student ⋈ department once for the\n"
            "owner (alice), once more for the borrower (bob) — exactly\n"
            "the join step we already walked through above.",
            font_size=21, color=WHITE, line_spacing=1.35,
        )
        note.next_to(heading2, DOWN, buff=0.6)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.6)

        result_cols = ["title", "ownerName", "ownerFaculty",
                       "borrowerName", "borrowerFaculty"]
        result_rows = [["Intro DB", "Alice", "Computing", "Bob", "Computing"]]
        result_t = relation_table(result_rows, result_cols, name="result",
                                   scale=0.48, name_color=GOOD)
        result_t.next_to(note, DOWN, buff=0.6)
        self.play(Create(result_t))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- 2(b): A selection with a different comparison
# ---------------------------------------------------------------------------

class S06_IntegrityCheck(WatermarkedScene):
    def construct(self):
        heading = Text("2(b) — Same σ, a stricter condition", font_size=28,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        stu_cols = ["email", "year"]
        stu_rows = [
            ["alice@nun.edu", "2021-08-15"],
            ["bob@nun.edu", "2020-01-01"],
        ]
        loan_cols = ["owner", "borrower", "borrowed"]
        loan_rows = [
            ["bob", "alice", "2021-01-01"],
            ["alice", "bob", "2022-06-01"],
        ]
        stu_t = relation_table(stu_rows, stu_cols, name="student", scale=0.48)
        loan_t = relation_table(loan_rows, loan_cols, name="loan", scale=0.48)
        both = VGroup(stu_t, loan_t).arrange(RIGHT, buff=1.0)
        both.next_to(heading, DOWN, buff=0.4)
        self.play(Create(both))

        ra = ra_expr(
            r"\sigma_{\,(\mathit{email}=\mathit{borrower}\ \lor\ "
            r"\mathit{email}=\mathit{owner})\ \land\ "
            r"\mathit{borrowed}\,<\,\mathit{year}}(\text{student}"
            r"\times\text{loan})",
            font_size=18,
        )
        ra.next_to(both, DOWN, buff=0.35)
        self.play(Write(ra))
        self.wait(0.8)

        note1 = Text(
            "Row 1: alice borrowed 2021-01-01, but only joined 2021-08-15"
            " — a violation.",
            font_size=17, color=BAD,
        )
        note2 = Text(
            "Row 2: bob lent 2022-06-01, long after he joined in 2020"
            " — fine.",
            font_size=17, color=GOOD,
        )
        notes = VGroup(note1, note2).arrange(DOWN, buff=0.15)
        notes.next_to(ra, DOWN, buff=0.35)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(1.6)

        result = Text('result = { alice@nun.edu }  — should normally be'
                       ' empty', font_size=20, color=HL)
        result.next_to(notes, DOWN, buff=0.4)
        self.play(FadeIn(result, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 7 -- Setup for 2(c)/(d)/(e): two selections, B and O
# ---------------------------------------------------------------------------

class S07_SetupBO(WatermarkedScene):
    def construct(self):
        heading = Text("2(c)/(d)/(e) all start from the same two sets",
                        font_size=27, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        b_ra = ra_expr(
            r"B = \pi_{\mathit{email}}\big(\sigma_{\,\mathit{email}="
            r"\mathit{borrower}\ \land\ \mathit{borrowed}=\mathit{year}}"
            r"(\text{student}\times\text{loan})\big)",
            font_size=19,
        )
        o_ra = ra_expr(
            r"O = \pi_{\mathit{email}}\big(\sigma_{\,\mathit{email}="
            r"\mathit{owner}\ \land\ \mathit{borrowed}=\mathit{year}}"
            r"(\text{student}\times\text{loan})\big)",
            font_size=19,
        )
        b_cap = Text("B — borrowed on their own join day", font_size=18,
                      color=ACCENT)
        o_cap = Text("O — lent on their own join day", font_size=18,
                      color=ACCENT)
        b_group = VGroup(b_cap, b_ra).arrange(DOWN, buff=0.15,
                                                aligned_edge=LEFT)
        o_group = VGroup(o_cap, o_ra).arrange(DOWN, buff=0.15,
                                                aligned_edge=LEFT)
        exprs = VGroup(b_group, o_group).arrange(DOWN, buff=0.4,
                                                    aligned_edge=LEFT)
        exprs.next_to(heading, DOWN, buff=0.5)
        self.play(FadeIn(b_group, shift=UP * 0.2))
        self.wait(0.5)
        self.play(FadeIn(o_group, shift=UP * 0.2))
        self.wait(1)

        b_t = relation_table([["alice"], ["bob"]], ["email"], name="B",
                              scale=0.5, name_color=HL)
        o_t = relation_table([["alice"], ["carol"]], ["email"], name="O",
                              scale=0.5, name_color=HL)
        tables = VGroup(b_t, o_t).arrange(RIGHT, buff=1.6)
        tables.next_to(exprs, DOWN, buff=0.55)
        self.play(Create(tables))
        self.wait(1)

        note = Text(
            "alice shows up in both — she borrowed AND lent on her own"
            " join day",
            font_size=19, color=HL,
        )
        note.next_to(tables, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 8 -- 2(c)/(d)/(e): union, intersect, except of B and O
# ---------------------------------------------------------------------------

class S08_SetOps(WatermarkedScene):
    def construct(self):
        heading = Text("2(c)/(d)/(e) — Combine B and O", font_size=30,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        b_t = relation_table([["alice"], ["bob"]], ["email"], name="B",
                              scale=0.45, name_color=ACCENT)
        o_t = relation_table([["alice"], ["carol"]], ["email"], name="O",
                              scale=0.45, name_color=ACCENT)
        both = VGroup(b_t, o_t).arrange(RIGHT, buff=1.2)
        both.next_to(heading, DOWN, buff=0.4)
        self.play(Create(both))
        self.wait(0.5)

        def combo(sym_tex, op_sql, question, result_str, color):
            sym = ra_expr(sym_tex, font_size=26, color=color)
            sqlw = Text(op_sql, font=MONO_FONT, font_size=17, color=color)
            q = Text(question, font_size=17, color=GREY_B)
            res = Text(result_str, font_size=19, color=color, weight=BOLD)
            group = VGroup(sym, sqlw, q, res).arrange(DOWN, buff=0.12)
            box = SurroundingRectangle(group, color=color, buff=0.2,
                                        corner_radius=0.08, stroke_width=2)
            return VGroup(box, group)

        c_box = combo(r"B \cup O", "UNION", "2(c) or",
                      "{alice, bob, carol}", ACCENT)
        d_box = combo(r"B \cap O", "INTERSECT", "2(d) and",
                      "{alice}", GOOD)
        e_box = combo(r"B - O", "EXCEPT", "2(e) but not",
                      "{bob}", BAD)
        row = VGroup(c_box, d_box, e_box).arrange(RIGHT, buff=0.55)
        row.next_to(both, DOWN, buff=0.55)
        self.play(FadeIn(row, lag_ratio=0.2))
        self.wait(2.6)

        note = Text(
            "Same two sets, three different set operators — three"
            " different questions.",
            font_size=20, color=HL,
        )
        note.next_to(row, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 9 -- 2(f): Set difference across two relations
# ---------------------------------------------------------------------------

class S09_NeverBorrowed(WatermarkedScene):
    def construct(self):
        heading = Text("2(f) — Set Difference Across Relations",
                        font_size=28, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        book_t = relation_table(
            [["111", "Intro DB"], ["222", "Algebra"], ["333", "Calculus"]],
            ["ISBN13", "title"], name="book", scale=0.48,
        )
        loan_t = relation_table(
            [["111"], ["222"]], ["book"], name="loan", scale=0.48,
        )
        both = VGroup(book_t, loan_t).arrange(RIGHT, buff=1.0)
        both.next_to(heading, DOWN, buff=0.4)
        self.play(Create(both))
        self.wait(0.5)

        ra = ra_expr(
            r"\pi_{\,\mathit{ISBN13}}(\text{book}) \;-\; "
            r"\pi_{\,\mathit{book}}(\text{loan})",
            font_size=26,
        )
        ra.next_to(both, DOWN, buff=0.4)
        self.play(Write(ra))
        self.wait(0.8)

        calc = ra_expr(
            r"\{111,222,333\} - \{111,222\} = \{333\}",
            font_size=24, color=HL,
        )
        calc.next_to(ra, DOWN, buff=0.35)
        self.play(FadeIn(calc, shift=UP * 0.2))
        self.wait(1.2)

        note = Text(
            "Equivalently: LEFT OUTER JOIN book with loan, then keep\n"
            "only the rows where the join found nothing (l.book IS NULL).",
            font_size=19, color=GREY_B, line_spacing=1.3,
        )
        note.next_to(calc, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 10 -- Takeaways: SQL <-> RA cheat sheet
# ---------------------------------------------------------------------------

class S10_Takeaway(WatermarkedScene):
    def construct(self):
        heading = Text("SQL, read as algebra", font_size=32, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        pairs = [
            ("WHERE ...", r"\sigma"),
            ("SELECT col1, col2", r"\pi"),
            ("SELECT DISTINCT", r"\pi \text{ then } \delta"),
            ("... JOIN ... ON ...", r"\Join"),
            ("UNION / INTERSECT / EXCEPT", r"\cup\ /\ \cap\ /\ -"),
        ]
        rows = VGroup()
        for sqlw, ratex in pairs:
            sq = Text(sqlw, font=MONO_FONT, font_size=22, color=ACCENT)
            arrow = MathTex(r"\rightarrow", font_size=24, color=GREY_B)
            ra = MathTex(ratex, font_size=26, color=HL)
            row = VGroup(sq, arrow, ra).arrange(RIGHT, buff=0.4)
            rows.add(row)
        rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        rows.next_to(heading, DOWN, buff=0.6)
        self.play(FadeIn(rows, lag_ratio=0.15))
        self.wait(2.2)

        note = Text(
            "Every query in this tutorial is one of these, or several"
            " chained together —\nnothing here needed nesting or"
            " aggregation.",
            font_size=21, color=WHITE, line_spacing=1.3,
        )
        note.next_to(rows, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.6)

        self.clear_scene()
