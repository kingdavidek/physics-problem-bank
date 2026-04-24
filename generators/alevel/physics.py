import random
import math

from generators.shared.utils import make_problem



def _sample_variants(pool, count):
    if count >= len(pool):
        picked = pool[:]
        random.shuffle(picked)
        return picked
    return random.sample(pool, count)


# -----------------------------------------------
# Contents
#
# 17 - Magnetism
#
#
# 2018 - Photoelectric effect and wave particle duality
#
# -----------------------------------------------

# -----------------------------------------------
# A-LEVEL PHYSICS — Fields: MAGNETISM - LESSON
# -----------------------------------------------


def aqa_mag_motor_effect():
    I = random.choice([1.5, 2.0, 3.5, 4.0, 5.5])
    l_cm = random.choice([15, 20, 25, 40])
    B = random.choice([0.15, 0.20, 0.45, 0.60])
    angle = random.choice([90, 30, 45, 60])

    l_m = l_cm / 100
    force = B * I * l_m * math.sin(math.radians(angle))

    q = rf"A wire of length {l_cm} cm carries a current of {I} A. It is placed in a uniform magnetic field of flux density {B} T at an angle of {angle}° to the field lines. Calculate the magnitude of the force on the wire."
    s = rf"Using \( F = BIl \sin\theta \):<br>Length in metres = {l_m} m<br>\( F = {B} \times {I} \times {l_m} \times \sin({angle}^\circ) \)<br><strong>F = {force:.3g} N</strong>"
    return {'question': q, 'solution': s}

def aqa_mag_particle_path():
    v_sci = random.choice([3.2, 4.5, 5.2, 6.0])
    v = v_sci * 10**6
    B = random.choice([0.15, 0.25, 0.40, 0.50])

    # Proton constants
    m = 1.67e-27
    q_charge = 1.60e-19

    r = (m * v) / (q_charge * B)

    q = rf"A proton (mass = \(1.67 \times 10^{{-27}}\) kg, charge = \(1.6 \times 10^{{-19}}\) C) enters a uniform magnetic field of flux density {B} T with a speed of \({v_sci} \times 10^6\) m s\(^{{-1}}\) perpendicular to the field. Calculate the radius of its circular path."
    s = rf"Equating magnetic force to centripetal force: \( BQv = \frac{{mv^2}}{{r}} \implies r = \frac{{mv}}{{BQ}} \)<br>\( r = \frac{{1.67 \times 10^{{-27}} \times {v_sci} \times 10^6}}{{1.6 \times 10^{{-19}} \times {B}}} \)<br><strong>r = {r:.3g} m</strong>"
    return {'question': q, 'solution': s}

def aqa_mag_flux_linkage():
    N = random.choice([50, 100, 200, 500])
    r_cm = random.choice([3.0, 5.0, 8.0, 10.0])
    B = random.choice([0.10, 0.20, 0.35, 0.50])

    r_m = r_cm / 100
    area = math.pi * (r_m ** 2)
    flux_linkage = B * area * N

    q = rf"A flat circular coil with {N} turns is placed perpendicular to a uniform magnetic field of flux density {B} T. The radius of the coil is {r_cm} cm. Calculate the magnetic flux linkage through the coil."
    s = rf"Area \( A = \pi r^2 = \pi \times ({r_m})^2 = {area:.3g} \text{{ m}}^2 \)<br>Because the coil is perpendicular to the field, \(\theta = 0^\circ\) (angle to the normal), so \(\cos(0) = 1\).<br>\( N\Phi = BAN = {B} \times {area:.3g} \times {N} \)<br><strong>Flux linkage = {flux_linkage:.3g} Wb turns</strong>"
    return {'question': q, 'solution': s}

def aqa_mag_faradays_law():
    N = random.choice([500, 800, 1000, 1500])
    area_sci = random.choice([2.0, 2.5, 4.0, 5.0])
    area = area_sci * 1e-4
    t_ms = random.choice([50, 100, 150, 200])
    emf = random.choice([1.2, 1.4, 2.0, 2.5])

    t_s = t_ms / 1000
    B = (emf * t_s) / (area * N)

    q = rf"A search coil of {N} turns and area \({area_sci} \times 10^{{-4}} \text{{ m}}^2\) is placed perpendicular to a magnetic field. It is completely removed from the field in {t_ms} ms, and an average e.m.f. of {emf} V is recorded. Calculate the flux density of the magnetic field."
    s = rf"Using Faraday's Law (magnitude): \( \varepsilon = \frac{{N \Delta\Phi}}{{\Delta t}} = \frac{{BAN}}{{\Delta t}} \)<br>Rearranging for B: \( B = \frac{{\varepsilon \Delta t}}{{AN}} \)<br>\( B = \frac{{{emf} \times {t_s}}}{{{area_sci} \times 10^{{-4}} \times {N}}} \)<br><strong>B = {B:.3g} T</strong>"
    return {'question': q, 'solution': s}

def aqa_mag_transformers():
    V_p = random.choice([11000, 25000, 33000])
    N_p = random.choice([50, 100, 200])
    N_s = random.choice([500, 750, 1000, 2000])

    V_s = V_p * (N_s / N_p)

    q = rf"An alternating current leaves a power station at {V_p} V and enters the primary coil of a step-up transformer. The transformer has {N_p} turns on its primary coil and {N_s} turns on its secondary coil. Assuming 100% efficiency, calculate the output voltage."
    s = rf"Using the transformer equation: \( \frac{{V_s}}{{V_p}} = \frac{{N_s}}{{N_p}} \)<br>\( V_s = V_p \times \frac{{N_s}}{{N_p}} \)<br>\( V_s = {V_p} \times \frac{{{N_s}}}{{{N_p}}} \)<br><strong>Output Voltage = {V_s:,.0f} V</strong>"
    return {'question': q, 'solution': s}

# -----------------------------------------------
# A-LEVEL PHYSICS — FIELDS AND THEIR CONSEQUENCES: MAGNETISM
# -----------------------------------------------

def mag_mcq():
    """20 randomised AQA-style multiple choice questions for magnetism."""
    import random

    questions = []

    # --- Q1: Radius proportionality (like AQA Q11) ---
    factors = [(2, 4, 'R/4', 'R/2', '2R', '4R', 'C',
                r"From r = mv/BQ, r ∝ v/B. Speed is halved (×½) and B is doubled (×2), so r is multiplied by (½)/2 = ¼. New radius = R/4.",
                r"An electron moves at speed v in field B following a circular path of radius R. A second electron moves at speed v/2 in a field of flux density 2B. What is the radius of the second electron's path?")]
    q1 = random.choice(factors)
    questions.append({
        'q': q1[8],
        'A': q1[2], 'B': q1[3], 'C': q1[4], 'D': q1[5],
        'answer': q1[6],
        'explanation': q1[7]
    })

    # --- Q2: Force on a wire numerical ---
    B2 = random.choice([0.5, 1.0, 1.5, 2.0])
    I2 = random.choice([2, 4, 5, 10])
    L2 = random.choice([0.2, 0.4, 0.5, 1.0])
    F2 = B2 * I2 * L2
    wrong2a = round(B2 * I2, 2)
    wrong2b = round(I2 * L2, 2)
    wrong2c = round(B2 + I2 + L2, 2)
    opts2 = [round(F2,2), wrong2a, wrong2b, wrong2c]
    random.shuffle(opts2)
    letters2 = ['A','B','C','D']
    ans2 = letters2[opts2.index(round(F2,2))]
    questions.append({
        'q': rf"A straight wire of length <strong>{L2} m</strong> carries a current of <strong>{I2} A</strong> perpendicular to a uniform magnetic field of flux density <strong>{B2} T</strong>. What is the magnetic force on the wire?",
        'A': f"{opts2[0]} N", 'B': f"{opts2[1]} N", 'C': f"{opts2[2]} N", 'D': f"{opts2[3]} N",
        'answer': ans2,
        'explanation': rf"F = BIL = {B2} × {I2} × {L2} = <strong>{round(F2,2)} N</strong>. The other options come from omitting one of the three variables in the formula."
    })

    # --- Q3: Lenz's Law — three falling magnets (like AQA Q16) ---
    questions.append({
        'q': r"Three identical bar magnets are dropped from the same height simultaneously. Magnet P falls freely through air. Magnet Q falls through a complete conducting copper ring. Magnet R falls through an identical copper ring that has a small gap cut into it. In which order do they reach the ground?",
        'A': r"P and R together, then Q",
        'B': r"Q and R together, then P",
        'C': r"P first, then R, then Q",
        'D': r"All three arrive simultaneously",
        'answer': 'A',
        'explanation': r"Lenz's Law: Q is slowed by induced eddy currents in the complete ring, which create an opposing upward force. R's ring has a gap — no complete circuit, no current, no braking force. So R falls at the same rate as P (free fall). Q arrives last. <strong>Answer: A</strong>."
    })

    # --- Q4: Phase difference flux vs EMF (like AQA Q8) ---
    questions.append({
        'q': r"A coil rotates at constant angular velocity in a uniform magnetic field, generating an alternating EMF. What is the phase difference between the magnetic flux linkage through the coil and the induced EMF?",
        'A': r"0",
        'B': r"π/4 rad",
        'C': r"π/2 rad",
        'D': r"π rad",
        'answer': 'C',
        'explanation': r"EMF = −d(NΦ)/dt. Flux linkage varies as NΦ = BAN cos(ωt), and EMF = BANω sin(ωt). Since sin(ωt) = cos(ωt − π/2), the EMF lags the flux linkage by <strong>π/2 rad (90°)</strong>."
    })

    # --- Q5: Transformer efficiency calculation (like AQA Q5) ---
    Np5 = random.choice([200, 400, 500])
    Ns5 = random.choice([1000, 2000, 800])
    Vp5 = random.choice([20, 25, 50])
    eff5 = random.choice([80, 90, 95])
    Ip5 = random.choice([2.0, 4.0, 5.0])
    Vs5 = round(Vp5 * Ns5 / Np5, 1)
    Pin5 = Vp5 * Ip5
    Pout5 = Pin5 * eff5 / 100
    Is5 = round(Pout5 / Vs5, 2)
    wrong_Is5a = round(Pin5 / Vs5, 2)
    wrong_Is5b = round(Ip5 * Np5 / Ns5, 2)
    wrong_Vs5 = round(Vp5 * Np5 / Ns5, 1)
    questions.append({
        'q': rf"A transformer has a primary coil of <strong>{Np5} turns</strong> and a secondary coil of <strong>{Ns5} turns</strong>. An rms voltage of <strong>{Vp5} V</strong> is applied to the primary, causing a primary rms current of <strong>{Ip5} A</strong>. The transformer is <strong>{eff5}% efficient</strong>. What are the secondary rms voltage and current?",
        'A': f"Vs = {Vs5} V,  Is = {Is5} A",
        'B': f"Vs = {Vs5} V,  Is = {wrong_Is5a} A",
        'C': f"Vs = {wrong_Vs5} V,  Is = {Is5} A",
        'D': f"Vs = {wrong_Vs5} V,  Is = {wrong_Is5a} A",
        'answer': 'A',
        'explanation': rf"Vs = Vp × (Ns/Np) = {Vp5} × {Ns5}/{Np5} = <strong>{Vs5} V</strong>. Output power = {eff5}% × (Vp × Ip) = {eff5/100} × {Pin5} = {Pout5} W. Is = Pout / Vs = {Pout5} / {Vs5} = <strong>{Is5} A</strong>. Option B ignores efficiency. Option C and D use the turns ratio inverted."
    })

    # --- Q6: Coil in field — which sides experience force? (like AQA Q12) ---
    questions.append({
        'q': r"A rectangular coil PQRS is placed with its plane <strong>parallel</strong> to a uniform magnetic field. A current flows in the coil. Which sides of the coil experience a magnetic force?",
        'A': r"PQ and RS only",
        'B': r"QR and SP only",
        'C': r"All four sides experience equal forces",
        'D': r"No sides experience any force",
        'answer': 'A',
        'explanation': r"F = BIL sinθ. The sides parallel to the field (QR and SP) have θ = 0°, so sin(0°) = 0 — no force. The sides perpendicular to the field (PQ and RS) have θ = 90°, giving maximum force F = BIL. <strong>Answer: A</strong>."
    })

    # --- Q7: Supporting a wire against gravity ---
    L7 = random.choice([0.25, 0.50, 0.75])
    W7 = random.choice([0.5, 1.0, 1.5])
    B7 = random.choice([1.0, 1.5, 2.0])
    I7 = round(W7 / (B7 * L7), 2)
    wrong7a = round(W7 * B7 * L7, 2)
    wrong7b = round(B7 * L7 / W7, 2)
    wrong7c = round(W7 / L7, 2)
    opts7 = [I7, wrong7a, wrong7b, wrong7c]
    random.shuffle(opts7)
    ans7 = ['A','B','C','D'][opts7.index(I7)]
    questions.append({
        'q': rf"A horizontal wire of length <strong>{L7} m</strong> and weight <strong>{W7} N</strong> is placed in a horizontal magnetic field of flux density <strong>{B7} T</strong> directed at 90° to the wire. What current is needed to just support the wire against gravity?",
        'A': f"{opts7[0]} A", 'B': f"{opts7[1]} A", 'C': f"{opts7[2]} A", 'D': f"{opts7[3]} A",
        'answer': ans7,
        'explanation': rf"Magnetic force must equal weight: BIL = W → I = W/(BL) = {W7}/({B7} × {L7}) = <strong>{I7} A</strong>. A common error is to calculate BIL directly without rearranging for I."
    })

    # --- Q8: Particle enters two chambers — speed in second (like AQA Q20) ---
    v8 = random.choice([60, 80, 100])
    r8a = random.choice([150, 200, 250])
    r8b = random.choice([50, 75, 100])
    B8a_factor = 1
    B8b_factor = round(r8a / r8b, 1)
    v8b = round(v8 * r8b / r8a, 1)
    wrong8a = round(v8 * r8a / r8b, 1)
    wrong8b = v8
    wrong8c = round(v8 / 2, 1)
    opts8 = [v8b, wrong8a, wrong8b, wrong8c]
    random.shuffle(opts8)
    ans8 = ['A','B','C','D'][opts8.index(v8b)]
    questions.append({
        'q': rf"A particle enters a first magnetic field at <strong>{v8} m s⁻¹</strong> and follows a circular path of radius <strong>{r8a} mm</strong>. It then enters a second magnetic field (flux density {B8b_factor}× stronger) where it follows a circular path of radius <strong>{r8b} mm</strong>. What is the speed of the particle in the second field?",
        'A': f"{opts8[0]} m s⁻¹", 'B': f"{opts8[1]} m s⁻¹", 'C': f"{opts8[2]} m s⁻¹", 'D': f"{opts8[3]} m s⁻¹",
        'answer': ans8,
        'explanation': rf"r = mv/BQ → v = BQr/m ∝ Br. In the second field: v₂ = v₁ × (B₂/B₁) × (r₂/r₁) = {v8} × {B8b_factor} × ({r8b}/{r8a}) = <strong>{v8b} m s⁻¹</strong>."
    })

    # --- Q9: EMF induced in a rotating coil — when is it maximum? ---
    questions.append({
        'q': r"A rectangular coil rotates at constant angular velocity in a uniform magnetic field. At which position is the induced EMF at its <strong>maximum</strong>?",
        'A': r"When the plane of the coil is perpendicular to the field lines (coil face-on to field)",
        'B': r"When the plane of the coil is parallel to the field lines (coil edge-on to field)",
        'C': r"When the flux linkage through the coil is at its maximum",
        'D': r"When the coil has completed exactly half a revolution",
        'answer': 'B',
        'explanation': r"EMF = BANω sin(ωt). EMF is maximum when sin(ωt) = 1, i.e., when the coil plane is <strong>parallel</strong> to the field (edge-on). This is when the coil is cutting field lines at the greatest rate. When perpendicular to the field (face-on), flux is maximum but rate of change is zero, so EMF = 0."
    })

    # --- Q10: National Grid — efficient transmission (like AQA Q23) ---
    questions.append({
        'q': r"The National Grid transfers electrical energy from power stations to consumers. What combination of transmission voltage and current gives the <strong>most efficient</strong> transfer of energy?",
        'A': r"High voltage, high current",
        'B': r"High voltage, low current",
        'C': r"Low voltage, high current",
        'D': r"Low voltage, low current",
        'answer': 'B',
        'explanation': r"Power lost as heat in cables = I²R. To transmit a fixed power P = IV at high V means low I. Since P_loss ∝ I², a small reduction in current causes a large reduction in energy loss. Step-up transformers achieve this. <strong>Answer: B</strong>."
    })

    # --- Q11: Coil P and Q — force after switch closed (like AQA Q10 / Q19) ---
    questions.append({
        'q': r"A coil P is connected to a cell and a switch. A separate closed coil Q sits parallel to P on the same axis. The switch is closed. Which statement correctly describes the force experienced by coil Q?",
        'A': r"A steady attractive force",
        'B': r"A steady repulsive force",
        'C': r"A brief force that increases then decreases to zero",
        'D': r"No force at all",
        'answer': 'C',
        'explanation': r"When the switch is closed, the current in P rises from zero to a steady value. The <em>changing</em> current produces a changing flux in Q, inducing a current in Q by Faraday's Law. By Lenz's Law, this induced current creates a repulsive force. Once P's current is steady, the flux is constant, no EMF is induced in Q, no current flows in Q, and the force drops to zero. The force is therefore <strong>brief — it increases then decreases to zero</strong>."
    })

    # --- Q12: Specific charge — radius proportionality ---
    questions.append({
        'q': r"A proton is accelerated through a potential difference V and enters a uniform magnetic field B, following a circular path of radius r. The potential difference is now increased to 4V (with B unchanged). What is the new radius of the circular path?",
        'A': r"r/2",
        'B': r"r√2",
        'C': r"2r",
        'D': r"4r",
        'answer': 'C',
        'explanation': r"From eV = ½mv², v ∝ √V. From r = mv/BQ, r ∝ v ∝ √V. If V is multiplied by 4, r is multiplied by √4 = <strong>2</strong>. New radius = 2r."
    })

    # --- Q13: Flux linkage numerical ---
    N13 = random.choice([50, 100, 200])
    A13_cm2 = random.choice([20, 40, 50])
    A13 = A13_cm2 / 10000
    B13 = random.choice([0.05, 0.10, 0.20])
    NFlux13 = round(N13 * B13 * A13 * 1000, 2)
    wrong13a = round(B13 * A13 * 1000, 3)
    wrong13b = round(N13 * B13 * 1000, 1)
    wrong13c = round(N13 * A13 * 1000, 2)
    opts13 = [NFlux13, wrong13a, wrong13b, wrong13c]
    random.shuffle(opts13)
    ans13 = ['A','B','C','D'][opts13.index(NFlux13)]
    questions.append({
        'q': rf"A coil has <strong>{N13} turns</strong> and a cross-sectional area of <strong>{A13_cm2} cm²</strong>. It is placed perpendicular to a uniform magnetic field of flux density <strong>{B13} T</strong>. What is the magnetic flux linkage in mWb?",
        'A': f"{opts13[0]} mWb", 'B': f"{opts13[1]} mWb", 'C': f"{opts13[2]} mWb", 'D': f"{opts13[3]} mWb",
        'answer': ans13,
        'explanation': rf"Flux linkage NΦ = NBA = {N13} × {B13} × {A13} = {N13*B13*A13:.4f} Wb = <strong>{NFlux13} mWb</strong>. Common errors: forgetting to convert cm² to m², or omitting the N turns multiplier."
    })

    # --- Q14: Cyclotron period independence ---
    questions.append({
        'q': r"A proton in a cyclotron is accelerated repeatedly as it spirals outward. Which quantity remains <strong>constant</strong> throughout the proton's acceleration?",
        'A': r"The radius of the proton's circular path",
        'B': r"The speed of the proton as it crosses each Dee",
        'C': r"The time taken to complete one full circular orbit",
        'D': r"The kinetic energy of the proton inside each Dee",
        'answer': 'C',
        'explanation': r"T = 2πm/BQ — the period depends only on mass m, flux density B, and charge Q, none of which change. This independence of speed and radius is the key principle that makes the cyclotron work. The radius increases with each orbit (r ∝ v), and speed increases at each gap crossing."
    })

    # --- Q15: EMF induced in coil rotating 90 degrees (like AQA Q21) ---
    N15 = random.choice([10, 20, 50])
    d15_mm = random.choice([40, 60, 80])
    d15 = d15_mm / 1000
    B15_mT = random.choice([60, 90, 120])
    B15 = B15_mT / 1000
    A15 = math.pi * (d15/2)**2
    NFlux15 = N15 * B15 * A15
    dt15 = random.choice([0.10, 0.15, 0.20])
    emf15 = round(NFlux15 / dt15 * 1000, 1)
    wrong15a = 0
    wrong15b = round(emf15 / 2, 1)
    wrong15c = round(emf15 * 2, 1)
    opts15 = [emf15, wrong15a, wrong15b, wrong15c]
    random.shuffle(opts15)
    ans15 = ['A','B','C','D'][opts15.index(emf15)]
    questions.append({
        'q': rf"A coil with <strong>{N15} turns</strong>, each of diameter <strong>{d15_mm} mm</strong>, is placed perpendicular to a magnetic field of flux density <strong>{B15_mT} mT</strong>. It is rotated 90° in <strong>{dt15} s</strong> so its plane is now parallel to the field. Assume constant rate of change of flux linkage. What is the induced EMF?",
        'A': f"{opts15[0]} mV", 'B': f"{opts15[1]} mV", 'C': f"{opts15[2]} mV", 'D': f"{opts15[3]} mV",
        'answer': ans15,
        'explanation': rf"Initial flux linkage = NBA = {N15} × {B15} × π×({d15/2:.3f})² = {NFlux15:.4f} Wb. Final flux linkage = 0 (parallel to field). ΔNΦ = {NFlux15:.4f} Wb. EMF = ΔNΦ/Δt = {NFlux15:.4f}/{dt15} = {NFlux15/dt15*1000:.1f} mV. A common error is choosing zero — that would be the answer if the coil were already parallel to the field."
    })

    # --- Q16: Magnetic force does no work ---
    questions.append({
        'q': r"A charged particle moves in a uniform magnetic field with no other forces present. Which of the following statements is correct?",
        'A': r"The magnetic force increases the particle's speed",
        'B': r"The magnetic force does positive work on the particle",
        'C': r"The particle's kinetic energy remains constant",
        'D': r"The particle's momentum remains constant in magnitude and direction",
        'answer': 'C',
        'explanation': r"The magnetic force F = BQv is always perpendicular to velocity v. Since Work = F·v = 0 at all times, no work is done and kinetic energy (and therefore speed) is constant — <strong>Answer C</strong>. The direction of the momentum vector does change (circular path), so D is incorrect. A and B are directly contradicted by the work argument."
    })

    # --- Q17: Peak power in a transformer/lamp ---
    Np17 = random.choice([2000, 2500, 3000])
    Ns17 = random.choice([100, 130, 150])
    Vp17rms = 230
    R17 = random.choice([4.0, 6.0, 8.0])
    Vs17rms = round(Vp17rms * Ns17 / Np17, 2)
    Vs17peak = round(Vs17rms * math.sqrt(2), 2)
    P_peak17 = round(Vs17peak**2 / R17, 1)
    P_rms17 = round(Vs17rms**2 / R17, 1)
    P_half17 = round(P_peak17 / 2, 1)
    P_quarter17 = round(P_peak17 / 4, 1)
    opts17 = [P_peak17, P_rms17, P_half17, P_quarter17]
    random.shuffle(opts17)
    ans17 = ['A','B','C','D'][opts17.index(P_peak17)]
    questions.append({
        'q': rf"A transformer has a primary coil of <strong>{Np17} turns</strong> and a secondary coil of <strong>{Ns17} turns</strong>, connected to the <strong>230 V rms</strong> mains. The secondary coil is connected to a lamp of resistance <strong>{R17} Ω</strong>. The transformer is 100% efficient. What is the <strong>peak power</strong> dissipated in the lamp?",
        'A': f"{opts17[0]} W", 'B': f"{opts17[1]} W", 'C': f"{opts17[2]} W", 'D': f"{opts17[3]} W",
        'answer': ans17,
        'explanation': rf"Vs(rms) = 230 × {Ns17}/{Np17} = {Vs17rms} V. Vs(peak) = Vs(rms) × √2 = {Vs17peak} V. Peak power = Vs(peak)²/R = {Vs17peak}²/{R17} = <strong>{P_peak17} W</strong>. A common error is using Vs(rms) directly, which gives the <em>mean</em> power {P_rms17} W, not the peak."
    })

    # --- Q18: Helical motion concept ---
    questions.append({
        'q': r"A charged particle enters a uniform magnetic field at an angle θ to the field lines (neither parallel nor perpendicular). Which statement best describes the resulting motion?",
        'A': r"The particle travels in a circular arc, then slows and reverses",
        'B': r"The particle travels in a straight line along the field",
        'C': r"The particle follows a helical path with the axis along the field direction",
        'D': r"The particle is immediately deflected perpendicular to both B and v",
        'answer': 'C',
        'explanation': r"The velocity component parallel to B (v cosθ) experiences no magnetic force and remains constant. The component perpendicular to B (v sinθ) experiences a centripetal magnetic force giving circular motion. The combination of constant forward drift and circular rotation is a <strong>helix</strong> with its axis along the field direction."
    })

    # --- Q19: Transformer turns ratio / voltage ---
    Np19 = random.choice([500, 1000, 2000])
    ratio19 = random.choice([5, 8, 10])
    Ns19 = Np19 * ratio19
    Vp19 = random.choice([25, 50, 100])
    Vs19 = Vp19 * ratio19
    wrong19a = Vp19 * Np19 // Ns19 if Ns19 != 0 else 1
    wrong19b = Vp19 + ratio19 * 10
    wrong19c = Vp19 * ratio19 * 2
    opts19 = [Vs19, wrong19a, wrong19b, wrong19c]
    random.shuffle(opts19)
    ans19 = ['A','B','C','D'][opts19.index(Vs19)]
    questions.append({
        'q': rf"A step-up transformer has <strong>{Np19} turns</strong> on the primary coil and <strong>{Ns19} turns</strong> on the secondary coil. An alternating voltage of <strong>{Vp19} V</strong> is applied to the primary. Assuming 100% efficiency, what is the output voltage?",
        'A': f"{opts19[0]} V", 'B': f"{opts19[1]} V", 'C': f"{opts19[2]} V", 'D': f"{opts19[3]} V",
        'answer': ans19,
        'explanation': rf"Vs/Vp = Ns/Np → Vs = Vp × (Ns/Np) = {Vp19} × ({Ns19}/{Np19}) = <strong>{Vs19} V</strong>. This is a step-up transformer (Ns > Np), so voltage increases. Option {['A','B','C','D'][opts19.index(wrong19a)]} gives the step-down result by inverting the ratio."
    })

    # --- Q20: Force on circular coil in uniform field ---
    questions.append({
        'q': r"A circular coil carrying a clockwise current is placed in a uniform magnetic field directed <strong>into the page</strong>, with the plane of the coil perpendicular to the field. What is the effect of the magnetic force on the coil?",
        'A': r"It rotates about a diameter",
        'B': r"It is pushed out of the field region",
        'C': r"It tends to expand — the diameter increases",
        'D': r"It tends to contract — the diameter decreases",
        'answer': 'C',
        'explanation': r"Use Fleming's Left Hand Rule on each small element of the coil. The current flows clockwise; the field is into the page. For every element, the magnetic force points <strong>radially outward</strong> from the centre. The net effect is that the coil is pushed outward on all sides simultaneously — it tries to expand. This is the principle used in railgun armatures and MRI gradient coils."
    })

    # Pick one at random
    chosen = random.choice(questions)

    opts_html = (
        f"<br><br><strong>A</strong> — {chosen['A']}<br>"
        f"<strong>B</strong> — {chosen['B']}<br>"
        f"<strong>C</strong> — {chosen['C']}<br>"
        f"<strong>D</strong> — {chosen['D']}"
    )
    q_text = chosen['q'] + opts_html
    s_text = (
        f"<strong>Correct answer: {chosen['answer']}</strong><br><br>"
        f"{chosen['explanation']}"
    )
    hint_text = "This is a multiple choice question — eliminate the distractors by checking each option against the physics."
    return q_text, s_text, hint_text, 1


