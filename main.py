#!/usr/bin/env python3
"""The World in One Day -- Wednesday, 25 November 2026.

Draws a one-page newspaper front page summing up the day's world news.
Pure Python 3 standard library. No network, no randomness, no timestamps:
two runs produce byte-identical output.

Layout (1024 x 1024, warm newsprint):
  masthead + dateline
  hero: drawn Gulf of Finland sea scene + headline (Ukraine / Russian ship)
  right rail: Nvidia (Huang reinstated) and Riyadh tower strike
  three-column row: NATO space defence, Sarkozy trial, Australia-Solomon pact
  "In brief" strip: South Korea minister quits, Dutch climate ruling,
  Huawei trade-secret verdict
  footer
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (20, 20, 20)
RED = (176, 32, 32)
BLUE = (31, 78, 121)
SEA = (38, 92, 140)
SKY = (178, 208, 226)
SKY2 = (214, 230, 240)
STEEL = (58, 64, 70)
GOLD = (198, 148, 42)
ORANGE = (232, 116, 28)
YELLOW = (244, 196, 66)
GREEN = (46, 120, 66)
GREY = (110, 110, 104)
LIGHT = (228, 222, 206)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '1' = ink. Uppercase + digits + punctuation.
# Headlines and summaries are set in capitals, newspaper style.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

CHAR_W = 6  # 5 glyph columns + 1 spacing column


def text_width(text, scale):
    return len(text) * CHAR_W * scale


def wrap(text, max_px, scale):
    """Greedy word wrap; returns list of lines fitting max_px width."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_px:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # hard-split an overlong single word
            while text_width(word, scale) > max_px:
                cut = max_px // (CHAR_W * scale)
                lines.append(word[:cut])
                word = word[cut:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                i = base + (xx - max(0, x)) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, color)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.set(xx, yy, color)

    def triangle(self, pts, color):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for y in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= y <= max(ay, by):
                    xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                for x in range(xa, xb + 1):
                    self.set(x, y, color)

    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch, FONT["?"])
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    self.rect(x + c * scale, y + r * scale, scale, scale, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, color)
            cx += CHAR_W * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)

    def para(self, x, y, text, max_px, scale, color, leading=None):
        lh = leading if leading is not None else 7 * scale + 4
        for line in wrap(text, max_px, scale):
            self.text(x, y, line, scale, color)
            y += lh
        return y


