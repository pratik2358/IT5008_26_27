"""
Manim Community animation explaining ER participation constraints
(min, max) -- built to accompany IT5008 Tutorial 1 (the NUN Book
Exchange schema). Every example reuses the entities/relationships from
tut_01.tex, with the same (min,max) values used in that tikz diagram,
so it reads as a continuation of that diagram.

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_01_participation_constraints.mp4 for
the site.
"""

from manim import *

# ---------------------------------------------------------------------------
# Shared styling (mirrors videos/er_aggregation for a consistent look)
# ---------------------------------------------------------------------------

ACCENT = "#6fa8dc"
ACCENT_SOFT = "#1b2733"
HL = "#f2c14e"
GOOD = "#89ca78"
BAD = "#e06c75"
STUDENT_FILL = "#2a1f2b"
MONO_FONT = "Menlo"

config.background_color = "#101114"


def data_table(data, col_labels, name=None, scale=0.5, name_color=ACCENT):
    table = Table(
        data,
        col_labels=[Text(c, font=MONO_FONT, weight=BOLD) for c in col_labels],
        include_outer_lines=True,
        line_config={"stroke_width": 1.5, "color": GREY_B},
    ).scale(scale)
    table.get_horizontal_lines().set_color(GREY_B)
    table.get_vertical_lines().set_color(GREY_B)
    group = table
    if name:
        cap = Text(name, font_size=26, color=name_color, weight=BOLD)
        cap.next_to(table, UP, buff=0.26)
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
# ER-diagram building blocks (same conventions as videos/er_aggregation)
# ---------------------------------------------------------------------------

def entity_box(label, width=1.9, height=0.7, fill=ACCENT_SOFT, font_size=20):
    box = Rectangle(width=width, height=height, color=WHITE,
                     fill_color=fill, fill_opacity=1, stroke_width=2.5)
    text = Text(label, font_size=font_size, weight=BOLD, color=WHITE)
    text.move_to(box.get_center())
    group = VGroup(box, text)
    group.box = box
    return group


def rel_diamond(label, width=1.6, height=0.8, font_size=17, color=WHITE):
    diamond = Polygon(UP, RIGHT, DOWN, LEFT, color=color, stroke_width=2.5)
    diamond.stretch_to_fit_width(width)
    diamond.stretch_to_fit_height(height)
    text = Text(label, font_size=font_size, color=WHITE)
    text.move_to(diamond.get_center())
    group = VGroup(diamond, text)
    group.diamond = diamond
    return group


def hline(left_mobj, right_mobj, color=GREY_B, stroke_width=2):
    return Line(left_mobj.get_right(), right_mobj.get_left(),
                color=color, stroke_width=stroke_width)


def vline(top_mobj, bottom_mobj, color=GREY_B, stroke_width=2):
    return Line(top_mobj.get_bottom(), bottom_mobj.get_top(),
                color=color, stroke_width=stroke_width)


def card_label(text, mobj, direction=UP, buff=0.1, font_size=19,
               color=HL):
    t = Text(text, font_size=font_size, color=color, weight=BOLD)
    t.next_to(mobj, direction, buff=buff)
    return t


def mini_aggregate(label, width=1.2, height=0.55, font_size=15,
                    box_pad=0.2):
    """The aggregate: a relationship diamond wrapped in a box that other
    relationships attach to (not the diamond itself)."""
    diamond = rel_diamond(label, width=width, height=height,
                           font_size=font_size)
    box = SurroundingRectangle(diamond, color=WHITE, buff=box_pad,
                                corner_radius=0.06, stroke_width=2)
    group = VGroup(box, diamond)
    group.box = box
    group.diamond = diamond
    return group


# ---------------------------------------------------------------------------
# Scene 1 -- Title
# ---------------------------------------------------------------------------

