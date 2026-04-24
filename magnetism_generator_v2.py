import random
import math

# -----------------------------------------------
# SVG HELPER FUNCTIONS
# -----------------------------------------------

def svg_wire_field_lines():
    """Concentric circles around a wire with current dot (out of page)"""
    return r"""<svg width="160" height="160" viewBox="0 0 160 160" style="margin:10px 0;display:block">
  <circle cx="80" cy="80" r="30" fill="none" stroke="#01696f" stroke-width="1.5" stroke-dasharray="4,3"/>
  <circle cx="80" cy="80" r="50" fill="none" stroke="#01696f" stroke-width="1.5" stroke-dasharray="4,3"/>
  <circle cx="80" cy="80" r="68" fill="none" stroke="#01696f" stroke-width="1" stroke-dasharray="4,3"/>
  <!-- wire cross-section -->
  <circle cx="80" cy="80" r="10" fill="#f9f8f5" stroke="#333" stroke-width="2"/>
  <!-- dot = current out of page -->
  <circle cx="80" cy="80" r="3" fill="#333"/>
  <!-- arrows on field lines -->
  <polygon points="110,77 110,83 117,80" fill="#01696f"/>
  <polygon points="50,77 50,83 43,80" fill="#01696f"/>
  <text x="80" y="152" text-anchor="middle" font-size="11" fill="#555" font-family="sans-serif">Current out of page (⊙)</text>
</svg>"""

def svg_wire_into_page():
    """Concentric circles, current into page"""
    return r"""<svg width="160" height="160" viewBox="0 0 160 160" style="margin:10px 0;display:block">
  <circle cx="80" cy="80" r="30" fill="none" stroke="#01696f" stroke-width="1.5" stroke-dasharray="4,3"/>
  <circle cx="80" cy="80" r="50" fill="none" stroke="#01696f" stroke-width="1.5" stroke-dasharray="4,3"/>
  <circle cx="80" cy="80" r="68" fill="none" stroke="#01696f" stroke-width="1" stroke-dasharray="4,3"/>
  <circle cx="80" cy="80" r="10" fill="#f9f8f5" stroke="#333" stroke-width="2"/>
  <!-- cross = current into page -->
  <line x1="74" y1="74" x2="86" y2="86" stroke="#333" stroke-width="2"/>
  <line x1="86" y1="74" x2="74" y2="86" stroke="#333" stroke-width="2"/>
  <!-- arrows clockwise -->
  <polygon points="110,83 110,77 117,80" fill="#01696f"/>
  <polygon points="50,83 50,77 43,80" fill="#01696f"/>
  <text x="80" y="152" text-anchor="middle" font-size="11" fill="#555" font-family="sans-serif">Current into page (⊗)</text>
</svg>"""

def svg_solenoid():
    """Simplified solenoid with field lines inside"""
    return r"""<svg width="240" height="100" viewBox="0 0 240 100" style="margin:10px 0;display:block">
  <!-- field lines inside -->
  <line x1="30" y1="50" x2="210" y2="50" stroke="#01696f" stroke-width="1.5" stroke-dasharray="6,3"/>
  <line x1="30" y1="38" x2="210" y2="38" stroke="#01696f" stroke-width="1" stroke-dasharray="6,3" opacity="0.6"/>
  <line x1="30" y1="62" x2="210" y2="62" stroke="#01696f" stroke-width="1" stroke-dasharray="6,3" opacity="0.6"/>
  <!-- arrow on central line -->
  <polygon points="200,47 200,53 210,50" fill="#01696f"/>
  <!-- coil windings (simplified arcs) -->
  <path d="M40,25 Q50,50 40,75" fill="none" stroke="#555" stroke-width="2"/>
  <path d="M60,25 Q70,50 60,75" fill="none" stroke="#555" stroke-width="2"/>
  <path d="M80,25 Q90,50 80,75" fill="none" stroke="#555" stroke-width="2"/>
  <path d="M100,25 Q110,50 100,75" fill="none" stroke="#555" stroke-width="2"/>
  <path d="M120,25 Q130,50 120,75" fill="none" stroke="#555" stroke-width="2"/>
  <path d="M140,25 Q150,50 140,75" fill="none" stroke="#555" stroke-width="2"/>
  <path d="M160,25 Q170,50 160,75" fill="none" stroke="#555" stroke-width="2"/>
  <path d="M180,25 Q190,50 180,75" fill="none" stroke="#555" stroke-width="2"/>
  <!-- N and S labels -->
  <text x="15" y="54" font-size="13" font-weight="bold" fill="#a12c7b" font-family="sans-serif">S</text>
  <text x="218" y="54" font-size="13" font-weight="bold" fill="#a13544" font-family="sans-serif">N</text>
  <text x="120" y="92" text-anchor="middle" font-size="11" fill="#555" font-family="sans-serif">Uniform field inside solenoid →</text>
</svg>"""

def svg_circular_motion(r_label="r", direction="anticlockwise"):
    """Charged particle in circular motion in a magnetic field"""
    cx, cy = 100, 100
    r = 55
    arrow_rot = -30 if direction == "anticlockwise" else 30
    return rf"""<svg width="200" height="200" viewBox="0 0 200 200" style="margin:10px 0;display:block">
  <!-- field dots (B out of page) -->
  {''.join(f'<text x="{x}" y="{y}" font-size="10" fill="#6b9" font-family="sans-serif">⊙</text>' 
           for x,y in [(15,20),(50,20),(85,20),(120,20),(155,20),(185,20),
                        (15,55),(185,55),(15,90),(185,90),(15,125),(185,125),
                        (15,160),(50,160),(85,160),(120,160),(155,160),(185,160)])}
  <!-- circular path -->
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#01696f" stroke-width="2" stroke-dasharray="5,3"/>
  <!-- radius line -->
  <line x1="{cx}" y1="{cy}" x2="{cx+r}" y2="{cy}" stroke="#888" stroke-width="1" stroke-dasharray="3,2"/>
  <text x="{cx + r//2 - 4}" y="{cy - 5}" font-size="11" fill="#888" font-family="sans-serif">{r_label}</text>
  <!-- particle -->
  <circle cx="{cx+r}" cy="{cy}" r="6" fill="#a13544"/>
  <!-- velocity arrow (upward for anticlockwise) -->
  <line x1="{cx+r}" y1="{cy}" x2="{cx+r}" y2="{cy-28}" stroke="#333" stroke-width="2" marker-end="url(#arr)"/>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
    <polygon points="0,0 8,4 0,8" fill="#333"/></marker></defs>
  <text x="{cx+r+8}" y="{cy-14}" font-size="11" fill="#333" font-family="sans-serif">v</text>
  <!-- centre dot -->
  <circle cx="{cx}" cy="{cy}" r="3" fill="#333"/>
  <!-- B label -->
  <text x="155" y="100" font-size="12" font-weight="bold" fill="#6b9" font-family="sans-serif">B ⊙</text>
</svg>"""

