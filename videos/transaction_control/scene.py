"""
Manim Community animation explaining transaction control -- BEGIN,
COMMIT, ROLLBACK, SAVEPOINT -- built to accompany IT5008 Tutorial 2
(the NUN Book Exchange schema, intern's alternative relational design).

Continues straight from the DEFERRABLE constraints video: tut_02.tex's
"Transaction 1/2" frames end with the note "you can also use commands
like BEGIN, COMMIT, SAVEPOINT my_savepoint, and ROLLBACK TO my
savepoint to control the flow of transactions" -- this video is that
note, expanded into a full walkthrough. The running example reuses
Q2(f)-(g) from T02-comments.pdf: renaming 'CS' to 'Computer Science'
(a clean UPDATE), and deleting the 'Chemistry' department's students
(which fails -- some of them still have loan records referencing
them), to show exactly why SAVEPOINT exists: one failed statement
poisons an entire PostgreSQL transaction unless you've marked a way
back.

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_02_transaction_control.mp4 for the
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
    "SELECT", "FROM", "WHERE", "AND",
    "BEGIN", "TRANSACTION", "END", "COMMIT", "ROLLBACK", "TO",
    "SAVEPOINT", "RELEASE",
    "SET", "CONSTRAINTS", "ALL", "IMMEDIATE", "DEFERRED",
    "DELETE", "UPDATE", "INSERT", "INTO", "VALUES",
]

config.background_color = "#101114"


def sql_block(lines, font_size=22, extra_colors=None):
    """extra_colors: {line_index: {substring: color}} -- lets a line's
    trailing comment (e.g. "-- 26 rows") carry its own color."""
    extra_colors = extra_colors or {}
    t2c = {kw: "#c586c0" for kw in SQL_KEYWORDS}
    rows = VGroup()
    for i, line in enumerate(lines):
        t2c_line = dict(t2c)
        t2c_line.update(extra_colors.get(i, {}))
        txt = Text(line, font=MONO_FONT, font_size=font_size, t2c=t2c_line)
        rows.add(txt)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    return rows


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
        title = Text("Transaction Control", font_size=48, weight=BOLD)
        sub = Text(
            "BEGIN, COMMIT, ROLLBACK, SAVEPOINT",
            font_size=26, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- Without BEGIN: autocommit
# ---------------------------------------------------------------------------

class S02_NoBegin(WatermarkedScene):
    def construct(self):
        heading = Text("Without BEGIN: autocommit", font_size=32,
                        weight=BOLD, color=BAD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        sub = Text(
            "By default, every statement you run is its own transaction.",
            font_size=23, color=WHITE,
        )
        sub.next_to(heading, DOWN, buff=0.6)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(0.8)

        code = sql_block([
            "DELETE FROM student",
            "WHERE department = 'Chemistry';",
        ], font_size=24)
        code.next_to(sub, DOWN, buff=0.6)
        self.play(FadeIn(code, shift=UP * 0.2))
        self.wait(0.4)

        stamp = Text("auto-BEGIN → runs → auto-COMMIT, instantly",
                      font_size=20, color=BAD, weight=BOLD)
        stamp.next_to(code, DOWN, buff=0.4)
        self.play(FadeIn(stamp, shift=UP * 0.2))
        self.wait(1.2)

        rb = sql_block(["ROLLBACK;"], font_size=22,
                        extra_colors={0: {}})
        rb_note = Text("✗ too late — it's already permanent", font_size=20,
                        color=BAD)
        rb_group = VGroup(rb, rb_note).arrange(RIGHT, buff=0.3)
        rb_group.next_to(stamp, DOWN, buff=0.5)
        self.play(FadeIn(rb_group, shift=UP * 0.2))
        self.wait(1.6)

        note = Text(
            "One wrong statement, no BEGIN, and it's gone for good.",
            font_size=22, color=HL,
        )
        note.next_to(rb_group, DOWN, buff=0.55)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- With BEGIN: nothing is final yet
# ---------------------------------------------------------------------------

class S03_WithBegin(WatermarkedScene):
    def construct(self):
        heading = Text("With BEGIN: nothing is final yet", font_size=32,
                        weight=BOLD, color=GOOD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        code = sql_block([
            "BEGIN;",
            "  UPDATE ...;",
            "  DELETE ...;",
        ], font_size=26)
        code.next_to(heading, DOWN, buff=0.7)
        self.play(FadeIn(code, shift=UP * 0.2))
        self.wait(0.5)

        note = Text(
            "Changes exist only inside this session — provisional,\n"
            "invisible to everyone else — until you decide.",
            font_size=22, color=WHITE, line_spacing=1.3,
        )
        note.next_to(code, DOWN, buff=0.6)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.2)

        def outcome_box(label, desc, color):
            box = Rectangle(width=4.6, height=1.5, color=color,
                             stroke_width=2.5)
            tag = Text(label, font_size=26, weight=BOLD, color=color)
            d = Text(desc, font_size=18, color=GREY_B)
            content = VGroup(tag, d).arrange(DOWN, buff=0.18)
            content.move_to(box.get_center())
            return VGroup(box, content)

        commit_box = outcome_box("COMMIT;", "make it all permanent", GOOD)
        rollback_box = outcome_box("ROLLBACK;",
                                     "undo everything since BEGIN", BAD)
        row = VGroup(commit_box, rollback_box).arrange(RIGHT, buff=0.8)
        row.next_to(note, DOWN, buff=0.6)
        self.play(FadeIn(row, lag_ratio=0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- Step 1: a good UPDATE, and how to judge it
# ---------------------------------------------------------------------------

class S04_GoodUpdate(WatermarkedScene):
    def construct(self):
        heading = Text("Step 1 — a good UPDATE", font_size=30, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        code = sql_block([
            "BEGIN;",
            "  UPDATE student",
            "    SET department = 'Computer Science'",
            "    WHERE department = 'CS';",
            "  -- 26 rows",
        ], font_size=22, extra_colors={4: {"-- 26 rows": GOOD}})
        code.next_to(heading, DOWN, buff=0.6)
        self.play(FadeIn(code, shift=UP * 0.2))
        self.wait(0.8)

        check = Text("✓", font_size=40, color=GOOD, weight=BOLD)
        check.next_to(code, RIGHT, buff=0.5).align_to(code[4], UP)
        self.play(FadeIn(check, scale=1.5))
        self.wait(0.6)

        note = Text(
            "26 rows — matches what we expected for the CS department.",
            font_size=22, color=GOOD,
        )
        note.next_to(code, DOWN, buff=0.55)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1)

        note2 = Text(
            "Looks right so far. But the transaction isn't over —\n"
            "judging COMMIT vs. ROLLBACK happens at the end, not per line.",
            font_size=21, color=HL, line_spacing=1.3,
        )
        note2.next_to(note, DOWN, buff=0.4)
        self.play(FadeIn(note2, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- Step 2: a DELETE goes wrong, and poisons everything
# ---------------------------------------------------------------------------

class S05_PoisonedTransaction(WatermarkedScene):
    def construct(self):
        heading = Text("Step 2 — a DELETE goes wrong", font_size=30,
                        weight=BOLD, color=BAD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        code = sql_block([
            "BEGIN;",
            "  UPDATE student SET department = 'Computer Science'",
            "    WHERE department = 'CS';         -- 26 rows",
            "  DELETE FROM student",
            "    WHERE department = 'Chemistry';",
        ], font_size=19, extra_colors={2: {"-- 26 rows": GOOD}})
        code.next_to(heading, DOWN, buff=0.55)
        self.play(FadeIn(code, shift=UP * 0.2))
        self.wait(0.5)

        box = SurroundingRectangle(code[3:5], color=BAD, buff=0.1)
        self.play(Create(box))
        err = Text(
            "ERROR: update or delete on table \"student\" violates\n"
            "foreign key constraint — still referenced from table \"loan\"",
            font_size=17, color=BAD, line_spacing=1.3,
        )
        err.next_to(code, DOWN, buff=0.5)
        self.play(FadeIn(err, shift=UP * 0.2))
        self.wait(1.4)

        select_line = sql_block(["SELECT * FROM student;  -- just checking..."],
                                  font_size=18)
        select_line.next_to(err, DOWN, buff=0.5)
        self.play(FadeIn(select_line, shift=UP * 0.2))
        err2 = Text(
            "ERROR: current transaction is aborted, commands ignored\n"
            "until end of transaction block",
            font_size=17, color=BAD, line_spacing=1.3,
        )
        err2.next_to(select_line, DOWN, buff=0.35)
        self.play(FadeIn(err2, shift=UP * 0.2))
        self.wait(1.4)

        banner = Text(
            "One failed statement poisons the ENTIRE transaction.",
            font_size=23, color=BAD, weight=BOLD,
        )
        banner.next_to(err2, DOWN, buff=0.45)
        self.play(FadeIn(banner, shift=UP * 0.2))
        self.wait(1)

        banner2 = Text(
            "Only way out: ROLLBACK — but that discards the good"
            " UPDATE too.",
            font_size=21, color=HL,
        )
        banner2.next_to(banner, DOWN, buff=0.3)
        self.play(FadeIn(banner2, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- Doing it with SAVEPOINT instead
# ---------------------------------------------------------------------------

class S06_Savepoint(WatermarkedScene):
    def construct(self):
        heading = Text("Doing it with SAVEPOINT instead", font_size=30,
                        weight=BOLD, color=GOOD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        code = sql_block([
            "BEGIN;",
            "  UPDATE student SET department = 'Computer Science'",
            "    WHERE department = 'CS';         -- 26 rows",
            "  SAVEPOINT s;",
            "  DELETE FROM student",
            "    WHERE department = 'Chemistry';  -- ERROR",
            "  ROLLBACK TO SAVEPOINT s;",
            "COMMIT;",
        ], font_size=17, extra_colors={
            2: {"-- 26 rows": GOOD},
            3: {"SAVEPOINT": HL, "s": HL},
            5: {"-- ERROR": BAD},
            6: {"ROLLBACK": HL, "TO": HL, "SAVEPOINT": HL, "s": HL},
        })
        code.next_to(heading, DOWN, buff=0.5)
        self.play(FadeIn(code[0:3], shift=UP * 0.2))
        self.wait(0.5)

        sp_marker = SurroundingRectangle(code[3], color=HL, buff=0.08)
        self.play(FadeIn(code[3]), Create(sp_marker))
        self.wait(0.5)

        self.play(FadeIn(code[4:6], shift=UP * 0.2))
        err_box = SurroundingRectangle(code[4:6], color=BAD, buff=0.08)
        self.play(Create(err_box))
        self.wait(0.8)

        self.play(FadeIn(code[6], shift=UP * 0.2))
        rewind = CurvedArrow(code[6].get_left() + LEFT * 0.15,
                               sp_marker.get_left() + LEFT * 0.15,
                               color=HL, angle=-TAU / 4, stroke_width=3)
        self.play(Create(rewind))
        strike = Line(code[4].get_left(), code[5].get_right(),
                       color=BAD, stroke_width=2.5)
        self.play(Create(strike))
        note = Text(
            "back to right after the SAVEPOINT — the UPDATE survives",
            font_size=19, color=GOOD,
        )
        note.next_to(code, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.4)

        self.play(FadeIn(code[7], shift=UP * 0.2))
        check = Text("✓", font_size=36, color=GOOD, weight=BOLD)
        check.next_to(code[7], RIGHT, buff=0.4)
        self.play(FadeIn(check, scale=1.5))
        self.wait(0.6)

        note2 = Text(
            "The transaction is still open, and still yours to control —",
            font_size=20, color=GOOD,
        )
        note3 = Text(
            "COMMIT keeps the good UPDATE; the failed DELETE never happened.",
            font_size=20, color=GOOD,
        )
        notes = VGroup(note2, note3).arrange(DOWN, buff=0.15)
        notes.next_to(note, DOWN, buff=0.35)
        self.play(FadeIn(notes, shift=UP * 0.2))
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
            "No BEGIN = autocommit: every statement is final the instant"
            " it succeeds.",
            font_size=21, color=WHITE,
        )
        b2 = Text(
            "BEGIN = nothing is final until COMMIT; ROLLBACK undoes"
            " everything since BEGIN.",
            font_size=21, color=WHITE,
        )
        b3 = Text(
            "In PostgreSQL, one error aborts the WHOLE transaction —"
            " even later correct\nstatements are refused until you"
            " ROLLBACK.",
            font_size=21, color=WHITE, line_spacing=1.3,
        )
        b4 = Text(
            "SAVEPOINT s + ROLLBACK TO s recovers from just the bad"
            " step, keeping\neverything that came before it.",
            font_size=21, color=WHITE, line_spacing=1.3,
        )
        b5 = Text(
            "Before COMMIT, judge the whole transaction: does the net"
            " effect match\nwhat you actually intended?",
            font_size=21, color=HL, line_spacing=1.3,
        )
        bullets = VGroup(b1, b2, b3, b4, b5).arrange(DOWN, buff=0.35,
                                                        aligned_edge=LEFT)
        bullets.next_to(heading, DOWN, buff=0.6)
        for b in bullets:
            self.play(FadeIn(b, shift=UP * 0.2))
            self.wait(0.4)
        self.wait(1.8)

        self.clear_scene()
