"""
Manim Community animation explaining aggregation in ER diagrams -- built
to accompany IT5008 Tutorial 1 (the NUN Book Exchange schema).

Source material: tut_01.tex, in particular the "Design Notes --- Ternary
Relationships & Aggregation" frame (lines 292-303) and the Logical
Design section (lines 313-376), which is where `own_copy` and `loan`
come from. Unlike the simplest textbook example, this scenario needs
*two* levels of aggregation chained together (own, then loan), which is
exactly what makes it a good teaching example.

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_01_er_aggregation.mp4 for the site.
"""

from manim import *

# ---------------------------------------------------------------------------
# Shared styling (mirrors the BT5110 videos for a consistent look)
# ---------------------------------------------------------------------------

ACCENT = "#6fa8dc"
ACCENT_SOFT = "#1b2733"
HL = "#f2c14e"
GOOD = "#89ca78"
BAD = "#e06c75"
STUDENT_FILL = "#2a1f2b"
MONO_FONT = "Menlo"

SQL_KEYWORDS = [
    "SELECT", "DISTINCT", "FROM", "WHERE", "AND",
    "CREATE", "REPLACE", "VIEW", "ALTER", "TABLE", "DROP", "COLUMN",
    "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "NOT", "NULL", "CHECK",
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
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    return rows


def labelled_box(mobj, label, color=ACCENT):
    cap = Text(label, font_size=24, color=color, weight=BOLD)
    group = VGroup(cap, mobj).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
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
# ER-diagram building blocks
# ---------------------------------------------------------------------------

def entity_box(label, width=2.1, height=0.8, fill=ACCENT_SOFT, font_size=24):
    box = Rectangle(width=width, height=height, color=WHITE,
                     fill_color=fill, fill_opacity=1, stroke_width=2.5)
    text = Text(label, font_size=font_size, weight=BOLD, color=WHITE)
    text.move_to(box.get_center())
    group = VGroup(box, text)
    group.box = box
    return group


def rel_diamond(label, width=1.8, height=0.95, font_size=19, color=WHITE):
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


def card_label(text, mobj, direction=UP, buff=0.1, font_size=17,
               color=GREY_B):
    t = Text(text, font_size=font_size, color=color)
    t.next_to(mobj, direction, buff=buff)
    return t


# ---------------------------------------------------------------------------
# Scene 1 -- Title
# ---------------------------------------------------------------------------

class S01_Title(WatermarkedScene):
    def construct(self):
        kicker = Text("IT5008 · Tutorial 1", font_size=28, color=ACCENT)
        title = Text("Aggregation in ER Diagrams", font_size=52, weight=BOLD)
        sub = Text(
            "Wiring one relationship into another",
            font_size=26, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- Relationships are verbs (and can have more than two arms)
# ---------------------------------------------------------------------------

class S02_RelationshipsAreVerbs(WatermarkedScene):
    def construct(self):
        heading = Text("A relationship is a verb", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        student = entity_box("Students", width=2.1, height=0.8,
                              font_size=22, fill=STUDENT_FILL)
        enroll = rel_diamond("enroll", width=1.6, height=0.85, font_size=18)
        dept = entity_box("Depts", width=2.1, height=0.8, font_size=22)
        row1 = VGroup(student, enroll, dept).arrange(RIGHT, buff=0.9)
        row1.move_to(UP * 1.8)
        l1a = hline(student, enroll)
        l1b = hline(enroll, dept)

        self.play(FadeIn(student), FadeIn(dept))
        self.play(Create(l1a), Create(l1b), FadeIn(enroll))
        cap1 = Text("a student enrolls in a department", font_size=23,
                     color=ACCENT)
        cap1.next_to(row1, DOWN, buff=0.3)
        self.play(FadeIn(cap1, shift=UP * 0.2))
        self.wait(1.4)

        # A relationship can have *more* than two arms.
        student2 = entity_box("Students", width=2.0, height=0.75,
                               font_size=20, fill=STUDENT_FILL)
        own = rel_diamond("own", width=1.5, height=0.85, font_size=18)
        book = entity_box("Books", width=1.9, height=0.72, font_size=20)
        copy = entity_box("Copy", width=1.9, height=0.72, font_size=20)

        student2.next_to(cap1, DOWN, buff=0.75)
        own.next_to(student2, DOWN, buff=0.55)
        book.next_to(own, LEFT, buff=0.9)
        copy.next_to(own, RIGHT, buff=0.9)

        self.play(FadeIn(student2), FadeIn(book), FadeIn(copy))
        self.play(
            Create(vline(student2, own)),
            Create(hline(book, own)),
            Create(hline(own, copy)),
            FadeIn(own),
        )
        cap2 = Text(
            "a student owns a copy of a book — three arms, not two",
            font_size=23, color=ACCENT,
        )
        cap2.next_to(copy, DOWN, buff=0.55).align_to(cap1, ORIGIN)
        cap2.set_x(0)
        self.play(FadeIn(cap2, shift=UP * 0.2))
        self.wait(1.8)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- The constraint the simple design misses
# ---------------------------------------------------------------------------

class S03_MissingConstraint(WatermarkedScene):
    def construct(self):
        heading = Text("A constraint this misses", font_size=34,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        b1 = Text(
            "Copy numbers restart at 1 for every (owner, book) pair --\n"
            "“copy #1” alone doesn't identify anything.",
            font_size=26, color=WHITE, line_spacing=1.3,
        )
        b2 = Text(
            "A loan is about one exact owned copy: which student owns\n"
            "it, which book, which copy number -- all three, together.",
            font_size=26, color=WHITE, line_spacing=1.3,
        )
        bullets = VGroup(b1, b2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        bullets.next_to(heading, DOWN, buff=0.7)
        self.play(FadeIn(b1, shift=UP * 0.2))
        self.wait(0.8)
        self.play(FadeIn(b2, shift=UP * 0.2))
        self.wait(1.2)

        conclusion = Text(
            "So a loan must refer to the whole own-fact --\n"
            "not just to Books or Copy alone.",
            font_size=27, color=HL, weight=BOLD, line_spacing=1.3,
        )
        conclusion.next_to(bullets, DOWN, buff=0.7)
        self.play(FadeIn(conclusion, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- Can a verb plug into another verb?
# ---------------------------------------------------------------------------

class S04_CantWireVerbToVerb(WatermarkedScene):
    def construct(self):
        heading = Text("Can loan just point at own?", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        student = entity_box("Students", width=1.9, height=0.7, font_size=20,
                              fill=STUDENT_FILL)
        own = rel_diamond("own", width=1.5, height=0.8, font_size=18)
        book = entity_box("Books", width=1.8, height=0.68, font_size=19)
        copy = entity_box("Copy", width=1.8, height=0.68, font_size=19)
        student.next_to(heading, DOWN, buff=0.7)
        own.next_to(student, DOWN, buff=0.5)
        book.next_to(own, LEFT, buff=0.7)
        copy.next_to(own, RIGHT, buff=0.7)
        self.play(FadeIn(student), FadeIn(book), FadeIn(copy))
        self.play(Create(vline(student, own)), Create(hline(book, own)),
                   Create(hline(own, copy)), FadeIn(own))

        student2 = entity_box("Students", width=1.9, height=0.7,
                               font_size=20, fill=STUDENT_FILL)
        loan = rel_diamond("loan", width=1.5, height=0.8, font_size=18)
        bottom_row = VGroup(student2, loan).arrange(RIGHT, buff=0.9)
        bottom_row.next_to(copy, DOWN, buff=1.1).align_to(copy, RIGHT)
        bottom_row.shift(LEFT * 0.6)
        self.play(FadeIn(bottom_row))
        self.play(Create(hline(student2, loan)))
        self.wait(0.5)

        bad_line = DashedLine(loan.get_top(), own.get_bottom(), color=BAD,
                               stroke_width=3)
        cross = Text("✗", font_size=34, color=BAD, weight=BOLD)
        cross.move_to(bad_line.get_center())
        self.play(Create(bad_line))
        self.play(FadeIn(cross, scale=1.4))
        self.wait(0.8)

        note = Text(
            "A relationship (diamond) can only connect to entities\n"
            "(rectangles) -- never straight to another relationship.",
            font_size=24, color=BAD, line_spacing=1.3,
        )
        note.next_to(bottom_row, DOWN, buff=0.6)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- The fix: aggregation
# ---------------------------------------------------------------------------

class S05_Aggregation(WatermarkedScene):
    def construct(self):
        heading = Text("Aggregation: turn the fact into an entity",
                        font_size=30, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        student = entity_box("Students", width=1.9, height=0.7, font_size=20,
                              fill=STUDENT_FILL)
        own = rel_diamond("own", width=1.5, height=0.8, font_size=18)
        book = entity_box("Books", width=1.8, height=0.68, font_size=19)
        copy = entity_box("Copy", width=1.8, height=0.68, font_size=19)
        student.next_to(heading, DOWN, buff=0.6)
        own.next_to(student, DOWN, buff=0.45)
        book.next_to(own, LEFT, buff=0.7)
        copy.next_to(own, RIGHT, buff=0.7)
        self.play(FadeIn(student), FadeIn(book), FadeIn(copy))
        self.play(Create(vline(student, own)), Create(hline(book, own)),
                   Create(hline(own, copy)), FadeIn(own))
        self.wait(0.5)

        agg_box = SurroundingRectangle(own, color=HL, buff=0.35,
                                        corner_radius=0.1, stroke_width=3)
        self.play(Create(agg_box))
        self.wait(0.4)

        note1 = Text(
            "The diamond is the verb. The box around it is the fact",
            font_size=22, color=HL,
        )
        note2 = Text(
            "that verb creates -- as if it were a brand-new entity.",
            font_size=22, color=HL,
        )
        notes = VGroup(note1, note2).arrange(DOWN, buff=0.12)
        notes.next_to(agg_box, DOWN, buff=0.35)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(1.8)
        self.play(FadeOut(notes))

        student2 = entity_box("Students", width=1.9, height=0.7,
                               font_size=20, fill=STUDENT_FILL)
        loan = rel_diamond("loan", width=1.5, height=0.8, font_size=18)
        borrow = entity_box("Borrow", width=1.8, height=0.68, font_size=19)
        loan.next_to(agg_box, DOWN, buff=1.0)
        student2.next_to(loan, LEFT, buff=0.7)
        borrow.next_to(loan, RIGHT, buff=0.7)
        self.play(FadeIn(student2), FadeIn(borrow))
        self.play(Create(hline(student2, loan)), Create(hline(loan, borrow)),
                   FadeIn(loan))
        connector = vline(agg_box, loan, color=GOOD, stroke_width=3)
        self.play(Create(connector))
        self.wait(0.4)

        note3 = Text(
            "Now loan legally connects three entities:",
            font_size=22, color=GOOD,
        )
        note4 = Text(
            "the borrower, Borrow, and the aggregate own-fact",
            font_size=22, color=GOOD,
        )
        notes2 = VGroup(note3, note4).arrange(DOWN, buff=0.12)
        notes2.next_to(borrow, DOWN, buff=0.5).set_x(0)
        self.play(FadeIn(notes2, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- The chain continues: loan gets boxed too
# ---------------------------------------------------------------------------

class S06_FullDiagram(WatermarkedScene):
    def construct(self):
        heading = Text("The chain continues: own → loan → been",
                        font_size=28, weight=BOLD)
        heading.to_edge(UP, buff=0.3)
        self.play(FadeIn(heading, shift=UP * 0.2))

        sw, sh, sf = 1.6, 0.6, 16
        dw, dh, df = 1.3, 0.68, 14

        student = entity_box("Students", width=sw, height=sh, font_size=sf,
                              fill=STUDENT_FILL)
        own = rel_diamond("own", width=dw, height=dh, font_size=df)
        book = entity_box("Books", width=sw, height=sh, font_size=sf)
        copy = entity_box("Copy", width=sw, height=sh, font_size=sf)

        student.move_to(UP * 2.6)
        own.next_to(student, DOWN, buff=0.5)
        book.next_to(own, LEFT, buff=0.65)
        copy.next_to(own, RIGHT, buff=0.65)

        own_box = SurroundingRectangle(own, color=WHITE, buff=0.26,
                                        corner_radius=0.08, stroke_width=2.2)

        student2 = entity_box("Students", width=sw, height=sh, font_size=sf,
                               fill=STUDENT_FILL)
        loan = rel_diamond("loan", width=dw, height=dh, font_size=df)
        borrow = entity_box("Borrow", width=sw, height=sh, font_size=sf)
        loan.next_to(own_box, DOWN, buff=0.85)
        student2.next_to(loan, LEFT, buff=0.65)
        borrow.next_to(loan, RIGHT, buff=0.65)

        loan_box = SurroundingRectangle(loan, color=WHITE, buff=0.26,
                                         corner_radius=0.08, stroke_width=2.2)

        been = rel_diamond("been", width=dw, height=dh, font_size=df)
        ret = entity_box("Return", width=sw, height=sh, font_size=sf)
        been.next_to(loan_box, DOWN, buff=0.7)
        ret.next_to(been, RIGHT, buff=0.65)

        lines = VGroup(
            vline(student, own), hline(book, own), hline(own, copy),
            vline(own_box, loan), hline(student2, loan), hline(loan, borrow),
            vline(loan_box, been), hline(been, ret),
        )

        self.play(FadeIn(student), FadeIn(book), FadeIn(copy))
        self.play(Create(lines[0]), Create(lines[1]), Create(lines[2]),
                   FadeIn(own))
        self.play(Create(own_box))
        self.wait(0.3)

        self.play(FadeIn(student2), FadeIn(borrow))
        self.play(Create(lines[3]), Create(lines[4]), Create(lines[5]),
                   FadeIn(loan))
        self.play(Create(loan_box))
        self.wait(0.3)

        self.play(FadeIn(ret))
        self.play(Create(lines[6]), Create(lines[7]), FadeIn(been))
        self.wait(0.5)

        c1 = card_label("(0,n)", lines[0], LEFT, buff=0.1)
        c2 = card_label("(0,n)", lines[1], UP, buff=0.08)
        c3 = card_label("(1,n)", lines[2], UP, buff=0.08)
        c4 = card_label("(0,n)", lines[3], LEFT, buff=0.1)
        c5 = card_label("(0,n)", lines[4], UP, buff=0.08)
        c6 = card_label("(1,n)", lines[5], UP, buff=0.08)
        c7 = card_label("(0,1)", lines[6], LEFT, buff=0.1)
        c8 = card_label("(1,n)", lines[7], UP, buff=0.08)
        cards = VGroup(c1, c2, c3, c4, c5, c6, c7, c8)
        self.play(FadeIn(cards, lag_ratio=0.08))
        self.wait(0.6)

        note = Text(
            "been needs “this particular loan event” as a whole --\n"
            "so loan gets boxed too, exactly like own did.",
            font_size=21, color=HL, line_spacing=1.3,
        )
        note.next_to(VGroup(been, ret), DOWN, buff=0.4).set_x(0)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.4)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 7 -- From ER to relational schema
# ---------------------------------------------------------------------------

class S07_ToRelational(WatermarkedScene):
    def construct(self):
        heading = Text("From aggregate to foreign key", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        own_sql = sql_block([
            "CREATE TABLE own_copy (",
            "  owner VARCHAR(256)",
            "    REFERENCES student(email),",
            "  book  CHAR(14)",
            "    REFERENCES book(isbn13),",
            "  copy  INT CHECK (copy > 0),",
            "  PRIMARY KEY (owner, book, copy)",
            ");",
        ], font_size=19, highlight_lines={0: ["CREATE", "TABLE"],
                                           6: ["PRIMARY", "KEY"]})
        own_panel = labelled_box(own_sql, "own  →  own_copy")

        loan_sql = sql_block([
            "CREATE TABLE loan (",
            "  borrower VARCHAR(256)",
            "    REFERENCES student(email),",
            "  owner VARCHAR(256), book CHAR(14),",
            "  copy INT, borrowed DATE,",
            "  returned DATE,",
            "  FOREIGN KEY (owner, book, copy)",
            "    REFERENCES own_copy(owner, book, copy)",
            ");",
        ], font_size=19, highlight_lines={7: ["REFERENCES"]})
        loan_panel = labelled_box(loan_sql, "loan (+ Borrow, Return)  →  loan")

        panels = VGroup(own_panel, loan_panel).arrange(
            RIGHT, buff=0.8, aligned_edge=UP)
        panels.next_to(heading, DOWN, buff=0.4)

        self.play(FadeIn(own_panel, shift=RIGHT * 0.2))
        self.wait(1)
        self.play(FadeIn(loan_panel, shift=LEFT * 0.2))
        self.wait(1.2)

        ref_line = loan_sql[7]
        ref_box = Underline(ref_line, color=HL, buff=0.05, stroke_width=3)
        self.play(Create(ref_box))
        self.wait(0.6)

        note = Text(
            "loan references own_copy, not book/copy directly -- exactly",
            font_size=22, color=HL,
        )
        note2 = Text(
            "what the aggregation encodes. loan also absorbs Borrow and",
            font_size=22, color=HL,
        )
        note3 = Text(
            "Return, the same way own absorbed Copy into own_copy.",
            font_size=22, color=HL,
        )
        notes = VGroup(note, note2, note3).arrange(DOWN, buff=0.1)
        notes.next_to(panels, DOWN, buff=0.6)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(2.6)

        self.clear_scene()