def alevel_physics_magnetism(difficulty, mode):
    # EXAM MODE + DIFFICULT gets the exclusive 12-15 mark variants

    if mode == 'mcq':
        q, s, hint, marks = mag_mcq()
        return make_problem(q, s, hint, difficulty, marks, 'alevel', 'physics', 'magnetism')

    if mode == 'exam' and difficulty == 'difficult':
        variant = random.choice([
            mag_exam_current_balance,
            mag_exam_fine_beam_tube,
            mag_exam_mass_spec_uranium,
            mag_exam_cyclotron_synoptic,
            mag_exam_bubble_chamber,
            mag_exam_mhd_blood_flow,
            mag_exam_railgun,
            mag_exam_galvanometer,
            mag_exam_helical_trap,
            mag_exam_crossed_fields_comparative,
            mag_exam_ac_generator,
            mag_exam_falling_magnet,
            mag_exam_transformer
        ])
    # Standard exam mode mixed difficulties
    elif mode == 'exam' and difficulty == 'mixed':
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
                mag_exam_current_balance,
                mag_exam_fine_beam_tube,
                mag_exam_mass_spec_uranium,
                mag_exam_cyclotron_synoptic,
                mag_exam_bubble_chamber,
                mag_exam_mhd_blood_flow,
                mag_exam_railgun,
                mag_exam_galvanometer,
                mag_exam_helical_trap,
                mag_exam_crossed_fields_comparative,
            ])
    # The rest is the standard routing for revision mode
    elif difficulty == 'foundational':
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
        # Standard difficult revision variants
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
            mag_diff_extra_levitation,
            mag_diff_extra_cyclotron_energy,
            mag_diff_extra_helical_pitch,
            mag_diff_extra_deflection_angle,
            mag_diff_extra_null_point,
            mag_diff_extra_isotope_ratio,
            mag_diff_extra_hall_drift,
            mag_diff_extra_crossed_accel,
            mag_diff_extra_earth_magnetic,
            mag_diff_extra_motor_efficiency,
        ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'alevel', 'physics', 'magnetism')

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
    while B == 0:
        B = round(random.uniform(0.1, 1.0), 2)
    T = (2 * math.pi * m) / (Q * B)
    if T == 0:
        T = 1e-10  # fallback, should never happen
    f = round(1 / T, 2)
    q = (rf"A proton (mass = 1.67 × 10⁻²⁷ kg, charge = 1.6 × 10⁻¹⁹ C) moves in a circular path inside a cyclotron. "
         rf"The magnetic flux density is <strong>{B} T</strong>.<br>"
         rf"<strong>a)</strong> Calculate the period of the proton's circular motion.<br>"
         rf"<strong>b)</strong> Calculate the frequency of the alternating voltage required for resonance.")
    s = (rf"<strong>a)</strong> T = 2πm / BQ = (2π × 1.67×10⁻²⁷) / ({B} × 1.6×10⁻¹⁹) = <strong>{T:.3e} s</strong>.<br><br>"
         rf"<strong>b)</strong> f = 1/T = <strong>{f:.2e} Hz</strong>.")
    hint = r"T = 2πm/BQ. This is independent of speed — that's what makes the cyclotron work!"
    return q, s, hint, 3

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


def mag_diff_extra_levitation():
    m_grams = random.randint(10, 50)
    m = m_grams / 1000
    L = round(random.uniform(0.1, 0.5), 2)
    B = round(random.uniform(0.05, 0.3), 3)
    g = 9.81
    I = round((m * g) / (B * L), 2)
    q = (rf"A stiff horizontal copper rod of mass <strong>{m_grams} g</strong> and length <strong>{L} m</strong> is suspended by two thin vertical wires. "
         rf"A uniform horizontal magnetic field of <strong>{B} T</strong> is applied perpendicular to the rod.<br>"
         rf"<strong>a)</strong> Calculate the current required to reduce the tension in the supporting wires to zero.<br>"
         rf"<strong>b)</strong> State the direction the current must flow relative to the magnetic field to achieve this, explaining your reasoning.")
    s = (rf"<strong>a)</strong> For zero tension, magnetic force must exactly balance weight: F<sub>B</sub> = mg.<br>"
         rf"BIL = mg → I = mg / BL<br>"
         rf"I = ({m} × 9.81) / ({B} × {L}) = <strong>{I} A</strong>.<br><br>"
         rf"<strong>b)</strong> By Fleming's Left Hand Rule: to produce an upward force (thumb up) with a horizontal magnetic field (first finger), "
         rf"the current (second finger) must flow mutually perpendicular to both, oriented such that the upward magnetic force opposes gravity.")
    hint = r"For levitation, magnetic force F = BIL must equal weight W = mg."
    return q, s, hint, 5

def mag_diff_extra_cyclotron_energy():
    R = round(random.uniform(0.3, 0.8), 2)
    B = round(random.uniform(0.5, 2.0), 2)
    m = 1.67e-27
    Q = 1.6e-19
    v_max = (B * Q * R) / m
    ke_joules = 0.5 * m * v_max**2
    ke_mev = round(ke_joules / (1.6e-19 * 1e6), 2)
    q = (rf"A cyclotron is used to accelerate protons (m = 1.67 × 10⁻²⁷ kg, Q = 1.6 × 10⁻¹⁹ C). "
         rf"The dees have a maximum radius of <strong>{R} m</strong> and the magnetic flux density is <strong>{B} T</strong>.<br>"
         rf"<strong>a)</strong> Derive an expression for the maximum kinetic energy of a particle in a cyclotron in terms of B, Q, R, and m.<br>"
         rf"<strong>b)</strong> Calculate the maximum kinetic energy of the protons emerging from this cyclotron, in <strong>MeV</strong>.")
    s = (rf"<strong>a)</strong> Max velocity occurs at max radius R: BQv = mv²/R → v = BQR/m.<br>"
         rf"Kinetic Energy E<sub>k</sub> = ½mv² = ½m(BQR/m)² = <strong>B²Q²R² / 2m</strong>.<br><br>"
         rf"<strong>b)</strong> E<sub>k</sub> = ({B}² × (1.6×10⁻¹⁹)² × {R}²) / (2 × 1.67×10⁻²⁷)<br>"
         rf"E<sub>k</sub> = {ke_joules:.3e} J.<br>"
         rf"In MeV: {ke_joules:.3e} / (1.6×10⁻¹³ J/MeV) = <strong>{ke_mev} MeV</strong>.")
    hint = r"Substitute v = BQR/m into KE = ½mv². Don't forget to convert Joules to MeV by dividing by 1.6×10⁻¹³."
    return q, s, hint, 5

def mag_diff_extra_helical_pitch():
    B = round(random.uniform(0.1, 0.5), 2)
    v = random.randint(2, 8) * 10**6
    theta = random.choice([30, 45, 60])
    m = 9.11e-31  # electron
    Q = 1.6e-19
    rad = math.radians(theta)
    v_par = v * math.cos(rad)
    T = (2 * math.pi * m) / (Q * B)
    pitch = v_par * T
    v_display = f"{v:.2e}"
    pitch_display = f"{pitch:.4e}"
    q = (rf"An electron (m = 9.11 × 10⁻³¹ kg, Q = 1.6 × 10⁻¹⁹ C) enters a uniform magnetic field of <strong>{B} T</strong> "
         rf"with a speed of <strong>{v_display} m s⁻¹</strong> at an angle of <strong>{theta}°</strong> to the magnetic field lines.<br>"
         rf"<strong>a)</strong> Calculate the time taken for one complete orbit (the period).<br>"
         rf"<strong>b)</strong> Calculate the 'pitch' of the helical path (the distance travelled parallel to the field during one orbit).")
    s = (rf"<strong>a)</strong> T = 2πm / BQ = (2π × 9.11×10⁻³¹) / ({B} × 1.6×10⁻¹⁹) = {T:.4e} s.<br><br>"
         rf"<strong>b)</strong> The parallel velocity component is unaffected by the field: v<sub>∥</sub> = v cos({theta}°).<br>"
         rf"v<sub>∥</sub> = {v_display} × cos({theta}°) = {v_par:.2e} m s⁻¹.<br>"
         rf"Pitch = v<sub>∥</sub> × T = {v_par:.2e} × {T:.4e} = <strong>{pitch_display} m</strong>.")
    hint = r"Pitch = parallel velocity × period. v_parallel = v cos(θ). T = 2πm/BQ."
    return q, s, hint, 4

def mag_diff_extra_deflection_angle():
    B = round(random.uniform(1.0, 5.0) * 1e-3, 3)
    v = random.randint(1, 5) * 10**7
    x_cm = random.randint(2, 8)
    x = x_cm / 100
    m = 9.11e-31
    Q = 1.6e-19
    R = (m * v) / (Q * B)
    # Ensure x < R for valid arcsin
    if x > R: x = R * 0.8
    angle = math.degrees(math.asin(x / R))
    v_display = f"{v:.2e}"
    q = (rf"A beam of electrons moving at <strong>{v_display} m s⁻¹</strong> enters a uniform magnetic field of <strong>{B} T</strong>. "
         rf"The field acts over a horizontal distance of <strong>{x_cm} cm</strong>, after which the electrons emerge.<br>"
         rf"<strong>a)</strong> Calculate the radius of curvature of the electrons inside the field.<br>"
         rf"<strong>b)</strong> Calculate the angle through which the beam has been deflected by the time it emerges from the field.")
    s = (rf"<strong>a)</strong> R = mv / BQ = (9.11×10⁻³¹ × {v_display}) / ({B} × 1.6×10⁻¹⁹) = <strong>{R:.4f} m</strong>.<br><br>"
         rf"<strong>b)</strong> The electron travels an arc of a circle. By geometry, sin(θ) = x / R, where x is the horizontal distance.<br>"
         rf"sin(θ) = {x} / {R:.4f} = {x/R:.4f}.<br>"
         rf"θ = sin⁻¹({x/R:.4f}) = <strong>{angle:.2f}°</strong>.")
    hint = r"Draw a right-angled triangle mapping the sector of the circular path. The angle of deflection θ satisfies sin(θ) = horizontal width / radius."
    return q, s, hint, 5

def mag_diff_extra_null_point():
    I1 = random.randint(2, 6)
    factor = random.choice([2, 3, 4])
    I2 = I1 * factor
    d_cm = random.randint(10, 30)
    d = d_cm / 100
    # For currents in same direction, null point is between them.
    # B1 = B2 -> I1/x = I2/(d-x) -> I1(d-x) = I2 x -> x = I1*d / (I1 + I2)
    x = (I1 * d) / (I1 + I2)
    q = (rf"Two long, straight parallel wires are placed <strong>{d_cm} cm</strong> apart. Wire A carries a current of <strong>{I1} A</strong> "
         rf"and Wire B carries a current of <strong>{I2} A</strong> in the <strong>same direction</strong>.<br>"
         rf"Calculate the exact distance from Wire A to the point between the wires where the net magnetic flux density is zero.")
    s = (rf"At the null point, the magnetic fields from A and B must be equal and opposite: B<sub>A</sub> = B<sub>B</sub>.<br>"
         rf"μ₀I₁ / 2πx = μ₀I₂ / 2π(d - x) → I₁ / x = I₂ / (d - x).<br>"
         rf"{I1} / x = {I2} / ({d} - x)<br>"
         rf"{I1}({d} - x) = {I2}x → {I1*d} - {I1}x = {I2}x → {I1+I2}x = {I1*d}<br>"
         rf"x = {I1*d} / {I1+I2} = <strong>{x:.3f} m</strong> (or {x*100:.1f} cm).")
    hint = r"Equate the two B fields using B = μ₀I/2πr. If distance from A is x, distance from B is (d - x)."
    return q, s, hint, 4

def mag_diff_extra_isotope_ratio():
    V = random.randint(500, 2000)
    B = round(random.uniform(0.1, 0.5), 2)
    # Comparing Carbon-12 and Carbon-14
    m12 = 12 * 1.66e-27
    m14 = 14 * 1.66e-27
    Q = 1.6e-19
    r12 = (1/B) * math.sqrt((2 * m12 * V) / Q)
    r14 = (1/B) * math.sqrt((2 * m14 * V) / Q)
    diff = (r14 - r12) * 1000  # in mm
    q = (rf"Carbon-12 (mass = 12 u) and Carbon-14 (mass = 14 u) ions, both with a charge of +e, are accelerated from rest "
         rf"through a potential difference of <strong>{V} V</strong>. They then enter a uniform magnetic field of <strong>{B} T</strong>.<br>"
         rf"<strong>a)</strong> Show that the radius of curvature r is given by r = (1/B)√(2mV/Q).<br>"
         rf"<strong>b)</strong> Calculate the difference in their radii of curvature in <strong>mm</strong>. (1 u = 1.66 × 10⁻²⁷ kg)")
    s = (rf"<strong>a)</strong> Work done by electric field = Kinetic energy gained: QV = ½mv² → v = √(2QV/m).<br>"
         rf"Magnetic force provides centripetal force: BQv = mv²/r → r = mv/BQ.<br>"
         rf"Substitute v: r = (m/BQ)√(2QV/m) = (1/B)√(2mV/Q).<br><br>"
         rf"<strong>b)</strong> For C-12: r₁₂ = (1/{B}) √(2 × 12 × 1.66×10⁻²⁷ × {V} / 1.6×10⁻¹⁹) = {r12:.4f} m.<br>"
         rf"For C-14: r₁₄ = (1/{B}) √(2 × 14 × 1.66×10⁻²⁷ × {V} / 1.6×10⁻¹⁹) = {r14:.4f} m.<br>"
         rf"Difference = r₁₄ - r₁₂ = {r14 - r12:.4f} m = <strong>{diff:.2f} mm</strong>.")
    hint = r"First equate electrical work QV to ½mv² to find v. Then use r = mv/BQ."
    return q, s, hint, 5

def mag_diff_extra_hall_drift():
    B = round(random.uniform(0.1, 0.8), 2)
    w_mm = random.randint(5, 15)
    w = w_mm / 1000
    V_H_mv = round(random.uniform(0.1, 5.0), 2)
    V_H = V_H_mv / 1000
    E = V_H / w
    v = E / B
    q = (rf"A Hall probe of width <strong>{w_mm} mm</strong> is placed in a magnetic field of <strong>{B} T</strong>. "
         rf"A Hall voltage of <strong>{V_H_mv} mV</strong> is measured across its width.<br>"
         rf"<strong>a)</strong> Calculate the strength of the transverse electric field E created inside the probe.<br>"
         rf"<strong>b)</strong> Calculate the drift velocity of the charge carriers in the probe.")
    s = (rf"<strong>a)</strong> Electric field E = V / d = V<sub>H</sub> / w.<br>"
         rf"E = {V_H} / {w} = <strong>{E:.3f} V m⁻¹</strong>.<br><br>"
         rf"<strong>b)</strong> In steady state, electric force balances magnetic force: QE = BQv → v = E / B.<br>"
         rf"v = {E:.3f} / {B} = <strong>{v:.3e} m s⁻¹</strong>.")
    hint = r"E = V_H / width. To find drift velocity without current or carrier density, use the force balance QE = BQv."
    return q, s, hint, 4

def mag_diff_extra_crossed_accel():
    E = random.randint(2, 8) * 10**4
    B = round(random.uniform(0.1, 0.5), 2)
    v = random.randint(1, 5) * 10**5  # speed is not exactly E/B
    m = 1.67e-27  # proton
    Q = 1.6e-19
    F_e = Q * E
    F_b = B * Q * v
    F_net = F_e - F_b
    a = F_net / m
    v_display = f"{v:.2e}"
    E_display = f"{E:.2e}"
    q = (rf"A proton enters a region of crossed electric and magnetic fields. The electric field is <strong>{E_display} V m⁻¹</strong> acting downwards. "
         rf"The magnetic field is <strong>{B} T</strong> acting into the page. The proton moves horizontally to the right at <strong>{v_display} m s⁻¹</strong>.<br>"
         rf"<strong>a)</strong> Determine the magnitude and direction of the net force on the proton at the instant it enters the region.<br>"
         rf"<strong>b)</strong> Calculate its initial acceleration.")
    s = (rf"<strong>a)</strong> Electric force F<sub>E</sub> = QE = 1.6×10⁻¹⁹ × {E_display} = {F_e:.3e} N (downwards).<br>"
         rf"Magnetic force F<sub>B</sub> = BQv = {B} × 1.6×10⁻¹⁹ × {v_display} = {F_b:.3e} N (upwards, by FLHR).<br>"
         rf"Net Force = {abs(F_net):.3e} N. "
         rf"Direction: <strong>{'Downwards' if F_net > 0 else 'Upwards'}</strong> (since F_{'E' if F_net > 0 else 'B'} is larger).<br><br>"
         rf"<strong>b)</strong> a = F<sub>net</sub> / m = {abs(F_net):.3e} / 1.67×10⁻²⁷ = <strong>{abs(a):.3e} m s⁻²</strong>.")
    hint = r"Calculate QE and BQv separately. Determine their directions (E field is downward for positive charge; FLHR for B field). Subtract them for net force."
    return q, s, hint, 5

def mag_diff_extra_earth_magnetic():
    B_earth = 3.5e-5  # typical equatorial field
    v = random.randint(2, 6) * 10**6
    m = 1.67e-27
    Q = 1.6e-19
    R_earth = 6.4e6
    R_path = (m * v) / (Q * B_earth)
    v_display = f"{v:.2e}"
    q = (rf"Earth's magnetic field at the equator is approximately <strong>3.5 × 10⁻⁵ T</strong> horizontally North. "
         rf"A proton from the solar wind arrives vertically downwards at the equator with a speed of <strong>{v_display} m s⁻¹</strong>.<br>"
         rf"<strong>a)</strong> Calculate the radius of the proton's resulting circular path.<br>"
         rf"<strong>b)</strong> State the initial direction of the magnetic force on the proton.<br>"
         rf"<strong>c)</strong> Explain why, in reality, protons from the solar wind get trapped in Earth's Van Allen belts rather than hitting the equator directly.")
    s = (rf"<strong>a)</strong> r = mv / BQ = (1.67×10⁻²⁷ × {v_display}) / (3.5×10⁻⁵ × 1.6×10⁻¹⁹) = <strong>{R_path:.0f} m</strong> (or {R_path/1000:.1f} km).<br><br>"
         rf"<strong>b)</strong> By Fleming's Left Hand Rule: current is down, field is North → force acts <strong>East</strong>.<br><br>"
         rf"<strong>c)</strong> Protons rarely arrive perfectly perpendicular to the field. Because they approach with a velocity component parallel to the "
         rf"Earth's magnetic field lines, they undergo helical (spiral) motion along the lines toward the poles, becoming trapped in the magnetosphere.")
    hint = r"Use r = mv/BQ for part a. For part b, remember conventional current is the direction of positive charge flow."
    return q, s, hint, 4

def mag_diff_extra_motor_efficiency():
    V = random.randint(6, 24)
    I = random.uniform(1.5, 4.0)
    R = round(random.uniform(0.5, 2.0), 2)
    P_in = V * I
    P_loss = (I**2) * R
    P_mech = P_in - P_loss
    efficiency = round((P_mech / P_in) * 100, 1)
    I_rounded = round(I, 2)
    q = (rf"A simple DC electric motor connected to a <strong>{V} V</strong> supply draws a current of <strong>{I_rounded} A</strong>. "
         rf"The internal resistance of the motor's coil is <strong>{R} Ω</strong>.<br>"
         rf"<strong>a)</strong> Calculate the electrical power supplied to the motor.<br>"
         rf"<strong>b)</strong> Calculate the rate of heat dissipation in the coil.<br>"
         rf"<strong>c)</strong> Assuming all remaining power is converted to useful mechanical power (rotating the coil against external resistance), calculate the efficiency of the motor.")
    s = (rf"<strong>a)</strong> P<sub>in</sub> = VI = {V} × {I_rounded} = <strong>{P_in:.1f} W</strong>.<br><br>"
         rf"<strong>b)</strong> Heat loss P<sub>loss</sub> = I²R = ({I_rounded})² × {R} = <strong>{P_loss:.1f} W</strong>.<br><br>"
         rf"<strong>c)</strong> Useful power = P<sub>in</sub> - P<sub>loss</sub> = {P_in:.1f} - {P_loss:.1f} = {P_mech:.1f} W.<br>"
         rf"Efficiency = (Useful / Input) × 100 = ({P_mech:.1f} / {P_in:.1f}) × 100 = <strong>{efficiency}%</strong>.")
    hint = r"Total power input = VI. Power wasted as heat in the coils = I²R. The rest is mechanical power doing work via the magnetic torque."
    return q, s, hint, 5





# -----------------------------------------------
# MAIN GENERATOR FUNCTION
# -----------------------------------------------