def svg_velocity_selector():
    """Velocity selector: parallel plates + crossed E and B fields"""
    return r"""<svg width="240" height="160" viewBox="0 0 240 160" style="margin:10px 0;display:block">
  <!-- plates -->
  <rect x="20" y="20" width="200" height="12" fill="#888" rx="2"/>
  <rect x="20" y="128" width="200" height="12" fill="#888" rx="2"/>
  <!-- E field arrows (downward, from + to -) -->
  <line x1="60" y1="38" x2="60" y2="122" stroke="#a13544" stroke-width="1.5" marker-end="url(#earr)"/>
  <line x1="100" y1="38" x2="100" y2="122" stroke="#a13544" stroke-width="1.5" marker-end="url(#earr)"/>
  <line x1="140" y1="38" x2="140" y2="122" stroke="#a13544" stroke-width="1.5" marker-end="url(#earr)"/>
  <line x1="180" y1="38" x2="180" y2="122" stroke="#a13544" stroke-width="1.5" marker-end="url(#earr)"/>
  <!-- B field dots (out of page) -->
  <text x="72" y="88" font-size="13" fill="#01696f" font-family="sans-serif">⊙</text>
  <text x="112" y="88" font-size="13" fill="#01696f" font-family="sans-serif">⊙</text>
  <text x="152" y="88" font-size="13" fill="#01696f" font-family="sans-serif">⊙</text>
  <!-- particle beam -->
  <line x1="20" y1="80" x2="220" y2="80" stroke="#333" stroke-width="2" marker-end="url(#varr)"/>
  <!-- labels -->
  <text x="8" y="28" font-size="11" font-weight="bold" fill="#a13544" font-family="sans-serif">+</text>
  <text x="8" y="138" font-size="11" font-weight="bold" fill="#a13544" font-family="sans-serif">−</text>
  <text x="42" y="70" font-size="11" fill="#a13544" font-family="sans-serif">E</text>
  <text x="170" y="70" font-size="11" fill="#01696f" font-family="sans-serif">B</text>
  <text x="222" y="84" font-size="11" fill="#333" font-family="sans-serif">v</text>
  <defs>
    <marker id="earr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><polygon points="0,0 8,4 0,8" fill="#a13544"/></marker>
    <marker id="varr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><polygon points="0,0 8,4 0,8" fill="#333"/></marker>
  </defs>
</svg>"""

def svg_cyclotron():
    """Two D-shaped dees with alternating field and spiral path"""
    return r"""<svg width="240" height="220" viewBox="0 0 240 220" style="margin:10px 0;display:block">
  <!-- Dee 1 (left half) -->
  <path d="M120,30 A90,90 0 0,0 120,190" fill="#e8f4f5" stroke="#01696f" stroke-width="2"/>
  <!-- Dee 2 (right half) -->
  <path d="M120,30 A90,90 0 0,1 120,190" fill="#fef0f0" stroke="#a13544" stroke-width="2"/>
  <!-- gap label -->
  <line x1="120" y1="30" x2="120" y2="190" stroke="#888" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="124" y="112" font-size="10" fill="#888" font-family="sans-serif">gap</text>
  <!-- spiral path (approximate) -->
  <path d="M120,110 Q140,95 155,110 Q165,130 145,148 Q120,162 95,148 Q72,128 80,105 Q90,78 120,68 Q155,58 175,85 Q192,115 178,148 Q160,180 120,188" 
        fill="none" stroke="#555" stroke-width="1.5" stroke-dasharray="3,2"/>
  <!-- B field labels -->
  <text x="60" y="112" font-size="12" font-weight="bold" fill="#01696f" font-family="sans-serif">B ⊙</text>
  <text x="155" y="112" font-size="12" font-weight="bold" fill="#a13544" font-family="sans-serif">B ⊗</text>
  <!-- particle start -->
  <circle cx="120" cy="110" r="4" fill="#333"/>
  <!-- caption -->
  <text x="120" y="212" text-anchor="middle" font-size="11" fill="#555" font-family="sans-serif">Cyclotron — spiral outward path</text>
</svg>"""