class S01_Title(WatermarkedScene):
    def construct(self):
        kicker = Text("IT5008 · Tutorial 1", font_size=28, color=ACCENT)
        title = Text("Participation Constraints", font_size=48, weight=BOLD)
        sub = Text(
            "What (min, max) actually means on a wire",
            font_size=26, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- What (min, max) means
# ---------------------------------------------------------------------------

class S02_WhatItMeans(WatermarkedScene):
    def construct(self):
        heading = Text("Two independent questions", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        entity = entity_box("A", width=1.4, height=0.7, font_size=22)
        diamond = rel_diamond("R", width=1.3, height=0.7, font_size=20)
        other = entity_box("B", width=1.4, height=0.7, font_size=22)
        row = VGroup(entity, diamond, other).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.5)
        line1 = hline(entity, diamond)
        line2 = hline(diamond, other)
        card = card_label("(min, max)", line1, UP, font_size=22)
        self.play(FadeIn(row), Create(line1), Create(line2))
        self.play(FadeIn(card, shift=UP * 0.2))
        self.wait(0.8)

        q1 = Text("min — must every entity take part at least once?",
                   font_size=24, color=WHITE)
        q1b = Text("0 = optional, can sit out      1 = mandatory",
                    font_size=22, color=GREY_B)
        q2 = Text("max — can one entity link to many R-instances?",
                   font_size=24, color=WHITE)
        q2b = Text("1 = at most one      n = as many as it likes",
                    font_size=22, color=GREY_B)
        qgroup = VGroup(q1, q1b, q2, q2b).arrange(DOWN, buff=0.22,
                                                    aligned_edge=LEFT)
        qgroup.next_to(row, DOWN, buff=0.6)
        self.play(FadeIn(qgroup, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()

        heading2 = Text("The four combinations", font_size=32, weight=BOLD)
        heading2.to_edge(UP)
        self.play(FadeIn(heading2, shift=UP * 0.2))

        def combo(label, desc, color):
            box = Rectangle(width=3.6, height=1.5, color=color,
                             stroke_width=2.5)
            tag = Text(label, font_size=32, weight=BOLD, color=color)
            d = Text(desc, font_size=18, color=GREY_B)
            content = VGroup(tag, d).arrange(DOWN, buff=0.15)
            content.move_to(box.get_center())
            return VGroup(box, content)

        c01 = combo("(0,1)", "optional · at most one", ACCENT)
        c11 = combo("(1,1)", "mandatory · exactly one", GOOD)
        c0n = combo("(0,n)", "optional · many allowed", ACCENT)
        c1n = combo("(1,n)", "mandatory · many allowed", GOOD)
        grid = VGroup(
            VGroup(c11, c0n).arrange(RIGHT, buff=0.6),
            VGroup(c1n, c01).arrange(RIGHT, buff=0.6),
        ).arrange(DOWN, buff=0.5)
        grid.next_to(heading2, DOWN, buff=0.6)
        self.play(FadeIn(grid, lag_ratio=0.15))
        self.wait(2.4)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- (1,1): mandatory, exactly one
# ---------------------------------------------------------------------------

class S03_OneOne(WatermarkedScene):
    def construct(self):
        heading = Text("(1,1) — mandatory, exactly one", font_size=30,
                        weight=BOLD, color=GOOD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        student = entity_box("Students", width=1.9, height=0.72,
                              font_size=19, fill=STUDENT_FILL)
        enroll = rel_diamond("enroll", width=1.6, height=0.8, font_size=17)
        dept = entity_box("Depts", width=1.9, height=0.72, font_size=19)
        row = VGroup(student, enroll, dept).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.45)
        l1 = hline(student, enroll)
        l2 = hline(enroll, dept)
        self.play(FadeIn(row), Create(l1), Create(l2))
        c1 = card_label("(1,1)", l1, UP)
        c2 = card_label("(0,n)", l2, UP, color=GREY_B)
        self.play(FadeIn(c1), FadeIn(c2))
        self.wait(0.8)

        cols = ["email", "department"]
        rows = [
            ["alice@u.nus.edu", "CS"],
            ["bob@u.nus.edu", "CS"],
            ["carol@u.nus.edu", "Math"],
        ]
        table = data_table(rows, cols, scale=0.5, name="Students")
        table.next_to(row, DOWN, buff=0.55)
        self.play(Create(table))
        self.wait(0.5)

        t = table[0]
        for r in range(len(rows)):
            t.get_entries((r + 2, 2)).set_color(GOOD)
        self.wait(0.4)

        note = Text(
            "Every student names exactly one department — never empty,"
            " never two",
            font_size=21, color=GOOD,
        )
        note.next_to(table, DOWN, buff=0.35)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.8)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- (0,1): optional, at most one
# ---------------------------------------------------------------------------

class S04_ZeroOne(WatermarkedScene):
    def construct(self):
        heading = Text("(0,1) — optional, at most one", font_size=30,
                        weight=BOLD, color=ACCENT)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        student = entity_box("Students", width=1.9, height=0.72,
                              font_size=19, fill=STUDENT_FILL)
        has = rel_diamond("has", width=1.6, height=0.8, font_size=17)
        grad = entity_box("Graduation", width=2.1, height=0.72,
                           font_size=17)
        row = VGroup(student, has, grad).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.45)
        l1 = hline(student, has)
        l2 = hline(has, grad)
        self.play(FadeIn(row), Create(l1), Create(l2))
        c1 = card_label("(0,1)", l1, UP)
        c2 = card_label("(1,n)", l2, UP, color=GREY_B)
        self.play(FadeIn(c1), FadeIn(c2))
        self.wait(0.8)

        st_cols = ["email", "joined"]
        st_rows = [
            ["alice@u.nus.edu", "2019"],
            ["bob@u.nus.edu", "2023"],
        ]
        gr_cols = ["date", "email"]
        gr_rows = [
            ["2023-05-01", "alice@u.nus.edu"],
        ]
        st = data_table(st_rows, st_cols, scale=0.46, name="Students")
        gr = data_table(gr_rows, gr_cols, scale=0.46, name="Graduation")
        both = VGroup(st, gr).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        both.next_to(row, DOWN, buff=0.5)
        self.play(Create(st), Create(gr))
        self.wait(0.6)

        alice = gr[0].get_entries((2, 2))
        alice_box = SurroundingRectangle(alice, color=GOOD, buff=0.06)
        self.play(Create(alice_box))
        self.wait(0.4)

        note = Text(
            "Bob hasn't graduated yet — no row for him in Graduation",
            font_size=20, color=BAD,
        )
        note2 = Text(
            "Alice has exactly one — never two graduation dates",
            font_size=20, color=GOOD,
        )
        notes = VGroup(note, note2).arrange(DOWN, buff=0.15)
        notes.next_to(both, DOWN, buff=0.4)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- (1,n): mandatory, many allowed
# ---------------------------------------------------------------------------

class S05_OneN(WatermarkedScene):
    def construct(self):
        heading = Text("(1,n) — mandatory, many allowed", font_size=30,
                        weight=BOLD, color=GOOD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        student = entity_box("Students", width=1.9, height=0.72,
                              font_size=19, fill=STUDENT_FILL)
        has = rel_diamond("has", width=1.6, height=0.8, font_size=17)
        grad = entity_box("Graduation", width=2.1, height=0.72,
                           font_size=17)
        row = VGroup(student, has, grad).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.4)
        l1 = hline(student, has)
        l2 = hline(has, grad)
        self.play(FadeIn(row), Create(l1), Create(l2))
        c1 = card_label("(0,1)", l1, UP, color=GREY_B)
        c2 = card_label("(1,n)", l2, UP)
        self.play(FadeIn(c1), FadeIn(c2))
        self.wait(0.8)

        st_cols = ["email", "graduated"]
        st_rows = [
            ["alice@u.nus.edu", "2023-05-01"],
            ["dave@u.nus.edu", "2023-05-01"],
        ]
        gr_cols = ["date"]
        gr_rows = [["2023-05-01"]]
        st = data_table(st_rows, st_cols, scale=0.46, name="Students")
        gr = data_table(gr_rows, gr_cols, scale=0.46, name="Graduation")
        both = VGroup(st, gr).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        both.next_to(row, DOWN, buff=0.45)
        self.play(Create(st), Create(gr))
        self.wait(0.6)

        shared = gr[0].get_entries((2, 1))
        shared_box = SurroundingRectangle(shared, color=GOOD, buff=0.06)
        self.play(Create(shared_box))
        self.wait(0.4)

        note = Text(
            "Alice and Dave graduated on the same day — they point at\n"
            "the very same Graduation entity, keyed only by its date.",
            font_size=19, color=GOOD, line_spacing=1.3,
        )
        note2 = Text(
            "That's why Graduation's side is (1,n): one date can back many\n"
            "students, but every date we store backs at least one.",
            font_size=19, color=GREY_B, line_spacing=1.3,
        )
        notes = VGroup(note, note2).arrange(DOWN, buff=0.22)
        notes.next_to(both, DOWN, buff=0.35)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(2.6)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- (0,n): optional, many allowed
# ---------------------------------------------------------------------------

class S06_ZeroN(WatermarkedScene):
    def construct(self):
        heading = Text("(0,n) — optional, many allowed", font_size=30,
                        weight=BOLD, color=ACCENT)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        book = entity_box("Books", width=1.9, height=0.72, font_size=19)
        own = rel_diamond("own", width=1.6, height=0.8, font_size=17)
        student = entity_box("Students", width=1.9, height=0.72,
                              font_size=19, fill=STUDENT_FILL)
        row = VGroup(book, own, student).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.4)
        l1 = hline(book, own)
        l2 = hline(own, student)
        self.play(FadeIn(row), Create(l1), Create(l2))
        c1 = card_label("(0,n)", l1, UP)
        c2 = card_label("(0,n)", l2, UP, color=GREY_B)
        self.play(FadeIn(c1), FadeIn(c2))
        self.wait(0.8)

        bk_cols = ["isbn13", "title"]
        bk_rows = [
            ["978-...844A", "Discrete Math (advised)"],
            ["978-...855B", "Database Systems"],
        ]
        oc_cols = ["owner", "book", "copy"]
        oc_rows = [
            ["alice@u.nus.edu", "...855B", "1"],
            ["bob@u.nus.edu", "...855B", "1"],
        ]
        bt = data_table(bk_rows, bk_cols, scale=0.42, name="Books")
        ot = data_table(oc_rows, oc_cols, scale=0.42, name="own_copy")
        both = VGroup(bt, ot).arrange(RIGHT, buff=0.9, aligned_edge=UP)
        both.next_to(row, DOWN, buff=0.4)
        self.play(Create(bt), Create(ot))
        self.wait(0.5)

        advised = bt[0].get_entries((2, 1))
        advised_box = SurroundingRectangle(advised, color=BAD, buff=0.06)
        self.play(Create(advised_box))
        self.wait(0.4)

        note = Text(
            "The advised book has zero owned copies — nobody's bought it yet",
            font_size=19, color=BAD,
        )
        note2 = Text(
            "Database Systems has two — two different students own a copy",
            font_size=19, color=GOOD,
        )
        notes = VGroup(note, note2).arrange(DOWN, buff=0.12)
        notes.next_to(both, DOWN, buff=0.35)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 7 -- Synthesis: the whole own -> loan -> been chain