def mag_exam_current_balance():
    L_cm = random.randint(4, 8)
    L = L_cm / 100
    I = round(random.uniform(2.0, 5.0), 2)
    B = round(random.uniform(0.04, 0.09), 3)
    g = 9.81
    dm_grams = round((B * I * L) / g * 1000, 2)
    diagram = r"""<svg width="220" height="120" viewBox="0 0 220 120" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <rect x="60" y="20" width="100" height="20" fill="#a13544" rx="3"/>
      <rect x="60" y="80" width="100" height="20" fill="#01696f" rx="3"/>
      <text x="110" y="35" fill="#fff" font-family="sans-serif" font-weight="bold" text-anchor="middle">N</text>
      <text x="110" y="95" fill="#fff" font-family="sans-serif" font-weight="bold" text-anchor="middle">S</text>
      <line x1="20" y1="60" x2="200" y2="60" stroke="#da7101" stroke-width="6"/>
      <text x="205" y="64" font-family="sans-serif" font-weight="bold">I</text>
      <polygon points="175,56 185,60 175,64" fill="#333"/>
    </svg>"""
    q = (r"<strong>[14 marks] Synoptic: The Current Balance & Resistivity</strong><br>"
         r"A student uses a top-pan balance to determine the magnetic flux density B of a horseshoe magnet. "
         rf"A rigid copper wire of length <strong>{L_cm} cm</strong> is clamped horizontally between the poles.<br>{diagram}"
         r"When the current is zero, the balance is tared to read 0.00 g.<br>"
         rf"When a current of <strong>{I} A</strong> flows, the balance reading changes to <strong>+{dm_grams} g</strong>.<br><br>"
         r"<strong>a)</strong> State and explain the direction of the magnetic force acting on the wire.<br>"
         r"<strong>b)</strong> Explain, referencing Newton's laws, why the balance registers a positive mass reading.<br>"
         r"<strong>c)</strong> Derive the equation relating the change in mass reading Δm, current I, length L, and flux density B.<br>"
         r"<strong>d)</strong> Calculate the magnetic flux density B of the magnet.<br>"
         r"<strong>e)</strong> The wire is connected to a power supply of constant voltage V. The wire has cross-sectional area A and resistivity ρ. "
         r"By combining equations for electricity and magnetism, show that the mass reading Δm is directly proportional to the cross-sectional area A (Δm ∝ A).<br>"
         r"<strong>f)</strong> Using the proportionality from (e), determine what would happen to the mass reading if a wire of the same length and material, but twice the diameter, were used.")
    s = (r"<strong>a)</strong> The force on the wire must be <strong>upwards</strong>. By Fleming's Left Hand Rule, field, current, and force are mutually perpendicular.<br><br>"
         r"<strong>b)</strong> By Newton's Third Law, if the magnet exerts an upward force on the wire, the wire exerts an equal and opposite <strong>downward</strong> force on the magnet. "
         r"This downward force pushes the magnet into the pan, registering as an increased mass.<br><br>"
         r"<strong>c)</strong> Magnetic force F = BIL. Apparent weight W = Δm g. Equating them: BIL = Δm g → Δm = (BL / g) I.<br><br>"
         rf"<strong>d)</strong> B = (Δm g) / (IL) = ({dm_grams} × 10⁻³ × 9.81) / ({I} × {L}) = <strong>{B:.3f} T</strong>.<br><br>"
         r"<strong>e)</strong> Current I = V / R. Resistance R = ρL / A. Therefore, I = V A / (ρL).<br>"
         r"Substitute I into the balance equation: Δm = (BL / g) × (V A / ρL) = (BV / ρg) A.<br>"
         r"Since B, V, ρ, and g are constant, Δm ∝ A.<br><br>"
         r"<strong>f)</strong> Area A = πd²/4. If diameter d is doubled, Area A increases by a factor of 4. "
         r"Since Δm ∝ A, the mass reading will be <strong>4 times larger</strong>.")
    hint = r"For part (e), substitute the resistivity equation into Ohm's law, then substitute that current expression into your equation from part (c)."
    return q, s, hint, 14

def mag_exam_fine_beam_tube():
    V = random.randint(150, 300)
    B_mT = round(random.uniform(0.5, 1.5), 2)
    B = B_mT * 1e-3
    r_cm = round(random.uniform(3.0, 6.0), 1)
    r = r_cm / 100
    e_m = (2 * V) / (B**2 * r**2)
    diagram = r"""<svg width="200" height="160" viewBox="0 0 200 160" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <circle cx="100" cy="80" r="60" fill="none" stroke="#01696f" stroke-width="2" stroke-dasharray="6,4"/>
      <circle cx="100" cy="20" r="5" fill="#333"/>
      <line x1="100" y1="20" x2="140" y2="20" stroke="#333" stroke-width="2"/>
      <polygon points="135,16 145,20 135,24" fill="#333"/>
      <text x="150" y="24" font-family="sans-serif" font-style="italic">v</text>
      <text x="100" y="85" font-family="sans-serif" text-anchor="middle" fill="#01696f">B-field ⊗</text>
      <line x1="100" y1="80" x2="100" y2="20" stroke="#888" stroke-dasharray="2,2"/>
      <text x="105" y="55" font-family="sans-serif" font-size="12">r</text>
    </svg>"""
    q = (r"<strong>[14 marks] Specific Charge & Proportionality</strong><br>"
         r"Electrons are emitted from a heated cathode and accelerated through a potential difference "
         rf"of <strong>{V} V</strong>. They enter a uniform magnetic field of <strong>{B_mT} mT</strong>. "
         rf"The electrons travel in a circular path of radius <strong>{r_cm} cm</strong>.<br>{diagram}"
         r"<strong>a)</strong> Show that the velocity v of the electrons entering the magnetic field is given by v = √(2eV/m).<br>"
         r"<strong>b)</strong> Show that the specific charge of the electron (e/m) is given by e/m = 2V / (B² r²).<br>"
         r"<strong>c)</strong> Calculate the specific charge of the electron using the experimental data provided.<br>"
         r"<strong>d)</strong> Rearrange the equation from (b) to show that the radius of the path r is proportional to √V (r ∝ √V), assuming B is constant.<br>"
         r"<strong>e)</strong> The accelerating voltage is increased by a factor of 3. State the exact factor by which the radius of the path increases.<br>"
         r"<strong>f)</strong> Explain why this method for finding e/m becomes invalid if the accelerating voltage V is increased to several million volts.")
    s = (r"<strong>a)</strong> Electrical work done = kinetic energy gained. eV = ½mv² → v² = 2eV/m → v = √(2eV/m).<br><br>"
         r"<strong>b)</strong> Centripetal force = magnetic force: mv²/r = Bev → v = Ber/m. Substitute v into eV = ½mv²:<br>"
         r"eV = ½m(Ber/m)² = (B² e² r²) / 2m. Rearranging gives e/m = 2V / (B² r²).<br><br>"
         rf"<strong>c)</strong> e/m = (2 × {V}) / ({B}² × {r}²) = <strong>{e_m:.2e} C kg⁻¹</strong>.<br><br>"
         r"<strong>d)</strong> From e/m = 2V / (B² r²), rearrange for r²: r² = 2V / (B² (e/m)).<br>"
         r"Taking the square root: r = √(2 / (B² e/m)) × √V. Since B, e, and m are constants, r ∝ √V.<br><br>"
         r"<strong>e)</strong> Since r ∝ √V, multiplying V by 3 means r is multiplied by <strong>√3</strong> (approx 1.73).<br><br>"
         r"<strong>f)</strong> At very high voltages, the electrons reach relativistic speeds. Their mass m increases, meaning the classical kinetic energy equation (E_k = ½mv²) is no longer valid.")
    hint = r"For proportionalities, isolate the variable of interest on one side, group all the constants together, and see what power the changing variable is raised to."
    return q, s, hint, 14

def mag_exam_mass_spec_uranium():
    B1 = round(random.uniform(0.1, 0.4), 2)
    B2 = round(random.uniform(0.5, 1.0), 2)
    E_kV = random.randint(10, 50)
    E = E_kV * 1000
    v = E / B1
    m235 = 235 * 1.66e-27
    m238 = 238 * 1.66e-27
    Q = 1.6e-19
    r235 = (m235 * v) / (Q * B2)
    r238 = (m238 * v) / (Q * B2)
    separation = (2 * r238) - (2 * r235)
    diagram = r"""<svg width="240" height="140" viewBox="0 0 240 140" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <rect x="40" y="20" width="160" height="8" fill="#888"/>
      <rect x="40" y="112" width="160" height="8" fill="#888"/>
      <text x="25" y="28" font-family="sans-serif" font-weight="bold" fill="#a13544">+</text>
      <text x="25" y="120" font-family="sans-serif" font-weight="bold" fill="#3b78ab">−</text>
      <line x1="80" y1="35" x2="80" y2="105" stroke="#a13544" stroke-width="1.5" stroke-dasharray="4,2"/>
      <line x1="120" y1="35" x2="120" y2="105" stroke="#a13544" stroke-width="1.5" stroke-dasharray="4,2"/>
      <line x1="160" y1="35" x2="160" y2="105" stroke="#a13544" stroke-width="1.5" stroke-dasharray="4,2"/>
      <text x="120" y="75" font-family="sans-serif" fill="#01696f" text-anchor="middle" font-size="14">⊗  ⊗  B₁  ⊗  ⊗</text>
      <line x1="10" y1="70" x2="230" y2="70" stroke="#333" stroke-width="2"/>
      <polygon points="220,66 230,70 220,74" fill="#333"/>
      <circle cx="50" cy="70" r="4" fill="#e8af34"/>
      <text x="45" y="60" font-family="sans-serif" font-size="12">v</text>
    </svg>"""
    q = (r"<strong>[15 marks] Uranium Isotope Separation & General Derivations</strong><br>"
         r"A mass spectrometer separates Uranium-235 and Uranium-238 ions (+e). They pass through a velocity selector "
         rf"(magnetic field B₁ = <strong>{B1} T</strong>, electric field E = <strong>{E_kV} kV m⁻¹</strong>).<br>{diagram}"
         rf"They then enter a deflection chamber (magnetic field B₂ = <strong>{B2} T</strong>).<br><br>"
         r"<strong>a)</strong> Derive the equation for the velocity v selected by the collimator.<br>"
         r"<strong>b)</strong> Calculate the selected velocity v.<br>"
         r"<strong>c)</strong> The ions trace a semicircle. Let the distance from the entry slit to the detector be x. Show that for an ion of mass m, x = 2mv / (B₂ Q).<br>"
         r"<strong>d)</strong> By using the expression from (c), show that the physical separation Δx between two isotopes with mass difference Δm is given by Δx = (2v / B₂ Q) Δm.<br>"
         r"<strong>e)</strong> Calculate the physical separation Δx between the U-235 and U-238 isotopes. (1 u = 1.66 × 10⁻²⁷ kg)<br>"
         r"<strong>f)</strong> If the electric field E in the velocity selector is increased, what happens to the separation Δx? Explain using your derived formulas.")
    s = (r"<strong>a)</strong> Electric force F_E = EQ. Magnetic force F_B = B₁Qv. For no deflection, F_E = F_B → EQ = B₁Qv → v = E / B₁.<br><br>"
         rf"<strong>b)</strong> v = {E} / {B1} = <strong>{v:.2e} m s⁻¹</strong>.<br><br>"
         r"<strong>c)</strong> Radius r = mv / (B₂ Q). The distance x is the diameter, so x = 2r = 2mv / (B₂ Q).<br><br>"
         r"<strong>d)</strong> Δx = x₂ - x₁ = [2m₂v / (B₂ Q)] - [2m₁v / (B₂ Q)].<br>"
         r"Factoring out the constants: Δx = (2v / B₂ Q) (m₂ - m₁) = (2v / B₂ Q) Δm.<br><br>"
         rf"<strong>e)</strong> Δm = (238 - 235) × 1.66×10⁻²⁷ = 4.98×10⁻²⁷ kg.<br>"
         rf"Δx = (2 × {v:.2e} / ({B2} × 1.6×10⁻¹⁹)) × 4.98×10⁻²⁷ = <strong>{separation:.4f} m</strong>.<br><br>"
         r"<strong>f)</strong> If E increases, the selected velocity v increases (v = E/B₁). From Δx = (2v / B₂ Q) Δm, we see that Δx ∝ v. "
         r"Therefore, a higher velocity results in a <strong>larger separation</strong> Δx.")
    hint = r"For part (d), start with x_2 - x_1 and factor out all the shared terms to leave (m_2 - m_1)."
    return q, s, hint, 15

def mag_exam_cyclotron_synoptic():
    B = round(random.uniform(0.5, 1.5), 2)
    f_MHz = round(random.uniform(10.0, 25.0), 1)
    f = f_MHz * 1e6
    V_kV = random.randint(20, 80)
    V = V_kV * 1000
    r_cm = random.randint(30, 60)
    r = r_cm / 100

    m_p = 1.67e-27
    e = 1.6e-19

    # Calculate required B for this frequency
    B_actual = (2 * math.pi * f * m_p) / e

    v_max = (B_actual * e * r) / m_p
    ke_max_J = 0.5 * m_p * v_max**2
    ke_max_MeV = ke_max_J / (e * 1e6)

    diagram = r"""<svg width="220" height="180" viewBox="0 0 220 180" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <path d="M 100,20 A 70,70 0 0,0 100,160 L 100,20 Z" fill="none" stroke="#3b78ab" stroke-width="4"/>
      <path d="M 120,20 A 70,70 0 0,1 120,160 L 120,20 Z" fill="none" stroke="#a13544" stroke-width="4"/>
      <text x="60" y="95" font-family="sans-serif" font-weight="bold" fill="#3b78ab">Dee 1</text>
      <text x="135" y="95" font-family="sans-serif" font-weight="bold" fill="#a13544">Dee 2</text>
      <text x="110" y="15" font-family="sans-serif" text-anchor="middle" fill="#01696f">Uniform B-field ⊙</text>
      <path d="M 110,90 Q 115,85 110,80 Q 100,70 110,60 Q 125,45 110,30 Q 90,10 110,-10" fill="none" stroke="#da7101" stroke-width="2" stroke-dasharray="4,2"/>
      <circle cx="110" cy="90" r="4" fill="#333"/>
      <rect x="95" y="170" width="30" height="8" fill="#333"/>
      <text x="110" y="186" font-family="sans-serif" font-size="10" text-anchor="middle">AC Supply</text>
      <line x1="100" y1="160" x2="100" y2="170" stroke="#333" stroke-width="1"/>
      <line x1="120" y1="160" x2="120" y2="170" stroke="#333" stroke-width="1"/>
    </svg>"""

    q = (r"<strong>[14 marks] Particle Accelerators: The Cyclotron</strong><br>"
         r"A cyclotron is used to accelerate protons to high kinetic energies for use in medical physics.<br>"
         rf"{diagram}"
         rf"The cyclotron consists of two hollow 'Dees' separated by a narrow gap, placed in a uniform magnetic field of flux density <strong>B</strong>. "
         rf"An alternating voltage of <strong>{V_kV} kV</strong> is applied across the gap. The oscillator frequency is set to <strong>{f_MHz} MHz</strong>.<br><br>"
         r"<strong>a)</strong> Explain the purpose of both the magnetic field and the alternating electric field in the cyclotron.<br>"
         r"<strong>b)</strong> Show that the time T taken for a proton to complete one full circular orbit is independent of its velocity and radius.<br>"
         r"<strong>c)</strong> Use your answer to (b) to calculate the exact magnetic flux density B required for the protons to stay in sync with the "
         rf"<strong>{f_MHz} MHz</strong> oscillator frequency. (m_p = 1.67 × 10⁻²⁷ kg)<br>"
         rf"<strong>d)</strong> The maximum radius of the Dees is <strong>{r_cm} cm</strong>. Calculate the maximum kinetic energy of the protons as they exit the cyclotron. Give your answer in MeV.<br>"
         r"<strong>e)</strong> A student suggests that to increase the maximum kinetic energy, they should simply increase the alternating voltage V across the gap. "
         r"Discuss whether this suggestion is correct.")
    s = (r"<strong>a)</strong> <strong>Magnetic field:</strong> Provides a force perpendicular to the velocity (F = Bqv), acting as a centripetal force to keep the protons moving in a circular path within the Dees.<br>"
         r"<strong>Electric field:</strong> Accelerates the protons across the gap between the Dees, increasing their kinetic energy. It must be alternating so that the field reverses direction every half-orbit, ensuring the proton is always accelerated forwards.<br><br>"
         r"<strong>b)</strong> Centripetal force = Magnetic force: mv²/r = Bqv → v = Bqr/m.<br>"
         r"Time for one orbit T = Distance / Speed = 2πr / v.<br>"
         r"Substitute v: T = 2πr / (Bqr/m) = 2πm / Bq. Since m, B, and q are constants, T is independent of v and r.<br><br>"
         r"<strong>c)</strong> Time period T = 1 / f. Therefore, 1/f = 2πm / Bq → B = 2πmf / q.<br>"
         rf"B = (2π × 1.67×10⁻²⁷ × {f_MHz}×10⁶) / (1.6×10⁻¹⁹) = <strong>{B_actual:.3f} T</strong>.<br><br>"
         rf"<strong>d)</strong> Max velocity v_max = Bqr / m = ({B_actual:.3f} × 1.6×10⁻¹⁹ × {r}) / 1.67×10⁻²⁷ = {v_max:.2e} m s⁻¹.<br>"
         rf"Max KE (Joules) = ½mv² = 0.5 × 1.67×10⁻²⁷ × ({v_max:.2e})² = {ke_max_J:.2e} J.<br>"
         rf"Max KE (MeV) = {ke_max_J:.2e} / (1.6×10⁻¹⁹ × 10⁶) = <strong>{ke_max_MeV:.1f} MeV</strong>.<br><br>"
         r"<strong>e)</strong> <strong>Incorrect.</strong> Increasing V only increases the energy gained <em>per gap crossing</em>, meaning the proton takes fewer orbits to reach the edge. "
         r"The maximum kinetic energy is determined entirely by the magnetic field B and the maximum radius of the Dees r (E_k ∝ B²r²).")
    hint = r"For (c), remember that the oscillator must complete one full cycle in the exact same time it takes the proton to complete one full orbit."
    return q, s, hint, 14

def mag_exam_bubble_chamber():
    B = round(random.uniform(1.5, 3.5), 2)
    r1 = round(random.uniform(0.1, 0.4), 3)
    Q = 1.6e-19
    m = 9.11e-31
    p1 = B * Q * r1
    ke1 = (B**2 * Q**2 * r1**2) / (2 * m)
    q = (r"<strong>[12 marks] Bubble Chamber & Kinetic Energy Relationships</strong><br>"
         rf"An electron enters a liquid hydrogen bubble chamber containing a uniform magnetic field of <strong>{B} T</strong>. "
         r"The electron leaves a visible track that spirals inwards due to collisions.<br><br>"
         r"<strong>a)</strong> Show that the momentum p of the electron is directly proportional to its radius of curvature r.<br>"
         r"<strong>b)</strong> Show that the kinetic energy E_k of the non-relativistic electron is given by E_k = (B² Q² r²) / (2m).<br>"
         r"<strong>c)</strong> Using the equation in (b), state the proportionality between kinetic energy and radius. If the radius of the track halves, by what factor does the kinetic energy decrease?<br>"
         rf"<strong>d)</strong> At point A, the radius of the track is <strong>{r1} m</strong>. Calculate the kinetic energy of the electron at A in Joules.<br>"
         r"<strong>e)</strong> Explain why liquid hydrogen is used in the chamber rather than a gas.")
    s = (r"<strong>a)</strong> Centripetal force = Magnetic force: mv²/r = BQv → mv/r = BQ → mv = BQr.<br>"
         r"Since p = mv, we have p = BQr. Because B and Q are constant, p ∝ r.<br><br>"
         r"<strong>b)</strong> Kinetic energy E_k = p² / 2m. From (a), p = BQr.<br>"
         r"Substitute p: E_k = (BQr)² / 2m = (B² Q² r²) / 2m.<br><br>"
         r"<strong>c)</strong> E_k ∝ r². If the radius halves (r → r/2), the kinetic energy is multiplied by (1/2)² = 1/4. "
         r"It decreases by a factor of 4.<br><br>"
         rf"<strong>d)</strong> E_k = ({B}² × (1.6×10⁻¹⁹)² × {r1}²) / (2 × 9.11×10⁻³¹) = <strong>{ke1:.2e} J</strong>.<br><br>"
         r"<strong>e)</strong> A liquid has a much higher density than a gas. This means more frequent collisions, which slows the particles down faster and ensures the entire track fits within the visible chamber.")
    hint = r"For (b), using the formula E_k = p²/2m is the fastest way to get the derivation."
    return q, s, hint, 12

def mag_exam_mhd_blood_flow():
    v = round(random.uniform(0.1, 0.5), 2)
    B = round(random.uniform(0.05, 0.20), 2)
    d_mm = random.randint(4, 12)
    d = d_mm / 1000
    V_mv = round(B * v * d * 1000, 3)
    Z = (math.pi * d**2 / 4) * v
    diagram = r"""<svg width="200" height="160" viewBox="0 0 200 160" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <circle cx="100" cy="80" r="50" fill="#fef0f0" stroke="#a13544" stroke-width="3"/>
      <text x="100" y="20" font-family="sans-serif" fill="#01696f" text-anchor="middle" font-weight="bold">B-field ↓</text>
      <line x1="100" y1="25" x2="100" y2="135" stroke="#01696f" stroke-width="2" stroke-dasharray="4,4"/>
      <polygon points="96,125 100,135 104,125" fill="#01696f"/>
      <text x="65" y="85" font-family="sans-serif" font-weight="bold" fill="#a13544">+</text>
      <text x="65" y="70" font-family="sans-serif" font-weight="bold" fill="#a13544">+</text>
      <text x="65" y="100" font-family="sans-serif" font-weight="bold" fill="#a13544">+</text>
      <text x="130" y="85" font-family="sans-serif" font-weight="bold" fill="#3b78ab">−</text>
      <text x="130" y="70" font-family="sans-serif" font-weight="bold" fill="#3b78ab">−</text>
      <text x="130" y="100" font-family="sans-serif" font-weight="bold" fill="#3b78ab">−</text>
      <text x="100" y="155" font-family="sans-serif" font-size="12" text-anchor="middle">Blood flow (v) into page ⊗</text>
    </svg>"""
    q = (r"<strong>[14 marks] Medical Physics: MHD Flowmeter & Volume Flow Rate</strong><br>"
         r"An electromagnetic flowmeter measures the speed of blood. "
         rf"The artery has an internal diameter of <strong>{d_mm} mm</strong>. A magnetic field of <strong>{B} T</strong> is applied.<br>{diagram}"
         r"<strong>a)</strong> Derive the equation V = Bvd for the potential difference across the artery, starting from the forces on a single ion.<br>"
         r"<strong>b)</strong> The volume flow rate Z (in m³ s⁻¹) is the volume of blood passing a point per second. "
         r"Derive an expression for Z in terms of V, d, and B.<br>"
         rf"<strong>c)</strong> The measured potential difference is <strong>{V_mv} mV</strong>. Calculate the blood velocity v.<br>"
         r"<strong>d)</strong> Calculate the volume flow rate Z in m³ s⁻¹.<br>"
         r"<strong>e)</strong> Suggest why the magnetic field must be alternating (AC) rather than static (DC) in a real medical device.")
    s = (r"<strong>a)</strong> Equilibrium occurs when electric force equals magnetic force: qE = Bqv → E = Bv. "
         r"For a uniform electric field across diameter d, V = Ed. Substituting E yields V = Bvd.<br><br>"
         r"<strong>b)</strong> Volume flow rate Z = Area × velocity = A v. The cross-sectional area of the artery A = πd² / 4. "
         r"From (a), v = V / (Bd). Substituting both: Z = (πd² / 4) × (V / Bd). Simplifying gives Z = πdV / 4B.<br><br>"
         rf"<strong>c)</strong> v = V / Bd = ({V_mv} × 10⁻³) / ({B} × {d}) = <strong>{v:.3f} m s⁻¹</strong>.<br><br>"
         rf"<strong>d)</strong> Z = A v = (π × {d}² / 4) × {v:.3f} = <strong>{Z:.2e} m³ s⁻¹</strong>.<br><br>"
         r"<strong>e)</strong> A static DC field causes ions to permanently migrate to the vessel walls, polarizing the artery (which creates resistance/polarization artifacts). "
         r"An AC field continuously flips the direction, preventing charge buildup and providing a cleaner signal.")
    hint = r"Volume flow rate Z = Cross-sectional Area × velocity. The area is a circle: πd²/4."
    return q, s, hint, 14