# ---------------------------------------------------------------- scenes
def draw_sea_scene(cv, x, y, w, h):
    """Gulf of Finland: sky, sea, cargo ship, drone, blast burst."""
    # sky bands
    cv.rect(x, y, w, h // 2, SKY2)
    cv.rect(x, y + h // 2, w, h - h // 2, SKY)
    # sun disc, pale
    cv.circle(x + w - 90, y + 42, 26, YELLOW)
    cv.circle(x + w - 90, y + 42, 20, (247, 214, 110))
    # sea
    sea_y = y + int(h * 0.62)
    cv.rect(x, sea_y, w, h - int(h * 0.62), SEA)
    cv.rect(x, sea_y, w, 4, (120, 170, 205))
    # wave dashes
    for i, wx in enumerate(range(x + 18, x + w - 30, 74)):
        cv.rect(wx, sea_y + 22 + (i % 3) * 14, 34, 3, (120, 170, 205))
    # cargo ship (dark hull, pale superstructure)
    hull_y = sea_y + 18
    cv.triangle(((x + 90, hull_y), (x + 430, hull_y),
                 (x + 400, hull_y + 46)), STEEL)
    cv.rect(x + 90, hull_y, 340, 34, STEEL)
    cv.rect(x + 250, hull_y - 52, 110, 52, (232, 228, 214))
    cv.rect(x + 262, hull_y - 44, 18, 12, INK)
    cv.rect(x + 292, hull_y - 44, 18, 12, INK)
    cv.rect(x + 322, hull_y - 44, 18, 12, INK)
    cv.rect(x + 150, hull_y - 34, 34, 34, RED)  # funnel
    cv.rect(x + 150, hull_y - 44, 34, 10, INK)
    # mast
    cv.vline(x + 400, hull_y - 66, 66, INK, 3)
    # smoke puffs
    for sx, sy, sr in ((x + 158, hull_y - 62, 9), (x + 176, hull_y - 76, 11),
                       (x + 196, hull_y - 88, 8)):
        cv.circle(sx, sy, sr, (200, 200, 192))
    # drone above the ship (small quadcopter)
    dx, dy = x + 500, y + 52
    cv.rect(dx - 16, dy - 5, 32, 10, INK)
    for ox in (-22, 22):
        cv.circle(dx + ox, dy, 7, INK)
        cv.hline(dx + ox - 12, dy - 8, 24, INK, 2)
    cv.line(dx - 16, dy, dx - 22, dy + 4, INK)
    cv.line(dx + 16, dy, dx + 22, dy + 4, INK)
    # explosion burst near the bow
    bx, by = x + 470, hull_y - 8
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 14, 34
        a = math.radians(ang)
        cv.triangle(((bx, by),
                     (bx + int(r1 * math.cos(a + 0.25)),
                      by + int(r1 * math.sin(a + 0.25))),
                     (bx + int(r2 * math.cos(a)),
                      by + int(r2 * math.sin(a)))), ORANGE)
    cv.circle(bx, by, 16, YELLOW)
    cv.circle(bx, by, 9, ORANGE)
    # caption strip
    cv.rect(x, y + h - 26, w, 26, INK)
    cv.text(x + 12, y + h - 19, "A DRONE OVER THE GULF OF FINLAND",
            1, PAPER)


def draw_chip(cv, x, y, s):
    """AI chip icon for the Nvidia story."""
    cv.rect(x, y, s, s, INK)
    cv.rect(x + 6, y + 6, s - 12, s - 12, (34, 64, 44))
    for i in range(4):
        px = x + 14 + i * 16
        cv.rect(px, y - 8, 6, 8, GOLD)
        cv.rect(px, y + s, 6, 8, GOLD)
        cv.rect(x - 8, y + 14 + i * 16, 8, 6, GOLD)
        cv.rect(x + s, y + 14 + i * 16, 8, 6, GOLD)
    cv.text(x + 14, y + s // 2 - 8, "AI", 2, YELLOW)


def draw_tower(cv, x, y, s):
    """Riyadh tower icon."""
    cv.rect(x + s // 2 - 10, y, 20, s, STEEL)
    cv.triangle(((x + s // 2 - 14, y), (x + s // 2 + 14, y),
                 (x + s // 2, y - 14)), GOLD)
    for wy in range(y + 16, y + s - 8, 14):
        cv.rect(x + s // 2 - 6, wy, 12, 5, YELLOW)
    # impact burst at the crown
    cv.circle(x + s // 2, y + 8, 12, ORANGE)
    cv.circle(x + s // 2, y + 8, 6, YELLOW)


def draw_satellite(cv, x, y, s):
    """Satellite icon for the NATO space story."""
    cv.rect(x + s // 2 - 12, y + s // 2 - 10, 24, 20, INK)
    cv.rect(x + 2, y + s // 2 - 6, 18, 12, BLUE)
    cv.rect(x + s - 20, y + s // 2 - 6, 18, 12, BLUE)
    cv.line(x + s // 2 - 12, y + s // 2, x + 2, y + s // 2, INK)
    cv.line(x + s // 2 + 12, y + s // 2, x + s - 2, y + s // 2, INK)
    for r in (26, 34):
        cv.circle(x + s // 2, y + s // 2, r, RED, fill=False)


def draw_gavel(cv, x, y, s):
    """Court gavel icon for the Sarkozy trial story."""
    cv.rect(x + 6, y + 8, 30, 14, (120, 82, 40))
    cv.line(x + 36, y + 15, x + s - 8, y + s - 12, (120, 82, 40))
    cv.rect(x + s - 14, y + s - 16, 12, 6, (120, 82, 40))
    cv.rect(x + 4, y + s - 10, s - 8, 6, INK)


def draw_pact(cv, x, y, s):
    """Signed pact icon: document, seal and check."""
    cv.rect(x + 6, y + 4, s - 22, s - 8, (232, 228, 214))
    cv.hline(x + 12, y + 12, s - 34, INK, 2)
    cv.hline(x + 12, y + 24, s - 34, INK, 2)
    cv.hline(x + 12, y + 36, s - 40, INK, 2)
    cv.circle(x + s - 26, y + s - 22, 12, RED)
    cv.text(x + s - 31, y + s - 29, "OK", 1, PAPER)


# ---------------------------------------------------------------- png write
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- page
def build():
    cv = Canvas(W, H, PAPER)
    M = 28  # margin
    CW = W - 2 * M  # 968

    # top double rule
    cv.hline(M, 14, CW, INK, 3)
    cv.hline(M, 20, CW, INK, 1)

    # masthead
    cv.text_center(W // 2, 34, "THE WORLD IN ONE DAY", 7, INK)

    # dateline bar
    cv.hline(M, 100, CW, INK, 1)
    cv.text(M, 110, "WEDNESDAY, 25 NOVEMBER 2026", 2, INK)
    right = "ONE DAY. ONE PAGE. THE WORLD."
    cv.text(W - M - text_width(right, 2), 110, right, 2, INK)
    cv.hline(M, 132, CW, INK, 3)

    # ---- hero column (left) ----
    HX, HW = M, 620
    draw_sea_scene(cv, HX, 148, HW, 202)
    y = 362
    cv.text(HX, y, "WAR AT SEA", 2, RED)
    y += 22
    y = cv.para(HX, y,
                "ZELENSKIY CONFIRMS UKRAINE HIT RUSSIAN SHIP IN GULF OF FINLAND",
                HW, 4, INK, leading=36)
    y += 6
    y = cv.para(HX, y,
                "KYIV SAYS SATURDAY'S DRONE ATTACK STRUCK A CARGO VESSEL IN THE"
                " GULF OF FINLAND. ALLY NORWAY URGES CAUTION AS THE WAR SPREADS"
                " TO NEW WATERS -- AND UKRAINE ALSO CLAIMS A RUSSIAN WARSHIP"
                " SUNK OFF THE COAST OF LIBYA.",
                HW, 2, INK, leading=18)

    # ---- right rail ----
    RX, RW = HX + HW + 24, W - M - (HX + HW + 24)
    y = 148
    cv.text(RX, y, "TECH", 2, RED)
    y += 20
    draw_chip(cv, RX, y, 48)
    y += 60
    y = cv.para(RX, y, "HUANG IS BACK: NVIDIA REINSTATES ITS CHIEF",
                RW, 3, INK, leading=26)
    y += 4
    y = cv.para(RX, y,
                "DAYS AFTER ACCEPTING HIS RESIGNATION, THE BOARD RESTORES"
                " JENSEN HUANG.",
                RW, 2, INK, leading=18)
    y += 14
    cv.hline(RX, y, RW, GREY, 1)
    y += 14
    cv.text(RX, y, "MIDDLE EAST", 2, RED)
    y += 20
    draw_tower(cv, RX, y, 48)
    y += 60
    y = cv.para(RX, y, "HOUTHIS HIT RIYADH'S TALLEST TOWER; 11 WOUNDED",
                RW, 3, INK, leading=26)
    y += 4
    y = cv.para(RX, y,
                "SAUDI CIVIL DEFENCE CONFIRMS THE STRIKE.",
                RW, 2, INK, leading=18)

    # ---- divider ----
    cv.hline(M, 618, CW, INK, 2)

    # ---- three-column row ----
    col_w = (CW - 2 * 24) // 3
    cols = [
        ("SPACE", draw_satellite,
         "NATO VOWS TO DEFEND SPACE AS RUSSIA ARMS ORBIT",
         "THE ALLIANCE SAYS IT WILL ANSWER THREATS IN ORBIT AFTER REPORTS"
         " OF A NUCLEAR-ARMED LAUNCH."),
        ("COURTS", draw_gavel,
         "SARKOZY AND WIFE CARLA BRUNI ORDERED TO TRIAL",
         "FRENCH OFFICIALS SEND THE EX-PRESIDENT'S CORRUPTION CASE TO"
         " TRIAL; FIRST HEARING 1 APRIL 2027."),
        ("PACIFIC", draw_pact,
         "AUSTRALIA SIGNS SOLOMON ISLANDS PACT",
         "CANBERRA BECOMES THE ISLANDS' MAIN SECURITY PARTNER IN A DEAL"
         " BARRING FOREIGN BASES."),
    ]
    y0 = 634
    for i, (kick, icon, head, body) in enumerate(cols):
        cx = M + i * (col_w + 24)
        icon(cv, cx, y0, 48)
        cv.text(cx + 60, y0 + 16, kick, 2, RED)
        yy = y0 + 56
        yy = cv.para(cx, yy, head, col_w, 3, INK, leading=26)
        yy += 4
        cv.para(cx, yy, body, col_w, 2, INK, leading=18)
        if i < 2:
            cv.vline(cx + col_w + 12, y0, 212, GREY, 1)

    # ---- in brief strip ----
    cv.hline(M, 864, CW, INK, 2)
    cv.text(M, 876, "IN BRIEF", 2, RED)
    briefs = [
        "SEOUL: SOUTH KOREA'S EDUCATION MINISTER QUITS OVER EXAM CHEATING.",
        "THE HAGUE: DUTCH COURT KEEPS BINDING CLIMATE TARGETS DURING APPEAL.",
        "WASHINGTON: HUAWEI GUILTY OF TRADE-SECRET THEFT, CLEARED OF"
        " RACKETEERING.",
    ]
    by = 898
    for i, b in enumerate(briefs):
        bx = M + i * (col_w + 24)
        cv.para(bx, by, b, col_w, 2, INK, leading=18)

    # ---- footer ----
    cv.hline(M, 970, CW, INK, 1)
    cv.text_center(W // 2, 982,
                   "COMPILED FROM WIRE REPORTS - WEDNESDAY, 25 NOVEMBER 2026",
                   2, INK)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    build()