# ---------------------------------------------------------------------------

class S07_Synthesis(WatermarkedScene):
    def construct(self):
        heading = Text("All four, on the own → loan → been chain",
                        font_size=28, weight=BOLD)
        heading.to_edge(UP, buff=0.3)
        self.play(FadeIn(heading, shift=UP * 0.2))

        sw, sh, sf = 1.5, 0.56, 15
        dw, dh, df = 1.25, 0.62, 13

        student = entity_box("Students", width=sw, height=sh, font_size=sf,
                              fill=STUDENT_FILL)
        own = rel_diamond("own", width=dw, height=dh, font_size=df)
        book = entity_box("Books", width=sw, height=sh, font_size=sf)
        copy = entity_box("Copy", width=sw, height=sh, font_size=sf)

        student.move_to(UP * 2.7)
        own.next_to(student, DOWN, buff=0.45)
        book.next_to(own, LEFT, buff=0.55)
        copy.next_to(own, RIGHT, buff=0.55)

        own_box = SurroundingRectangle(own, color=WHITE, buff=0.24,
                                        corner_radius=0.07, stroke_width=2)

        student2 = entity_box("Students", width=sw, height=sh, font_size=sf,
                               fill=STUDENT_FILL)
        loan = rel_diamond("loan", width=dw, height=dh, font_size=df)
        borrow = entity_box("Borrow", width=sw, height=sh, font_size=sf)
        loan.next_to(own_box, DOWN, buff=0.75)
        student2.next_to(loan, LEFT, buff=0.55)
        borrow.next_to(loan, RIGHT, buff=0.55)

        loan_box = SurroundingRectangle(loan, color=WHITE, buff=0.24,
                                         corner_radius=0.07, stroke_width=2)

        been = rel_diamond("been", width=dw, height=dh, font_size=df)
        ret = entity_box("Return", width=sw, height=sh, font_size=sf)
        been.next_to(loan_box, DOWN, buff=0.6)
        ret.next_to(been, RIGHT, buff=0.55)

        lines = VGroup(
            vline(student, own), hline(book, own), hline(own, copy),
            vline(own_box, loan), hline(student2, loan), hline(loan, borrow),
            vline(loan_box, been), hline(been, ret),
        )

        self.play(FadeIn(student), FadeIn(book), FadeIn(copy))
        self.play(Create(lines[0]), Create(lines[1]), Create(lines[2]),
                   FadeIn(own))
        self.play(Create(own_box))
        self.play(FadeIn(student2), FadeIn(borrow))
        self.play(Create(lines[3]), Create(lines[4]), Create(lines[5]),
                   FadeIn(loan))
        self.play(Create(loan_box))
        self.play(FadeIn(ret))
        self.play(Create(lines[6]), Create(lines[7]), FadeIn(been))
        self.wait(0.4)

        diagram = VGroup(student, own, book, copy, own_box, student2, loan,
                          borrow, loan_box, been, ret, lines)

        mand = GOOD
        opt = ACCENT
        c1 = card_label("(0,n)", lines[0], LEFT, buff=0.08, font_size=14,
                         color=opt)
        c2 = card_label("(0,n)", lines[1], UP, buff=0.06, font_size=14,
                         color=opt)
        c3 = card_label("(1,n)", lines[2], UP, buff=0.06, font_size=14,
                         color=mand)
        c4 = card_label("(0,n)", lines[3], LEFT, buff=0.08, font_size=14,
                         color=opt)
        c5 = card_label("(0,n)", lines[4], UP, buff=0.06, font_size=14,
                         color=opt)
        c6 = card_label("(1,n)", lines[5], UP, buff=0.06, font_size=14,
                         color=mand)
        c7 = card_label("(0,1)", lines[6], LEFT, buff=0.08, font_size=14,
                         color=opt)
        c8 = card_label("(1,n)", lines[7], UP, buff=0.06, font_size=14,
                         color=mand)
        cards = VGroup(c1, c2, c3, c4, c5, c6, c7, c8)
        self.play(FadeIn(cards, lag_ratio=0.08))
        self.wait(1.2)

        legend1 = VGroup(
            Text("●", font_size=18, color=mand),
            Text("mandatory (min = 1)", font_size=18, color=GREY_B),
        ).arrange(RIGHT, buff=0.12)
        legend2 = VGroup(
            Text("●", font_size=18, color=opt),
            Text("optional (min = 0)", font_size=18, color=GREY_B),
        ).arrange(RIGHT, buff=0.12)
        legend = VGroup(legend1, legend2).arrange(RIGHT, buff=0.6)
        legend.next_to(VGroup(been, ret), DOWN, buff=0.4).set_x(0)
        self.play(FadeIn(legend, shift=UP * 0.2))

        foot = Text(
            "(the full diagram also has enroll/in/has on the\n"
            "department & faculty side — see the Tutorial 1 slides)",
            font_size=15, color=GREY_C, line_spacing=1.2,
        )
        foot.next_to(legend, DOWN, buff=0.3).set_x(0)
        self.play(FadeIn(foot))
        self.wait(2.6)

        self.clear_scene()