def mag_exam_railgun():
    B = round(random.uniform(0.5, 2.0), 2)
    I = random.randint(1000, 5000)
    L_cm = random.randint(10, 30)
    L = L_cm / 100
    m_g = random.randint(5, 20)
    m = m_g / 1000
    track_len = round(random.uniform(1.0, 3.0), 1)
    F = B * I * L
    a = F / m
    v_exit = math.sqrt(2 * a * track_len)
    diagram = r"""<svg width="240" height="120" viewBox="0 0 240 120" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <rect x="20" y="30" width="200" height="8" fill="#a13544"/>
      <rect x="20" y="82" width="200" height="8" fill="#3b78ab"/>
      <rect x="80" y="38" width="12" height="44" fill="#da7101"/>
      <line x1="92" y1="60" x2="140" y2="60" stroke="#333" stroke-width="2"/>
      <polygon points="135,56 145,60 135,64" fill="#333"/>
      <text x="115" y="50" font-family="sans-serif" font-size="12" font-style="italic">v</text>
      <text x="25" y="65" font-family="sans-serif" font-size="12" fill="#01696f">B-field ⊙ (Out of page)</text>
    </svg>"""
    q = (r"<strong>[14 marks] Electromagnetic Railgun & Kinetic Energy Scaling</strong><br>"
         r"A railgun uses magnetic forces to accelerate a projectile. A projectile of mass "
         rf"<strong>{m_g} g</strong> slides across two rails separated by <strong>{L_cm} cm</strong>.<br>{diagram}"
         rf"A magnetic field of <strong>{B} T</strong> is applied, and a current of <strong>{I} A</strong> flows.<br><br>"
         r"<strong>a)</strong> Derive an expression for the final exit velocity v of the projectile in terms of B, I, L, mass m, and track length s. Assume it starts from rest.<br>"
         r"<strong>b)</strong> Show that the exit velocity v ∝ √I.<br>"
         r"<strong>c)</strong> State the proportionality between the exit kinetic energy and the current I. If the current is tripled, by what factor does the exit kinetic energy increase?<br>"
         rf"<strong>d)</strong> If the rails are <strong>{track_len} m</strong> long, calculate the final exit velocity of the projectile.<br>"
         r"<strong>e)</strong> Explain how Faraday's Law limits the maximum velocity achievable in reality.")
    s = (r"<strong>a)</strong> Magnetic force F = BIL. Acceleration a = F / m = BIL / m. "
         r"Using kinematics: v² = u² + 2as. With u = 0: v² = 2(BIL/m)s → v = √(2BILs / m).<br><br>"
         r"<strong>b)</strong> From v = √(2BILs / m), we can separate the constant terms: v = √(2BLs/m) × √I. "
         r"Since B, L, s, and m are constants, v ∝ √I.<br><br>"
         r"<strong>c)</strong> Kinetic energy E_k = ½mv². Since v ∝ √I, v² ∝ I. Therefore E_k ∝ I. "
         r"Because it is directly proportional, tripling the current increases the kinetic energy by a factor of <strong>3</strong>.<br><br>"
         rf"<strong>d)</strong> a = ({B} × {I} × {L}) / {m} = {a:.0f} m s⁻².<br>"
         rf"v = √(2 × {a:.0f} × {track_len}) = <strong>{v_exit:.1f} m s⁻¹</strong>.<br><br>"
         r"<strong>e)</strong> As the projectile accelerates, it cuts the magnetic field lines faster. By Faraday's Law, this induces an EMF. "
         r"By Lenz's Law, this back-EMF opposes the driving voltage, reducing the net current in the circuit. As current drops, acceleration drops towards zero.")
    hint = r"Combine F=BIL, Newton's second law (F=ma), and the suvat equation v² = u² + 2as."
    return q, s, hint, 14

def mag_exam_galvanometer():
    N = random.randint(50, 200)
    B = round(random.uniform(0.1, 0.4), 2)
    A_cm2 = round(random.uniform(2.0, 6.0), 1)
    A = A_cm2 * 1e-4
    k_e6 = random.randint(2, 8)
    k = k_e6 * 1e-6
    I = random.randint(1, 5) * 1e-3
    tau = N * B * I * A
    theta_rad = tau / k
    theta_deg = math.degrees(theta_rad)
    diagram = r"""<svg width="220" height="160" viewBox="0 0 220 160" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <path d="M 40,20 A 70,70 0 0,0 40,140 L 10,140 L 10,20 Z" fill="#a13544"/>
      <text x="20" y="85" fill="#fff" font-family="sans-serif" font-weight="bold">N</text>
      <path d="M 180,20 A 70,70 0 0,1 180,140 L 210,140 L 210,20 Z" fill="#01696f"/>
      <text x="190" y="85" fill="#fff" font-family="sans-serif" font-weight="bold">S</text>
      <circle cx="110" cy="80" r="35" fill="#dcd9d5"/>
      <rect x="105" y="35" width="10" height="90" fill="none" stroke="#da7101" stroke-width="4"/>
      <line x1="45" y1="80" x2="70" y2="80" stroke="#333" stroke-width="1" stroke-dasharray="2,2"/>
      <line x1="150" y1="80" x2="175" y2="80" stroke="#333" stroke-width="1" stroke-dasharray="2,2"/>
      <text x="110" y="15" font-family="sans-serif" font-size="10" text-anchor="middle">Radial Field</text>
    </svg>"""
    q = (r"<strong>[12 marks] Moving Coil Galvanometer & Sensitivity</strong><br>"
         r"A galvanometer coil is suspended in a radial magnetic field.<br>{diagram}"
         rf"The coil has <strong>{N} turns</strong>, area <strong>{A_cm2} cm²</strong>, and flux density <strong>{B} T</strong>. "
         rf"The restoring torque is τ_r = kθ, where k = <strong>{k_e6} × 10⁻⁶ N m rad⁻¹</strong>.<br><br>"
         r"<strong>a)</strong> Show that the angle of deflection θ is given by θ = (BAN/k) I, and explain why a radial field is essential for this linear relationship.<br>"
         r"<strong>b)</strong> The 'current sensitivity' of a galvanometer is defined as θ / I. "
         r"A manufacturer modifies the coil by doubling the number of turns N, but to keep the mass constant, they halve the cross-sectional area A of the coil. "
         r"Using the equation from (a), determine the effect on the current sensitivity.<br>"
         rf"<strong>c)</strong> A current of <strong>{I * 1000:.1f} mA</strong> flows. Calculate the steady deflection angle θ in degrees.<br>"
         r"<strong>d)</strong> Explain how a galvanometer is converted into a voltmeter.")
    s = (r"<strong>a)</strong> Magnetic torque τ_m = BIAN sin(φ). A radial field ensures the coil is always parallel to field lines, so φ = 90° and sin(φ) = 1. "
         r"At equilibrium, τ_m = τ_r → BIAN = kθ → θ = (BAN/k) I. Without a radial field, sin(φ) varies, making the scale non-linear.<br><br>"
         r"<strong>b)</strong> Current sensitivity θ / I = BAN / k. "
         r"If N is doubled (N → 2N) and A is halved (A → A/2), the product AN becomes (A/2)(2N) = AN. "
         r"The sensitivity remains exactly the <strong>same</strong> (unchanged).<br><br>"
         rf"<strong>c)</strong> τ = {B} × {I:.3e} × {A:.1e} × {N} = {tau:.2e} N m.<br>"
         rf"θ_rad = τ / k = {tau:.2e} / {k:.1e} = {theta_rad:.3f} rad.<br>"
         rf"In degrees: {theta_rad:.3f} × (180 / π) = <strong>{theta_deg:.1f}°</strong>.<br><br>"
         r"<strong>d)</strong> A very high value resistor (multiplier) is connected in series with the galvanometer. This ensures it draws minimal current from the circuit it is measuring across.")
    hint = r"For part b, substitute the new values (2N and A/2) into the expression for BAN/k and see what cancels."
    return q, s, hint, 12

def mag_exam_helical_trap():
    B1 = round(random.uniform(1.0, 3.0), 1)
    v = random.randint(2, 8) * 10**6
    theta = random.choice([30, 45, 60])
    m = 1.67e-27
    Q = 1.6e-19
    r1 = (m * v * math.sin(math.radians(theta))) / (Q * B1)
    q = (r"<strong>[12 marks] Synoptic: Magnetic Mirrors & Helical Pitch</strong><br>"
         r"A proton in a fusion reactor's central region (where B = <strong>{B1} T</strong>) is moving at "
         rf"<strong>{v:.2e} m s⁻¹</strong> at an angle of <strong>{theta}°</strong> to the field lines.<br><br>"
         r"<strong>a)</strong> Show that the pitch p of the helix (distance between successive coils) is given by p = (2πmv cosθ) / (BQ).<br>"
         r"<strong>b)</strong> The proton is replaced by an alpha particle entering at the same speed and angle. "
         r"By considering the mass and charge ratios, determine by what factor the pitch of the helix changes.<br>"
         rf"<strong>c)</strong> Calculate the radius of the proton's helical path.<br>"
         r"<strong>d)</strong> Explain qualitatively how the shape of the helix changes as the proton moves into a region of stronger magnetic field, causing it to be reflected.")
    s = (r"<strong>a)</strong> Time period T = 2πm / BQ. Parallel velocity v_parallel = v cosθ.<br>"
         r"Pitch p = distance travelled parallel to B in one orbit = v_parallel × T.<br>"
         r"Substituting gives: p = v cosθ × (2πm / BQ) = (2πmv cosθ) / BQ.<br><br>"
         r"<strong>b)</strong> Alpha particle has mass 4m and charge 2Q. "
         r"Pitch p ∝ m/Q. For alpha, m/Q ratio is 4m / 2Q = 2(m/Q). "
         r"Therefore, the pitch is <strong>doubled</strong> (factor of 2).<br><br>"
         rf"<strong>c)</strong> v_perp = v sin({theta}°) = {v:.2e} × sin({theta}°) = {v * math.sin(math.radians(theta)):.2e} m s⁻¹.<br>"
         rf"r = m v_perp / BQ = (1.67×10⁻²⁷ × {v * math.sin(math.radians(theta)):.2e}) / ({B1} × 1.6×10⁻¹⁹) = <strong>{r1:.4f} m</strong>.<br><br>"
         r"<strong>d)</strong> As B increases, the radius r decreases (tighter spiral). Due to conservation of energy and magnetic moment, v_perp increases while v_parallel decreases. "
         r"Eventually v_parallel becomes zero, and the gradient of the magnetic field exerts a backward force, reflecting the proton.")
    hint = r"For the alpha particle, remember it has 2 protons and 2 neutrons, so mass = 4m_p and charge = +2e."
    return q, s, hint, 12

def mag_exam_crossed_fields_comparative():
    E = random.randint(10, 50) * 1000
    B = round(random.uniform(1.0, 3.0) * 1e-3, 3)
    L_cm = random.randint(2, 5)
    L = L_cm / 100
    v = E / B
    m = 9.11e-31
    Q = 1.6e-19
    r_B = (m * v) / (Q * B)
    if r_B <= L:
        L = r_B * 0.5
    time = L / v
    deflect_B = r_B - math.sqrt(r_B**2 - L**2)
    q = (r"<strong>[14 marks] Deflection Approximations: E-field vs B-field</strong><br>"
         rf"An electron beam passes undeflected through crossed fields where E = <strong>{E:.1e} V m⁻¹</strong> and B = <strong>{B} T</strong>. "
         rf"Both fields act over a horizontal distance of exactly <strong>{L:.3f} m</strong>.<br><br>"
         r"<strong>a)</strong> Calculate the velocity v of the electrons.<br>"
         r"<strong>b)</strong> Show that the vertical deflection y_E in the electric field alone is given by y_E = (QEL²) / (2mv²).<br>"
         r"<strong>c)</strong> For a magnetic field alone, geometry gives (r - y_B)² + L² = r². For small deflections, y_B² is negligible. "
         r"Use this to show that the magnetic deflection is approximately y_B ≈ L² / 2r.<br>"
         r"<strong>d)</strong> Hence derive an expression for the ratio y_E / y_B in terms of E, B, and v.<br>"
         r"<strong>e)</strong> Calculate the actual magnetic deflection y_B using the full geometric formula (without the small-angle approximation).")
    s = (rf"<strong>a)</strong> EQ = BQv → v = E / B = {E:.1e} / {B} = <strong>{v:.2e} m s⁻¹</strong>.<br><br>"
         r"<strong>b)</strong> Time in field t = L / v. Vertical acceleration a = EQ / m. "
         r"Deflection y_E = ½at² = ½(EQ/m)(L/v)² = (QEL²) / (2mv²).<br><br>"
         r"<strong>c)</strong> Expand the bracket: r² - 2ry_B + y_B² + L² = r². "
         r"The r² cancels. Ignore y_B² (since it is very small): -2ry_B + L² ≈ 0 → 2ry_B ≈ L² → y_B ≈ L² / 2r.<br><br>"
         r"<strong>d)</strong> From (c), substitute r = mv/BQ: y_B ≈ L² / (2mv/BQ) = (BQL²) / 2mv.<br>"
         r"Ratio y_E / y_B = [(QEL²) / (2mv²)] / [(BQL²) / 2mv]. "
         r"The Q, L², 2, and m terms all cancel, leaving: y_E / y_B = E / (Bv).<br><br>"
         rf"<strong>e)</strong> r = mv / BQ = (9.11×10⁻³¹ × {v:.2e}) / ({B} × 1.6×10⁻¹⁹) = {r_B:.4f} m.<br>"
         rf"y_B = r - √({r_B:.4f}² - {L:.3f}²) = <strong>{deflect_B:.4f} m</strong>.")
    hint = r"For part c, expand the bracket first. For part d, write both equations out fully and cancel terms top and bottom."
    return q, s, hint, 14

def mag_exam_ac_generator():
    N = random.randint(100, 500)
    A_cm2 = random.randint(20, 80)
    A = A_cm2 / 10000
    B = round(random.uniform(0.1, 0.5), 2)
    f = random.choice([25, 50, 60])
    w = 2 * math.pi * f
    e_max = 2 * math.pi * f * B * A * N
    diagram = r"""<svg width="220" height="150" viewBox="0 0 220 150" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <rect x="10" y="45" width="30" height="60" fill="#a13544" rx="2"/>
      <rect x="180" y="45" width="30" height="60" fill="#01696f" rx="2"/>
      <text x="25" y="80" fill="#fff" font-family="sans-serif" font-weight="bold" text-anchor="middle">N</text>
      <text x="195" y="80" fill="#fff" font-family="sans-serif" font-weight="bold" text-anchor="middle">S</text>
      <polygon points="80,55 140,35 140,95 80,115" fill="#e8f4f5" stroke="#da7101" stroke-width="3" opacity="0.8"/>
      <line x1="110" y1="15" x2="110" y2="135" stroke="#555" stroke-dasharray="4,4" stroke-width="2"/>
      <path d="M 90,25 A 20,10 0 0,1 130,25" fill="none" stroke="#333" stroke-width="2"/>
      <polygon points="125,23 132,25 125,27" fill="#333"/>
      <text x="140" y="25" font-family="sans-serif" font-style="italic">ω</text>
    </svg>"""
    q = (r"<strong>[14 marks] Electromagnetic Induction: The AC Generator</strong><br>"
         r"An alternating current (AC) generator consists of a rectangular coil rotating in a uniform magnetic field.<br>"
         rf"{diagram}"
         rf"The coil has <strong>{N} turns</strong>, an area of <strong>{A_cm2} cm²</strong>, and rotates at a constant frequency of <strong>{f} Hz</strong>. "
         rf"The uniform magnetic flux density is <strong>{B} T</strong>.<br><br>"
         r"<strong>a)</strong> Define <em>magnetic flux linkage</em>.<br>"
         r"<strong>b)</strong> State Faraday's law of electromagnetic induction.<br>"
         r"<strong>c)</strong> The flux linkage NΦ at time t is given by NΦ = BAN cos(ωt). By using calculus to differentiate this expression, show that the induced EMF ε is given by ε = BANω sin(ωt).<br>"
         r"<strong>d)</strong> Calculate the maximum induced EMF (ε_max) of the generator.<br>"
         r"<strong>e)</strong> The frequency of rotation is doubled to " + str(f*2) + r" Hz. State and explain the effect this has on both the maximum EMF and the time period of the alternating output.<br>"
         r"<strong>f)</strong> Sketch the graph of EMF against time for one full rotation, clearly labeling the axes with your maximum EMF and the time period.")
    s = (r"<strong>a)</strong> Magnetic flux linkage (NΦ) is the product of the magnetic flux (Φ) passing through a coil and the number of turns (N) on the coil.<br><br>"
         r"<strong>b)</strong> Faraday's Law states that the magnitude of the induced EMF is directly proportional to the rate of change of magnetic flux linkage (ε = - d(NΦ)/dt).<br><br>"
         r"<strong>c)</strong> ε = - d/dt [BAN cos(ωt)]. The derivative of cos(ωt) is -ω sin(ωt). "
         r"Therefore, ε = - BAN × (-ω sin(ωt)) = BANω sin(ωt).<br><br>"
         rf"<strong>d)</strong> ω = 2πf = 2π × {f} = {w:.1f} rad s⁻¹.<br>"
         rf"ε_max = BANω = {B} × {A:.4f} × {N} × {w:.1f} = <strong>{e_max:.1f} V</strong>.<br><br>"
         r"<strong>e)</strong> Since ε_max = BAN(2πf), ε_max ∝ f. Doubling the frequency <strong>doubles</strong> the maximum EMF. "
         r"Since Time Period T = 1/f, doubling the frequency <strong>halves</strong> the time period.<br><br>"
         r"<strong>f)</strong> [Graph features]: A sine wave starting at origin (0,0). Peak positive value at +" + f"{e_max:.1f}" + r" V, peak negative at -" + f"{e_max:.1f}" + r" V. "
         r"One full cycle completes at T = 1/f = " + f"{1/f:.3f}" + r" s.")
    hint = r"For part (c), remember the chain rule: d/dt(cos(kt)) = -k sin(kt). Max EMF occurs when sin(ωt) = 1."
    return q, s, hint, 14

def mag_exam_falling_magnet():
    N = random.randint(400, 1000)
    dPhi_mWb = round(random.uniform(1.0, 5.0), 2)
    dPhi = dPhi_mWb * 1e-3
    dt_ms = random.randint(15, 40)
    dt = dt_ms * 1e-3
    emf = (N * dPhi) / dt
    diagram = r"""<svg width="200" height="180" viewBox="0 0 200 180" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <rect x="85" y="20" width="30" height="25" fill="#01696f" rx="1"/>
      <rect x="85" y="45" width="30" height="25" fill="#a13544" rx="1"/>
      <text x="100" y="38" fill="#fff" font-family="sans-serif" font-weight="bold" text-anchor="middle">S</text>
      <text x="100" y="63" fill="#fff" font-family="sans-serif" font-weight="bold" text-anchor="middle">N</text>
      <line x1="100" y1="75" x2="100" y2="95" stroke="#333" stroke-width="2"/>
      <polygon points="96,90 100,98 104,90" fill="#333"/>
      <text x="110" y="90" font-family="sans-serif" font-style="italic">v</text>
      <path d="M 60,110 Q 100,130 140,110 Q 100,90 60,110" fill="none" stroke="#da7101" stroke-width="4"/>
      <path d="M 60,125 Q 100,145 140,125 Q 100,105 60,125" fill="none" stroke="#da7101" stroke-width="4"/>
      <path d="M 60,140 Q 100,160 140,140 Q 100,120 60,140" fill="none" stroke="#da7101" stroke-width="4"/>
      <line x1="60" y1="125" x2="30" y2="125" stroke="#333" stroke-width="2"/>
      <line x1="140" y1="125" x2="170" y2="125" stroke="#333" stroke-width="2"/>
      <text x="100" y="170" font-family="sans-serif" font-size="11" text-anchor="middle">To Oscilloscope</text>
    </svg>"""
    q = (r"<strong>[15 marks] Lenz's Law: Magnet Falling Through a Coil</strong><br>"
         r"A strong neodymium bar magnet is dropped vertically through a short coil of wire. The coil is connected to an oscilloscope.<br>"
         rf"{diagram}"
         r"<strong>a)</strong> State Lenz's Law.<br>"
         r"<strong>b)</strong> The oscilloscope trace shows a positive peak followed by a negative peak. Explain, using Lenz's Law, why the EMF changes direction as the magnet passes through the coil.<br>"
         r"<strong>c)</strong> Explain why the second (negative) peak on the oscilloscope trace has a larger maximum magnitude and a shorter duration than the first peak.<br>"
         rf"<strong>d)</strong> The coil has <strong>{N} turns</strong>. As the magnet enters, the flux through the coil changes by <strong>{dPhi_mWb} mWb</strong> over a time interval of <strong>{dt_ms} ms</strong>. "
         r"Calculate the average induced EMF during this time.<br>"
         r"<strong>e)</strong> The coil is replaced by a long, solid copper pipe. The magnet is dropped down the pipe. "
         r"Explain why the magnet falls through the copper pipe at a constant terminal velocity much lower than free-fall (electromagnetic braking).")
    s = (r"<strong>a)</strong> Lenz's Law states that the direction of an induced EMF (or current) is always such that it opposes the change in magnetic flux that caused it.<br><br>"
         r"<strong>b)</strong> As the N-pole approaches, the flux in the coil increases. The induced current creates a N-pole at the top to repel the magnet (opposing the increase), creating a positive EMF. "
         r"As the magnet leaves, the flux decreases. The induced current reverses to create a N-pole at the bottom to attract the leaving S-pole (opposing the decrease), resulting in a negative EMF.<br><br>"
         r"<strong>c)</strong> The magnet accelerates due to gravity as it falls. Therefore, it leaves the coil faster than it entered. "
         r"A higher velocity means a shorter time duration (Δt is smaller). Since ε ∝ 1/Δt (Faraday's Law), a shorter time results in a larger peak magnitude EMF.<br><br>"
         rf"<strong>d)</strong> ε = N (ΔΦ / Δt) = {N} × ({dPhi_mWb} × 10⁻³ / {dt_ms} × 10⁻³) = <strong>{emf:.2f} V</strong>.<br><br>"
         r"<strong>e)</strong> The falling magnet continuously induces large EMFs in the solid copper pipe. Because copper has low resistance, large eddy currents flow. "
         r"By Lenz's Law, the magnetic fields of these eddy currents oppose the magnet's motion, creating an upward magnetic force. "
         r"When this upward magnetic force equals the downward weight (mg), the net force is zero, and it falls at terminal velocity.")
    hint = r"For part (b) and (c), this is the classic 'two-peak' trace. Remember that gravity makes it fall faster as time progresses!"
    return q, s, hint, 15

