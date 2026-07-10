"""
GCSE Computer Science – Fundamentals of Data Representation
10 foundational · 10 intermediate · 10 difficult · 10 MCQ (fixed)
Each practice variant returns (question, solution, hint, marks).
MCQ: ten named variants for lesson quiz and quick tests (no duplicate stems).
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import run_mcq_variant, pick_named_variant


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _denary_to_binary(n):
    if n == 0:
        return "0"
    bits = []
    while n > 0:
        bits.append(str(n % 2))
        n //= 2
    return "".join(reversed(bits))


def _binary_to_denary(b):
    return int(b.replace(" ", ""), 2)


def _denary_to_hex(n):
    return format(n, "X")


def _hex_to_denary(h):
    return int(h, 16)


def _pad8(b):
    return b.zfill(8)


_HEX_DIGITS = "0123456789ABCDEF"


def _hex_digit_value(char):
    return _hex_to_denary(char.upper())


def _binary_place_values(length):
    return [2 ** i for i in range(length - 1, -1, -1)]


def _format_binary_table(bits):
    """Place-value row + bit row for GCSE working."""
    places = _binary_place_values(len(bits))
    place_row = " &nbsp; ".join(f"{p:>3}" for p in places)
    bit_row = " &nbsp; ".join(f"{bit:>3}" for bit in bits)
    return (
        f"Place values:&nbsp; <code>{place_row}</code><br>"
        f"Binary:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <code>{bit_row}</code>"
    )


def _solution_binary_to_denary(bits):
    bits = bits.replace(" ", "")
    places = _binary_place_values(len(bits))
    terms = [place for place, bit in zip(places, bits) if bit == "1"]
    total = sum(terms)
    if not terms:
        working = "0"
    elif len(terms) == 1:
        working = str(terms[0])
    else:
        working = " + ".join(str(t) for t in terms)

    return (
        f"Write the place values above each bit (powers of 2 from right to left):<br>"
        f"{_format_binary_table(bits)}<br><br>"
        f"Add the place values where the bit is <strong>1</strong>: "
        f"{working} = <strong>{total}</strong>."
    )


def _solution_denary_to_binary(n):
    if n == 0:
        return "Denary 0 is <strong>0</strong> in binary."

    steps = []
    value = n
    remainders = []
    while value > 0:
        remainder = value % 2
        quotient = value // 2
        steps.append(
            f"{value} ÷ 2 = {quotient} remainder <strong>{remainder}</strong>"
        )
        remainders.append(str(remainder))
        value = quotient

    binary = "".join(reversed(remainders))
    steps_html = "<br>".join(steps)
    return (
        f"Repeatedly divide by 2 and write down each remainder:<br>"
        f"{steps_html}<br><br>"
        f"Read the remainders from <strong>bottom to top</strong>: "
        f"<strong>{binary}</strong>."
    )


def _solution_hex_to_denary(hex_value):
    hex_value = hex_value.upper()
    if len(hex_value) == 1:
        digit = _hex_digit_value(hex_value)
        if hex_value.isdigit():
            return (
                f"Single hex digit <strong>{hex_value}</strong> is the same in denary: "
                f"<strong>{digit}</strong>."
            )
        return (
            f"Hex digit <strong>{hex_value}</strong> = <strong>{digit}</strong> in denary "
            f"(A=10, B=11, C=12, D=13, E=14, F=15)."
        )

    parts = []
    total = 0
    for index, char in enumerate(hex_value):
        power = len(hex_value) - 1 - index
        digit = _hex_digit_value(char)
        contribution = digit * (16 ** power)
        total += contribution
        if power == 0:
            parts.append(f"{char} × 1 = <strong>{digit}</strong>")
        else:
            parts.append(
                f"{char} × 16<sup>{power}</sup> = {digit} × {16 ** power} = "
                f"<strong>{contribution}</strong>"
            )

    parts_html = "<br>".join(parts)
    return (
        f"Convert each hex digit, then multiply by its place value (16<sup>0</sup>, "
        f"16<sup>1</sup>, … from the right):<br>"
        f"{parts_html}<br><br>"
        f"Add the parts: <strong>{total}</strong>."
    )


def _solution_denary_to_hex(n):
    if n == 0:
        return "Denary 0 is <strong>0</strong> in hexadecimal."

    steps = []
    value = n
    digits = []
    while value > 0:
        remainder = value % 16
        quotient = value // 16
        digit = _HEX_DIGITS[remainder]
        if remainder >= 10:
            label = f"{remainder} (letter <strong>{digit}</strong>)"
        else:
            label = str(remainder)
        steps.append(
            f"{value} ÷ 16 = {quotient} remainder <strong>{label}</strong>"
        )
        digits.append(digit)
        value = quotient

    hex_value = "".join(reversed(digits))
    steps_html = "<br>".join(steps)
    return (
        f"Repeatedly divide by 16 and write each remainder (10→A, 11→B, … 15→F):<br>"
        f"{steps_html}<br><br>"
        f"Read the remainders from <strong>bottom to top</strong>: "
        f"<strong>{hex_value}</strong>."
    )


def _solution_hex_to_binary(hex_value, width=None):
    hex_value = hex_value.upper()
    denary = _hex_to_denary(hex_value)
    binary = _denary_to_binary(denary)
    if width:
        binary = binary.zfill(width)

    if len(hex_value) == 1:
        return (
            f"Hex <strong>{hex_value}</strong> = <strong>{denary}</strong> in denary.<br>"
            f"Convert to binary: <strong>{binary}</strong>."
        )

    nybble_parts = []
    for char in hex_value:
        nybble = format(_hex_digit_value(char), "04b")
        nybble_parts.append(f"<strong>{char}</strong> → <code>{nybble}</code>")

    return (
        f"Each hex digit is one nybble (4 bits):<br>"
        f"{'<br>'.join(nybble_parts)}<br><br>"
        f"Join the nybbles: <strong>{binary}</strong>."
    )


def _solution_binary_to_hex(bits, width=8):
    bits = bits.replace(" ", "")
    padded = bits.zfill(width)
    denary = _binary_to_denary(padded)
    hex_value = _denary_to_hex(denary)

    nybble_rows = []
    for index in range(0, len(padded), 4):
        chunk = padded[index:index + 4]
        nybble_rows.append(
            f"<code>{chunk}</code> → <strong>{format(int(chunk, 2), 'X')}</strong>"
        )

    return (
        f"Group into nybbles of 4 bits (from the right), padding if needed:<br>"
        f"{'<br>'.join(nybble_rows)}<br><br>"
        f"Join the hex digits: <strong>{hex_value}</strong> "
        f"(check: {denary} in denary)."
    )


def _solution_binary_add(a, b, answer, denary_a, denary_b, denary_sum):
    return (
        f"Line up the bits and add from the <strong>right</strong>, carrying when a "
        f"column sums to 2 or more (1 + 1 writes <strong>0</strong> and carries "
        f"<strong>1</strong>):<br>"
        f"<code>&nbsp;&nbsp;{a}</code><br>"
        f"<code>+ {b}</code><br>"
        f"<code>------</code><br>"
        f"<code>&nbsp;{answer}</code><br><br>"
        f"Check in denary: {denary_a} + {denary_b} = <strong>{denary_sum}</strong>."
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10)
# ══════════════════════════════════════════════════════════════════════════════

def _dr_f1_denary_to_binary():
    n = random.choice([5, 9, 13, 19, 22, 25, 37, 45])
    q = f"Convert denary <strong>{n}</strong> to binary (no leading zeros required)."
    s = _solution_denary_to_binary(n)
    return q, s, "Same as sharing into groups of 2 — remainder 0 or 1 each time.", 2


def _dr_f2_binary_to_denary():
    vals = ["1010", "1101", "10011", "11110", "101101"]
    b = random.choice(vals)
    q = f"Convert binary <strong>{b}</strong> to denary."
    s = _solution_binary_to_denary(b)
    return q, s, "Think 8, 4, 2, 1 switches — add labels that are ON.", 2


def _dr_f3_hex_to_denary():
    h = random.choice(["A", "B", "C", "D", "E", "F", "1A", "2F", "3C"])
    q = f"Convert hexadecimal <strong>{h}</strong> to denary."
    s = _solution_hex_to_denary(h)
    return q, s, "A=10 … F=15; multiply each digit by 16^position.", 2


def _dr_f4_denary_to_hex():
    n = random.choice([10, 15, 16, 26, 31, 47, 255])
    q = f"Convert denary <strong>{n}</strong> to hexadecimal."
    s = _solution_denary_to_hex(n)
    return q, s, "Divide by 16; remainders 10–15 become A–F.", 2


def _dr_f5_bits_in_byte():
    q = "How many <strong>bits</strong> are in one <strong>byte</strong>?"
    s = "One byte = <strong>8 bits</strong>."
    return q, s, "One byte is the usual size for one English character in memory.", 1


def _dr_f6_bytes_storage():
    bits = random.choice([16, 24, 32, 64])
    bytes_ = bits // 8
    q = f"A file uses <strong>{bits} bits</strong> of storage. How many <strong>bytes</strong> is that?"
    s = f"{bits} ÷ 8 = <strong>{bytes_} bytes</strong>."
    return q, s, "8 bits make 1 byte — divide by 8.", 1


def _dr_f7_binary_add_small():
    """5 + 3 style — matches lesson worked example."""
    pairs = [
        ("101", "11", "1000", 5, 3, 8),
        ("10", "11", "101", 2, 3, 5),
        ("11", "1", "100", 3, 1, 4),
    ]
    a, b, ans, da, db, ds = random.choice(pairs)
    q = (
        f"Add binary <strong>{a}</strong> + <strong>{b}</strong> "
        f"(same as {da} + {db} in denary). Give the answer in binary."
    )
    s = _solution_binary_add(a, b, ans, da, db, ds)
    return q, s, "Start from the right; carry when the column sum is 2 or more.", 2


def _dr_f8_ascii_chars():
    n = random.choice([5, 8, 12, 20])
    bits = n * 7
    q = (
        f"A plain text file has <strong>{n}</strong> characters using "
        f"<strong>7-bit ASCII</strong>. How many <strong>bits</strong> of data?"
    )
    s = f"{n} × 7 = <strong>{bits} bits</strong>."
    return q, s, "Multiply character count by bits per character from the question.", 2


def _dr_f9_max_denary_n_bits():
    n = random.choice([3, 4, 5, 6])
    mx = (2 ** n) - 1
    q = f"What is the <strong>largest denary number</strong> you can store with <strong>{n} bits</strong> (unsigned)?"
    s = f"All bits set to 1: 2^{n} − 1 = <strong>{mx}</strong>."
    return q, s, "Like a 3-wheel lock with 0–7 on each — max is all wheels at max.", 2


def _dr_f10_nybble_hex():
    q = "One hexadecimal digit represents how many <strong>bits</strong>?"
    s = "One hex digit = one nybble = <strong>4 bits</strong>."
    return q, s, "16 values need 4 binary digits — that is why hex shortens binary.", 1


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _dr_i1_binary_to_hex():
    n = random.choice([42, 85, 170, 255])
    b = _denary_to_binary(n)
    q = f"Binary <strong>{_pad8(b)}</strong> (8-bit) → convert to hexadecimal."
    s = _solution_binary_to_hex(b, width=8)
    return q, s, "Split into groups of 4 bits from the right; pad if needed.", 2


def _dr_i2_image_size():
    w, h = random.choice([(800, 600), (640, 480), (1920, 1080)])
    depth = random.choice([8, 16, 24])
    total = w * h * depth
    mb = total / (8 * 1_000_000)
    q = (
        f"Image: <strong>{w} × {h}</strong> pixels, <strong>{depth}-bit</strong> colour depth. "
        "Uncompressed size in <strong>bytes</strong>?"
    )
    s = (
        f"Every pixel stored: {w}×{h}×{depth} = {total} bits. "
        f"÷ 8 = <strong>{total // 8:,} bytes</strong> "
        f"(≈ {mb:.2f} MB if 1 MB = 10⁶ bytes)."
    )
    return q, s, "Multiply width × height × depth, then ÷ 8 for bytes.", 3


def _dr_i3_sound_size():
    rate = random.choice([22050, 44100])
    depth = random.choice([8, 16])
    secs = random.choice([10, 30, 60])
    bits = rate * depth * secs
    bytes_ = bits // 8
    q = (
        f"Sound: sample rate <strong>{rate} Hz</strong>, <strong>{depth}-bit</strong> samples, "
        f"<strong>{secs} seconds</strong> (mono). File size in <strong>bytes</strong>?"
    )
    s = (
        f"Snapshots per second × precision × length: {rate} × {depth} × {secs} = {bits} bits. "
        f"÷ 8 = <strong>{bytes_:,} bytes</strong>."
    )
    return q, s, "Rate × bit depth × seconds (× 2 if stereo).", 3


def _dr_i4_kb_to_bytes():
    kb = random.choice([4, 12, 50, 250])
    b = kb * 1000
    q = f"<strong>{kb} KB</strong> (1 KB = 1000 bytes). How many bytes?"
    s = f"{kb} × 1000 = <strong>{b:,} bytes</strong>."
    return q, s, "Use the value given in the question for KB.", 2


def _dr_i5_binary_add_8bit():
    a = random.randint(20, 100)
    b = random.randint(10, 50)
    if a + b > 255:
        a, b = 90, 40
    ba, bb = _pad8(_denary_to_binary(a)), _pad8(_denary_to_binary(b))
    ans = _pad8(_denary_to_binary(a + b))
    q = (
        f"Add 8-bit binary <strong>{ba}</strong> + <strong>{bb}</strong> "
        f"(denary {a} + {b})."
    )
    s = _solution_binary_add(ba, bb, ans, a, b, a + b)
    return q, s, "Same as denary column addition; 1+1 → 0 carry 1.", 3


def _dr_i6_overflow():
    q = "8-bit unsigned storage holds max <strong>255</strong>. You add 1 to 255. What happens?"
    s = (
        "Value wraps to <strong>0</strong> — <strong>overflow</strong> "
        "(like a car odometer running out of digits)."
    )
    return q, s, "Fixed bits cannot store 256 in 8-bit unsigned.", 2


def _dr_i7_unicode_vs_ascii():
    q = "Why does Unicode use more bits per character than standard ASCII for many languages?"
    s = (
        "Unicode represents <strong>thousands of characters</strong> worldwide; "
        "ASCII only needs <strong>128</strong> English-focused codes."
    )
    return q, s, "More symbols in the table → more bits needed on average.", 2


def _dr_i8_colour_depth_bits():
    colours = random.choice([16, 256, 65536])
    bits = {16: 4, 256: 8, 65536: 16}[colours]
    q = f"An image uses <strong>{colours}</strong> distinct colours. Minimum <strong>colour depth</strong> (bits per pixel)?"
    s = f"2^{bits} = {colours} → need <strong>{bits} bits</strong> per pixel."
    return q, s, "Number of colours = 2^(bits per pixel).", 2


def _dr_i9_compression_type():
    scenarios = [
        ("A photo for a website where tiny size matters more than perfect quality", "lossy", "JPEG-style loss removes detail humans barely notice."),
        ("A program source code archive that must open exactly as saved", "lossless", "Code must be restored bit-for-bit."),
        ("A row of 20 identical white pixels in a simple graphic", "lossless", "Run-length encoding (RLE) can store count + value without losing data."),
    ]
    text, ans, why = random.choice(scenarios)
    q = f"<strong>Scenario:</strong> {text}. <strong>Lossy</strong> or <strong>lossless</strong> compression?"
    s = f"<strong>{ans.capitalize()}</strong> — {why}"
    return q, s, "Lossy = smaller but data lost forever; lossless = exact restore.", 2


def _dr_i10_hex_binary_nybble():
    h = random.choice(["3", "7", "B", "F"])
    q = f"Hex digit <strong>{h}</strong> → 4-bit binary?"
    s = _solution_hex_to_binary(h, width=4)
    return q, s, "Each hex digit maps to exactly four binary digits.", 1


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _dr_d1_large_denary_binary():
    n = random.choice([129, 187, 200, 231])
    b = _denary_to_binary(n)
    q = f"Convert denary <strong>{n}</strong> to an 8-bit binary number."
    s = (
        f"{_solution_denary_to_binary(n)}<br><br>"
        f"Pad with leading zeros to 8 bits: <strong>{_pad8(b)}</strong>."
    )
    return q, s, "Build binary then pad to the required bit width.", 3


def _dr_d2_image_mb():
    w, h = random.choice([(1024, 768), (1280, 720)])
    depth = 24
    bytes_ = w * h * depth // 8
    mb = bytes_ / 1_000_000
    q = (
        f"Uncompressed image <strong>{w}×{h}</strong>, <strong>24-bit</strong> colour. "
        "Size in <strong>MB</strong> (1 MB = 1 000 000 bytes)?"
    )
    s = (
        f"{w}×{h}×24 = {w*h*24} bits → {bytes_:,} bytes → "
        f"<strong>{mb:.2f} MB</strong>."
    )
    return q, s, "Bits → bytes (÷8) → MB (÷1 000 000).", 4


def _dr_d3_stereo_sound():
    rate, depth, secs = 44100, 16, 120
    bits = rate * depth * secs * 2
    bytes_ = bits // 8
    q = (
        f"Stereo sound: <strong>{rate} Hz</strong>, <strong>{depth}-bit</strong>, "
        f"<strong>{secs} s</strong>. Size in <strong>bytes</strong>?"
    )
    s = (
        f"Left + right channel: {rate}×{depth}×{secs}×<strong>2</strong> = {bits} bits. "
        f"Bytes = <strong>{bytes_:,}</strong>."
    )
    return q, s, "Stereo = two channels — multiply by 2 at the end.", 4


def _dr_d4_binary_shift_left():
    b = random.choice(["00010110", "00110001", "00001101"])
    shifted = b[1:] + "0"
    d_before = _binary_to_denary(b)
    d_after = _binary_to_denary(shifted)
    q = f"8-bit value <strong>{b}</strong> is shifted left one place (new bit 0 on the right). New denary value?"
    s = (
        f"Value before shift:<br>{_solution_binary_to_denary(b)}<br><br>"
        f"Shift left: every bit moves one place left and a <strong>0</strong> is added on the "
        f"right → <code>{shifted}</code>.<br><br>"
        f"New value: {_solution_binary_to_denary(shifted)}<br><br>"
        f"Shifting left once <strong>doubles</strong> the value: "
        f"{d_before} × 2 = <strong>{d_after}</strong>."
    )
    return q, s, "Like writing 37 then 370 — shifting left multiplies by 2.", 3


def _dr_d5_hex_binary_full():
    h = random.choice(["2A", "B4", "FF", "3D"])
    q = f"Convert hex <strong>{h}</strong> to 8-bit binary."
    s = _solution_hex_to_binary(h, width=8)
    return q, s, "Hex → denary → binary; pad to 8 bits.", 3


def _dr_d6_storage_multiple_files():
    photos = random.randint(3, 8)
    mb_each = random.choice([2, 3, 4])
    total = photos * mb_each
    q = f"<strong>{photos}</strong> photos each <strong>{mb_each} MB</strong>. Total storage in MB?"
    s = f"{photos} × {mb_each} = <strong>{total} MB</strong>."
    return q, s, "Multiply file size by count.", 2


def _dr_d7_bits_for_text_unicode():
    chars = random.choice([100, 250, 500])
    bytes_ = chars * 2
    q = (
        f"A Unicode text file stores each character in <strong>2 bytes</strong>. "
        f"<strong>{chars}</strong> characters → how many <strong>bytes</strong>?"
    )
    s = f"{chars} × 2 = <strong>{bytes_} bytes</strong>."
    return q, s, "Bytes per character × number of characters.", 2


def _dr_d8_overflow_add():
    q = "In 4-bit unsigned binary, <strong>1111</strong> + <strong>0001</strong>. What is the 4-bit result?"
    s = "15 + 1 = 16, but only 4 bits kept → <strong>0000</strong> (overflow)."
    return q, s, "Only the lowest n bits are stored — extra bits are lost.", 3


def _dr_d9_colours_from_depth():
    bits = random.choice([6, 10, 12])
    colours = 2 ** bits
    q = f"Colour depth <strong>{bits} bits</strong> per pixel. Maximum number of colours?"
    s = f"2^{bits} = <strong>{colours}</strong> colours."
    return q, s, "Each bit doubles the number of colour choices.", 2


def _dr_d10_lossy_lossless_compare():
    q = "State <strong>one advantage</strong> of lossy compression and <strong>one advantage</strong> of lossless."
    s = (
        "<strong>Lossy:</strong> much smaller files (photos/audio streaming). "
        "<strong>Lossless:</strong> perfect reconstruction (programs, ZIP, RLE graphics)."
    )
    return q, s, "Compare file size vs getting the exact original back.", 3


def _dr_d11_sample_rate_calc():
    rate = random.choice([22050, 44100])
    seconds = random.randint(2, 5)
    depth = 16
    size_bits = rate * seconds * depth
    q = (
        f"A <strong>mono</strong> sound clip lasts <strong>{seconds} seconds</strong> at "
        f"<strong>{rate} Hz</strong> sample rate and <strong>{depth}-bit</strong> depth. "
        f"How many <strong>bits</strong> of uncompressed audio data?"
    )
    s = f"{rate} × {seconds} × {depth} = <strong>{size_bits:,} bits</strong>."
    return q, s, "Sample rate × duration × bit depth (mono).", 3


def _dr_d12_metadata_vs_payload():
    q = (
        "A JPEG photo file includes <strong>EXIF metadata</strong> (camera model, GPS) "
        "alongside the compressed image data. Explain one reason metadata is useful and "
        "one <strong>privacy</strong> concern."
    )
    s = (
        "<strong>Useful:</strong> sorting photos by date/location, editing software knows camera settings. "
        "<strong>Privacy:</strong> GPS or device info may reveal <strong>where/when</strong> a photo was taken when shared online."
    )
    return q, s, "Metadata is extra data about the file, not the main image pixels.", 3


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _dr_d13_multipart_number_systems():
    n = random.choice([150, 172, 198, 205, 219])
    binary = _pad8(_denary_to_binary(n))
    hex_value = _denary_to_hex(n)
    q = (
        f"A sensor stores the denary reading <strong>{n}</strong> in a single byte.<br><br>"
        f"<strong>a)</strong> Convert <strong>{n}</strong> to an 8-bit binary number. "
        f"Show your working. [2]<br>"
        f"<strong>b)</strong> Convert your 8-bit answer from part (a) to hexadecimal. [2]<br>"
        f"<strong>c)</strong> State one reason programmers often write byte values in "
        f"hexadecimal rather than binary. [2]"
    )
    s = (
        f"<strong>a)</strong> {_solution_denary_to_binary(n)}<br>"
        f"Pad to 8 bits: <strong>{binary}</strong>.<br><br>"
        f"<strong>b)</strong> {_solution_binary_to_hex(binary, width=8)}<br><br>"
        f"<strong>c)</strong> Hexadecimal is much <strong>shorter and easier to read</strong> "
        f"than binary (one hex digit replaces four bits), so there are fewer digits to write "
        f"and <strong>fewer mistakes</strong> when copying values."
    )
    return q, s, "Divide by 2 for (a), group bits into nybbles for (b).", 6


def _dr_d14_multipart_image_size():
    w, h = random.choice([(100, 80), (200, 150), (160, 120)])
    depth = random.choice([8, 16, 24])
    total_bits = w * h * depth
    total_bytes = total_bits // 8
    total_kb = total_bytes / 1000
    q = (
        f"An uncompressed bitmap image is <strong>{w} × {h}</strong> pixels with a colour "
        f"depth of <strong>{depth} bits</strong> per pixel.<br><br>"
        f"<strong>a)</strong> Calculate the total number of pixels in the image. [1]<br>"
        f"<strong>b)</strong> Calculate the file size in <strong>bytes</strong>. "
        f"Show your working. [3]<br>"
        f"<strong>c)</strong> The image is edited to use a colour depth of "
        f"<strong>{depth * 2} bits</strong> instead. State the effect on the file size. [2]"
    )
    s = (
        f"<strong>a)</strong> Pixels = width × height = {w} × {h} = "
        f"<strong>{w * h:,}</strong> pixels.<br><br>"
        f"<strong>b)</strong> Total bits = pixels × colour depth = "
        f"{w * h:,} × {depth} = {total_bits:,} bits.<br>"
        f"Convert to bytes (÷ 8): {total_bits:,} ÷ 8 = "
        f"<strong>{total_bytes:,} bytes</strong> (≈ {total_kb:.1f} KB).<br><br>"
        f"<strong>c)</strong> Doubling the colour depth <strong>doubles the file size</strong>, "
        f"because each pixel now needs twice as many bits to store its colour."
    )
    return q, s, "Pixels × depth = bits; ÷ 8 for bytes. Depth is directly proportional to size.", 6


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (12 fixed — 3 foundational, 5 intermediate, 4 difficult)
# ══════════════════════════════════════════════════════════════════════════════

_DR_MCQ_BANK = [
    {
        "difficulty": "foundational",
        "q": "How many bits are in one byte?",
        "opts": ["A  4", "B  8", "C  16", "D  1000"],
        "ans": "B", "marks": 1,
        "sol": "1 byte = <strong>8 bits</strong>. Answer: <strong>B</strong>",
        "hint": "One byte is eight bits in GCSE definitions.",
    },
    {
        "difficulty": "foundational",
        "q": "Denary 13 in binary is:",
        "opts": ["A  1011", "B  1101", "C  1110", "D  1100"],
        "ans": "B", "marks": 2,
        "sol": (
            "13 ÷ 2 = 6 remainder <strong>1</strong><br>"
            "6 ÷ 2 = 3 remainder <strong>0</strong><br>"
            "3 ÷ 2 = 1 remainder <strong>1</strong><br>"
            "1 ÷ 2 = 0 remainder <strong>1</strong><br>"
            "Read bottom to top → <strong>1101</strong>. Answer: <strong>B</strong>"
        ),
        "hint": "Divide 13 by 2 and read remainders upwards.",
    },
    {
        "difficulty": "foundational",
        "q": "Binary 101 + 11 equals (same as 5 + 3 in denary):",
        "opts": ["A  1000", "B  110", "C  111", "D  1010"],
        "ans": "A", "marks": 2,
        "sol": (
            "<code>&nbsp;101</code><br>"
            "<code>+&nbsp;11</code><br>"
            "<code>-----</code><br>"
            "<code>1000</code><br>"
            "Check: 5 + 3 = 8. Answer: <strong>A</strong>"
        ),
        "hint": "Add columns from the right; 1+1 writes 0 and carries 1.",
    },
    {
        "difficulty": "intermediate",
        "q": "Hexadecimal F in denary is:",
        "opts": ["A  14", "B  15", "C  16", "D  255"],
        "ans": "B", "marks": 1,
        "sol": "F = <strong>15</strong>. Answer: <strong>B</strong>",
        "hint": "A=10 through F=15.",
    },
    {
        "difficulty": "intermediate",
        "q": "Uncompressed image size in bits equals:",
        "opts": ["A  width + height + depth", "B  width × height × colour depth",
                 "C  width × depth only", "D  height ÷ depth"],
        "ans": "B", "marks": 2,
        "sol": "Every pixel: <strong>width × height × depth</strong>. Answer: <strong>B</strong>",
        "hint": "Count every pixel’s colour bits.",
    },
    {
        "difficulty": "intermediate",
        "q": "Doubling sample rate (same duration, bit depth, mono) will:",
        "opts": ["A  halve file size", "B  keep file size the same",
                 "C  double file size", "D  quarter file size"],
        "ans": "C", "marks": 2,
        "sol": "More snapshots per second → <strong>double</strong> the data. Answer: <strong>C</strong>",
        "hint": "Sample rate is in the sound size formula.",
    },
    {
        "difficulty": "intermediate",
        "q": "Unicode is used instead of basic ASCII mainly because Unicode:",
        "opts": ["A  uses fewer bits for every character",
                 "B  represents many more characters worldwide",
                 "C  only stores images", "D  cannot represent English"],
        "ans": "B", "marks": 2,
        "sol": "Global character set. Answer: <strong>B</strong>",
        "hint": "Think emoji and non-English scripts.",
    },
    {
        "difficulty": "difficult",
        "q": "Maximum denary value in 6 unsigned bits:",
        "opts": ["A  32", "B  63", "C  64", "D  127"],
        "ans": "B", "marks": 2,
        "sol": "2⁶−1 = <strong>63</strong>. Answer: <strong>B</strong>",
        "hint": "All bits 1 gives max value.",
    },
    {
        "difficulty": "difficult",
        "q": "Binary 1111 + 0001 in 4-bit storage gives:",
        "opts": ["A  10000", "B  11110", "C  0000", "D  1111"],
        "ans": "C", "marks": 2,
        "sol": "16 in 4 bits wraps to <strong>0000</strong>. Answer: <strong>C</strong>",
        "hint": "Odometer overflow — only 4 bits kept.",
    },
    {
        "difficulty": "difficult",
        "q": "Lossy compression:",
        "opts": ["A  restores data perfectly", "B  never reduces file size",
                 "C  permanently removes some data", "D  is only for text"],
        "ans": "C", "marks": 2,
        "sol": "Some data is discarded forever. Answer: <strong>C</strong>",
        "hint": "JPEG/MP3 style — cannot get every original bit back.",
    },
    {
        "difficulty": "intermediate",
        "q": "1 KB (binary) equals how many bytes?",
        "opts": ["A  1000", "B  1024", "C  8", "D  512"],
        "ans": "B", "marks": 2,
        "sol": "1 KB = 2¹⁰ = <strong>1024 bytes</strong>. Answer: <strong>B</strong>",
        "hint": "Binary prefixes use powers of 2.",
    },
    {
        "difficulty": "difficult",
        "q": "Run-length encoding (RLE) is most effective on images with:",
        "opts": ["A  long runs of identical pixels", "B  every pixel a different colour",
                 "C  no repeated data", "D  only text characters"],
        "ans": "A", "marks": 2,
        "sol": "RLE stores <strong>repeated values</strong> efficiently. Answer: <strong>A</strong>",
        "hint": "Think simple graphics with large blocks of one colour.",
    },
    {
        "difficulty": "foundational",
        "q": "The largest denary value stored in 4 unsigned bits is:",
        "opts": ["A  8", "B  15", "C  16", "D  31"],
        "ans": "B", "marks": 2,
        "sol": "2⁴ − 1 = <strong>15</strong> (1111). Answer: <strong>B</strong>",
        "hint": "All four bits set to 1.",
    },
    {
        "difficulty": "foundational",
        "q": "Binary 1010 in denary is:",
        "opts": ["A  8", "B  10", "C  12", "D  20"],
        "ans": "B", "marks": 2,
        "sol": "8 + 2 = <strong>10</strong>. Answer: <strong>B</strong>",
        "hint": "Add place values where bits are 1.",
    },
    {
        "difficulty": "intermediate",
        "q": "Denary 255 in hexadecimal is:",
        "opts": ["A  EE", "B  FF", "C  255", "D  F0"],
        "ans": "B", "marks": 2,
        "sol": "255 = <strong>FF</strong>. Answer: <strong>B</strong>",
        "hint": "Two hex digits fit 0–255.",
    },
    {
        "difficulty": "intermediate",
        "q": "Increasing colour depth from 8 bits to 16 bits per pixel:",
        "opts": ["A  halves image file size", "B  doubles the bits per pixel",
                 "C  removes colour information", "D  only affects sound files"],
        "ans": "B", "marks": 2,
        "sol": "More bits per pixel → <strong>double the colour data</strong>. Answer: <strong>B</strong>",
        "hint": "Colour depth is in the image size formula.",
    },
    {
        "difficulty": "difficult",
        "q": "Lossless compression:",
        "opts": ["A  permanently deletes data", "B  reduces size and can restore the original exactly",
                 "C  only works on video", "D  always increases file size"],
        "ans": "B", "marks": 2,
        "sol": "Original can be rebuilt <strong>perfectly</strong>. Answer: <strong>B</strong>",
        "hint": "PNG and ZIP are lossless examples.",
    },
]


def _make_mcq_variant(item, index):
    """One fixed MCQ per bank row (unique stem for lesson quiz)."""
    def _variant():
        return (
            item["q"],
            item["sol"],
            item.get("hint", ""),
            item.get("marks", 1),
            item["opts"],
            item["ans"],
        )

    _variant.__name__ = f"data_rep_mcq_{index + 1}"
    _variant._mcq_difficulty = item["difficulty"]
    _variant._fixed_stem = True
    return _variant


_MCQ_VARIANTS_ALL = [_make_mcq_variant(item, i) for i, item in enumerate(_DR_MCQ_BANK)]


def data_rep_mcq():
    """Random MCQ (legacy); prefer named variants for quizzes."""
    item = random.choice(_DR_MCQ_BANK)
    return item["q"], item["sol"], item.get("hint", ""), item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _dr_f1_denary_to_binary, _dr_f2_binary_to_denary, _dr_f3_hex_to_denary,
    _dr_f4_denary_to_hex, _dr_f5_bits_in_byte, _dr_f6_bytes_storage,
    _dr_f7_binary_add_small, _dr_f8_ascii_chars, _dr_f9_max_denary_n_bits,
    _dr_f10_nybble_hex,
]

_INTERMEDIATE = [
    _dr_i1_binary_to_hex, _dr_i2_image_size, _dr_i3_sound_size,
    _dr_i4_kb_to_bytes, _dr_i5_binary_add_8bit, _dr_i6_overflow,
    _dr_i7_unicode_vs_ascii, _dr_i8_colour_depth_bits,
    _dr_i9_compression_type, _dr_i10_hex_binary_nybble,
]

_DIFFICULT = [
    _dr_d1_large_denary_binary, _dr_d2_image_mb, _dr_d3_stereo_sound,
    _dr_d4_binary_shift_left, _dr_d5_hex_binary_full, _dr_d6_storage_multiple_files,
    _dr_d7_bits_for_text_unicode, _dr_d8_overflow_add, _dr_d9_colours_from_depth,
    _dr_d10_lossy_lossless_compare, _dr_d11_sample_rate_calc, _dr_d12_metadata_vs_payload,
    _dr_d13_multipart_number_systems, _dr_d14_multipart_image_size,
]

_PRACTICE_POOLS = {
    "foundational": _FOUNDATIONAL,
    "intermediate": _INTERMEDIATE,
    "difficult": _DIFFICULT,
}


def gcse_data_rep_variants(difficulty, mode="practice"):
    if mode == "mcq":
        # Ten fixed stems; lesson quiz filters by difficulty when generating.
        return list(_MCQ_VARIANTS_ALL)

    pool = _PRACTICE_POOLS.get(difficulty)
    if not pool:
        combined = _FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT
        return random.sample(combined, min(10, len(combined)))

    return random.sample(pool, len(pool))


def gcse_data_rep(difficulty, mode, variant_name=None):
    if mode == "mcq":
        variants = gcse_data_rep_variants(difficulty, "mcq")
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            "gcse", "cs", "data_rep",
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_data_rep_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        "gcse", "cs", "data_rep",
    )