def svg_flhr(current_dir="right", field_dir="up", force_dir="out"):
    """Fleming's Left Hand Rule diagram with labelled arrows"""
    arrows = {
        "right":  (1,0), "left": (-1,0), "up": (0,-1), "down": (0,1),
        "out":    (0.7,-0.7), "in": (-0.7,0.7)
    }
    cx, cy = 120, 100
    scale = 55
    colors = {"current": "#a13544", "field": "#01696f", "force": "#333"}
    labels = {"current": f"I ({current_dir})", "field": f"B ({field_dir})", "force": f"F ({force_dir})"}
    dirs = {"current": current_dir, "field": field_dir, "force": force_dir}
    lines = []
    for name, color in colors.items():
        dx, dy = arrows[dirs[name]]
        x2, y2 = cx + dx*scale, cy + dy*scale
        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{color}" stroke-width="2.5" marker-end="url(#{name}arr)"/>')
        lx, ly = cx + dx*(scale+16), cy + dy*(scale+16)
        lines.append(f'<text x="{lx:.0f}" y="{ly:.0f}" font-size="10" fill="{color}" text-anchor="middle" font-family="sans-serif">{labels[name]}</text>')
    defs = ''.join([
        f'<marker id="{n}arr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><polygon points="0,0 8,4 0,8" fill="{c}"/></marker>'
        for n, c in colors.items()
    ])
    return f'<svg width="240" height="200" viewBox="0 0 240 200" style="margin:10px 0;display:block"><defs>{defs}</defs>{"".join(lines)}<circle cx="{cx}" cy="{cy}" r="4" fill="#555"/><text x="120" y="192" text-anchor="middle" font-size="10" fill="#555" font-family="sans-serif">Fleming\'s Left Hand Rule</text></svg>'

def svg_hall_probe():
    """Hall probe diagram showing charge separation"""
    return r"""<svg width="220" height="160" viewBox="0 0 220 160" style="margin:10px 0;display:block">
  <!-- probe body -->
  <rect x="60" y="40" width="100" height="80" fill="#e8f4f5" stroke="#01696f" stroke-width="2" rx="3"/>
  <!-- current arrow (left to right) -->
  <line x1="20" y1="80" x2="55" y2="80" stroke="#a13544" stroke-width="2" marker-end="url(#iarr)"/>
  <line x1="165" y1="80" x2="200" y2="80" stroke="#a13544" stroke-width="2" marker-end="url(#iarr)"/>
  <text x="12" y="74" font-size="11" fill="#a13544" font-family="sans-serif">I</text>
  <!-- B field (downward into probe) -->
  <text x="90" y="60" font-size="13" fill="#01696f" font-family="sans-serif">⊗</text>
  <text x="120" y="60" font-size="13" fill="#01696f" font-family="sans-serif">⊗</text>
  <text x="150" y="60" font-size="11" fill="#01696f" font-family="sans-serif">B</text>
  <!-- charge buildup -->
  <text x="110" y="52" font-size="12" font-weight="bold" fill="#a13544" font-family="sans-serif">+ + +</text>
  <text x="110" y="115" font-size="12" font-weight="bold" fill="#01696f" font-family="sans-serif">− − −</text>
  <!-- Hall voltage arrow -->
  <line x1="58" y1="48" x2="58" y2="112" stroke="#888" stroke-width="1.5" stroke-dasharray="3,2"/>
  <text x="30" y="84" font-size="11" fill="#888" font-family="sans-serif">V_H</text>
  <defs>
    <marker id="iarr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><polygon points="0,0 8,4 0,8" fill="#a13544"/></marker>
  </defs>
  <text x="110" y="152" text-anchor="middle" font-size="11" fill="#555" font-family="sans-serif">Hall probe cross-section</text>
</svg>"""

def svg_fil_angle(theta=30):
    """Wire at angle theta to field lines"""
    rad = math.radians(theta)
    cx, cy = 120, 100
    L = 60
    dx = L * math.cos(rad)
    dy = L * math.sin(rad)
    x1, y1 = cx - dx, cy + dy
    x2, y2 = cx + dx, cy - dy
    # field lines (horizontal)
    field_lines = ''.join([
        f'<line x1="20" y1="{y}" x2="220" y2="{y}" stroke="#01696f" stroke-width="1" opacity="0.4"/>'
        for y in [40, 65, 90, 115, 140]
    ])
    return f"""<svg width="240" height="180" viewBox="0 0 240 180" style="margin:10px 0;display:block">
  {field_lines}
  <!-- B label -->
  <polygon points="205,88 205,92 215,90" fill="#01696f"/>
  <text x="195" y="86" font-size="11" fill="#01696f" font-family="sans-serif">B</text>
  <!-- wire -->
  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#a13544" stroke-width="3" stroke-linecap="round"/>
  <!-- current arrow along wire -->
  <polygon points="{cx-4:.1f},{cy+4:.1f} {cx+4:.1f},{cy-4:.1f} {x2:.1f},{y2:.1f}" fill="#a13544" opacity="0.5"/>
  <!-- angle arc -->
  <path d="M {cx+30:.1f},{cy} A 30,30 0 0,0 {cx+30*math.cos(rad):.1f},{cy-30*math.sin(rad):.1f}" fill="none" stroke="#888" stroke-width="1.5"/>
  <text x="{cx+32:.0f}" y="{cy-8}" font-size="11" fill="#888" font-family="sans-serif">θ={theta}°</text>
  <text x="120" y="172" text-anchor="middle" font-size="11" fill="#555" font-family="sans-serif">Wire at angle θ to field B</text>
</svg>"""

# -----------------------------------------------
# FOUNDATIONAL (10 questions)
# -----------------------------------------------

def mag_found_force_on_conductor():
    B = round(random.uniform(0.1, 2.0), 2)
    I = random.randint(2, 20)
    L = round(random.uniform(0.1, 1.0), 2)
    F = round(B * I * L, 3)
    q = (rf"A straight conductor of length <strong>{L} m</strong> carries a current of <strong>{I} A</strong> "
         rf"perpendicular to a uniform magnetic field of flux density <strong>{B} T</strong>. "
         rf"Calculate the force on the conductor.")
    s = rf"Using F = BIL:<br>F = {B} × {I} × {L} = <strong>{F} N</strong>"
    hint = r"<strong>F = BIL</strong> when conductor is perpendicular to <strong>B</strong>. For an angle θ, use F = BIL sinθ."
    return q, s, hint, 2

def mag_found_force_on_conductor_b():
    """Reverse: find B given F, I, L"""
    F = round(random.uniform(0.5, 10.0), 2)
    I = random.randint(2, 15)
    L = round(random.uniform(0.2, 1.0), 2)
    B = round(F / (I * L), 3)
    q = (rf"A straight conductor of length <strong>{L} m</strong> carrying a current of <strong>{I} A</strong> "
         rf"perpendicular to a magnetic field experiences a force of <strong>{F} N</strong>. "
         rf"Calculate the magnetic flux density.")
    s = rf"Rearranging F = BIL:<br>B = F / IL = {F} / ({I} × {L}) = <strong>{B} T</strong>"
    hint = r"Rearrange <strong>F = BIL</strong> → <strong>B = F / IL</strong>."
    return q, s, hint, 2

def mag_found_flhr_a():
    scenario = ("current flowing East, field pointing vertically upward", "out of the page (North)", "right")
    diagram = svg_flhr("right", "up", "out")
    q = (rf"The diagram shows a current-carrying conductor.<br>{diagram}<br>"
         rf"The current flows <strong>East</strong> and the magnetic field points <strong>vertically upward</strong>. "
         rf"Use Fleming's Left Hand Rule to state the direction of the force.")
    s = rf"The force acts <strong>out of the page</strong>.<br><br>First finger (B) → upward. Second finger (I) → East. Thumb (F) → out of page."
    hint = r"<strong>FLHR</strong>: First finger = field B, seCond finger = Current I, thuMb = Motion (force F)."
    return q, s, hint, 2

def mag_found_flhr_b():
    diagram = svg_flhr("up", "right", "out")
    q = (rf"The diagram shows a current-carrying conductor.<br>{diagram}<br>"
         rf"The current flows <strong>vertically upward</strong> and the magnetic field points <strong>East</strong>. "
         rf"Use Fleming's Left Hand Rule to state the direction of the force.")
    s = rf"The force acts <strong>out of the page / North</strong>.<br><br>First finger (B) → East. Second finger (I) → up. Thumb (F) → out of page."
    hint = r"<strong>FLHR</strong>: First finger = B (East), seCond finger = I (up), thuMb = force direction."
    return q, s, hint, 2

def mag_found_flhr_c():
    scenarios = [
        ("South", "into the page", "The current flows South, field is upward — thumb points into the page."),
        ("downward", "West", "Current downward, field pointing East — thumb points West."),
        ("into the page", "downward", "Current into the page, field pointing East — thumb points downward."),
        ("West", "out of the page", "Current West, field upward — thumb points out of the page."),
    ]
    current, force, explanation = random.choice(scenarios)
    q = (rf"A horizontal wire carries a conventional current flowing <strong>{current}</strong>. "
         rf"A uniform magnetic field acts <strong>vertically upward</strong>. "
         rf"Using Fleming's Left Hand Rule, state the direction of the magnetic force on the wire.")
    s = rf"The force acts <strong>{force}</strong>.<br><br>{explanation}"
    hint = r"<strong>FLHR</strong>: First finger = B, seCond = I, thuMb = Force. All three are mutually perpendicular."
    return q, s, hint, 2

def mag_found_flux_density_definition():
    q = (r"<strong>a)</strong> Define magnetic flux density.<br>"
         r"<strong>b)</strong> State its SI unit and express it in base SI units.<br>"
         r"<strong>c)</strong> State what is meant by a uniform magnetic field.")
    s = (r"<strong>a)</strong> Magnetic flux density <em>B</em> is the force per unit length per unit current "
         r"on a straight conductor perpendicular to the field: B = F / IL.<br><br>"
         r"<strong>b)</strong> SI unit: <strong>Tesla (T)</strong>. In base units: 1 T = 1 kg s⁻² A⁻¹.<br><br>"
         r"<strong>c)</strong> A uniform magnetic field has the same magnitude and direction at every point — "
         r"represented by equally spaced parallel field lines.")
    hint = r"B = F / IL → F = BIL. Tesla = kg s⁻² A⁻¹."
    return q, s, hint, 3

def mag_found_force_on_charge():
    B = round(random.uniform(0.1, 1.5), 2)
    v = random.randint(1, 8) * 10**6
    Q = 1.6e-19
    F = B * Q * v
    v_display = f"{v:.2e}"
    F_display = f"{F:.4e}"
    q = (rf"A proton moves with velocity <strong>{v_display} m s⁻¹</strong> perpendicular to a magnetic field "
         rf"of flux density <strong>{B} T</strong>. Calculate the magnetic force on the proton.<br>"
         rf"(charge of proton = 1.6 × 10⁻¹⁹ C)")
    s = rf"F = BQv = {B} × 1.6 × 10⁻¹⁹ × {v_display}<br><strong>F = {F_display} N</strong>"
    hint = r"<strong>F = BQv</strong> for perpendicular motion. For angle θ: F = BQv sinθ."
    return q, s, hint, 2

def mag_found_force_on_charge_b():
    """Electron instead of proton, find v given F and B"""
    B = round(random.uniform(0.05, 0.8), 2)
    F_given = round(random.randint(1, 9) * 1e-14, 15)
    Q = 1.6e-19
    v = round(F_given / (Q * B), 2)
    F_display = f"{F_given:.2e}"
    v_display = f"{v:.4e}"
    q = (rf"An electron (charge = 1.6 × 10⁻¹⁹ C) moves perpendicular to a magnetic field of "
         rf"flux density <strong>{B} T</strong> and experiences a force of <strong>{F_display} N</strong>. "
         rf"Calculate the speed of the electron.")
    s = rf"Rearranging F = BQv:<br>v = F / BQ = {F_display} / ({B} × 1.6 × 10⁻¹⁹)<br><strong>v = {v_display} m s⁻¹</strong>"
    hint = r"Rearrange <strong>F = BQv</strong> → <strong>v = F / BQ</strong>."
    return q, s, hint, 2

def mag_found_field_pattern_wire():
    diagram = svg_wire_field_lines()
    q = (rf"The diagram shows a cross-section of a long straight wire carrying a current out of the page.<br>{diagram}<br>"
         rf"<strong>a)</strong> Describe the shape of the magnetic field lines around the wire.<br>"
         rf"<strong>b)</strong> State the rule used to determine the direction of the field.")
    s = (r"<strong>a)</strong> The field lines form <strong>concentric circles</strong> centred on the wire, "
         r"in planes perpendicular to the wire. The field strength decreases with distance from the wire.<br><br>"
         r"<strong>b)</strong> The <strong>right-hand grip rule</strong>: thumb points in the direction of conventional "
         r"current, fingers curl in the direction of the magnetic field.")
    hint = r"Concentric circles, getting more spaced out further away. Right-hand grip rule for direction."
    return q, s, hint, 3

def mag_found_field_pattern_solenoid():
    diagram = svg_solenoid()
    q = (rf"The diagram shows a solenoid carrying a current.<br>{diagram}<br>"
         rf"<strong>a)</strong> Describe the magnetic field <em>inside</em> the solenoid.<br>"
         rf"<strong>b)</strong> Describe the field <em>outside</em> the solenoid.<br>"
         rf"<strong>c)</strong> How do you identify which end is the North pole?")
    s = (r"<strong>a)</strong> Inside: the field is <strong>uniform</strong> (parallel, equally spaced lines) along the axis.<br><br>"
         r"<strong>b)</strong> Outside: the field pattern resembles that of a <strong>bar magnet</strong> — field lines curve "
         r"from North to South around the outside.<br><br>"
         r"<strong>c)</strong> Apply the right-hand grip rule: curl the fingers of the right hand in the direction of "
         r"conventional current in the coils — the thumb points toward the <strong>North pole</strong>.")
    hint = r"Inside solenoid = uniform field. Outside = bar magnet pattern. Right-hand grip rule → North pole direction."
    return q, s, hint, 3

# -----------------------------------------------
# INTERMEDIATE (10 questions)
# -----------------------------------------------

def mag_inter_circular_motion():
    B = round(random.uniform(0.05, 0.5), 3)
    m = 1.67e-27
    Q = 1.6e-19
    v = random.randint(1, 9) * 10**6
    r = m * v / (Q * B)
    v_display = f"{v:.2e}"
    r_display = f"{r:.4e}"
    diagram = svg_circular_motion("r")
    q = (rf"A proton (m = 1.67 × 10⁻²⁷ kg, Q = 1.6 × 10⁻¹⁹ C) enters a uniform magnetic field of "
         rf"flux density <strong>{B} T</strong> perpendicular to the field with speed <strong>{v_display} m s⁻¹</strong>.<br>"
         rf"{diagram}<br>"
         rf"<strong>a)</strong> Explain why the proton follows a circular path.<br>"
         rf"<strong>b)</strong> Calculate the radius of the circular path.")
    s = (rf"<strong>a)</strong> The magnetic force F = BQv is always perpendicular to the velocity — it changes "
         rf"direction but not speed. This perpendicular force provides centripetal acceleration → circular motion.<br><br>"
         rf"<strong>b)</strong> BQv = mv²/r → r = mv/BQ<br>"
         rf"r = (1.67×10⁻²⁷ × {v_display}) / ({B} × 1.6×10⁻¹⁹)<br><strong>r = {r_display} m</strong>")
    hint = r"Set <strong>BQv = mv²/r</strong> → <strong>r = mv/BQ</strong>. Magnetic force ⊥ v → changes direction, not speed."
    return q, s, hint, 4

def mag_inter_velocity_selector():
    E = random.randint(1, 9) * 10**4
    B = round(random.uniform(0.05, 0.5), 3)
    v = round(E / B, 0)
    E_display = f"{E:.2e}"
    diagram = svg_velocity_selector()
    q = (rf"A velocity selector uses crossed electric and magnetic fields as shown.<br>{diagram}<br>"
         rf"The electric field strength is <strong>{E_display} V m⁻¹</strong> and the magnetic flux density is <strong>{B} T</strong>.<br>"
         rf"<strong>a)</strong> Explain the principle of a velocity selector.<br>"
         rf"<strong>b)</strong> Calculate the speed of particles that pass through undeflected.")
    s = (rf"<strong>a)</strong> Particles experience electric force F<sub>E</sub> = QE and magnetic force F<sub>B</sub> = BQv "
         rf"in opposite directions. Only when F<sub>E</sub> = F<sub>B</sub> do particles pass through undeflected — "
         rf"all others are deflected out.<br><br>"
         rf"<strong>b)</strong> QE = BQv → v = E/B = {E_display} / {B} = <strong>{v:.2e} m s⁻¹</strong>")
    hint = r"Balance forces: <strong>QE = BQv</strong> → <strong>v = E/B</strong>. Q cancels — selected speed is independent of charge."
    return q, s, hint, 4

def mag_inter_fil_angle():
    B = round(random.uniform(0.1, 1.5), 2)
    I = random.randint(2, 15)
    L = round(random.uniform(0.2, 1.0), 2)
    theta = random.choice([30, 45, 60])
    F = round(B * I * L * math.sin(math.radians(theta)), 3)
    diagram = svg_fil_angle(theta)
    q = (rf"The diagram shows a conductor at angle θ to a uniform magnetic field.<br>{diagram}<br>"
         rf"The conductor has length <strong>{L} m</strong>, carries current <strong>{I} A</strong>, "
         rf"and the field has flux density <strong>{B} T</strong>. Calculate the force on the conductor.")
    s = (rf"F = BIL sinθ = {B} × {I} × {L} × sin({theta}°)<br>"
         rf"= {B} × {I} × {L} × {round(math.sin(math.radians(theta)),4)}<br>"
         rf"<strong>F = {F} N</strong>")
    hint = r"<strong>F = BIL sinθ</strong> — maximum at 90°, zero at 0° (parallel to field)."
    return q, s, hint, 3

def mag_inter_period_cyclotron():
    m = 1.67e-27
    Q = 1.6e-19
    B = round(random.uniform(0.1, 1.0), 2)
    T = 2 * math.pi * m / (Q * B)
    f = 1 / T
    T_display = f"{T:.4e}"
    f_display = f"{f:.4e}"
    diagram = svg_cyclotron()
    q = (rf"A proton (m = 1.67 × 10⁻²⁷ kg, Q = 1.6 × 10⁻¹⁹ C) moves in a cyclotron with magnetic "
         rf"flux density <strong>{B} T</strong>.<br>{diagram}<br>"
         rf"<strong>a)</strong> Show that the period of circular motion is independent of the proton's speed.<br>"
         rf"<strong>b)</strong> Calculate the period and frequency.")
    s = (rf"<strong>a)</strong> r = mv/BQ, so T = 2πr/v = 2π(mv/BQ)/v = <strong>2πm/BQ</strong> — v cancels, so T is independent of speed.<br><br>"
         rf"<strong>b)</strong> T = 2πm/BQ = (2π × 1.67×10⁻²⁷) / ({B} × 1.6×10⁻¹⁹)<br>"
         rf"<strong>T = {T_display} s</strong><br><strong>f = {f_display} Hz</strong>")
    hint = r"Substitute r = mv/BQ into T = 2πr/v — v cancels giving <strong>T = 2πm/BQ</strong>. This is the cyclotron frequency."
    return q, s, hint, 4

def mag_inter_hall_voltage():
    B = round(random.uniform(0.05, 0.5), 3)
    I = random.randint(1, 10)
    n = random.choice([8.5e28, 6.0e28, 1.0e29])
    t = round(random.uniform(0.001, 0.01), 4)
    Q = 1.6e-19
    V_H = B * I / (n * Q * t)
    n_display = f"{n:.2e}"
    V_display = f"{V_H:.4e}"
    diagram = svg_hall_probe()
    q = (rf"The diagram shows a Hall probe in a magnetic field.<br>{diagram}<br>"
         rf"The probe has thickness <strong>{t} m</strong>, charge carrier density <strong>{n_display} m⁻³</strong>. "
         rf"A current of <strong>{I} A</strong> flows perpendicular to a field of <strong>{B} T</strong>.<br>"
         rf"<strong>a)</strong> Explain how the Hall voltage is established.<br>"
         rf"<strong>b)</strong> Calculate the Hall voltage.")
    s = (rf"<strong>a)</strong> Charge carriers experience magnetic force F = BQv sideways, causing charge buildup on one face. "
         rf"This creates an electric field E opposing further buildup. Equilibrium: QE = BQv → E = Bv. "
         rf"Since v = I/nQt (from I = nQvA with A = wt), V<sub>H</sub> = Et = Bvt = BI/nQt.<br><br>"
         rf"<strong>b)</strong> V<sub>H</sub> = BI/nQt = ({B} × {I}) / ({n_display} × 1.6×10⁻¹⁹ × {t})<br>"
         rf"<strong>V<sub>H</sub> = {V_display} V</strong>")
    hint = r"<strong>V<sub>H</sub> = BI/nQt</strong>. Derived by balancing QE = BQv. n = carrier density, t = probe thickness."
    return q, s, hint, 5

def mag_inter_find_mass():
    """Find mass from circular motion radius"""
    B = round(random.uniform(0.1, 0.8), 2)
    Q = 1.6e-19
    v = random.randint(1, 5) * 10**6
    r = round(random.uniform(0.05, 0.5), 3)
    m = round(Q * B * r / v, 32)
    v_display = f"{v:.2e}"
    m_display = f"{m:.4e}"
    diagram = svg_circular_motion("r = " + str(r) + " m")
    q = (rf"An ion of charge 1.6 × 10⁻¹⁹ C moves in a circle of radius <strong>{r} m</strong> in a magnetic field "
         rf"of flux density <strong>{B} T</strong> with speed <strong>{v_display} m s⁻¹</strong>.<br>{diagram}<br>"
         rf"Calculate the mass of the ion.")
    s = (rf"From r = mv/BQ:<br>m = BQr/v = {B} × 1.6×10⁻¹⁹ × {r} / {v_display}<br>"
         rf"<strong>m = {m_display} kg</strong>")
    hint = r"Rearrange <strong>r = mv/BQ</strong> → <strong>m = BQr/v</strong>."
    return q, s, hint, 3

def mag_inter_force_between_wires():
    I1 = random.randint(5, 30)
    I2 = random.randint(5, 30)
    d = round(random.uniform(0.01, 0.1), 3)
    L = round(random.uniform(0.1, 1.0), 2)
    mu0 = 4 * math.pi * 1e-7
    F = mu0 * I1 * I2 * L / (2 * math.pi * d)
    F_display = f"{F:.4e}"
    q = (rf"Two long parallel wires are separated by <strong>{d} m</strong>. Wire 1 carries <strong>{I1} A</strong> "
         rf"and Wire 2 carries <strong>{I2} A</strong> in the same direction.<br>"
         rf"<strong>a)</strong> State whether the force between the wires is attractive or repulsive.<br>"
         rf"<strong>b)</strong> Calculate the force per unit length between the wires, and hence the total force over a length of <strong>{L} m</strong>.<br>"
         rf"(μ₀ = 4π × 10⁻⁷ T m A⁻¹)")
    s = (rf"<strong>a)</strong> The force is <strong>attractive</strong> — parallel currents in the same direction attract.<br><br>"
         rf"<strong>b)</strong> F/L = μ₀I₁I₂ / 2πd = (4π×10⁻⁷ × {I1} × {I2}) / (2π × {d})<br>"
         rf"F/L = {f'{mu0*I1*I2/(2*math.pi*d):.4e}'} N m⁻¹<br>"
         rf"Total force over {L} m: <strong>F = {F_display} N</strong>")
    hint = r"<strong>F/L = μ₀I₁I₂ / 2πd</strong>. Same direction currents → attract. Opposite → repel."
    return q, s, hint, 4

def mag_inter_electron_circle():
    """Electron in circular motion — direction of deflection"""
    B = round(random.uniform(0.05, 0.3), 3)
    m_e = 9.11e-31
    Q = 1.6e-19
    v = random.randint(1, 5) * 10**7
    r = m_e * v / (Q * B)
    v_display = f"{v:.2e}"
    r_display = f"{r:.4e}"
    diagram = svg_circular_motion("r")
    q = (rf"An electron (m = 9.11 × 10⁻³¹ kg, Q = 1.6 × 10⁻¹⁹ C) moves at <strong>{v_display} m s⁻¹</strong> "
         rf"perpendicular to a magnetic field of <strong>{B} T</strong>.<br>{diagram}<br>"
         rf"<strong>a)</strong> Explain why the electron moves in a circle.<br>"
         rf"<strong>b)</strong> Calculate the radius of the circular path.<br>"
         rf"<strong>c)</strong> State one difference in the circular motion compared to a proton in the same field and speed.")
    s = (rf"<strong>a)</strong> The magnetic force on the electron is always perpendicular to its velocity, "
         rf"providing centripetal force → circular motion at constant speed.<br><br>"
         rf"<strong>b)</strong> r = mv/BQ = (9.11×10⁻³¹ × {v_display}) / ({B} × 1.6×10⁻¹⁹)<br>"
         rf"<strong>r = {r_display} m</strong><br><br>"
         rf"<strong>c)</strong> The electron curves in the <strong>opposite direction</strong> (negative charge reverses force direction) "
         rf"and has a <strong>much smaller radius</strong> (mass ~1800× smaller than proton).")
    hint = r"r = mv/BQ. Electron has smaller mass → smaller radius. Negative charge → opposite deflection to proton."
    return q, s, hint, 4

def mag_inter_fil_angle_b():
    """F = BIL sinθ — find angle given F"""
    B = round(random.uniform(0.2, 1.5), 2)
    I = random.randint(3, 15)
    L = round(random.uniform(0.3, 1.0), 2)
    theta = random.choice([30, 45, 60])
    F = round(B * I * L * math.sin(math.radians(theta)), 3)
    sin_val = round(F / (B * I * L), 4)
    diagram = svg_fil_angle(theta)
    q = (rf"A conductor of length <strong>{L} m</strong> carrying current <strong>{I} A</strong> in a field of "
         rf"<strong>{B} T</strong> experiences a force of <strong>{F} N</strong>.<br>{diagram}<br>"
         rf"Calculate the angle between the conductor and the field.")
    s = (rf"F = BIL sinθ → sinθ = F / BIL = {F} / ({B} × {I} × {L}) = {sin_val}<br>"
         rf"θ = sin⁻¹({sin_val}) = <strong>{theta}°</strong>")
    hint = r"Rearrange <strong>F = BIL sinθ</strong> → <strong>sinθ = F / BIL</strong>, then θ = sin⁻¹(...)."
    return q, s, hint, 3

def mag_inter_current_field_wire():
    """Field strength at distance from wire"""
    I = random.randint(5, 50)
    d = round(random.uniform(0.01, 0.2), 3)
    mu0 = 4 * math.pi * 1e-7
    B = mu0 * I / (2 * math.pi * d)
    B_display = f"{B:.4e}"
    diagram = svg_wire_field_lines()
    q = (rf"The diagram shows a long straight wire carrying a current of <strong>{I} A</strong>.<br>{diagram}<br>"
         rf"Calculate the magnetic flux density at a perpendicular distance of <strong>{d} m</strong> from the wire.<br>"
         rf"(μ₀ = 4π × 10⁻⁷ T m A⁻¹)")
    s = (rf"B = μ₀I / 2πd = (4π×10⁻⁷ × {I}) / (2π × {d})<br>"
         rf"<strong>B = {B_display} T</strong>")
    hint = r"<strong>B = μ₀I / 2πd</strong> for a long straight wire. Field decreases with distance."
    return q, s, hint, 3

# -----------------------------------------------
# DIFFICULT (10 questions)
# -----------------------------------------------

def mag_diff_no_work():
    q = (r"A charged particle moves through a uniform magnetic field.<br>"
         r"<strong>a)</strong> Show that the magnetic force does no work on the particle.<br>"
         r"<strong>b)</strong> Explain what this means for the particle's speed and kinetic energy.<br>"
         r"<strong>c)</strong> A student claims that because the magnetic force does no work, it cannot change "
         r"the particle's momentum. Evaluate this claim.")
    s = (r"<strong>a)</strong> Work done W = F · ds = F · v dt. The magnetic force F = BQv is always perpendicular "
         r"to v, so F · v = 0 at all times → W = 0.<br><br>"
         r"<strong>b)</strong> Since no work is done, KE = ½mv² is constant → speed is constant throughout.<br><br>"
         r"<strong>c)</strong> The claim is <strong>incorrect</strong>. Momentum is a vector. The speed (|p| = mv) is "
         r"unchanged, but the <em>direction</em> of momentum continuously changes as the force redirects the particle. "
         r"The magnetic force changes the direction of momentum without changing its magnitude.")
    hint = r"W = F·v. Magnetic force ⊥ v → F·v = 0. Speed constant. But momentum direction changes — it's a vector!"
    return q, s, hint, 5

def mag_diff_mass_spectrometer():
    m1 = 1.67e-27
    m2 = 3.34e-27
    Q = 1.6e-19
    B = round(random.uniform(0.1, 0.5), 3)
    v = random.randint(1, 5) * 10**6
    r1 = m1 * v / (Q * B)
    r2 = m2 * v / (Q * B)
    sep = 2 * (r2 - r1)
    v_display = f"{v:.2e}"
    diagram = svg_circular_motion("r")
    q = (rf"In a mass spectrometer, protons (m = 1.67 × 10⁻²⁷ kg) and deuterons (m = 3.34 × 10⁻²⁷ kg, Q = +e) "
         rf"are accelerated to <strong>{v_display} m s⁻¹</strong> before entering a field of <strong>{B} T</strong>.<br>{diagram}<br>"
         rf"<strong>a)</strong> Calculate the radius of curvature for each particle.<br>"
         rf"<strong>b)</strong> Calculate the separation between their impact points on the detector plate.<br>"
         rf"<strong>c)</strong> Explain why a velocity selector precedes the deflection region.")
    s = (rf"<strong>a)</strong> r = mv/BQ<br>"
         rf"Proton: r₁ = (1.67×10⁻²⁷ × {v_display}) / ({B} × 1.6×10⁻¹⁹) = <strong>{r1:.4e} m</strong><br>"
         rf"Deuteron: r₂ = (3.34×10⁻²⁷ × {v_display}) / ({B} × 1.6×10⁻¹⁹) = <strong>{r2:.4e} m</strong><br><br>"
         rf"<strong>b)</strong> Separation = 2r₂ − 2r₁ = 2({r2:.4e} − {r1:.4e}) = <strong>{sep:.4e} m</strong><br><br>"
         rf"<strong>c)</strong> Ions from the source have a spread of speeds. Without selection, r = mv/BQ varies with v, "
         rf"broadening the impact spot and reducing mass resolution. The velocity selector ensures all ions enter at the same speed.")
    hint = r"r = mv/BQ. Separation = 2(r₂ − r₁). Velocity selector: v = E/B — makes deflection depend only on m/Q."
    return q, s, hint, 6

def mag_diff_hall_semiconductor():
    diagram = svg_hall_probe()
    q = (rf"The diagram shows a Hall probe.<br>{diagram}<br>"
         rf"A semiconductor Hall probe gives a much larger Hall voltage than a metallic one for the same conditions.<br>"
         rf"<strong>a)</strong> Using V<sub>H</sub> = BI/nQt, explain why.<br>"
         rf"<strong>b)</strong> Give one advantage and one disadvantage of using a semiconductor probe.<br>"
         rf"<strong>c)</strong> The probe is rotated 90° so it lies parallel to the field. What happens to V<sub>H</sub>? Explain.")
    s = (r"<strong>a)</strong> V<sub>H</sub> = BI/nQt. Semiconductors have much lower carrier density <em>n</em> "
         r"(~10²² m⁻³) compared to metals (~10²⁸ m⁻³). Since V<sub>H</sub> ∝ 1/n, the lower n gives a much larger Hall voltage.<br><br>"
         r"<strong>b)</strong> <em>Advantage</em>: higher sensitivity — larger V<sub>H</sub> easier to measure.<br>"
         r"<em>Disadvantage</em>: n varies with temperature in semiconductors, making readings temperature-dependent.<br><br>"
         r"<strong>c)</strong> V<sub>H</sub> → <strong>zero</strong>. V<sub>H</sub> arises from the component of B perpendicular "
         r"to the probe face. When parallel, B is along the current direction — no sideways force on carriers, no charge separation.")
    hint = r"V<sub>H</sub> ∝ 1/n. Zero when B ∥ probe face. Max when B ⊥ probe face."
    return q, s, hint, 5

def mag_diff_cyclotron_extended():
    diagram = svg_cyclotron()
    q = (rf"The diagram shows a cyclotron.<br>{diagram}<br>"
         rf"<strong>a)</strong> Explain why the period of revolution of a proton in a cyclotron is independent of its speed.<br>"
         rf"<strong>b)</strong> Explain how the proton gains energy in the cyclotron.<br>"
         rf"<strong>c)</strong> Explain why the radius of the proton's path increases with each half-revolution.<br>"
         rf"<strong>d)</strong> At very high energies, the cyclotron no longer works correctly. Suggest why.")
    s = (r"<strong>a)</strong> T = 2πm/BQ — the period depends only on m, B, Q, not on v. As the proton speeds up, "
         r"r = mv/BQ increases proportionally, so the time for each half-circle remains constant.<br><br>"
         r"<strong>b)</strong> The proton is accelerated each time it crosses the gap between the dees by the alternating "
         r"electric field. The frequency of alternation matches the cyclotron frequency (resonance condition) so the "
         r"field always accelerates (not decelerates) the proton.<br><br>"
         r"<strong>c)</strong> r = mv/BQ. As the proton gains KE, its speed v increases. Since m, B, Q are constant, "
         r"r ∝ v — so the radius increases with each pass, producing the characteristic outward spiral.<br><br>"
         r"<strong>d)</strong> At relativistic speeds, the proton's mass increases (relativistic mass). Since T = 2πm/BQ, "
         r"the period increases, so the proton falls out of resonance with the alternating electric field and is no longer "
         r"accelerated efficiently. A <em>synchrocyclotron</em> varies the frequency to compensate.")
    hint = r"T = 2πm/BQ (constant). Energy gain at the gap. r ∝ v → spiral. Relativistic mass increase breaks the resonance condition."
    return q, s, hint, 6

def mag_diff_compare_fields():
    q = (r"A proton moves horizontally to the right and enters a region with both a uniform electric field "
         r"and a uniform magnetic field directed vertically upward.<br>"
         r"<strong>a)</strong> State the direction of the electric force on the proton.<br>"
         r"<strong>b)</strong> State the direction of the magnetic force on the proton.<br>"
         r"<strong>c)</strong> Explain why the path in the electric field alone is parabolic, but in the magnetic field alone is circular.<br>"
         r"<strong>d)</strong> Explain why the magnetic force does no work, whereas the electric force does.")
    s = (r"<strong>a)</strong> Electric force on positive charge is in field direction: <strong>vertically upward</strong>.<br><br>"
         r"<strong>b)</strong> FLHR: current East, field up → force <strong>out of the page</strong>.<br><br>"
         r"<strong>c)</strong> Electric force is constant in magnitude and direction, giving constant acceleration ⊥ to initial "
         r"velocity → <strong>parabolic</strong> path (like projectile motion). Magnetic force is always ⊥ to v — changes "
         r"direction but not speed → constant centripetal acceleration → <strong>circular</strong> path.<br><br>"
         r"<strong>d)</strong> Work = F·d. Electric force has a component along displacement as proton accelerates upward → "
         r"does positive work, increases KE. Magnetic force is always ⊥ to v → F·v = 0 → no work done, KE unchanged.")
    hint = r"Electric: constant direction → parabola. Magnetic: always ⊥ to v → circle. F·v = 0 for magnetic force → no work."
    return q, s, hint, 5

def mag_diff_helical_motion():
    q = (r"<em>Describe and explain the motion of a charged particle that enters a region of uniform magnetic field "
         r"at an angle that is neither perpendicular nor parallel to the field lines. Your answer should include the "
         r"shape of the path, the forces involved, and any quantities that remain constant.</em>")
    s = (r"Resolve the velocity into two components:<br>"
         r"<ul style='margin:8px 0;padding-left:20px'>"
         r"<li><strong>Parallel to B</strong>: v‖ = v cosθ — no magnetic force (F = BQv sin0° = 0) → uniform motion along field direction</li>"
         r"<li><strong>Perpendicular to B</strong>: v⊥ = v sinθ — experiences force F = BQv⊥ → circular motion ⊥ to B</li>"
         r"</ul>"
         r"The combination of constant forward motion and circular motion produces a <strong>helical path</strong> along B.<br><br>"
         r"<strong>Constant quantities</strong>: speed |v|, kinetic energy, radius r = mv⊥/BQ, pitch = v‖ × T = v cosθ × 2πm/BQ.<br><br>"
         r"This explains how charged particles spiral along Earth's magnetic field lines toward the poles, producing the aurora.")
    hint = r"v‖ (parallel) → unchanged → forward motion. v⊥ (perpendicular) → circular motion. Combined = <strong>helix</strong>."
    return q, s, hint, 6

def mag_diff_magnetic_bottle():
    q = (r"A magnetic bottle uses non-uniform magnetic fields to confine charged particles.<br>"
         r"<strong>a)</strong> Explain, in terms of helical motion, how a non-uniform field can reflect a charged particle "
         r"back before it escapes from the ends of the bottle.<br>"
         r"<strong>b)</strong> Explain why this principle is used in nuclear fusion reactors (tokamaks).<br>"
         r"<strong>c)</strong> State one limitation of magnetic confinement in tokamaks.")
    s = (r"<strong>a)</strong> As a particle spiralling along field lines enters a region of stronger field, the radius of "
         r"the circular component r = mv⊥/BQ decreases (B increases, r decreases). The pitch also decreases. Eventually v‖ → 0 "
         r"and the particle is reflected back — the stronger field region acts as a magnetic mirror.<br><br>"
         r"<strong>b)</strong> Fusion requires plasma at ~10⁸ K — no physical container can withstand this temperature. "
         r"Magnetic fields confine the plasma without physical contact, preventing heat loss to walls and maintaining the "
         r"conditions needed for fusion.<br><br>"
         r"<strong>c)</strong> Any one of: plasma instabilities cause particles to escape; very large and expensive superconducting "
         r"magnets required; sustaining net energy gain (Q > 1) has not yet been achieved commercially.")
    hint = r"Stronger B → smaller r → v‖ decreases → particle reflected. Confinement avoids physical contact with hot plasma."
    return q, s, hint, 5

def mag_diff_relativistic():
    q = (r"A proton is accelerated to 90% of the speed of light (v = 0.9c) in a particle accelerator.<br>"
         r"<strong>a)</strong> State why the formula r = mv/BQ underestimates the actual radius of curvature at this speed.<br>"
         r"<strong>b)</strong> The relativistic momentum of the proton is p = γmv, where γ = 1/√(1 − v²/c²). "
         r"Calculate γ for v = 0.9c, giving your answer to 3 significant figures.<br>"
         r"<strong>c)</strong> Explain one practical implication of relativistic mass increase for the design of particle accelerators.")
    import math as _m
    gamma = round(1 / _m.sqrt(1 - 0.9**2), 3)
    s = (rf"<strong>a)</strong> At relativistic speeds, the proton's effective (relativistic) mass γm is greater than its rest mass m. "
         rf"Since r = p/BQ = γmv/BQ, the actual radius is larger than the non-relativistic formula predicts. Using r = mv/BQ underestimates r.<br><br>"
         rf"<strong>b)</strong> γ = 1/√(1 − 0.9²) = 1/√(1 − 0.81) = 1/√0.19 = <strong>{gamma}</strong><br><br>"
         rf"<strong>c)</strong> Any one of: synchrocyclotrons must decrease their frequency as particles accelerate (to maintain resonance); "
         rf"synchrotrons must increase B as particles speed up to maintain constant radius; "
         rf"accelerating particles to truly relativistic speeds requires disproportionately large energy inputs as m increases toward infinity.")
    hint = rf"γ = 1/√(1−v²/c²). At v = 0.9c, γ = {gamma}. Relativistic momentum p = γmv is larger → larger r. Design implications: synchrocyclotron or synchrotron."
    return q, s, hint, 5

def mag_diff_hall_derive():
    diagram = svg_hall_probe()
    q = (rf"The diagram shows a Hall probe of width w, thickness t, with current I, in a field B.<br>{diagram}<br>"
         rf"<strong>a)</strong> Starting from the condition for equilibrium of forces on charge carriers, derive an expression "
         rf"for the Hall voltage V<sub>H</sub> in terms of B, I, n, Q, and t.<br>"
         rf"<strong>b)</strong> Explain why the Hall voltage is independent of the width w of the probe.<br>"
         rf"<strong>c)</strong> A student doubles both the current and the thickness. State and explain the effect on V<sub>H</sub>.")
    s = (r"<strong>a)</strong> Carriers experience magnetic force F<sub>B</sub> = BQv sideways. Charge builds up, creating "
         r"electric field E = V<sub>H</sub>/t. Equilibrium: QE = BQv → E = Bv → V<sub>H</sub>/t = Bv.<br>"
         r"Current: I = nQvA = nQv(wt) → v = I/nQwt.<br>"
         r"Substituting: V<sub>H</sub>/t = B × I/nQwt → <strong>V<sub>H</sub> = BI/nQt</strong> (w cancels).<br><br>"
         r"<strong>b)</strong> w cancels in the derivation — the Hall voltage depends only on the thickness t (which sets the "
         r"electric field strength), not the width.<br><br>"
         r"<strong>c)</strong> V<sub>H</sub> = BI/nQt. Doubling I doubles V<sub>H</sub>; doubling t halves V<sub>H</sub>. "
         r"Combined effect: V<sub>H</sub> is <strong>unchanged</strong> — the two changes cancel.")
    hint = r"Derive from QE = BQv and I = nQvA. w cancels. V<sub>H</sub> ∝ I/t — doubling both leaves V<sub>H</sub> the same."
    return q, s, hint, 6

def mag_diff_force_current_loop():
    n = random.randint(50, 500)
    I = random.randint(1, 10)
    A = round(random.uniform(0.001, 0.05), 4)
    B = round(random.uniform(0.1, 1.0), 2)
    tau = round(n * I * A * B, 5)
    q = (rf"A rectangular coil has <strong>{n} turns</strong>, area <strong>{A} m²</strong>, and carries a current of "
         rf"<strong>{I} A</strong>. It is placed with its plane parallel to a uniform magnetic field of <strong>{B} T</strong>.<br>"
         rf"<strong>a)</strong> Explain why forces on two sides of the coil produce a turning effect (torque).<br>"
         rf"<strong>b)</strong> Calculate the torque on the coil.<br>"
         rf"<strong>c)</strong> State the position of the coil at which the torque is zero, and explain why.")
    s = (rf"<strong>a)</strong> The two sides perpendicular to the field each experience force F = BIL but in opposite "
         rf"directions (by FLHR — opposite currents). This produces a couple — equal, opposite, non-collinear forces "
         rf"that create a net rotational effect (torque) about the axis of the coil.<br><br>"
         rf"<strong>b)</strong> τ = nBIA = {n} × {B} × {I} × {A} = <strong>{tau} N m</strong><br><br>"
         rf"<strong>c)</strong> Torque is zero when the coil plane is <strong>perpendicular to the field</strong> (normal to coil is "
         rf"parallel to B). At this position the forces on all sides are either parallel/antiparallel to the axis or cancel — "
         rf"no turning effect.")
    hint = r"τ = nBIA (for plane parallel to B — maximum torque). Zero torque when coil normal ∥ B. This is the principle of a DC motor."
    return q, s, hint, 5


# -----------------------------------------------
# MAIN GENERATOR FUNCTION
# -----------------------------------------------

def alevel_physics_magnetism(difficulty, mode):
    if mode == 'exam':
        difficulty = random.choices(
            ['foundational', 'intermediate', 'difficult'],
            weights=[60, 30, 10]
        )[0]

    if difficulty == 'foundational':
        variant = random.choice([
            mag_found_force_on_conductor,
            mag_found_force_on_conductor_b,
            mag_found_flhr_a,
            mag_found_flhr_b,
            mag_found_flhr_c,
            mag_found_flux_density_definition,
            mag_found_force_on_charge,
            mag_found_force_on_charge_b,
            mag_found_field_pattern_wire,
            mag_found_field_pattern_solenoid,
        ])
    elif difficulty == 'intermediate':
        variant = random.choice([
            mag_inter_circular_motion,
            mag_inter_velocity_selector,
            mag_inter_fil_angle,
            mag_inter_period_cyclotron,
            mag_inter_hall_voltage,
            mag_inter_find_mass,
            mag_inter_force_between_wires,
            mag_inter_electron_circle,
            mag_inter_fil_angle_b,
            mag_inter_current_field_wire,
        ])
    else:
        variant = random.choice([
            mag_diff_no_work,
            mag_diff_mass_spectrometer,
            mag_diff_hall_semiconductor,
            mag_diff_cyclotron_extended,
            mag_diff_compare_fields,
            mag_diff_helical_motion,
            mag_diff_magnetic_bottle,
            mag_diff_relativistic,
            mag_diff_hall_derive,
            mag_diff_force_current_loop,
        ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'alevel', 'physics', 'magnetism')