def mag_exam_transformer():
    V_p = random.choice([25000, 33000, 132000])
    V_s = 400000
    N_p = random.randint(400, 1000)
    N_s = int(N_p * (V_s / V_p))
    I_p = random.randint(200, 500)
    P_in = V_p * I_p
    efficiency = random.choice([95, 96, 97, 98])
    P_out = P_in * (efficiency / 100)
    I_s = P_out / V_s
    diagram = r"""<svg width="220" height="160" viewBox="0 0 220 160" style="margin:15px 0;display:block;background:#f9f8f5;border-radius:8px;padding:10px;">
      <rect x="40" y="30" width="140" height="100" fill="none" stroke="#dcd9d5" stroke-width="24"/>
      <rect x="45" y="35" width="130" height="90" fill="none" stroke="#888" stroke-width="1"/>
      <rect x="50" y="40" width="120" height="80" fill="none" stroke="#888" stroke-width="1"/>
      <path d="M 18,50 L 52,50 M 18,65 L 52,65 M 18,80 L 52,80 M 18,95 L 52,95 M 18,110 L 52,110" stroke="#a13544" stroke-width="4"/>
      <path d="M 168,40 L 202,40 M 168,50 L 202,50 M 168,60 L 202,60 M 168,70 L 202,70 M 168,80 L 202,80 M 168,90 L 202,90 M 168,100 L 202,100 M 168,110 L 202,110 M 168,120 L 202,120" stroke="#01696f" stroke-width="3"/>
      <text x="15" y="25" font-family="sans-serif" font-size="12" fill="#a13544" font-weight="bold">Primary AC</text>
      <text x="140" y="25" font-family="sans-serif" font-size="12" fill="#01696f" font-weight="bold">Secondary</text>
    </svg>"""
    q = (r"<strong>[14 marks] Electromagnetic Induction: Real vs Ideal Transformers</strong><br>"
         r"A step-up transformer at a power station is used to transmit power into the National Grid.<br>"
         rf"{diagram}"
         rf"The primary coil has <strong>{N_p} turns</strong> and receives an alternating input voltage of <strong>{V_p / 1000:.0f} kV</strong>. "
         rf"The secondary coil steps this up to <strong>{V_s / 1000:.0f} kV</strong>.<br><br>"
         r"<strong>a)</strong> Explain the core physical principles by which an alternating voltage across the primary coil induces an EMF in the secondary coil.<br>"
         r"<strong>b)</strong> Calculate the required number of turns on the secondary coil.<br>"
         r"<strong>c)</strong> State two causes of energy loss in a real transformer, and for each, describe a design feature used to minimize it.<br>"
         rf"<strong>d)</strong> The current in the primary coil is <strong>{I_p} A</strong>. The transformer operates at exactly <strong>{efficiency}% efficiency</strong>. "
         r"Calculate the current delivered to the National Grid by the secondary coil.<br>"
         r"<strong>e)</strong> Show mathematically that transmitting power at 400 kV instead of 25 kV reduces the power lost as heat in the transmission cables by a factor of 256.")
    s = (r"<strong>a)</strong> An alternating voltage in the primary coil causes an alternating current. This generates a continuously changing magnetic flux. "
         r"The soft iron core links this changing flux to the secondary coil. By Faraday's Law, the changing flux linkage induces an alternating EMF in the secondary coil.<br><br>"
         rf"<strong>b)</strong> N_s / N_p = V_s / V_p → N_s = N_p × (V_s / V_p) = {N_p} × ({V_s} / {V_p}) = <strong>{N_s} turns</strong>.<br><br>"
         r"<strong>c)</strong> 1. Eddy currents heating the core: minimized by making the core out of laminated sheets separated by thin insulators.<br>"
         r"2. Resistive heating (I²R) in the coils: minimized by using thick, low-resistance copper wire.<br>"
         r"3. Hysteresis loss: minimized by using a 'soft' iron core that is easy to magnetise and demagnetise.<br><br>"
         rf"<strong>d)</strong> Input Power P_in = V_p × I_p = {V_p} × {I_p} = {P_in:.2e} W.<br>"
         rf"Output Power P_out = P_in × {efficiency/100:.2f} = {P_out:.2e} W.<br>"
         rf"Secondary Current I_s = P_out / V_s = {P_out:.2e} / {V_s} = <strong>{I_s:.2f} A</strong>.<br><br>"
         r"<strong>e)</strong> For a fixed transmitted power P = VI, current I = P/V. If V increases by a factor of 16 (400/25 = 16), current I decreases by a factor of 16. "
         r"Power lost in cables P_loss = I²R. Since I is divided by 16, the power lost is divided by 16², which is <strong>256</strong>.")
    hint = r"For (e), the power lost in the cables is I²R, but the power transmitted is P=VI. Don't mix up the two powers!"
    return q, s, hint, 14



# ================================================================
# A-LEVEL PHYSICS — PHOTOELECTRIC EFFECT & WAVE-PARTICLE DUALITY
# Fixed lesson generators for the lesson template
# ================================================================

def aqa_pe_basic():
    metal = random.choice(["zinc", "sodium", "caesium"])
    below_or_above = random.choice(["below", "above"])

    if below_or_above == "below":
        q = rf"""
Light of a frequency <strong>below the threshold frequency</strong> is shone on a clean surface of {metal}.
Explain what happens and why increasing the intensity will still not cause photoelectrons to be emitted.
"""
        s = rf"""
No photoelectrons are emitted. Each electron absorbs one photon, and if the photon energy is below the work function,
the electron cannot escape the metal surface.<br><br>
Increasing the intensity only increases the number of photons arriving each second, not the energy of each photon.
So if the frequency is below threshold, the photons still do not have enough energy to cause emission.
"""
        hint = "Think carefully about what changing intensity changes, and what changing frequency changes."
        marks = 3
    else:
        q = rf"""
Light of a frequency <strong>above the threshold frequency</strong> is shone on a clean surface of {metal}.
State what happens if the intensity is increased, and explain your answer using the photon model.
"""
        s = rf"""
Photoelectrons are emitted, and increasing the intensity increases the <strong>number</strong> of photoelectrons emitted per second.<br><br>
This is because higher intensity means more photons arrive each second. Since the frequency is already above threshold,
each photon has enough energy to release an electron, so more photons means more emitted electrons.
"""
        hint = "Above threshold: intensity affects number emitted, not the maximum kinetic energy."
        marks = 3

    return q, s, hint, marks


def aqa_pe_threshold_frequency():
    f0 = random.choice([4.8, 5.2, 5.6, 6.0, 6.4]) * 10**14
    h = 6.63e-34
    phi = h * f0
    phi_ev = phi / 1.60e-19

    q = rf"""
A metal has a threshold frequency of \( {f0/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \).<br><br>
(a) Calculate the work function of the metal in joules.<br>
(b) Convert your answer to electronvolts (eV).
"""
    s = rf"""
Use \( \phi = hf_0 \).<br><br>
(a) \( \phi = 6.63 \times 10^{{-34}} \times {f0/10**14:.1f} \times 10^{{14}} \)<br>
\( \phi = \boxed{{{phi:.3g} \, \text{{J}}}} \)<br><br>
(b) Convert to eV using \( 1 \, \text{{eV}} = 1.60 \times 10^{{-19}} \, \text{{J}} \):<br>
\( \phi = \frac{{{phi:.3g}}}{{1.60 \times 10^{{-19}}}} = \boxed{{{phi_ev:.3g} \, \text{{eV}}}} \)
"""
    hint = r"Use \( \phi = hf_0 \), then divide by \( 1.60 \times 10^{-19} \) to convert J to eV."
    return q, s, hint, 4


def aqa_pe_photoelectric_equation():
    f = random.choice([6.8, 7.2, 7.5, 8.0, 8.5]) * 10**14
    phi = random.choice([2.0, 2.2, 2.4, 2.6]) * 1.60e-19
    h = 6.63e-34
    photon_energy = h * f
    ke = photon_energy - phi

    while ke <= 0:
        f = random.choice([7.5, 8.0, 8.5, 9.0]) * 10**14
        phi = random.choice([1.8, 2.0, 2.2, 2.4]) * 1.60e-19
        photon_energy = h * f
        ke = photon_energy - phi

    q = rf"""
Ultraviolet radiation of frequency \( {f/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \) is incident on a metal surface.
The work function of the metal is \( {phi:.3g} \, \text{{J}} \).<br><br>
Calculate the maximum kinetic energy of the emitted photoelectrons.
"""
    s = rf"""
Use Einstein's photoelectric equation:<br>
\( hf = \phi + E_k \Rightarrow E_k = hf - \phi \)<br><br>
Photon energy:<br>
\( hf = 6.63 \times 10^{{-34}} \times {f/10**14:.1f} \times 10^{{14}} = {photon_energy:.3g} \, \text{{J}} \)<br><br>
So:<br>
\( E_k = {photon_energy:.3g} - {phi:.3g} = \boxed{{{ke:.3g} \, \text{{J}}}} \)
"""
    hint = r"Use \( E_k = hf - \phi \). First calculate the photon energy."
    return q, s, hint, 4


def aqa_pe_stopping_potential():
    Vs = random.choice([0.45, 0.62, 0.78, 0.95, 1.10])
    e = 1.60e-19
    ke = e * Vs

    q = rf"""
In a photoelectric experiment, the stopping potential is measured to be \( {Vs} \, \text{{V}} \).<br><br>
Calculate the maximum kinetic energy of the emitted photoelectrons.
"""
    s = rf"""
At the stopping potential, the electrical work done equals the maximum kinetic energy:<br>
\( eV_s = E_k \)<br><br>
\( E_k = 1.60 \times 10^{{-19}} \times {Vs} \)<br>
\( E_k = \boxed{{{ke:.3g} \, \text{{J}}}} \)
"""
    hint = r"Use \( E_k = eV_s \)."
    return q, s, hint, 3


def aqa_pe_debroglie():
    m = 9.11e-31
    v = random.choice([1.8, 2.2, 2.5, 3.0, 3.5]) * 10**6
    h = 6.63e-34
    p = m * v
    wavelength = h / p

    q = rf"""
An electron moves with a speed of \( {v/10**6:.1f} \times 10^{{6}} \, \text{{m s}}^{{-1}} \).<br><br>
Calculate its de Broglie wavelength.
"""
    s = rf"""
Use the de Broglie equation:<br>
\( \lambda = \frac{{h}}{{p}} = \frac{{h}}{{mv}} \)<br><br>
Momentum:<br>
\( p = mv = 9.11 \times 10^{{-31}} \times {v/10**6:.1f} \times 10^{{6}} = {p:.3g} \, \text{{kg m s}}^{{-1}} \)<br><br>
So:<br>
\( \lambda = \frac{{6.63 \times 10^{{-34}}}}{{{p:.3g}}} = \boxed{{{wavelength:.3g} \, \text{{m}}}} \)
"""
    hint = r"Use \( \lambda = h/p \), and for an electron \( p = mv \)."
    return q, s, hint, 4



# ================================================================
# A-LEVEL PHYSICS — PHOTOELECTRIC EFFECT & WAVE-PARTICLE DUALITY
# MAIN GENERATOR
# ================================================================


def alevel_physics_photoelectric(difficulty, mode, variant_name=None):
    # Handle MCQ mode separately — it doesn't use the variant system
    if mode == 'mcq':
        q, s, hint, marks, options, correct_letter = pe_mcq()
        return make_problem(
            q, s, hint, difficulty, marks,
            'alevel', 'physics', 'photoelectric',
            options=options,
            correct_answer=correct_letter,
        )

    variants = alevel_physics_photoelectric_variants(difficulty, mode)

    if variant_name is None:
        variant = random.choice(variants)
    else:
        variant_map = {v.__name__: v for v in variants}
        if variant_name not in variant_map:
            # Safe fallback if queue/session becomes stale after code changes
            variant = random.choice(variants)
        else:
            variant = variant_map[variant_name]

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'alevel', 'physics', 'photoelectric')

# ================================================================
# A-LEVEL PHYSICS — PHOTOELECTRIC EFFECT & WAVE-PARTICLE DUALITY
# VARIANT HELPERS
# ================================================================

def _pe_found_threshold_definition():
    q = "Define the threshold frequency in the context of the photoelectric effect."
    s = r"""The threshold frequency is the <strong>minimum frequency</strong> of electromagnetic radiation
required to cause photoelectron emission from the surface of a metal."""
    hint = "Think: the lowest frequency that still works."
    return q, s, hint, 1


def _pe_found_work_function_definition():
    q = "Define the work function of a metal."
    s = r"""The work function is the <strong>minimum energy required</strong> for an electron to escape
from the surface of a metal."""
    hint = "It is the minimum energy needed for emission."
    return q, s, hint, 1


def _pe_found_below_threshold():
    metal = random.choice(["zinc", "sodium", "caesium", "potassium"])
    q = rf"""Light of frequency below the threshold frequency is shone on a clean surface of {metal}.
State what happens to the electrons at the surface."""
    s = r"""No photoelectrons are emitted because each photon has insufficient energy
to overcome the work function."""
    hint = "Below threshold means no emission."
    return q, s, hint, 1


def _pe_found_intensity_effect():
    q = """State the effect of increasing light intensity, while keeping the frequency above threshold,
on the number of emitted photoelectrons."""
    s = r"""The number of emitted photoelectrons per second <strong>increases</strong>,
because more photons arrive each second."""
    hint = "Intensity changes how many photons arrive."
    return q, s, hint, 1


def _pe_found_frequency_effect():
    q = """State the effect of increasing the frequency of the incident light, while keeping the intensity constant
and the frequency above threshold."""
    s = r"""The <strong>maximum kinetic energy</strong> of the emitted photoelectrons increases,
because each photon has more energy."""
    hint = "Frequency changes energy per photon."
    return q, s, hint, 1


def _pe_found_photon_energy():
    f = random.choice([4.5, 5.0, 6.0, 7.5, 8.0]) * 10**14
    h = 6.63e-34
    E = h * f
    q = rf"""Calculate the energy of a photon of frequency
\( {f/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \)."""
    s = rf"""Use \( E = hf \).<br>
\( E = 6.63 \times 10^{{-34}} \times {f/10**14:.1f} \times 10^{{14}} \)<br>
\( E = \boxed{{{E:.3g} \, \text{{J}}}} \)"""
    hint = r"Use \( E = hf \)."
    return q, s, hint, 2


def _pe_found_work_function_from_threshold():
    f0 = random.choice([4.8, 5.2, 5.6, 6.0]) * 10**14
    h = 6.63e-34
    phi = h * f0
    q = rf"""A metal has threshold frequency \( {f0/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \).
Calculate its work function in joules."""
    s = rf"""Use \( \phi = hf_0 \).<br>
\( \phi = 6.63 \times 10^{{-34}} \times {f0/10**14:.1f} \times 10^{{14}} \)<br>
\( \phi = \boxed{{{phi:.3g} \, \text{{J}}}} \)"""
    hint = r"Use \( \phi = hf_0 \)."
    return q, s, hint, 2


def _pe_found_convert_ev_to_j():
    phi_ev = random.choice([1.8, 2.1, 2.4, 2.7, 3.0])
    phi_j = phi_ev * 1.60e-19
    q = rf"""A metal has a work function of \( {phi_ev} \, \text{{eV}} \).
Convert this value to joules."""
    s = rf"""Use \( 1 \, \text{{eV}} = 1.60 \times 10^{{-19}} \, \text{{J}} \).<br>
\( \phi = {phi_ev} \times 1.60 \times 10^{{-19}} \)<br>
\( \phi = \boxed{{{phi_j:.3g} \, \text{{J}}}} \)"""
    hint = "Multiply by \( 1.60 \times 10^{-19} \)."
    return q, s, hint, 2


def _pe_found_convert_j_to_ev():
    phi_ev = random.choice([1.9, 2.2, 2.5, 2.8])
    phi_j = phi_ev * 1.60e-19
    q = rf"""A work function is \( {phi_j:.3g} \, \text{{J}} \).
Convert this value to electronvolts."""
    s = rf"""Use \( 1 \, \text{{eV}} = 1.60 \times 10^{{-19}} \, \text{{J}} \).<br>
\( \phi = \frac{{{phi_j:.3g}}}{{1.60 \times 10^{{-19}}}} \)<br>
\( \phi = \boxed{{{phi_ev:.3g} \, \text{{eV}}}} \)"""
    hint = "Divide by \( 1.60 \times 10^{-19} \)."
    return q, s, hint, 2


def _pe_found_photoelectric_observation():
    q = """State one observation from the photoelectric effect that cannot be explained by classical wave theory."""
    observations = [
        "There is a threshold frequency below which no photoelectrons are emitted.",
        "Photoelectrons are emitted with no measurable time delay when the frequency is above threshold.",
        "Increasing intensity below threshold does not cause emission."
    ]
    ans = random.choice(observations)
    s = rf"""One valid observation is: <strong>{ans}</strong>"""
    hint = "Think about threshold frequency or the immediate emission."
    return q, s, hint, 1


# --- INTERMEDIATE (10 variants) ---

def _pe_inter_threshold_from_work_function():
    phi_ev = random.choice([1.8, 2.1, 2.4, 2.7])
    phi = phi_ev * 1.60e-19
    h = 6.63e-34
    f0 = phi / h
    q = rf"""A metal has a work function of \( {phi_ev} \, \text{{eV}} \).
Calculate its threshold frequency."""
    s = rf"""First convert the work function to joules:<br>
\( \phi = {phi_ev} \times 1.60 \times 10^{{-19}} = {phi:.3g} \, \text{{J}} \)<br><br>
Then use \( f_0 = \frac{{\phi}}{{h}} \):<br>
\( f_0 = \frac{{{phi:.3g}}}{{6.63 \times 10^{{-34}}}} = \boxed{{{f0:.3g} \, \text{{Hz}}}} \)"""
    hint = r"Convert eV to J first, then use \( f_0 = \phi/h \)."
    return q, s, hint, 3


def _pe_inter_ke_from_photon():
    f = random.choice([6.5, 7.0, 7.5, 8.0]) * 10**14
    phi_ev = random.choice([1.8, 2.0, 2.2])
    phi = phi_ev * 1.60e-19
    h = 6.63e-34
    E = h * f
    ke = E - phi
    while ke <= 0:
        f = random.choice([7.5, 8.0, 8.5]) * 10**14
        E = h * f
        ke = E - phi
    q = rf"""Radiation of frequency \( {f/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \) falls on a metal
with work function \( {phi_ev} \, \text{{eV}} \). Calculate the maximum kinetic energy of the emitted photoelectrons."""
    s = rf"""Photon energy:<br>
\( hf = 6.63 \times 10^{{-34}} \times {f/10**14:.1f} \times 10^{{14}} = {E:.3g} \, \text{{J}} \)<br>
Work function:<br>
\( \phi = {phi_ev} \times 1.60 \times 10^{{-19}} = {phi:.3g} \, \text{{J}} \)<br><br>
Use \( E_k = hf - \phi \):<br>
\( E_k = {E:.3g} - {phi:.3g} = \boxed{{{ke:.3g} \, \text{{J}}}} \)"""
    hint = r"Use \( E_k = hf - \phi \)."
    return q, s, hint, 4


def _pe_inter_stopping_potential_from_ke():
    Vs = random.choice([0.35, 0.48, 0.62, 0.75, 0.90])
    e = 1.60e-19
    ke = e * Vs
    q = rf"""In a photoelectric experiment the maximum kinetic energy of the emitted electrons is
\( {ke:.3g} \, \text{{J}} \). Calculate the stopping potential."""
    s = rf"""Use \( E_k = eV_s \).<br>
\( V_s = \frac{{E_k}}{{e}} = \frac{{{ke:.3g}}}{{1.60 \times 10^{{-19}}}} \)<br>
\( V_s = \boxed{{{Vs} \, \text{{V}}}} \)"""
    hint = r"Rearrange \( E_k = eV_s \)."
    return q, s, hint, 3


def _pe_inter_frequency_for_given_ke():
    phi_ev = random.choice([1.9, 2.1, 2.3])
    ke = random.choice([1.2, 1.5, 1.8, 2.0]) * 10**-19
    phi = phi_ev * 1.60e-19
    h = 6.63e-34
    f = (phi + ke) / h
    q = rf"""A metal has work function \( {phi_ev} \, \text{{eV}} \).
What minimum frequency of incident radiation is needed for the emitted photoelectrons to have
maximum kinetic energy \( {ke:.2g} \, \text{{J}} \)?"""
    s = rf"""Convert work function:<br>
\( \phi = {phi_ev} \times 1.60 \times 10^{{-19}} = {phi:.3g} \, \text{{J}} \)<br><br>
Use \( hf = \phi + E_k \):<br>
\( f = \frac{{\phi + E_k}}{{h}} = \frac{{{phi:.3g} + {ke:.2g}}}{{6.63 \times 10^{{-34}}}} \)<br>
\( f = \boxed{{{f:.3g} \, \text{{Hz}}}} \)"""
    hint = r"Use \( hf = \phi + E_k \)."
    return q, s, hint, 4


def _pe_inter_compare_intensity_frequency():
    q = """Explain why increasing intensity increases the photoelectric current, but increasing frequency increases the maximum kinetic energy."""
    s = r"""Increasing intensity means <strong>more photons per second</strong>, so more electrons are emitted each second
and the photoelectric current increases.<br><br>
Increasing frequency means each photon has <strong>more energy</strong>, so once the work function has been overcome,
the emitted electrons have greater maximum kinetic energy."""
    hint = "Intensity changes number of photons. Frequency changes energy per photon."
    return q, s, hint, 3


def _pe_inter_debroglie_basic():
    m = 9.11e-31
    v = random.choice([1.5, 2.0, 2.5, 3.0]) * 10**6
    h = 6.63e-34
    lam = h / (m * v)
    q = rf"""An electron travels at \( {v/10**6:.1f} \times 10^{{6}} \, \text{{m s}}^{{-1}} \).
Calculate its de Broglie wavelength."""
    s = rf"""Use \( \lambda = \frac{{h}}{{mv}} \).<br>
\( \lambda = \frac{{6.63 \times 10^{{-34}}}}{{9.11 \times 10^{{-31}} \times {v/10**6:.1f} \times 10^{{6}}}} \)<br>
\( \lambda = \boxed{{{lam:.3g} \, \text{{m}}}} \)"""
    hint = r"Use \( \lambda = h/(mv) \)."
    return q, s, hint, 3


def _pe_inter_momentum_from_wavelength():
    lam = random.choice([1.2, 1.5, 2.0, 2.5]) * 10**-10
    h = 6.63e-34
    p = h / lam
    q = rf"""An electron has de Broglie wavelength \( {lam:.2g} \, \text{{m}} \).
Calculate its momentum."""
    s = rf"""Use \( p = \frac{{h}}{{\lambda}} \).<br>
\( p = \frac{{6.63 \times 10^{{-34}}}}{{{lam:.2g}}} \)<br>
\( p = \boxed{{{p:.3g} \, \text{{kg m s}}^{{-1}}}} \)"""
    hint = r"Rearrange \( \lambda = h/p \)."
    return q, s, hint, 3


def _pe_inter_potential_well():
    q = "Explain the potential well model for electrons in a metal."
    s = r"""Electrons in a metal can be thought of as being trapped in a <strong>potential well</strong>.
To escape from the surface, an electron must gain enough energy to get out of the well.
This minimum energy is the work function."""
    hint = "Electrons are trapped and need minimum energy to escape."
    return q, s, hint, 2


def _pe_inter_electron_diffraction_explain():
    q = "Explain how electron diffraction provides evidence for wave-particle duality."
    s = r"""Diffraction is a wave behaviour. When electrons are diffracted by a crystal,
this shows that electrons can behave as <strong>waves</strong>.<br><br>
In other experiments electrons behave as particles, so this supports wave-particle duality."""
    hint = "Diffraction is the key wave idea."
    return q, s, hint, 2


def _pe_inter_stopping_potential_ke_ev():
    Vs = random.choice([0.42, 0.55, 0.73, 0.88])
    ke_ev = Vs
    q = rf"""The stopping potential for photoelectrons is \( {Vs} \, \text{{V}} \).
State the maximum kinetic energy of the photoelectrons in electronvolts."""
    s = rf"""For electrons, a stopping potential of \( {Vs} \, \text{{V}} \) corresponds directly to
a maximum kinetic energy of \( \boxed{{{ke_ev} \, \text{{eV}}}} \)."""
    hint = "For one electron, 1 V corresponds to 1 eV."
    return q, s, hint, 2


# --- DIFFICULT (10 variants) ---

def _pe_diff_multistep_photoelectric():
    phi_ev = random.choice([2.0, 2.2, 2.4])
    f = random.choice([7.0, 7.5, 8.0, 8.5]) * 10**14
    phi = phi_ev * 1.60e-19
    h = 6.63e-34
    E = h * f
    ke = E - phi
    while ke <= 0:
        f = random.choice([8.0, 8.5, 9.0]) * 10**14
        E = h * f
        ke = E - phi
    Vs = ke / 1.60e-19
    q = rf"""A metal has work function \( {phi_ev} \, \text{{eV}} \). Light of frequency
\( {f/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \) is incident on the surface.<br>
(a) Calculate the photon energy.<br>
(b) Calculate the maximum kinetic energy of the emitted electrons.<br>
(c) Calculate the stopping potential."""
    s = rf"""(a) \( E = hf = 6.63 \times 10^{{-34}} \times {f/10**14:.1f} \times 10^{{14}}
= {E:.3g} \, \text{{J}} \)<br><br>
(b) \( \phi = {phi_ev} \times 1.60 \times 10^{{-19}} = {phi:.3g} \, \text{{J}} \)<br>
\( E_k = hf - \phi = {E:.3g} - {phi:.3g} = {ke:.3g} \, \text{{J}} \)<br><br>
(c) \( V_s = \frac{{E_k}}{{e}} = \frac{{{ke:.3g}}}{{1.60 \times 10^{{-19}}}} = \boxed{{{Vs:.3g} \, \text{{V}}}} \)"""
    hint = r"Use \( E = hf \), then \( E_k = hf - \phi \), then \( V_s = E_k/e \)."
    return q, s, hint, 6


def _pe_diff_max_ke_from_threshold_frequency():
    f = random.choice([7.0, 7.5, 8.0]) * 10**14
    f0 = random.choice([4.5, 5.0, 5.5]) * 10**14
    while f <= f0:
        f = random.choice([7.0, 7.5, 8.0, 8.5]) * 10**14
    h = 6.63e-34
    ke = h * (f - f0)
    q = rf"""A metal has threshold frequency \( {f0/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \).
Light of frequency \( {f/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \) is incident on the metal.
Calculate the maximum kinetic energy of the emitted photoelectrons."""
    s = rf"""Use \( \phi = hf_0 \) and \( E_k = hf - \phi \).<br>
So \( E_k = h(f-f_0) \).<br>
\( E_k = 6.63 \times 10^{{-34}} \times ({f/10**14:.1f} - {f0/10**14:.1f}) \times 10^{{14}} \)<br>
\( E_k = \boxed{{{ke:.3g} \, \text{{J}}}} \)"""
    hint = r"Use \( E_k = h(f-f_0) \)."
    return q, s, hint, 4


def _pe_diff_find_work_function_from_stopping_potential():
    f = random.choice([7.2, 7.6, 8.0]) * 10**14
    Vs = random.choice([0.55, 0.72, 0.88, 1.05])
    h = 6.63e-34
    e = 1.60e-19
    phi = h * f - e * Vs
    phi_ev = phi / e
    q = rf"""Light of frequency \( {f/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \) produces photoelectrons
with stopping potential \( {Vs} \, \text{{V}} \). Calculate the work function of the metal in eV."""
    s = rf"""Use \( hf = \phi + eV_s \), so \( \phi = hf - eV_s \).<br>
\( hf = 6.63 \times 10^{{-34}} \times {f/10**14:.1f} \times 10^{{14}} = {(h*f):.3g} \, \text{{J}} \)<br>
\( eV_s = 1.60 \times 10^{{-19}} \times {Vs} = {(e*Vs):.3g} \, \text{{J}} \)<br>
\( \phi = {(h*f):.3g} - {(e*Vs):.3g} = {phi:.3g} \, \text{{J}} \)<br>
\( \phi = \boxed{{{phi_ev:.3g} \, \text{{eV}}}} \)"""
    hint = r"Rearrange \( hf = \phi + eV_s \)."
    return q, s, hint, 5


def _pe_diff_debroglie_from_ke():
    ke = random.choice([2.5, 3.0, 3.5, 4.0]) * 10**-19
    m = 9.11e-31
    h = 6.63e-34
    v = math.sqrt(2 * ke / m)
    lam = h / (m * v)
    q = rf"""An electron has kinetic energy \( {ke:.2g} \, \text{{J}} \).
Calculate its de Broglie wavelength."""
    s = rf"""First find the speed from \( E_k = \frac12 mv^2 \):<br>
\( v = \sqrt{{\frac{{2E_k}}{{m}}}} = \sqrt{{\frac{{2 \times {ke:.2g}}}{{9.11 \times 10^{{-31}}}}}} = {v:.3g} \, \text{{m s}}^{{-1}} \)<br><br>
Then use \( \lambda = \frac{{h}}{{mv}} \):<br>
\( \lambda = \frac{{6.63 \times 10^{{-34}}}}{{9.11 \times 10^{{-31}} \times {v:.3g}}} = \boxed{{{lam:.3g} \, \text{{m}}}} \)"""
    hint = r"First use \( E_k = \frac12 mv^2 \), then \( \lambda = h/(mv) \)."
    return q, s, hint, 5


def _pe_diff_compare_two_metals():
    f = random.choice([7.5, 8.0, 8.5]) * 10**14
    phi1_ev = random.choice([1.8, 2.0, 2.2])
    phi2_ev = phi1_ev + random.choice([0.3, 0.4, 0.5])
    h = 6.63e-34
    E = h * f
    ke1 = E - phi1_ev * 1.60e-19
    ke2 = E - phi2_ev * 1.60e-19
    q = rf"""Light of frequency \( {f/10**14:.1f} \times 10^{{14}} \, \text{{Hz}} \) is incident on two metals.
Metal A has work function \( {phi1_ev} \, \text{{eV}} \) and Metal B has work function \( {phi2_ev} \, \text{{eV}} \).<br>
Which metal emits photoelectrons with greater maximum kinetic energy? Explain."""
    s = rf"""Metal A emits electrons with greater maximum kinetic energy.<br><br>
For both metals the photon energy is the same, but \( E_k = hf - \phi \). Since Metal A has the
<strong>smaller work function</strong>, more of the photon energy remains as kinetic energy.<br><br>
Numerically:<br>
Metal A: \( E_k \approx {ke1:.3g} \, \text{{J}} \)<br>
Metal B: \( E_k \approx {ke2:.3g} \, \text{{J}} \)"""
    hint = "Compare the work functions using \( E_k = hf - \phi \)."
    return q, s, hint, 4


def _pe_diff_explain_classical_failure():
    q = """Explain why the classical wave model fails to explain the photoelectric effect, and why the photon model succeeds."""
    s = r"""The classical wave model predicts that energy is spread continuously through the wave,
so increasing intensity should eventually cause electrons to escape even at low frequency.
It also suggests there could be a time delay while electrons absorb energy.<br><br>
Experimentally, there is a threshold frequency and emission is effectively immediate above threshold.
The photon model explains this by saying light arrives in discrete packets of energy \( E = hf \),
and one electron absorbs one photon. Emission only occurs if a single photon has enough energy to exceed the work function."""
    hint = "Talk about threshold frequency, no delay, and one photon per electron."
    return q, s, hint, 4


def _pe_diff_electron_vs_photon():
    q = """State one experiment showing light behaves as a particle and one experiment showing electrons behave as waves."""
    s = r"""The <strong>photoelectric effect</strong> shows light behaving as particles (photons).<br>
<strong>Electron diffraction</strong> shows electrons behaving as waves."""
    hint = "Think: photons in the photoelectric effect, electrons in diffraction."
    return q, s, hint, 2


def _pe_diff_line_spectrum():
    q = """Explain how line spectra provide evidence for discrete energy levels in atoms."""
    s = r"""A line spectrum contains only specific wavelengths of light, not a continuous range.
Each wavelength corresponds to a photon of definite energy \( E = hf \).<br><br>
This shows that electrons in atoms can only move between specific energy levels,
because only fixed energy differences are emitted or absorbed."""
    hint = "Link specific wavelengths to specific photon energies."
    return q, s, hint, 3


def _pe_diff_excitation_vs_ionisation():
    q = """Explain the difference between excitation and ionisation of an atom."""
    s = r"""<strong>Excitation</strong> occurs when an electron gains enough energy to move to a higher energy level
but remains in the atom.<br><br>
<strong>Ionisation</strong> occurs when an electron gains enough energy to leave the atom completely."""
    hint = "Excited = still in atom. Ionised = removed."
    return q, s, hint, 2


def _pe_diff_stopping_potential_graph():
    h = 6.63e-34
    e = 1.60e-19
    gradient = h / e
    q = """A graph of stopping potential \(V_s\) against frequency \(f\) is plotted for a metal.
Explain what the gradient and the intercept on the frequency axis represent."""
    s = rf"""From \( eV_s = hf - \phi \), we get:
\( V_s = \frac{{h}}{{e}}f - \frac{{\phi}}{{e}} \).<br><br>
So the gradient is \( \frac{{h}}{{e}} \approx \boxed{{{gradient:.3g}}} \, \text{{V s}} \),
and the intercept on the frequency axis is the <strong>threshold frequency</strong>."""
    hint = r"Rearrange to \( V_s = (h/e)f - \phi/e \)."
    return q, s, hint, 4



# ================================================================
# A-LEVEL PHYSICS — PHOTOELECTRIC EFFECT & WAVE-PARTICLE DUALITY
# ================================================================

H = 6.63e-34
C = 3.00e8
E_CHARGE = 1.60e-19
M_E = 9.11e-31


# ------------------------------------------------
# SVG HELPERS
# ------------------------------------------------
def svg_emission_spectra():
    # Helium lines A–F (wavelengths in nm)
    he_lines = [
        ("A", 390), ("B", 440), ("C", 490), ("D", 505), ("E", 590), ("F", 670)
    ]
    # Sodium – yellow doublet + weaker line
    na_lines = [568, 589.3]     # 589.3 is the average of the doublet
    # Hydrogen – all four visible Balmer lines
    h_lines = [410, 434, 486, 656]

    # Larger viewBox: 750 x 280
    width, height = 750, 280
    x_min, x_max = 380, 700
    x_start = 60          # left margin for labels
    x_end = width - 20     # right margin
    x_range = x_end - x_start   # 670

    def x_pos(wl):
        return x_start + (wl - x_min) / (x_max - x_min) * x_range

    def draw_spectrum(y, label, lines, color, line_height=36, text_size=14):
        svg = []
        # label on the left
        svg.append(f'<text x="10" y="{y + line_height/2 + 6}" font-size="{text_size}" font-family="sans-serif" fill="#222">{label}</text>')
        for item in lines:
            if isinstance(item, tuple):
                letter, wl = item
            else:
                letter, wl = None, item
            x = x_pos(wl)
            svg.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + line_height}" stroke="{color}" stroke-width="3"/>')
            if letter:
                svg.append(f'<text x="{x}" y="{y - 10}" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#222">{letter}</text>')
        return "\n".join(svg)

    # Row Y positions (scaled)
    y_helium = 40
    y_sodium = 110
    y_hydrogen = 180
    scale_bottom = 240   # axis line

    # Ticks every 50 nm from 400 to 650
    ticks = [400, 450, 500, 550, 600, 650]
    tick_marks = []
    for wl in ticks:
        x = x_pos(wl)
        tick_marks.append(f'<line x1="{x}" y1="{scale_bottom - 6}" x2="{x}" y2="{scale_bottom + 6}" stroke="#555" stroke-width="1.5"/>')
        tick_marks.append(f'<text x="{x}" y="{scale_bottom + 22}" text-anchor="middle" font-size="13" font-family="sans-serif">{wl}</text>')

    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     style="margin:12px 0; display:block; background:#f9f8f5; border-radius:8px; padding:8px; max-width:100%;">
      <text x="{width/2}" y="22" text-anchor="middle" font-size="18" font-family="sans-serif" font-weight="bold">Emission spectra</text>
      {draw_spectrum(y_helium, "Helium", he_lines, "#2a5c8a", 36, 14)}
      {draw_spectrum(y_sodium, "Sodium", na_lines, "#d49c3d", 36, 14)}
      {draw_spectrum(y_hydrogen, "Hydrogen", h_lines, "#a13544", 36, 14)}
      <line x1="{x_start}" y1="{scale_bottom}" x2="{x_end}" y2="{scale_bottom}" stroke="#555" stroke-width="1.5"/>
      {''.join(tick_marks)}
      <text x="{width/2}" y="{scale_bottom + 42}" text-anchor="middle" font-size="14" font-family="sans-serif">wavelength / nm</text>
    </svg>"""
    return svg


def svg_photoelectric_cell():
    return r"""<svg width="300" height="180" viewBox="0 0 300 180" style="margin:14px 0;display:block;background:#f9f8f5;border-radius:8px;padding:8px;">
  <rect x="35" y="35" width="210" height="90" rx="10" fill="none" stroke="#555" stroke-width="2"/>
  <rect x="65" y="55" width="16" height="50" fill="#01696f"/>
  <rect x="195" y="55" width="16" height="50" fill="#a13544"/>
  <line x1="81" y1="80" x2="195" y2="80" stroke="#888" stroke-dasharray="4,3" />
  <circle cx="270" cy="80" r="18" fill="none" stroke="#333" stroke-width="2"/>
  <text x="270" y="85" text-anchor="middle" font-size="14" font-family="sans-serif">μA</text>
  <line x1="211" y1="80" x2="252" y2="80" stroke="#333" stroke-width="2"/>
  <line x1="65" y1="125" x2="65" y2="150" stroke="#333" stroke-width="2"/>
  <line x1="65" y1="150" x2="215" y2="150" stroke="#333" stroke-width="2"/>
  <line x1="215" y1="150" x2="215" y2="125" stroke="#333" stroke-width="2"/>
  <line x1="140" y1="150" x2="140" y2="168" stroke="#333" stroke-width="2"/>
  <circle cx="140" cy="168" r="10" fill="none" stroke="#333" stroke-width="2"/>
  <line x1="132" y1="168" x2="148" y2="168" stroke="#333" stroke-width="2"/>
  <line x1="140" y1="160" x2="140" y2="176" stroke="#333" stroke-width="2"/>
  <text x="58" y="48" font-size="12" font-family="sans-serif" fill="#01696f">Emitter</text>
  <text x="184" y="48" font-size="12" font-family="sans-serif" fill="#a13544">Collector</text>
  <line x1="8" y1="50" x2="58" y2="68" stroke="#d19900" stroke-width="3"/>
  <line x1="8" y1="72" x2="58" y2="82" stroke="#d19900" stroke-width="3"/>
  <line x1="8" y1="94" x2="58" y2="96" stroke="#d19900" stroke-width="3"/>
  <text x="8" y="38" font-size="12" font-family="sans-serif" fill="#d19900">incident light</text>
  <text x="120" y="24" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#555">photoelectric tube</text>
</svg>"""


def svg_stopping_graph(x_intercept=5.0, grad=4.2):
    y0 = x_intercept * grad
    x1, y1 = 40, 140
    x2 = 250
    y2 = 140 - ((x2 - 40) / 210) * y0
    x_zero = 40 + 210 * (x_intercept / 8.0)
    return rf"""<svg width="300" height="200" viewBox="0 0 300 200" style="margin:14px 0;display:block;background:#f9f8f5;border-radius:8px;padding:8px;">
  <line x1="40" y1="20" x2="40" y2="150" stroke="#333" stroke-width="2"/>
  <line x1="40" y1="150" x2="265" y2="150" stroke="#333" stroke-width="2"/>
  <line x1="40" y1="20" x2="250" y2="{max(25, y2)}" stroke="#01696f" stroke-width="3"/>
  <circle cx="{x_zero:.1f}" cy="150" r="4" fill="#a13544"/>
  <text x="{x_zero:.1f}" y="168" text-anchor="middle" font-size="11" font-family="sans-serif" fill="#a13544">f₀</text>
  <text x="17" y="90" transform="rotate(-90,17,90)" font-size="12" font-family="sans-serif">Vₛ / V</text>
  <text x="160" y="185" font-size="12" font-family="sans-serif">frequency / 10¹⁴ Hz</text>
  <text x="32" y="154" text-anchor="end" font-size="11" font-family="sans-serif">0</text>
</svg>"""


def svg_energy_levels(levels):
    base_x1, base_x2 = 60, 220
    labels_x = 235
    min_e = min(levels.values())
    max_e = max(levels.values())
    def y_map(E):
        return 150 - (E - min_e) / (max_e - min_e + 0.01) * 100
    lines = []
    for label, energy in levels.items():
        y = y_map(energy)
        lines.append(
            f'<line x1="{base_x1}" y1="{y:.1f}" x2="{base_x2}" y2="{y:.1f}" stroke="#01696f" stroke-width="2"/>'
            f'<text x="{labels_x}" y="{y+4:.1f}" font-size="12" font-family="sans-serif" fill="#333">{label} = {energy:.2f} eV</text>'
        )
    joined = "".join(lines)
    return rf"""<svg width="320" height="190" viewBox="0 0 320 190" style="margin:14px 0;display:block;background:#f9f8f5;border-radius:8px;padding:8px;">
  <text x="140" y="18" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#555">energy levels</text>
  <line x1="40" y1="20" x2="40" y2="160" stroke="#333" stroke-width="2"/>
  <text x="18" y="95" transform="rotate(-90,18,95)" font-size="12" font-family="sans-serif">energy</text>
  {joined}
</svg>"""


def svg_electron_diffraction():
    return r"""<svg width="340" height="180" viewBox="0 0 340 180" style="margin:14px 0;display:block;background:#f9f8f5;border-radius:8px;padding:8px;">
  <circle cx="165" cy="90" r="72" fill="none" stroke="#555" stroke-width="2"/>
  <rect x="42" y="76" width="18" height="28" fill="#a13544"/>
  <line x1="60" y1="90" x2="125" y2="90" stroke="#333" stroke-width="2"/>
  <polygon points="119,86 129,90 119,94" fill="#333"/>
  <rect x="130" y="55" width="12" height="70" fill="#01696f"/>
  <line x1="142" y1="90" x2="205" y2="90" stroke="#333" stroke-width="2"/>
  <circle cx="245" cy="90" r="8" fill="#01696f"/>
  <circle cx="245" cy="90" r="30" fill="none" stroke="#d19900" stroke-width="2"/>
  <circle cx="245" cy="90" r="48" fill="none" stroke="#d19900" stroke-width="2"/>
  <text x="38" y="68" font-size="12" font-family="sans-serif">filament</text>
  <text x="110" y="42" font-size="12" font-family="sans-serif">graphite</text>
  <text x="230" y="28" font-size="12" font-family="sans-serif">fluorescent screen</text>
  <text x="80" y="108" font-size="12" font-family="sans-serif" fill="#333">P</text>
  <text x="146" y="108" font-size="12" font-family="sans-serif" fill="#333">Q</text>
  <text x="280" y="90" font-size="12" font-family="sans-serif" fill="#333">R</text>
</svg>"""


def svg_spectrum_lines(wavelengths):
    x0, width = 40, 220
    wl_min, wl_max = 380, 700
    lines = []
    for wl, color in wavelengths:
        x = x0 + (wl - wl_min) / (wl_max - wl_min) * width
        lines.append(f'<line x1="{x:.1f}" y1="35" x2="{x:.1f}" y2="120" stroke="{color}" stroke-width="4"/>')
    return rf"""<svg width="300" height="160" viewBox="0 0 300 160" style="margin:14px 0;display:block;background:#111;border-radius:8px;padding:8px;">
  <rect x="40" y="35" width="220" height="85" fill="#000" stroke="#666"/>
  {''.join(lines)}
  <text x="150" y="145" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#ddd">visible spectrum / nm</text>
  <text x="40" y="132" font-size="10" font-family="sans-serif" fill="#ddd">380</text>
  <text x="245" y="132" font-size="10" font-family="sans-serif" fill="#ddd">700</text>
</svg>"""


# ------------------------------------------------
# DIFFICULT EXAM VARIANTS (10)
# ------------------------------------------------

def pe_exam_work_function_stopping():
    f = random.choice([1.10e15, 1.20e15, 1.35e15, 1.50e15])
    Ek_eV = random.choice([0.85, 1.10, 1.35, 1.60])
    photon_E_eV = H * f / E_CHARGE
    phi_eV = photon_E_eV - Ek_eV
    Vs = Ek_eV
    diagram = svg_photoelectric_cell()
    q = (rf"<strong>[9 marks] Work Function and Stopping Potential</strong><br>"
         rf"{diagram}"
         rf"Ultraviolet radiation of frequency <strong>{f:.2e} Hz</strong> is incident on a metal surface. "
         rf"The maximum kinetic energy of the emitted photoelectrons is <strong>{Ek_eV:.2f} eV</strong>.<br>"
         r"<strong>a)</strong> Calculate the energy of one incident photon in eV.<br>"
         r"<strong>b)</strong> Calculate the work function of the metal in eV.<br>"
         r"<strong>c)</strong> Determine the stopping potential needed to prevent the most energetic photoelectrons reaching the collector.<br>"
         r"<strong>d)</strong> Explain why increasing the intensity at the same frequency would not increase the stopping potential.")
    s = (rf"<strong>a)</strong> Photon energy: \(E = hf\).<br>"
         rf"\(E = 6.63\times10^{{-34}} \times {f:.2e} = {H*f:.3e}\,\text{{J}}\).<br>"
         rf"In eV: \(E = \frac{{{H*f:.3e}}}{{1.60\times10^{{-19}}}} = <strong>{photon_E_eV:.2f}\,\text{{eV}}</strong>\).<br><br>"
         rf"<strong>b)</strong> Einstein equation: \(hf = \phi + E_{{k,\max}}\).<br>"
         rf"\(\phi = {photon_E_eV:.2f} - {Ek_eV:.2f} = <strong>{phi_eV:.2f}\,\text{{eV}}</strong>\).<br><br>"
         rf"<strong>c)</strong> At stopping potential, \(eV_s = E_{{k,\max}}\). In eV this gives numerically "
         rf"\(V_s = <strong>{Vs:.2f}\,\text{{V}}</strong>\).<br><br>"
         r"<strong>d)</strong> Stopping potential depends on the maximum kinetic energy of individual photoelectrons. "
         r"At fixed frequency, photon energy is unchanged, so the maximum kinetic energy is unchanged. "
         r"Higher intensity means more photons per second and therefore more emitted electrons, not more energetic electrons.")
    hint = r"Use \(hf = \phi + E_{k,\max}\). In eV, the stopping potential is numerically equal to the maximum kinetic energy in eV."
    return q, s, hint, 9


def pe_exam_threshold_frequency_compare():
    phi_eV = random.choice([2.10, 2.30, 2.50, 2.80])
    phi_J = phi_eV * E_CHARGE
    f0 = phi_J / H
    lam0 = C / f0
    f1 = f0 * random.choice([0.90, 0.95])
    f2 = f0 * random.choice([1.20, 1.35])
    E2_eV = H * f2 / E_CHARGE
    Ek2 = E2_eV - phi_eV
    q = (rf"<strong>[10 marks] Threshold Frequency and Emission</strong><br>"
         rf"A metal has work function <strong>{phi_eV:.2f} eV</strong>.<br>"
         r"<strong>a)</strong> Calculate the threshold frequency of the metal.<br>"
         r"<strong>b)</strong> Calculate the threshold wavelength.<br>"
         rf"<strong>c)</strong> Light of frequency <strong>{f1:.2e} Hz</strong> is incident on the metal. Explain whether photoelectrons are emitted.<br>"
         rf"<strong>d)</strong> Light of frequency <strong>{f2:.2e} Hz</strong> is incident on the metal. Calculate the maximum kinetic energy of the emitted photoelectrons in eV and in J.<br>"
         r"<strong>e)</strong> Explain why the classical wave model fails to account for the existence of a threshold frequency.")
    s = (rf"<strong>a)</strong> Threshold frequency is given by \( \phi = hf_0 \).<br>"
         rf"\(f_0 = \frac{{{phi_J:.3e}}}{{6.63\times10^{{-34}}}} = <strong>{f0:.2e}\,\text{{Hz}}</strong>\).<br><br>"
         rf"<strong>b)</strong> \( \lambda_0 = \frac{{c}}{{f_0}} = \frac{{3.00\times10^8}}{{{f0:.2e}}} = <strong>{lam0:.2e}\,\text{{m}}</strong>\).<br><br>"
         rf"<strong>c)</strong> Since \( {f1:.2e}\,\text{{Hz}} < f_0 \), each photon has less energy than the work function. "
         rf"No photoelectrons are emitted, whatever the intensity.<br><br>"
         rf"<strong>d)</strong> Photon energy at \(f = {f2:.2e}\,\text{{Hz}}\): "
         rf"\(E = hf = {E2_eV:.2f}\,\text{{eV}}\).<br>"
         rf"\(E_{{k,\max}} = hf - \phi = {E2_eV:.2f} - {phi_eV:.2f} = <strong>{Ek2:.2f}\,\text{{eV}}</strong>\).<br>"
         rf"In joules: \(E_{{k,\max}} = {Ek2:.2f}\times1.60\times10^{{-19}} = <strong>{Ek2*E_CHARGE:.3e}\,\text{{J}}</strong>\).<br><br>"
         r"<strong>e)</strong> Classical wave theory predicts that energy is delivered continuously, so sufficiently intense low-frequency radiation should eventually eject electrons. "
         r"Experimentally this does not happen. The photon model explains this because an electron absorbs energy in one interaction from one photon, so emission occurs only if \(hf \ge \phi\).")
    hint = r"Start with \( \phi = hf_0 \). Then use \( \lambda_0 = c/f_0 \) and \( E_{k,\max} = hf - \phi \)."
    return q, s, hint, 10


def pe_exam_plate_discharge_explanation():
    freq_state = random.choice(["below", "above"])
    q = (r"<strong>[12 marks] Extended Response: Frequency, Intensity and Loss of Charge</strong><br>"
         r"An isolated metal plate is given a negative charge. Electromagnetic radiation is then incident on the plate, and the plate loses charge due to the photoelectric effect.<br>"
         r"Discuss how the rate at which the plate loses charge depends on the frequency and intensity of the incident radiation.<br>"
         r"In your answer you should explain:<br>"
         r"• why the plate loses charge,<br>"
         r"• why the effect only occurs for frequencies above a threshold value,<br>"
         r"• why increased intensity changes the rate of charge loss only when the frequency is above the threshold.")
    s = (r"The metal plate is negatively charged, so it has an excess of electrons on its surface. "
         r"If incident electromagnetic radiation has sufficiently energetic photons, electrons are emitted from the surface as photoelectrons. "
         r"As electrons leave, the plate loses negative charge and becomes less negatively charged.<br><br>"
         r"Emission occurs only if the photon energy is at least equal to the work function of the metal. "
         r"This minimum energy is required to remove an electron from the surface. "
         r"Since photon energy is \(E = hf\), there is a threshold frequency \(f_0\) such that \(hf_0 = \phi\). "
         r"For frequencies below \(f_0\), no photoelectric emission occurs because individual photons do not carry enough energy, regardless of intensity.<br><br>"
         r"If the frequency is above the threshold, increasing intensity means more photons strike the surface each second. "
         r"That causes more electrons to be emitted each second, so the plate loses charge more rapidly. "
         r"However, the maximum kinetic energy of emitted electrons depends on frequency, not intensity, because each electron still absorbs energy from a single photon.<br><br>"
         r"This behaviour supports the photon model and cannot be explained fully by the classical wave model, which would predict that sufficiently intense radiation of any frequency should eventually cause emission.")
    hint = r"Structure the answer around three ideas: emission of electrons, threshold frequency via \(E = hf\), and intensity meaning photons per second."
    return q, s, hint, 12


def pe_exam_stopping_graph():
    f0x = random.choice([4.6, 5.0, 5.4])
    grad = random.choice([3.6, 4.0, 4.4])
    diagram = svg_stopping_graph(f0x, grad)
    f_test = random.choice([6.2, 6.8, 7.2]) * 1e14
    Vs = (f_test / 1e14 - f0x) * grad / 10
    photon_E = H * f_test / E_CHARGE
    q = (rf"<strong>[10 marks] Stopping Potential Graph</strong><br>"
         rf"The graph shows how stopping potential \(V_s\) varies with frequency for a metal.<br>{diagram}"
         r"<strong>a)</strong> State what is meant by stopping potential.<br>"
         r"<strong>b)</strong> Use the graph to determine the threshold frequency.<br>"
         rf"<strong>c)</strong> Estimate the stopping potential when the incident frequency is <strong>{f_test:.2e} Hz</strong>.<br>"
         r"<strong>d)</strong> Explain why the graph is a straight line.<br>"
         r"<strong>e)</strong> State what physical quantity is represented by the x-intercept.")
    s = (r"<strong>a)</strong> The stopping potential is the minimum reverse potential difference required to prevent the most energetic photoelectrons from reaching the collector.<br><br>"
         rf"<strong>b)</strong> The threshold frequency is the x-intercept of the graph: "
         rf"<strong>{f0x:.1f} \times 10^{{14}}\,\text{{Hz}}</strong>.<br><br>"
         rf"<strong>c)</strong> From the straight-line graph, at \(f = {f_test:.2e}\,\text{{Hz}}\), "
         rf"\(V_s \approx <strong>{Vs:.2f}\,\text{{V}}</strong>\).<br><br>"
         r"<strong>d)</strong> Einstein's photoelectric equation gives \(hf = \phi + E_{k,\max}\). "
         r"Since \(E_{k,\max} = eV_s\), this becomes \(V_s = \frac{h}{e}f - \frac{\phi}{e}\). "
         r"This has the form \(y = mx + c\), so the graph is linear.<br><br>"
         r"<strong>e)</strong> The x-intercept represents the threshold frequency, where emitted electrons have zero maximum kinetic energy.")
    hint = r"Use \(eV_s = E_{k,\max}\) together with \(hf = \phi + E_{k,\max}\)."
    return q, s, hint, 10


def pe_exam_energy_levels_visible_uv():
    levels = {"ground": -21.56, "A": -4.96, "B": -3.16}
    diagram = svg_energy_levels(levels)
    transfer = 18.4
    delta_BA = levels["B"] - levels["A"]
    lambda_BA = H * C / (delta_BA * E_CHARGE)
    q = (rf"<strong>[11 marks] Excitation, De-excitation and Visible Light</strong><br>"
         rf"A gas atom has the following three lowest energy levels.<br>{diagram}"
         rf"An electron in a beam transfers <strong>{transfer:.1f} eV</strong> to an atom initially in the ground state.<br>"
         r"<strong>a)</strong> Determine which excited state the atom reaches. Support your answer with a calculation.<br>"
         r"<strong>b)</strong> The atom subsequently emits a photon of visible light. Determine which transition is responsible.<br>"
         r"<strong>c)</strong> Calculate the wavelength of this photon and show that it lies in the visible region.<br>"
         r"<strong>d)</strong> Explain why the direct transition from the excited state to the ground state would not produce visible light.")
    s = (rf"<strong>a)</strong> Starting from the ground state \((-21.56\,\text{{eV}})\), "
         rf"adding \(18.4\,\text{{eV}}\) gives \(-3.16\,\text{{eV}}\). "
         rf"So the electron is excited to level <strong>B</strong>.<br><br>"
         rf"<strong>b)</strong> Energy difference for \(B \to A\): "
         rf"\((-3.16) - (-4.96) = <strong>{delta_BA:.2f}\,\text{{eV}}</strong>\). "
         rf"This is small enough to correspond to visible light, so the visible photon comes from <strong>B to A</strong>.<br><br>"
         rf"<strong>c)</strong> \(E = hf = hc/\lambda\), so \( \lambda = \frac{{hc}}{{E}} \).<br>"
         rf"\(\lambda = \frac{{6.63\times10^{{-34}}\times3.00\times10^8}}{{{delta_BA:.2f}\times1.60\times10^{{-19}}}} "
         rf"= <strong>{lambda_BA:.2e}\,\text{{m}}</strong>\).<br>"
         r"This is about \(6.9\times10^{-7}\,\text{m}\) or 690 nm, which is in the visible red region.<br><br>"
         r"<strong>d)</strong> A direct transition from B to the ground state would involve a much larger energy difference, so the emitted photon would have a much shorter wavelength in the ultraviolet, not the visible region.")
    hint = r"Compare the transferred energy with the gaps between levels. Then use \( \lambda = hc/E \)."
    return q, s, hint, 11


def pe_exam_diffraction_voltage():
    V1 = random.choice([2500, 3200, 4000])
    factor = random.choice([1.5, 2.0, 2.5])
    V2 = V1 * factor
    ratio = 1 / math.sqrt(factor)
    diagram = svg_electron_diffraction()
    q = (rf"<strong>[9 marks] Electron Diffraction and Accelerating Voltage</strong><br>"
         rf"{diagram}"
         rf"In an electron diffraction tube, electrons are first accelerated through a potential difference of <strong>{V1} V</strong>. "
         rf"The potential difference is then increased to <strong>{V2} V</strong>.<br>"
         r"<strong>a)</strong> Explain at which part of the apparatus the electrons demonstrate wave-like behaviour.<br>"
         r"<strong>b)</strong> Show that increasing the accelerating voltage decreases the de Broglie wavelength.<br>"
         r"<strong>c)</strong> Deduce the factor by which the ring diameter changes when the voltage is increased from \(V_1\) to \(V_2\).<br>"
         r"<strong>d)</strong> Explain physically why the diffraction pattern becomes smaller.")
    s = (r"<strong>a)</strong> The electrons show wave-like behaviour at the graphite target, where they diffract as they pass through the atomic layers, and in producing the bright ring pattern by interference on the screen.<br><br>"
         r"<strong>b)</strong> For electrons accelerated through potential difference \(V\), "
         r"\(eV = \frac{1}{2}mv^2\), so \(p = mv = \sqrt{2meV}\). "
         r"Since de Broglie wavelength is \( \lambda = h/p \), we get \( \lambda \propto 1/\sqrt{V} \). "
         r"So increasing \(V\) decreases \( \lambda \).<br><br>"
         rf"<strong>c)</strong> The diffraction angle, and hence ring diameter, is proportional to wavelength. "
         rf"So \(D \propto \lambda \propto 1/\sqrt{{V}}\).<br>"
         rf"\(\frac{{D_2}}{{D_1}} = \sqrt{{\frac{{V_1}}{{V_2}}}} = \sqrt{{\frac{{1}}{{{factor}}}}} = <strong>{ratio:.3f}</strong>\).<br>"
         rf"So the new diameter is <strong>{ratio:.3f} times</strong> the original.<br><br>"
         r"<strong>d)</strong> Faster electrons have greater momentum, so their de Broglie wavelength is shorter. "
         r"Shorter wavelength means less diffraction by the graphite spacing, so the rings appear at smaller angles and the pattern shrinks.")
    hint = r"Use \(eV = \frac{1}{2}mv^2\), then \(p = \sqrt{2meV}\), then \( \lambda = h/p \)."
    return q, s, hint, 9


def pe_exam_debroglie_numeric():
    V = random.choice([1800, 2500, 3600, 5000])
    p = math.sqrt(2 * M_E * E_CHARGE * V)
    lam = H / p
    q = (rf"<strong>[10 marks] de Broglie Wavelength of an Electron</strong><br>"
         rf"Electrons are accelerated from rest through a potential difference of <strong>{V} V</strong>.<br>"
         r"<strong>a)</strong> Show that the momentum of an electron after acceleration is \(p = \sqrt{2meV}\).<br>"
         r"<strong>b)</strong> Calculate the momentum of the electron.<br>"
         r"<strong>c)</strong> Calculate the de Broglie wavelength of the electron.<br>"
         r"<strong>d)</strong> Explain why electrons can be diffracted by graphite but everyday objects cannot readily be observed to diffract.")
    s = (r"<strong>a)</strong> The gain in kinetic energy is \(eV\). "
         r"Since \(eV = \frac{1}{2}mv^2\), multiplying by \(2m\) gives \(2meV = m^2v^2 = p^2\). "
         r"So \(p = \sqrt{2meV}\).<br><br>"
         rf"<strong>b)</strong> \(p = \sqrt{{2\times9.11\times10^{{-31}}\times1.60\times10^{{-19}}\times{V}}} "
         rf"= <strong>{p:.3e}\,\text{{kg m s}}^{{-1}}</strong>\).<br><br>"
         rf"<strong>c)</strong> \( \lambda = \frac{{h}}{{p}} = \frac{{6.63\times10^{{-34}}}}{{{p:.3e}}} "
         rf"= <strong>{lam:.3e}\,\text{{m}}</strong>\).<br><br>"
         r"<strong>d)</strong> Diffraction is significant only when wavelength is comparable to the spacing of the structure causing diffraction. "
         r"For electrons accelerated through a few kilovolts, the wavelength is of the same order as atomic spacing in graphite. "
         r"Everyday objects have enormously larger momentum, so their de Broglie wavelengths are far too small to observe diffraction.")
    hint = r"Start from \(eV = \frac{1}{2}mv^2\), then use \(p = mv\) and \( \lambda = h/p \)."
    return q, s, hint, 10


def pe_exam_duality_compare():
    q = (r"<strong>[12 marks] Evaluating Wave-Particle Duality</strong><br>"
         r"Discuss how the photoelectric effect and electron diffraction together provide evidence for wave-particle duality.<br>"
         r"In your answer:<br>"
         r"• explain what each experiment shows,<br>"
         r"• state why a single classical model is insufficient,<br>"
         r"• comment on why modern physics uses different models in different situations.")
    s = (r"The photoelectric effect shows that electromagnetic radiation transfers energy in discrete packets called photons. "
         r"Key evidence includes the threshold frequency, the fact that maximum photoelectron kinetic energy depends on frequency rather than intensity, "
         r"and the immediate emission of electrons when the frequency is above threshold. "
         r"These observations support a particle model of light.<br><br>"
         r"Electron diffraction shows that electrons behave as waves. "
         r"When accelerated electrons pass through graphite, they diffract and produce rings due to interference. "
         r"This is characteristic wave behaviour and is explained by the de Broglie relation \( \lambda = h/p \).<br><br>"
         r"No single classical model explains both sets of observations. "
         r"A purely wave model of light struggles to explain the threshold frequency and instantaneous emission in the photoelectric effect. "
         r"A purely particle model of electrons cannot explain diffraction and interference patterns.<br><br>"
         r"Wave-particle duality means that matter and radiation are best described using whichever model correctly predicts the phenomenon being observed. "
         r"This is not a contradiction but a limitation of classical intuition. Modern quantum theory combines these ideas into a deeper description.")
    hint = r"Use one paragraph for photoelectric effect, one for electron diffraction, and one comparing why classical physics is insufficient."
    return q, s, hint, 12


def pe_exam_spectrum_transition():
    wl = random.choice([410, 434, 486, 589, 656])
    E_J = H * C / (wl * 1e-9)
    E_eV = E_J / E_CHARGE
    diagram = svg_spectrum_lines([
        (410, "#7f7fff"),
        (434, "#5c79ff"),
        (486, "#4cd2ff"),
        (589, "#ffd84d"),
        (656, "#ff5a4d"),
    ])
    q = (rf"<strong>[8 marks] Spectral Line and Transition Energy</strong><br>"
         rf"The visible emission spectrum of a gas includes the lines shown below.<br>{diagram}"
         rf"One spectral line has wavelength <strong>{wl} nm</strong>.<br>"
         r"<strong>a)</strong> Calculate the energy of the photon corresponding to this line in J.<br>"
         r"<strong>b)</strong> Convert this energy to eV.<br>"
         r"<strong>c)</strong> Explain how an emission spectrum is produced in terms of atomic energy levels.<br>"
         r"<strong>d)</strong> Explain how an absorption spectrum differs from an emission spectrum.")
    s = (rf"<strong>a)</strong> \(E = \frac{{hc}}{{\lambda}}\).<br>"
         rf"\(E = \frac{{6.63\times10^{{-34}}\times3.00\times10^8}}{{{wl}\times10^{{-9}}}} = <strong>{E_J:.3e}\,\text{{J}}</strong>\).<br><br>"
         rf"<strong>b)</strong> In eV: \(E = \frac{{{E_J:.3e}}}{{1.60\times10^{{-19}}}} = <strong>{E_eV:.2f}\,\text{{eV}}</strong>\).<br><br>"
         r"<strong>c)</strong> In an emission spectrum, electrons in atoms first move to higher energy levels and then de-excite. "
         r"When an electron drops to a lower level, it emits a photon whose energy equals the difference between the two levels. "
         r"Discrete energy differences therefore produce discrete spectral lines.<br><br>"
         r"<strong>d)</strong> In an absorption spectrum, photons of particular energies are absorbed by atoms, causing electrons to move up to higher levels. "
         r"This produces dark lines at those wavelengths in an otherwise continuous spectrum.")
    hint = r"Use \(E = hc/\lambda\), then divide by \(1.60\times10^{-19}\) to convert J to eV."
    return q, s, hint, 8


def pe_exam_photoelectron_speed():
    f = random.choice([9.5e14, 1.05e15, 1.25e15])
    phi_eV = random.choice([2.00, 2.20, 2.50])
    photon_eV = H * f / E_CHARGE
    Ek_eV = photon_eV - phi_eV
    Ek_J = Ek_eV * E_CHARGE
    v = math.sqrt(2 * Ek_J / M_E)
    q = (rf"<strong>[10 marks] Maximum Speed of Photoelectrons</strong><br>"
         rf"Radiation of frequency <strong>{f:.2e} Hz</strong> is incident on a metal with work function <strong>{phi_eV:.2f} eV</strong>.<br>"
         r"<strong>a)</strong> Calculate the photon energy in eV.<br>"
         r"<strong>b)</strong> Calculate the maximum kinetic energy of an emitted photoelectron in eV and in J.<br>"
         r"<strong>c)</strong> Calculate the maximum speed of the emitted photoelectrons.<br>"
         r"<strong>d)</strong> State one reason why not all emitted electrons have this maximum speed.")
    s = (
        rf"<strong>a)</strong> \(E = hf = 6.63\times10^{{-34}}\times{f:.2e} = {H*f:.3e}\,\text{{J}}\).<br>"
        rf"In eV this is <strong>{photon_eV:.2f}\,\text{{eV}}</strong>.<br><br>"
        rf"<strong>b)</strong> \(E_{{k,\max}} = hf - \phi = {photon_eV:.2f} - {phi_eV:.2f} = "
        rf"<strong>{Ek_eV:.2f}\,\text{{eV}}</strong>\).<br>"
        rf"In joules: \(E_{{k,\max}} = {Ek_eV:.2f}\times1.60\times10^{{-19}} = "
        rf"<strong>{Ek_J:.3e}\,\text{{J}}</strong>\).<br><br>"
        r"<strong>c)</strong> Using \(E_k = \frac{1}{2}mv^2\):<br><br>"
        rf"\(v = \sqrt{{\frac{{2E_k}}{{m}}}} = \sqrt{{\frac{{2\times{Ek_J:.3e}}}{{9.11\times10^{{-31}}}}}} "
        rf"= <strong>{v:.3e}\,\text{{m s}}^{{-1}}</strong>\).<br><br>"
        r"<strong>d)</strong> Not all electrons are emitted from the surface with the same initial conditions. "
        r"Some lose energy inside the metal before leaving the surface, so they emerge with less than the maximum kinetic energy."
    )
    hint = r"Find photon energy first, then use \(hf = \phi + E_{k,\max}\), then \(E_k = \frac{1}{2}mv^2\)."
    return q, s, hint, 10


def pe_exam_photon_count_intensity():
    intensity = random.choice([120, 180, 250])
    area_cm2 = random.choice([2.0, 3.5, 5.0])
    f = random.choice([1.10e15, 1.30e15, 1.50e15])
    area = area_cm2 * 1e-4
    power = intensity * area
    E = H * f
    photons_per_s = power / E
    q = (rf"<strong>[11 marks] Intensity, Photon Rate and Photoelectron Rate</strong><br>"
         rf"Ultraviolet radiation of intensity <strong>{intensity} W m⁻²</strong> and frequency <strong>{f:.2e} Hz</strong> falls normally on a metal surface of area <strong>{area_cm2:.1f} cm²</strong>.<br>"
         r"Assume every incident photon has sufficient energy to cause emission and that each photon liberates at most one electron.<br>"
         r"<strong>a)</strong> Calculate the power incident on the metal surface.<br>"
         r"<strong>b)</strong> Calculate the energy of one photon.<br>"
         r"<strong>c)</strong> Calculate the number of photons incident per second.<br>"
         r"<strong>d)</strong> Deduce the maximum possible rate of photoelectron emission.<br>"
         r"<strong>e)</strong> Explain why increasing intensity increases the rate of emission but not the maximum kinetic energy.")
    s = (rf"<strong>a)</strong> Area \(= {area_cm2:.1f}\times10^{{-4}} = {area:.3e}\,\text{{m}}^2\).<br>"
         rf"Power \(P = IA = {intensity}\times{area:.3e} = <strong>{power:.3e}\,\text{{W}}</strong>\).<br><br>"
         rf"<strong>b)</strong> Photon energy \(E = hf = 6.63\times10^{{-34}}\times{f:.2e} = <strong>{E:.3e}\,\text{{J}}</strong>\).<br><br>"
         rf"<strong>c)</strong> Number of photons per second \(N = P/E = {power:.3e}/{E:.3e} = <strong>{photons_per_s:.3e}\,\text{{s}}^{{-1}}</strong>\).<br><br>"
         rf"<strong>d)</strong> If each photon ejects at most one electron, the maximum possible photoelectron emission rate is "
         rf"<strong>{photons_per_s:.3e}\,\text{{electrons s}}^{{-1}}</strong>.<br><br>"
         r"<strong>e)</strong> Greater intensity means more energy per second and therefore more photons per second at the same frequency. "
         r"That increases the number of emitted electrons per second. "
         r"However, maximum kinetic energy depends on the energy of each photon, \(hf\), so at fixed frequency it remains unchanged.")
    hint = r"Use \(P = IA\), then \(E = hf\), then photons per second \(= P/E\)."
    return q, s, hint, 11




H = 6.63e-34
C = 3.00e8
E_CHARGE = 1.60e-19

def svg_energy_levels_q1_clone():
    return r"""<svg width="360" height="220" viewBox="0 0 360 220"
    style="margin:12px 0; display:block; background:#f9f8f5; border-radius:8px; padding:8px;">
  <line x1="55" y1="25" x2="55" y2="185" stroke="#333" stroke-width="2"/>
  <text x="24" y="110" transform="rotate(-90 24 110)" font-size="12" font-family="sans-serif" fill="#333">energy / eV</text>

  <line x1="90" y1="165" x2="230" y2="165" stroke="#01696f" stroke-width="3"/>
  <text x="240" y="169" font-size="13" font-family="sans-serif" fill="#333">ground = -21.56 eV</text>

  <line x1="90" y1="76" x2="230" y2="76" stroke="#01696f" stroke-width="3"/>
  <text x="240" y="80" font-size="13" font-family="sans-serif" fill="#333">A = -4.96 eV</text>

  <line x1="90" y1="66" x2="230" y2="66" stroke="#01696f" stroke-width="3"/>
  <text x="240" y="70" font-size="13" font-family="sans-serif" fill="#333">B = -3.16 eV</text>

  <text x="160" y="24" text-anchor="middle" font-size="13" font-family="sans-serif" fill="#555">three lowest energy levels</text>
</svg>"""


def pe_exam_aqa_q1_clone():
    uv_energy_eV = random.choice([5.8, 6.1, 6.4, 6.7, 7.0, 7.3])
    uv_energy_J = uv_energy_eV * E_CHARGE
    uv_wavelength = H * C / uv_energy_J

    ground = -21.56
    A = -4.96
    B = -3.16
    transfer_eV = 18.4

    gap_ground_to_B = B - ground
    gap_B_to_A = B - A
    gap_B_to_ground = B - ground
    gap_A_to_ground = A - ground

    lambda_BA = H * C / (gap_B_to_A * E_CHARGE)
    lambda_BG = H * C / (gap_B_to_ground * E_CHARGE)
    lambda_AG = H * C / (gap_A_to_ground * E_CHARGE)

    diagram = svg_energy_levels_q1_clone()

    q = rf"""
<strong>Q1.</strong> A tube contains a vapour of mercury atoms at low pressure.
In an experiment, the vapour is bombarded by a beam of electrons.

An electron in the beam gains <strong>{uv_energy_eV:.1f} eV</strong> of kinetic energy by moving through a potential difference <strong>V</strong>.

<strong>(a)</strong> Deduce <strong>V</strong>.<br>
V = ____________________ V <strong>(1)</strong><br><br>

The electron collides with a mercury atom.
The atom subsequently emits a photon of ultraviolet radiation with an energy of <strong>{uv_energy_eV:.1f} eV</strong>.

<strong>(b)</strong> Calculate the wavelength of the emitted photon of this ultraviolet radiation.<br>
wavelength = ____________________ m <strong>(3)</strong><br><br>

The experiment is repeated with a different gas.
The figure below shows the three lowest energy levels for an atom of the gas.

{diagram}

When an electron in the beam collides with the gas atom, <strong>18.4 eV</strong> of energy is transferred to the atom.

The atom subsequently emits a photon of visible light.

<strong>(c)</strong> State and explain the energy transitions that are involved.
Support your answer with appropriate calculations.<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________ <strong>(4)</strong><br><br>

<strong>(Total 8 marks)</strong>
"""

    s = rf"""
<strong>(a)</strong><br>
Since 1 eV is the energy gained by an electron moving through a potential difference of 1 V,
\[
V = \boxed{{{uv_energy_eV:.1f}\ \text{{V}}}}
\]

<strong>(b)</strong><br>
Convert the photon energy to joules:
\[
E = {uv_energy_eV:.1f} \times 1.60 \times 10^{{-19}} = {uv_energy_J:.3e}\ \text{{J}}
\]

Use
\[
E = hf \quad \text{{and}} \quad c = f\lambda
\]
so
\[
\lambda = \frac{{hc}}{{E}}
\]

\[
\lambda = \frac{{6.63\times10^{{-34}} \times 3.00\times10^8}}{{{uv_energy_J:.3e}}}
= \boxed{{{uv_wavelength:.2e}\ \text{{m}}}}
\]

<strong>(c)</strong><br>
The atom starts in the ground state at <strong>-21.56 eV</strong>.

The energy transferred is <strong>18.4 eV</strong> and
\[
-21.56 + 18.4 = -3.16\ \text{{eV}}
\]
so the atomic electron is excited from the <strong>ground state to level B</strong>.

The visible photon is emitted when the atom de-excites from <strong>B to A</strong>.

This is because the energy difference between B and A is
\[
(-3.16) - (-4.96) = 1.80\ \text{{eV}}
\]

The wavelength of this photon is
\[
\lambda = \frac{{hc}}{{E}} =
\frac{{6.63\times10^{{-34}} \times 3.00\times10^8}}{{1.80 \times 1.60\times10^{{-19}}}}
= {lambda_BA:.2e}\ \text{{m}}
\]
which is about <strong>{lambda_BA*1e9:.0f} nm</strong>, so it is visible.

A transition from <strong>B to ground</strong> would have energy difference
\[
(-3.16) - (-21.56) = 18.4\ \text{{eV}}
\]
giving wavelength
\[
{lambda_BG:.2e}\ \text{{m}}
\]
which is ultraviolet, not visible.

A transition from <strong>A to ground</strong> would have energy difference
\[
(-4.96) - (-21.56) = 16.60\ \text{{eV}}
\]
giving wavelength
\[
{lambda_AG:.2e}\ \text{{m}}
\]
which is also ultraviolet.

Therefore the transitions involved are:
- <strong>ground state to B</strong> when 18.4 eV is absorbed,
- <strong>B to A</strong> when the visible photon is emitted.
"""

    hint = r"""
For (a), use the definition of the electronvolt.
For (b), convert eV to J and use \( \lambda = \frac{hc}{E} \).
For (c), match 18.4 eV to the upward transition, then test which downward transition gives visible light.
"""

    marks = 8
    return q, s, hint, marks




def svg_molecule_percentage_chart(labels, values, title="percentage of molecules in the sample"):
    max_v = max(values)
    x0 = 60
    bar_w = 42
    gap = 34
    base_y = 155
    scale = 90 / max_v if max_v else 1

    bars = []
    for i, (lab, val) in enumerate(zip(labels, values)):
        x = x0 + i * (bar_w + gap)
        h = val * scale
        y = base_y - h
        bars.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" rx="4" fill="#01696f"/>'
            f'<text x="{x + bar_w/2}" y="{y - 8:.1f}" text-anchor="middle" font-size="12" font-family="sans-serif">{val}</text>'
            f'<text x="{x + bar_w/2}" y="{base_y + 18}" text-anchor="middle" font-size="12" font-family="sans-serif">{lab}</text>'
        )

    return rf"""<svg width="320" height="210" viewBox="0 0 320 210"
    style="margin:12px 0; display:block; background:#f9f8f5; border-radius:8px; padding:8px;">
  <line x1="42" y1="28" x2="42" y2="155" stroke="#333" stroke-width="2"/>
  <line x1="42" y1="155" x2="290" y2="155" stroke="#333" stroke-width="2"/>
  <text x="18" y="95" transform="rotate(-90 18 95)" font-size="12" font-family="sans-serif">percentage</text>
  <text x="165" y="24" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#555">{title}</text>
  {''.join(bars)}
</svg>"""


def pe_exam_aqa_q2_clone():
    # tightly constrained for authentic AQA-clone feel
    element = random.choice([
        {"name": "chlorine", "proton": 17, "light": 35, "heavy": 37},
        {"name": "bromine", "proton": 35, "light": 79, "heavy": 81},
    ])

    name = element["name"]
    proton = element["proton"]
    light = element["light"]
    heavy = element["heavy"]

    ll = 2 * light
    lh = light + heavy
    hh = 2 * heavy

    percentages = [25, 50, 25]
    labels = [str(ll), str(lh), str(hh)]

    diagram = svg_molecule_percentage_chart(labels, percentages)
    heavier_neutrons = heavy - proton

    q = rf"""
<strong>Q2.</strong> A sample of {name} gas contains a mixture of two isotopes.

An experiment is done to find the percentage of each isotope in this sample.

<strong>(a)</strong> In the experiment, the gas is ionised by a beam of electrons.
Explain how the beam of electrons causes a particle of the gas to have a charge of <strong>+1e</strong>.
_____________________________________________________________ <strong>(2)</strong><br><br>

The gas consists of {name} molecules.
Each molecule has two {name} atoms.

The experiment finds that the {name} molecules contain <strong>{ll}</strong>, <strong>{lh}</strong> or <strong>{hh}</strong> nucleons.

The figure below shows the percentage of these different molecules in the sample.

{diagram}

<strong>(b)</strong> {name.title()} has a proton number of <strong>{proton}</strong>.
The two isotopes in the sample have different nucleon numbers.

Calculate the number of neutrons for the isotope that has the greater nucleon number.<br>
number of neutrons = _______________ <strong>(2)</strong><br><br>

<strong>(c)</strong> Deduce the percentage of each isotope in the gas.
Justify your conclusion.<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________ <strong>(2)</strong><br><br>

<strong>(Total 6 marks)</strong>
"""

    s = rf"""
<strong>(a)</strong><br>
An electron in the beam collides with an electron in a gas particle,
or transfers some of its kinetic energy to an electron in the gas particle.

One electron leaves the particle.
The particle has therefore lost one electron and has a charge of <strong>+1e</strong>.

<strong>(b)</strong><br>
The isotope with the greater nucleon number is <strong>{heavy}</strong>.

Number of neutrons
\[
= {heavy} - {proton}
= \boxed{{{heavier_neutrons}}}
\]

<strong>(c)</strong><br>
A molecule with <strong>{ll}</strong> nucleons must contain two atoms of the lighter isotope.

A molecule with <strong>{hh}</strong> nucleons must contain two atoms of the heavier isotope.

A molecule with <strong>{lh}</strong> nucleons must contain one atom of each isotope.

The percentages of the molecules are:
- <strong>{ll}</strong>: 25%
- <strong>{lh}</strong>: 50%
- <strong>{hh}</strong>: 25%

So 25% of the molecules are light-light, 25% are heavy-heavy, and 50% are mixed.

The mixed molecules contain one atom of each isotope, so they contribute equally to the total number of light and heavy atoms.

Therefore each isotope makes up
\[
\boxed{{50\%}}
\]
of the gas by number.
"""

    hint = rf"""
For (a), think electron-impact ionisation: one electron is removed.
For (b), neutrons = nucleon number − proton number.
For (c), identify light-light, light-heavy and heavy-heavy molecules, then use the 25 : 50 : 25 pattern.
"""

    marks = 6
    return q, s, hint, marks





H = 6.63e-34
E_CHARGE = 1.60e-19
M_E = 9.11e-31

def svg_electron_diffraction_apparatus():
    return r"""<svg width="520" height="220" viewBox="0 0 520 220"
    style="margin:12px 0; display:block; background:#f9f8f5; border-radius:8px; padding:8px;">
  <rect x="20" y="55" width="430" height="110" rx="10" fill="none" stroke="#333" stroke-width="2"/>
  <line x1="60" y1="80" x2="60" y2="140" stroke="#964219" stroke-width="4"/>
  <text x="42" y="72" font-size="12" font-family="sans-serif">filament</text>

  <line x1="110" y1="65" x2="110" y2="155" stroke="#555" stroke-width="3"/>
  <text x="92" y="52" font-size="12" font-family="sans-serif">anode</text>

  <rect x="255" y="72" width="10" height="76" fill="#01696f"/>
  <text x="230" y="58" font-size="12" font-family="sans-serif">graphite</text>
  <text x="232" y="172" font-size="12" font-family="sans-serif">target</text>

  <path d="M400,82 A42,42 0 0 1 400,138" fill="none" stroke="#a12c7b" stroke-width="3"/>
  <path d="M390,92 A30,30 0 0 1 390,128" fill="none" stroke="#a12c7b" stroke-width="2"/>
  <text x="412" y="75" font-size="12" font-family="sans-serif">fluorescent</text>
  <text x="426" y="90" font-size="12" font-family="sans-serif">screen</text>

  <line x1="70" y1="110" x2="245" y2="110" stroke="#333" stroke-width="2"/>
  <polygon points="245,110 236,105 236,115" fill="#333"/>

  <text x="150" y="95" font-size="12" font-family="sans-serif">electron beam</text>

  <text x="155" y="150" font-size="12" font-family="sans-serif">P</text>
  <text x="270" y="110" font-size="12" font-family="sans-serif">Q</text>
  <text x="392" y="92" font-size="12" font-family="sans-serif">R</text>
</svg>"""


def pe_exam_aqa_q4_clone():
    V1, V2 = random.choice([
        (3500, 5000),
        (4000, 6000),
        (4500, 6500),
        (5000, 7000),
    ])

    # de Broglie wavelengths for teacher solution
    lam1 = H / ((2 * M_E * E_CHARGE * V1) ** 0.5)
    lam2 = H / ((2 * M_E * E_CHARGE * V2) ** 0.5)

    apparatus = svg_electron_diffraction_apparatus()

    q = rf"""
<strong>Q4.</strong> The figure below shows apparatus used to demonstrate the wave–particle duality of electrons.

{apparatus}

The heated filament emits slow-moving electrons.
In region <strong>P</strong>, the electrons are accelerated to a high speed.
At <strong>Q</strong>, the fast-moving electrons are incident on the graphite target.
<strong>R</strong> is a point on one of the bright rings that are formed where the electrons strike the fluorescent screen.

<strong>(a)</strong> The electrons demonstrate wave-like and particle-like behaviour as they travel from the filament to the screen.

State and explain at which of <strong>P</strong>, <strong>Q</strong> or <strong>R</strong> the electrons are demonstrating wave-like behaviour.<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________ <strong>(2)</strong><br><br>

<strong>(b)</strong> The apparatus is adjusted so that the electrons are accelerated through a larger potential difference,
increasing from <strong>{V1} V</strong> to <strong>{V2} V</strong>, before reaching the graphite target.

Explain why the bright rings formed on the screen now have a smaller diameter.<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________ <strong>(3)</strong><br><br>

<strong>(Total 5 marks)</strong>
"""

    s = rf"""
<strong>(a)</strong><br>
The electrons are demonstrating wave-like behaviour at <strong>Q</strong>.

At Q the electrons are diffracted by the graphite target.
The gaps between layers / atoms in the graphite act like slits, so the electrons behave as waves.

<strong>(b)</strong><br>
When the accelerating potential difference increases, the electrons gain more kinetic energy and so have greater momentum.

The de Broglie wavelength is
\[
\lambda = \frac{{h}}{{p}}
\]
so a greater momentum means a smaller wavelength.

For example:
\[
\lambda_1 \approx {lam1:.2e}\ \text{{m}}
\qquad
\lambda_2 \approx {lam2:.2e}\ \text{{m}}
\]

Because the wavelength is now smaller compared with the spacing in the graphite, the electrons diffract less.

So the angle of diffraction is smaller, and this gives bright rings of smaller diameter on the screen.
"""

    hint = r"""
For (a), think about where diffraction happens.
For (b), use the chain:
greater speed / greater momentum \(\rightarrow\) smaller de Broglie wavelength \(\rightarrow\) less diffraction \(\rightarrow\) smaller ring diameter.
"""

    marks = 5
    return q, s, hint, marks


def pe_exam_aqa_q5_clone():
    # --- Fixed values from the actual AQA paper ---
    # Part (a) - alpha decay
    # Part (b) - tritium decay -> W⁻
    # Part (c) - evidence for/against using emission spectra
    # Part (d) - energy of line E (wavelength = 587 nm to match markscheme range)
    # Part (e) - emission vs absorption
    # New part (f) - highest energy line (line A, 390 nm)

    spectrum = svg_emission_spectra()

    # Part (d) wavelength (mark scheme says 580-590 nm; use 587 nm)
    wl_E = 587e-9   # m
    h, c, e = 6.63e-34, 3.00e8, 1.60e-19
    E_J = h * c / wl_E
    E_eV = E_J / e

    # Part (f) highest energy -> line A (390 nm)
    wl_A = 390e-9
    E_A_J = h * c / wl_A
    E_A_eV = E_A_J / e

    q = rf"""
<strong>Q5.</strong> Two stable isotopes of helium are <sup>4</sup><sub>2</sub>He and <sup>3</sup><sub>2</sub>He.
<br><br>
<strong>(a)</strong> An atom of <sup>4</sup><sub>2</sub>He is produced in a rock that contains uranium. It is produced following the radioactive decay of a <sup>238</sup><sub>92</sub>U atom. The decay also creates an atom of thorium (Th).
Write an equation for the decay of <sup>238</sup><sub>92</sub>U.
<br>_____________________________________________________________<br>
_____________________________________________________________ <strong>(2)</strong><br><br>
<strong>(b)</strong> A <sup>3</sup><sub>2</sub>He nucleus can be produced by the decay of a tritium nucleus <sup>3</sup><sub>1</sub>H.
State and explain which exchange particle is responsible for this decay.
<br>_____________________________________________________________<br>
_____________________________________________________________ <strong>(2)</strong><br><br>
Helium was discovered by analysing the light in the absorption spectrum of the Sun.
The figure below shows the positions of the brightest lines, labelled A to F, in the emission spectrum of helium. The brightest lines in the emission spectra of sodium and hydrogen are also shown.
{spectrum}
<strong>(c)</strong> Before helium was identified, some scientists suggested that the lines of the helium spectrum seen in the absorption spectrum of the Sun were due to the presence of sodium and hydrogen.
Discuss, with reference to the lines A to F in the figure above, the evidence for and against this suggestion.
<br>_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________ <strong>(2)</strong><br><br>
<strong>(d)</strong> Calculate, in eV, the change in energy level responsible for the spectral line labelled E in the diagram above.
<br>change in energy level = ____________________ eV <strong>(3)</strong><br><br>
<strong>(e)</strong> Explain, with reference to the processes within an atom, the difference between an emission spectrum and an absorption spectrum.
<br>_____________________________________________________________<br>
_____________________________________________________________<br>
_____________________________________________________________ <strong>(3)</strong><br><br>
<strong>(f)</strong> Identify which line (A–F) in the helium spectrum corresponds to the highest‑energy photon, and calculate its energy in eV.
<br>_____________________________________________________________<br>
_____________________________________________________________ <strong>(2)</strong><br><br>
<strong>(Total 14 marks)</strong>
"""

    s = rf"""
<strong>(a)</strong> Alpha decay of uranium‑238:
\[
^{{238}}_{{92}}U \rightarrow ^{{234}}_{{90}}Th + ^{{4}}_{{2}}He
\]
(Mass numbers and atomic numbers must balance; do not accept beta particles.)

<strong>(b)</strong> The decay is beta‑minus (β⁻) decay:
\[
^{{3}}_{{1}}H \rightarrow ^{{3}}_{{2}}He + e^{{-}} + \bar{{\nu}}_{{e}}
\]
The exchange particle is the <strong>W⁻</strong> boson, because a neutron changes into a proton, and the weak interaction requires a charged intermediate vector boson to conserve charge.

<strong>(c)</strong>
<em>For</em> the suggestion:
- Line C (≈490 nm) is present in both the helium and hydrogen spectra.
- Line E (≈590 nm) is present in both the helium and sodium spectra.
<em>Against</em> the suggestion:
- Line D (≈505 nm) is present in helium but appears in neither the hydrogen nor the sodium spectrum. This indicates a unique element, helium.

<strong>(d)</strong> Line E has a wavelength of approximately {wl_E*1e9:.0f} nm = {wl_E:.3e} m.
Photon energy:
\[
E = \frac{{hc}}{{\lambda}} = \frac{{6.63 \times 10^{{-34}} \times 3.00 \times 10^{{8}}}}{{{wl_E}}} = {E_J:.3e}\,\text{{J}}
\]
\[
E = \frac{{{E_J:.3e}}}{{1.60 \times 10^{{-19}}}} = \boxed{{{E_eV:.2f}\,\text{{eV}}}}
\]

<strong>(e)</strong>
- <strong>Emission spectrum:</strong> Electrons in an atom fall from higher to lower energy levels, releasing photons of specific energies. These appear as bright lines on a dark background.
- <strong>Absorption spectrum:</strong> Electrons absorb photons of specific energies and jump to higher levels. The missing wavelengths appear as dark lines on a continuous rainbow background.
In both cases, the photon energy matches the difference between two discrete energy levels: \( \Delta E = hf \).

<strong>(f)</strong>
The highest‑energy photon corresponds to the shortest wavelength. Line <strong>A</strong> (≈390 nm) is the shortest wavelength.
Photon energy:
\[
E = \frac{{hc}}{{\lambda}} = \frac{{6.63 \times 10^{{-34}} \times 3.00 \times 10^{{8}}}}{{390 \times 10^{{-9}}}} = {E_A_J:.2e}\,\text{{J}}
\]
\[
E = \frac{{{E_A_J:.2e}}}{{1.60 \times 10^{{-19}}}} = \boxed{{{E_A_eV:.2f}\,\text{{eV}}}}
\]
"""

    hint = r"""
For (a), remember that an alpha particle is a helium nucleus \(^4_2He\).
For (b), beta‑minus decay involves a neutron turning into a proton; the weak interaction is mediated by the W⁻ boson.
For (c), compare which lines appear in which spectra: if a line appears in helium but not in hydrogen/sodium, it cannot be explained by those elements.
For (d) and (f), use \(E = \frac{hc}{\lambda}\) and convert J → eV by dividing by \(1.60 \times 10^{-19}\).
For (e), think about whether electrons are moving up (absorption) or down (emission) between energy levels.
"""

    marks = 14   # 2+2+2+3+3+2
    return q, s, hint, marks


def _sample_variants(pool, count):
    if count >= len(pool):
        picked = pool[:]
        random.shuffle(picked)
        return picked
    return random.sample(pool, count)


def alevel_physics_photoelectric_variants(difficulty, mode):
    foundational = [
        _pe_found_threshold_definition,
        _pe_found_work_function_definition,
        _pe_found_below_threshold,
        _pe_found_intensity_effect,
        _pe_found_frequency_effect,
        _pe_found_photon_energy,
        _pe_found_work_function_from_threshold,
        _pe_found_convert_ev_to_j,
        _pe_found_convert_j_to_ev,
        _pe_found_photoelectric_observation,
    ]

    intermediate = [
        _pe_inter_threshold_from_work_function,
        _pe_inter_ke_from_photon,
        _pe_inter_stopping_potential_from_ke,
        _pe_inter_frequency_for_given_ke,
        _pe_inter_compare_intensity_frequency,
        _pe_inter_debroglie_basic,
        _pe_inter_momentum_from_wavelength,
        _pe_inter_potential_well,
        _pe_inter_electron_diffraction_explain,
        _pe_inter_stopping_potential_ke_ev,
    ]

    difficult = [
        _pe_diff_multistep_photoelectric,
        _pe_diff_max_ke_from_threshold_frequency,
        _pe_diff_find_work_function_from_stopping_potential,
        _pe_diff_debroglie_from_ke,
        _pe_diff_compare_two_metals,
        _pe_diff_explain_classical_failure,
        _pe_diff_electron_vs_photon,
        _pe_diff_line_spectrum,
        _pe_diff_excitation_vs_ionisation,
        _pe_diff_stopping_potential_graph,
        pe_exam_aqa_q5_clone,
    ]

    exam_difficult = [
        pe_exam_aqa_q1_clone,
        pe_exam_aqa_q2_clone,
        pe_exam_aqa_q4_clone,
        pe_exam_work_function_stopping,
        pe_exam_threshold_frequency_compare,
        pe_exam_plate_discharge_explanation,
        pe_exam_stopping_graph,
        pe_exam_energy_levels_visible_uv,
        pe_exam_diffraction_voltage,
        pe_exam_debroglie_numeric,
        pe_exam_duality_compare,
        pe_exam_spectrum_transition,
        pe_exam_photoelectron_speed,
        pe_exam_photon_count_intensity,
        pe_exam_aqa_q5_clone,
    ]

    if mode == 'exam' and difficulty == 'difficult':
        queue = exam_difficult[:]
        random.shuffle(queue)
        return queue

    if difficulty == 'foundational':
        queue = foundational[:]
        random.shuffle(queue)
        return queue

    if difficulty == 'intermediate':
        queue = intermediate[:]
        random.shuffle(queue)
        return queue

    if difficulty == 'mixed':
        found_block = _sample_variants(foundational, 4)
        inter_block = _sample_variants(intermediate, 4)
        diff_block = _sample_variants(difficult, 2)
        return found_block + inter_block + diff_block

    if mode == 'mcq':
        return [pe_mcq] * 10

    queue = difficult[:]
    random.shuffle(queue)
    return queue

def pe_mcq():
    import random

    questions = [
        {
            "q": "Which of the following best explains why the photoelectric effect cannot be explained by the wave theory of light?",
            "opts": [
                "A  Waves cannot transfer energy to electrons.",
                "B  The wave theory predicts that any frequency of light should eventually eject electrons if the intensity is high enough.",
                "C  Waves do not have an electric field.",
                "D  The wave theory requires photons to have mass."
            ],
            "ans": "B",
            "hint": "Wave theory predicts continuous energy absorption; the photoelectric effect shows a threshold frequency."
        },
        {
            "q": "The work function of a metal is 2.0 eV. What is the threshold frequency? (h = 6.63 × 10⁻³⁴ J s, 1 eV = 1.60 × 10⁻¹⁹ J)",
            "opts": [
                "A  4.0 × 10¹⁴ Hz",
                "B  4.8 × 10¹⁴ Hz",
                "C  5.0 × 10¹⁴ Hz",
                "D  6.0 × 10¹⁴ Hz"
            ],
            "ans": "B",
            "hint": r"\(\phi = hf_0 \Rightarrow f_0 = \frac{2.0 \times 1.6\times10^{-19}}{6.63\times10^{-34}} \approx 4.83\times10^{14}\,\text{Hz}\)."
        },
        {
            "q": "Increasing the intensity of light above the threshold frequency while keeping frequency constant will:",
            "opts": [
                "A  increase the maximum kinetic energy of photoelectrons.",
                "B  increase the number of photoelectrons emitted per second.",
                "C  decrease the threshold frequency.",
                "D  decrease the stopping potential."
            ],
            "ans": "B",
            "hint": "Intensity ∝ number of photons; each photon still has the same energy, so more electrons are emitted but Kmax stays the same."
        },
        {
            "q": "Light of frequency 8.0 × 10¹⁴ Hz is shone on a metal with work function 2.2 eV. What is the maximum kinetic energy of the emitted photoelectrons in eV?",
            "opts": [
                "A  1.1 eV",
                "B  2.2 eV",
                "C  3.3 eV",
                "D  5.5 eV"
            ],
            "ans": "A",
            "hint": r"Photon energy: \(hf = 6.63\times10^{-34}\times8.0\times10^{14} \approx 5.30\times10^{-19}\,\text{J} = 3.31\,\text{eV}\). Then \(K_\text{max} = hf - \phi = 3.31 - 2.2 = 1.11\,\text{eV}\)."
        },
        {
            "q": "Which phenomenon provides evidence that light behaves as a particle?",
            "opts": [
                "A  Diffraction of light",
                "B  Interference of light",
                "C  Photoelectric effect",
                "D  Refraction of light"
            ],
            "ans": "C",
            "hint": "The photoelectric effect requires the photon model; wave theory cannot explain the threshold frequency."
        },
        {
            "q": "The de Broglie wavelength of an electron accelerated through 54 V is approximately:",
            "opts": [
                "A  0.17 nm",
                "B  1.7 nm",
                "C  17 nm",
                "D  0.017 nm"
            ],
            "ans": "A",
            "hint": r"\( \lambda = \frac{h}{\sqrt{2meV}} \approx 1.67\times10^{-10}\,\text{m} = 0.167\,\text{nm}\)."
        },
        {
            "q": "In the electron diffraction experiment, wave‑like behaviour is demonstrated when electrons:",
            "opts": [
                "A  are emitted from the filament.",
                "B  are accelerated through a potential difference.",
                "C  strike the fluorescent screen.",
                "D  pass through the graphite target."
            ],
            "ans": "D",
            "hint": "Diffraction occurs as the electrons interact with the layers of atoms in the graphite."
        },
        {
            "q": "A line emission spectrum is produced when electrons in an atom:",
            "opts": [
                "A  move randomly between energy levels.",
                "B  drop from higher to lower energy levels.",
                "C  are ejected from the atom.",
                "D  absorb photons and jump to higher energy levels."
            ],
            "ans": "B",
            "hint": "Emission spectra result from de‑excitation; the photon energy equals the energy difference between the levels."
        },
        {
            "q": "The stopping potential in a photoelectric experiment is a measure of:",
            "opts": [
                "A  the work function of the metal.",
                "B  the maximum kinetic energy of the emitted electrons.",
                "C  the threshold frequency.",
                "D  the intensity of the incident light."
            ],
            "ans": "B",
            "hint": "At the stopping potential, \(eV_s = K_\text{max}\)."
        },
        {
            "q": "The graph of maximum kinetic energy of photoelectrons against frequency is a straight line. Its gradient represents:",
            "opts": [
                "A  the work function divided by e.",
                "B  Planck's constant.",
                "C  the threshold frequency.",
                "D  1 divided by Planck's constant."
            ],
            "ans": "B",
            "hint": "Einstein's equation: \(K_\text{max} = hf - \phi\); the gradient is h."
        }
    ]

    qdata = random.choice(questions)
    q = qdata["q"]
    options = qdata["opts"]
    correct = qdata["ans"]
    s = f"Answer: {correct}\n\n{qdata['hint']}"
    hint = qdata["hint"]
    marks = 1
    return q, s, hint, marks, options, correct