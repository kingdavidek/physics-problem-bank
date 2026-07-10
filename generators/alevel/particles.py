"""A-level physics — particle physics and the Standard Model."""
import random

from generators.shared.utils import make_problem
from generators.shared.variant_utils import pick_named_variant


# ================================================================
# A-LEVEL PHYSICS – PARTICLE PHYSICS (DISTINCT VARIANTS)
# ================================================================


# ---------- FOUNDATIONAL (10 distinct functions) ----------
def part_found_atom_basics(difficulty, mode):
    q = "State what is meant by the proton number Z and the nucleon number A of an atom."
    s = "Z is the number of protons in the nucleus. A is the total number of protons and neutrons (nucleons)."
    hint = "Z = protons, A = protons + neutrons."
    return make_problem(q, s, hint, difficulty, 2, 'alevel', 'physics', 'particles')

def part_found_isotope_def(difficulty, mode):
    q = "Define the term isotope."
    s = "Isotopes are atoms of the same element (same proton number) but with different numbers of neutrons (different nucleon number)."
    hint = "Same Z, different A."
    return make_problem(q, s, hint, difficulty, 1, 'alevel', 'physics', 'particles')

def part_found_specific_charge_electron(difficulty, mode):
    e, me = 1.60e-19, 9.11e-31
    sc = e / me
    q = "Calculate the specific charge of an electron in C kg⁻¹. (e = 1.60×10⁻¹⁹ C, mₑ = 9.11×10⁻³¹ kg)"
    s = rf"Specific charge = Q/m = 1.60×10⁻¹⁹ / 9.11×10⁻³¹ = {sc:.3e} C kg⁻¹."
    hint = "Divide charge by mass."
    return make_problem(q, s, hint, difficulty, 2, 'alevel', 'physics', 'particles')

def part_found_specific_charge_proton(difficulty, mode):
    e, mp = 1.60e-19, 1.67e-27
    sc = e / mp
    q = "Calculate the specific charge of a proton in C kg⁻¹. (e = 1.60×10⁻¹⁹ C, mₚ = 1.67×10⁻²⁷ kg)"
    s = rf"Specific charge = Q/m = 1.60×10⁻¹⁹ / 1.67×10⁻²⁷ = {sc:.3e} C kg⁻¹."
    hint = "Divide charge by mass."
    return make_problem(q, s, hint, difficulty, 2, 'alevel', 'physics', 'particles')

def part_found_quark_proton(difficulty, mode):
    q = "State the quark composition and total charge of a proton."
    s = "Proton = uud (up, up, down). Charge = +⅔ + ⅔ − ⅓ = +1 (in units of e)."
    hint = "Proton has two up quarks and one down quark."
    return make_problem(q, s, hint, difficulty, 1, 'alevel', 'physics', 'particles')

def part_found_nucleon_number(difficulty, mode):
    q = "State what is meant by the nucleon number A and give an example for carbon-12."
    s = "A is the total number of protons and neutrons in the nucleus. Carbon-12 has A=12 (6 protons + 6 neutrons)."
    hint = "A = Z + N."
    return make_problem(q, s, hint, difficulty, 1, 'alevel', 'physics', 'particles')

def part_found_hadron_lepton_diff(difficulty, mode):
    q = "State one difference between a hadron and a lepton."
    s = "Hadrons feel the strong force; leptons do not. (Also: hadrons are made of quarks; leptons are fundamental)."
    hint = "Think about the strong interaction."
    return make_problem(q, s, hint, difficulty, 1, 'alevel', 'physics', 'particles')

def part_found_neutron_charge_baryon(difficulty, mode):
    q = "State the charge and baryon number of a neutron."
    s = "Charge = 0; baryon number B = +1."
    hint = "Neutron is a baryon with no net charge."
    return make_problem(q, s, hint, difficulty, 1, 'alevel', 'physics', 'particles')

def part_found_quark_generations(difficulty, mode):
    q = "Name the three generations of quarks in the Standard Model."
    s = "First generation: up (u), down (d). Second: charm (c), strange (s). Third: top (t), bottom (b)."
    hint = "Each generation has a +2/3 and a -1/3 quark."
    return make_problem(q, s, hint, difficulty, 2, 'alevel', 'physics', 'particles')

def part_found_specific_charge_definition(difficulty, mode):
    q = "Define specific charge. How is it calculated?"
    s = "Specific charge = charge/mass (Q/m). It is usually expressed in C kg⁻¹."
    hint = "It's a ratio."
    return make_problem(q, s, hint, difficulty, 1, 'alevel', 'physics', 'particles')



# ---------- INTERMEDIATE (10 distinct functions) ----------
def part_inter_specific_charge_alpha(difficulty, mode):
    e, u = 1.60e-19, 1.66e-27
    charge = 2 * e
    mass = 4 * u
    sc = charge / mass
    q = "Calculate the specific charge of an alpha particle (⁴₂He²⁺) in C kg⁻¹. (e = 1.60×10⁻¹⁹ C, u = 1.66×10⁻²⁷ kg)"
    s = rf"Charge = +2e = {charge:.2e} C. Mass = 4u = {mass:.2e} kg. Specific charge = {charge:.2e} / {mass:.2e} = {sc:.3e} C kg⁻¹."
    hint = "Alpha is a helium nucleus: 2 protons, 2 neutrons."
    return make_problem(q, s, hint, difficulty, 3, 'alevel', 'physics', 'particles')

def part_inter_neutron_quark_change(difficulty, mode):
    q = "In beta-minus decay, a neutron changes into a proton. Describe the quark change and the exchange particle."
    s = "A neutron (udd) becomes a proton (uud). One down quark changes to an up quark, emitting a W⁻ boson which then decays to e⁻ + ̄νₑ."
    hint = "Think: udd → uud; which flavour changes?"
    return make_problem(q, s, hint, difficulty, 3, 'alevel', 'physics', 'particles')

def part_inter_baryon_number(difficulty, mode):
    q = "State the baryon number B of a proton, a neutron, a π⁺ meson, and an antiproton. What is the baryon number of a quark?"
    s = "Proton: B = +1. Neutron: B = +1. π⁺: B = 0. Antiproton: B = −1. Quark: B = +1/3."
    hint = "Baryons B=+1, antibaryons B=−1, mesons B=0."
    return make_problem(q, s, hint, difficulty, 2, 'alevel', 'physics', 'particles')

def part_inter_muon_decay(difficulty, mode):
    q = "Write the decay equation for a muon and verify that charge and lepton number are conserved."
    s = r"μ⁻ → e⁻ + νμ + ̄νₑ. Charge: −1 → (−1) + 0 + 0 = −1. Lepton numbers: Lμ = 1 initially (μ⁻ has Lμ=+1). After: νμ has Lμ=+1, e⁻ has Lₑ=1, ̄νₑ has Lₑ=−1 → total Lμ=1, Lₑ=0 (initial Lₑ=0). Conserved."
    hint = "Check muon number and electron number separately."
    return make_problem(q, s, hint, difficulty, 4, 'alevel', 'physics', 'particles')

def part_inter_pion_composition(difficulty, mode):
    q = "Give the quark composition of a π⁺ and a π⁻ meson, and state their charges."
    s = "π⁺ = ūd (up quark, anti‑down), charge = +1. π⁻ = d̄u (down, anti‑up), charge = −1."
    hint = "Mesons are quark‑antiquark pairs."
    return make_problem(q, s, hint, difficulty, 2, 'alevel', 'physics', 'particles')

def part_inter_sigma_charge(difficulty, mode):
    q = "The Σ⁺ baryon has quark composition uus. Calculate its charge in units of e."
    s = "u = +2/3, u = +2/3, s = -1/3. Charge = 2/3 + 2/3 - 1/3 = +1."
    hint = "Add the charges of the quarks."
    return make_problem(q, s, hint, difficulty, 2, 'alevel', 'physics', 'particles')

def part_inter_pi_zero_decay(difficulty, mode):
    q = "The neutral pion π⁰ decays into two photons. Write the decay equation and state which fundamental force is responsible."
    s = "π⁰ → γ + γ. Electromagnetic interaction."
    hint = "π⁰ is chargeless; photons are EM."
    return make_problem(q, s, hint, difficulty, 2, 'alevel', 'physics', 'particles')

def part_inter_kaon_lepton_conservation(difficulty, mode):
    q = "The kaon K⁺ decays to a muon and a muon neutrino: K⁺ → μ⁺ + νμ. Show that muon lepton number is conserved in this decay."
    s = "Initial Lμ = 0 (K⁺ is not a lepton). Final: μ⁺ has Lμ = -1, νμ has Lμ = +1 → total Lμ = 0. Conserved."
    hint = "Anti‑muon has Lμ = -1."
    return make_problem(q, s, hint, difficulty, 3, 'alevel', 'physics', 'particles')

def part_inter_deuteron_specific_charge(difficulty, mode):
    e, u = 1.60e-19, 1.66e-27
    charge = e
    mass = 2 * u
    sc = charge / mass
    q = "Calculate the specific charge of a deuteron (²H nucleus containing one proton and one neutron). (e = 1.60×10⁻¹⁹ C, u = 1.66×10⁻²⁷ kg)"
    s = rf"Charge = +e = {charge:.2e} C, mass = 2u = {mass:.2e} kg. Specific charge = {charge:.2e} / {mass:.2e} = {sc:.3e} C kg⁻¹."
    hint = "Deuteron: A=2, Z=1."
    return make_problem(q, s, hint, difficulty, 3, 'alevel', 'physics', 'particles')

def part_inter_virtual_photon(difficulty, mode):
    q = "Explain what is meant by a virtual photon and how it mediates the electromagnetic force between two electrons."
    s = "A virtual photon is a temporary exchange particle that exists only during the interaction. It transfers energy and momentum between the two electrons, causing repulsion."
    hint = "Virtual particles are not directly observable."
    return make_problem(q, s, hint, difficulty, 3, 'alevel', 'physics', 'particles')



# ---------- DIFFICULT (10 distinct functions) ----------
def part_diff_conservation_check(difficulty, mode):
    import random
    reactions = [
        # (reaction, allowed?, explanation)
        ("p + π⁻ → K⁺ + Σ⁻", True,
         "Charge: +1−1=0 → +1−1=0 ✔. Baryon: +1 → +1 ✔. Strangeness: 0 → 0 ✔. Strong interaction conserves S, so allowed."),
        ("p + π⁻ → K⁺ + π⁰", False,
         "Baryon number: +1 → 0 ✘. Baryon number is not conserved; reaction impossible."),
        ("Σ⁰ → Λ + γ", True,
         "Charge: 0 → 0 ✔. Baryon: +1 → +1 ✔. Strangeness: −1 → −1 ✔. Electromagnetic interaction conserves S, so allowed."),
        ("Ξ⁰ → n + π⁰", False,
         "Strangeness changes from −2 to 0 (ΔS = +2). In the Standard Model a single interaction can only change strangeness by ±1 or 0; this reaction cannot occur in one step."),
        ("π⁺ → μ⁺ + νμ", True,
         "Charge: +1 → +1+0 ✔. Lepton numbers: Lμ=0 → −1+1=0 ✔. Weak interaction; allowed."),
        ("p + e⁺ → e⁻ + Σ⁰ + K⁺", False,
         "Charge: +1+1=+2 → −1+0+1=0 ✘. Lepton number: Lₑ = 0−1 = −1 → +1+0+0 = +1 ✘. Both charge and electron lepton number are not conserved; reaction impossible."),
        ("K⁺ → μ⁺ + νμ", True,
         "Charge: +1 → +1 ✔. Strangeness: +1 → 0 (ΔS=1), allowed in weak decay."),
        ("n → p + e⁻ + ̄νe", True,
         "Beta‑minus decay: charge 0→+1−1=0, baryon +1→+1, lepton numbers Lₑ:0→1−1=0. Allowed."),
        ("p + e⁻ → n + νe", True,
         "Electron capture: charge +1−1=0, baryon +1→+1, Lₑ:1→0+1=1. Allowed via weak interaction."),
        ("μ⁻ → e⁻ + νe", False,
         "Lepton numbers: Lμ=1 initially, Lμ=0 after; Lₑ:0→1+1=2. Both muon and electron lepton numbers are not conserved (a muon neutrino is required). Reaction impossible."),
    ]
    reaction, allowed, explanation = random.choice(reactions)
    q = f"Determine whether the following reaction is possible, applying conservation laws for charge, baryon number, and lepton numbers (where relevant). Justify your answer.\n\n{reaction}"
    s = f"{'Allowed' if allowed else 'Not allowed'}. {explanation}"
    hint = "Check charge, baryon number, and (if leptons are involved) separate lepton numbers. Strangeness need only be conserved in strong/EM interactions."
    return make_problem(q, s, hint, difficulty, 4, 'alevel', 'physics', 'particles')


def part_diff_specific_charge_comparison(difficulty, mode):
    e, me, mp = 1.60e-19, 9.11e-31, 1.67e-27
    sc_e = e / me
    sc_p = e / mp
    q = "Calculate the specific charge of an electron and a proton. Hence explain why electrons are deflected much more than protons in a given magnetic field."
    s = rf"Electron: {sc_e:.2e} C kg⁻¹; Proton: {sc_p:.2e} C kg⁻¹. The electron's specific charge is ~1800 times larger, so for equal speeds the magnetic force causes a much tighter curve (r = mv/qB)."
    hint = "Compare Q/m; larger specific charge → smaller radius."
    return make_problem(q, s, hint, difficulty, 4, 'alevel', 'physics', 'particles')

def part_diff_feynman_diagram(difficulty, mode):
    import random
    interactions = [
        (
            "beta‑minus decay of a neutron",
            "Neutron (udd) → proton (uud) + electron + electron antineutrino. Exchange particle: W⁻ boson. Quark change: down → up.",
            "W⁻ boson; d → u."
        ),
        (
            "beta‑plus decay of a proton",
            "Proton (uud) → neutron (udd) + positron + electron neutrino. Exchange particle: W⁺ boson. Quark change: up → down.",
            "W⁺ boson; u → d."
        ),
        (
            "electron capture by a proton",
            "Proton + electron → neutron + electron neutrino. Exchange particle: W⁺ boson. Quark change: up → down.",
            "W⁺ boson; u → d, electron absorbed."
        ),
        (
            "electromagnetic repulsion between two electrons",
            "e⁻ + e⁻ → e⁻ + e⁻ via virtual photon (γ) exchange. No quark change; fermion lines with photon squiggle.",
            "Virtual photon (γ); no quark change."
        ),
        (
            "strong interaction between an up and a down quark inside a nucleon",
            "Up quark + down quark exchange a gluon (g). Both quarks remain inside the nucleon; diagram shows two quark lines with a gluon squiggle between them.",
            "Gluon (g); quarks exchange colour."
        ),
    ]
    interaction, description, hint_text = random.choice(interactions)
    q = f"Draw a Feynman diagram for {interaction}. Label all particles and the exchange boson. Describe any quark transformation that occurs."
    s = description
    hint = hint_text
    return make_problem(q, s, hint, difficulty, 4, 'alevel', 'physics', 'particles')

def part_diff_kaon_strangeness(difficulty, mode):
    q = "Explain why kaons are always produced in pairs in strong interactions, yet decay via the weak interaction."
    s = "Kaons contain a strange quark (S = ±1). Strong interactions conserve strangeness → pair production. Weak interactions allow ΔS = ±1, so kaons decay via the weak force."
    hint = "Strangeness conservation rules."
    return make_problem(q, s, hint, difficulty, 3, 'alevel', 'physics', 'particles')

def part_diff_pair_production(difficulty, mode):
    q = "Explain why pair production cannot occur in free space and state the minimum photon energy required to create an electron‑positron pair."
    s = "A nearby nucleus must absorb momentum. Minimum photon energy = 2mₑc² = 1.022 MeV."
    hint = "Momentum conservation; E_min = 2×0.511 MeV."
    return make_problem(q, s, hint, difficulty, 3, 'alevel', 'physics', 'particles')

def part_diff_pp_pi_zero(difficulty, mode):
    q = "Determine whether the reaction p + p → p + p + π⁰ is possible. Apply conservation laws for charge, baryon number, and energy. (m_p = 938 MeV/c², m_π₀ = 135 MeV/c²; assume sufficient kinetic energy in the initial protons.)"
    s = "Charge: +1+1 = +2 → +1+1+0 = +2 ✔. Baryon number: +1+1 = +2 → +1+1+0 = +2 ✔. Energy: with enough kinetic energy, total energy before can equal rest energies after. Possible via strong interaction."
    hint = "Check Q, B, and rest energy."
    return make_problem(q, s, hint, difficulty, 4, 'alevel', 'physics', 'particles')

def part_diff_sigma_decay(difficulty, mode):
    q = "The Σ⁰ baryon decays to Λ + γ. State the forces involved and explain why this decay is electromagnetic rather than weak."
    s = "Σ⁰ → Λ + γ is electromagnetic because a photon is emitted and strangeness is conserved (S: -1 → -1). The weak interaction is much slower; if EM is allowed, it dominates."
    hint = "EM is faster than weak when allowed by conservation laws."
    return make_problem(q, s, hint, difficulty, 4, 'alevel', 'physics', 'particles')

def part_diff_pair_annihilation_energy(difficulty, mode):
    q = "An electron and a positron annihilate at rest, producing two photons. Calculate the energy of each photon in MeV. (m_e = 0.511 MeV/c²)"
    s = "Total rest energy = 2 × 0.511 MeV = 1.022 MeV. Each photon gets half (to conserve momentum): 0.511 MeV."
    hint = "E = m c², and momentum conservation requires two equal-energy photons."
    return make_problem(q, s, hint, difficulty, 3, 'alevel', 'physics', 'particles')

def part_diff_omega_decay(difficulty, mode):
    q = "The Ω⁻ baryon (sss) decays into Ξ⁰ + π⁻. Determine the change in strangeness and explain why this decay must proceed via the weak interaction."
    s = "Ω⁻: S = -3. Ξ⁰: S = -2, π⁻: S = 0. ΔS = +1. Strangeness changes, so the decay cannot be strong or electromagnetic; it must be weak (allows ΔS = ±1)."
    hint = "Weak interaction is the only one that can change quark flavour."
    return make_problem(q, s, hint, difficulty, 4, 'alevel', 'physics', 'particles')

def part_diff_feynman_pair_production(difficulty, mode):
    q = "Draw a Feynman diagram for pair production (γ → e⁺ + e⁻) in the presence of a nucleus. Label all particles and explain the role of the nucleus."
    s = "Diagram: a photon (squiggly line) splits into an electron (forward arrow) and a positron (backward arrow). The nucleus (heavy line) absorbs some momentum to conserve momentum. The nucleus is not part of the fundamental vertex but is necessary for momentum conservation."
    hint = "Momentum must be conserved; the nucleus provides a recoil."
    return make_problem(q, s, hint, difficulty, 5, 'alevel', 'physics', 'particles')


def part_diff_aqa_q1(difficulty, mode):
    # Fixed values from the paper
    # (a) neutrino interaction explanation
    # (b) specific charge of argon-37
    # (c) Feynman diagram (electron capture by a proton)
    # (d) 6‑mark essay on nuclear forces

    q = r"""
An electron neutrino interacts with a chlorine‑37 nucleus to produce an argon‑37 nucleus and an electron:
\[
\nu_e + {}^{37}_{17}\mathrm{Cl} \rightarrow {}^{37}_{18}\mathrm{Ar} + e^-
\]

<strong>(a)</strong> Explain, with reference to appropriate conservation laws, why the electron is emitted in this interaction.<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________ <strong>(2)</strong><br><br>

<strong>(b)</strong> Calculate the specific charge of the argon‑37 nucleus.<br>
specific charge = ____________________ C kg⁻¹ <strong>(3)</strong><br><br>

<strong>(c)</strong> In a different interaction, the argon‑37 nucleus interacts with an electron. The figure below represents the interaction of a quark in a baryon of the nucleus.<br><br>
(A diagram showing an incoming electron, a quark line emitting a W⁻ boson, and the quark changing flavour.)
<br><br>
Deduce the exchange particle and the effect on the baryon. Give one reason to support each answer.<br>
exchange particle: ____________________<br>
reason: __________________________________________________<br>
effect on baryon: ______________________________________________<br>
reason: __________________________________________________ <strong>(4)</strong><br><br>

<strong>(d)</strong> The argon‑37 nucleus decays into a stable nucleus.<br>
Describe the nature of the forces that act between nucleons and how these forces can maintain nuclear stability.<br>
In your answer, describe:<br>
&bull; the forces of repulsion and attraction that act between nucleons<br>
&bull; exchange particles associated with these forces<br>
&bull; the role of these forces in keeping the nucleus stable.<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________ <strong>(6)</strong><br><br>
<strong>(Total 14 marks)</strong>
"""

    s = r"""
<strong>(a)</strong> The electron is emitted to conserve <strong>charge</strong> and <strong>lepton number</strong>.<br>
Charge: LHS = 0 + 17 = +17, RHS = 18 + (-1) = +17 ✔<br>
Lepton number: LHS (νₑ has Lₑ = 1) + 0 = 1; RHS (e⁻ has Lₑ = 1) + 0 = 1 ✔

<strong>(b)</strong> Charge of argon nucleus = 18 × 1.60×10⁻¹⁹ = 2.88×10⁻¹⁸ C.<br>
Mass ≈ 37 × 1.67×10⁻²⁷ = 6.18×10⁻²⁶ kg.<br>
Specific charge = (2.88×10⁻¹⁸) / (6.18×10⁻²⁶) ≈ <strong>4.66×10⁷ C kg⁻¹</strong>.

<strong>(c)</strong> Exchange particle: <strong>W⁻ boson</strong>.<br>
Reason: it is the weak interaction (electron capture); charge is conserved at the vertex (e⁻ → νₑ + W⁻).<br>
Effect on baryon: a <strong>proton changes to a neutron</strong> (uud → ddu).<br>
Reason: an up quark changes to a down quark (u → d), so the baryon's charge decreases by +1.

<strong>(d)</strong> <em>Forces:</em><br>
- Electromagnetic repulsion between positively‑charged protons.<br>
- Gravitational attraction between all nucleons (negligible).<br>
- Strong interaction – both attractive and repulsive, acting between nucleons.<br><br>
<em>Exchange particles:</em><br>
- Virtual photons mediate the EM force.<br>
- Pions (or gluons) mediate the strong interaction between nucleons.<br><br>
<em>Role in stability:</em><br>
The strong force is much stronger than EM repulsion at nuclear distances (≈1 fm). It provides a short‑range attractive force (up to ~3 fm) that binds nucleons together, but becomes repulsive at very short range (< 0.5 fm) to prevent collapse. This balance, along with the right neutron‑to‑proton ratio, keeps the nucleus stable.
"""

    hint = r"For (a), check charge and lepton number. (b) specific charge = charge/mass. (c) look at the quark vertex – W⁻ changes u→d. (d) mention strong, EM, exchange particles, and range."
    marks = 14
    return make_problem(q, s, hint, difficulty, marks, 'alevel', 'physics', 'particles')


def part_diff_aqa_q2(difficulty, mode):
    q = r"""


<strong>(a)</strong> State the names of the four fundamental interactions.<br>
1. ____________________  2. ____________________<br>
3. ____________________  4. ____________________ <strong>(1)</strong><br><br>

<strong>(b)</strong> State the products of the decay of a free neutron.<br>
______________________________________________________________________________________ <strong>(1)</strong><br><br>

<strong>(c)</strong> Explain which of the fundamental interactions is responsible for the decay of the neutron.<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________ <strong>(2)</strong><br><br>

<strong>(d)</strong> The forces between two moving electrons cause their paths to change.<br>
Explain, using the concept of exchange particles, why the electron paths change.<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________ <strong>(3)</strong><br><br>
<strong>(Total 7 marks)</strong>
"""

    s = r"""
<strong>(a)</strong> 1. Gravity<br>2. Weak interaction<br>3. Strong interaction<br>4. Electromagnetic<br>(any order)

<strong>(b)</strong> Proton + electron + electron antineutrino (p + e⁻ + ̄νₑ).

<strong>(c)</strong> The <strong>weak</strong> interaction is responsible.<br>
Reason: the decay involves a change of quark flavour (down → up), and/or leptons are involved (electron and antineutrino), which only feel the weak force.

<strong>(d)</strong> The electrons repel via the electromagnetic force, which is mediated by <strong>virtual photons</strong>. These exchange particles carry momentum between the electrons. When a photon is emitted by one electron and absorbed by the other, momentum is transferred, causing both paths to change. This satisfies conservation of momentum.
"""

    hint = r"Four forces: strong, weak, EM, gravity. Neutron decay: β⁻. Exchange particles for EM: virtual photons."
    marks = 7
    return make_problem(q, s, hint, difficulty, marks, 'alevel', 'physics', 'particles')



# ---------- MCQ (unchanged) ----------
def pe_mcq_particles():
    import random
    questions = [
        {"q": "What is the specific charge of an electron?",
         "opts": ["A  1.76 × 10¹¹ C kg⁻¹","B  9.58 × 10⁷","C  1.76 × 10⁻¹¹","D  4.82 × 10⁷"],
         "ans": "A", "hint": "e/mₑ ≈ 1.76×10¹¹."},
        {"q": "Which of the following is not a fundamental particle?",
         "opts": ["A  Electron","B  Up quark","C  Proton","D  Muon"],
         "ans": "C", "hint": "Proton is a hadron (uud)."},
        {"q": "What is the charge, in units of e, of a strange quark?",
         "opts": ["A  +⅔","B  −⅓","C  +⅓","D  −⅔"],
         "ans": "B", "hint": "Strange quark = −⅓."},
        {"q": "A baryon has a baryon number of:",
         "opts": ["A  0","B  +1","C  −1","D  +1/3"],
         "ans": "B", "hint": "Baryons have B = +1."},
        {"q": "Which force is responsible for beta decay?",
         "opts": ["A  EM","B  Strong","C  Weak","D  Gravity"],
         "ans": "C", "hint": "Quark flavour change → weak interaction."},
        {"q": "What is the quark composition of a π⁺ meson?",
         "opts": ["A  uud","B  ūd","C  d̄u","D  ud̄"],
         "ans": "B", "hint": "π⁺ = up + anti‑down."},
        {"q": "How many quarks are in a neutron?",
         "opts": ["A  2","B  3","C  4","D  1"],
         "ans": "B", "hint": "Neutron = udd."},
        {"q": "Which of the following particles is a lepton?",
         "opts": ["A  Pion","B  Muon","C  Proton","D  Kaon"],
         "ans": "B", "hint": "Muon is a lepton."},
        {"q": "The exchange particle of the strong interaction is:",
         "opts": ["A  Photon","B  W boson","C  Gluon","D  Graviton"],
         "ans": "C", "hint": "Gluons carry the strong force."},
        {"q": "An alpha particle has nucleon number 4, proton number 2. Its specific charge (C kg⁻¹) is approx:",
         "opts": ["A  4.8×10⁷","B  9.6×10⁷","C  1.2×10⁷","D  2.4×10⁷"],
         "ans": "A", "hint": "2e/4u ≈ 4.82×10⁷."}
    ]
    qdata = random.choice(questions)
    return qdata["q"], f"Answer: {qdata['ans']}\n\n{qdata['hint']}", qdata["hint"], 1, qdata["opts"], qdata["ans"]


def part_diff_aqa_q4(difficulty, mode):
    q = r"""
A strong interaction between a negative kaon (K⁻) and a proton (p) produces an omega‑minus (Ω⁻) particle, a neutral kaon (K⁰) and an unidentified particle Y.
\[
K^- + p \rightarrow \Omega^- + K^0 + Y
\]

The table below contains information on the particles in this interaction.

<table style="border-collapse:collapse; width:100%; margin:10px 0;">
<tr><th>Particle</th><th>K⁻</th><th>p</th><th>Ω⁻</th><th>K⁰</th><th>Y</th></tr>
<tr><td>Rest energy / MeV</td><td>493.8</td><td>938.3</td><td>1672</td><td>497.8</td><td>493.8</td></tr>
<tr><td>Baryon number</td><td>0</td><td>+1</td><td>+1</td><td>0</td><td>……</td></tr>
<tr><td>Charge</td><td>-1e</td><td>+1e</td><td>-1e</td><td>0</td><td>……</td></tr>
<tr><td>Strangeness</td><td>-1</td><td>0</td><td>-3</td><td>+1</td><td>……</td></tr>
</table>

<strong>(a)</strong> Complete the table above for particle Y.<br>
______________________________________________________________________________________ <strong>(2)</strong><br><br>

<strong>(b)</strong> Calculate, in J, the rest energy of the Ω⁻.<br>
rest energy = ____________________ J <strong>(2)</strong><br><br>

<strong>(c)</strong> Suggest how energy is conserved in this interaction. Refer to the rest energies of the particles in the table above.<br>
______________________________________________________________________________________<br>
______________________________________________________________________________________ <strong>(2)</strong><br><br>

The quark structure of the Ω⁻ particle is sss. The Ω⁻ is unstable. It decays into a proton through a series of decays:
\[
\Omega^- \rightarrow \Xi^0 + \pi^-
\]
\[
\Xi^0 \rightarrow \Lambda^0 + \pi^0
\]
\[
\Lambda^0 \rightarrow p + \pi^-
\]
The Ξ⁰ and Λ⁰ are both hadrons.

<strong>(d)</strong> Deduce the quark structure of the Λ⁰ particle.<br>
quark structure of Λ⁰ = ____________________ <strong>(4)</strong><br><br>

The products of the decay series include π⁰ and π⁻ particles. These particles are unstable and decay.

<strong>(e)</strong> The π⁰ decays into gamma photons. Each gamma photon has a wavelength of 1.25 × 10⁻¹⁴ m. Calculate the energy of one of these photons.<br>
energy of photon = ____________________ J <strong>(2)</strong><br><br>

<strong>(f)</strong> The negative pion π⁻ decays.<br>
Which row shows the particles that could be created in this decay? Tick <strong>one</strong> box.<br>
□ μ⁻ + ν_μ<br>
□ e⁻ + ̄ν_e<br>
□ μ⁺ + ̄ν_μ<br>
□ e⁺ + ν_e <strong>(1)</strong><br><br>
<strong>(Total 13 marks)</strong>
"""

    s = r"""
<strong>(a)</strong> For particle Y:<br>
Baryon number = 0, Charge = +1e, Strangeness = +1.

<strong>(b)</strong> Rest energy = 1672 MeV = 1672 × 10⁶ × 1.60 × 10⁻¹⁹ J = 2.68 × 10⁻¹⁰ J (2.675 × 10⁻¹⁰ J).

<strong>(c)</strong> The total rest energy of the reactants (K⁻ + p) = 493.8 + 938.3 = 1432.1 MeV.<br>
Total rest energy of the products (Ω⁻ + K⁰ + Y) = 1672 + 497.8 + 493.8 = 2663.6 MeV.<br>
The products have more rest energy than the reactants, so the extra energy comes from the kinetic energy of the incoming particles. Energy is conserved overall when kinetic energy is included.

<strong>(d)</strong> Λ⁰ quark structure = <strong>uds</strong>.<br>
(From the decays: Ω⁻(sss) → Ξ⁰(uss) + π⁻(dū). Then Ξ⁰(uss) → Λ⁰(uds) + π⁰(uū/dd). At the last step, Λ⁰(uds) → p(uud) + π⁻(dū). Baryon number, charge and strangeness are all consistent.)

<strong>(e)</strong> E = hc/λ = (6.63 × 10⁻³⁴ × 3.00 × 10⁸) / (1.25 × 10⁻¹⁴) = 1.59 × 10⁻¹¹ J (1.591 × 10⁻¹¹ J).

<strong>(f)</strong> The correct row is: <strong>e⁻ + ̄ν_e</strong>. (π⁻ decays via the weak interaction to an electron and an electron antineutrino.)
"""

    hint = r"For (b) 1 MeV = 1.60 × 10⁻¹³ J. (d) track baryon number and strangeness through each decay. (e) use E = hc/λ."
    marks = 13
    return make_problem(q, s, hint, difficulty, marks, 'alevel', 'physics', 'particles')






# ---------- VARIANTS FUNCTION ----------
def alevel_physics_particles_variants(difficulty, mode):
    if mode == 'mcq':
        return [pe_mcq_particles] * 10
    if difficulty == 'foundational':
        pool = [
            part_found_atom_basics,
            part_found_isotope_def,
            part_found_specific_charge_electron,
            part_found_specific_charge_proton,
            part_found_quark_proton,
        ]
    elif difficulty == 'intermediate':
        pool = [
            part_inter_specific_charge_alpha,
            part_inter_neutron_quark_change,
            part_inter_baryon_number,
            part_inter_muon_decay,
            part_inter_pion_composition,
        ]
    elif difficulty == 'difficult':
        pool = [
            part_diff_conservation_check,
            part_diff_specific_charge_comparison,
            part_diff_feynman_diagram,
            part_diff_kaon_strangeness,
            part_diff_pair_production,
            part_diff_aqa_q1,
            part_diff_aqa_q2,
            part_diff_aqa_q4,
        ]
    elif difficulty == 'mixed':
        pool = (
            random.sample([
                part_found_atom_basics, part_found_isotope_def,
                part_found_specific_charge_electron, part_found_specific_charge_proton,
                part_found_quark_proton,
            ], 4) +
            random.sample([
                part_inter_specific_charge_alpha, part_inter_neutron_quark_change,
                part_inter_baryon_number, part_inter_muon_decay,
                part_inter_pion_composition,
            ], 4) +
            random.sample([
                part_diff_conservation_check, part_diff_specific_charge_comparison,
                part_diff_feynman_diagram, part_diff_kaon_strangeness,
                part_diff_pair_production,
            ], 2)
        )
        return pool
    else:
        pool = [
            part_diff_conservation_check,
            part_diff_specific_charge_comparison,
            part_diff_feynman_diagram,
            part_diff_kaon_strangeness,
            part_diff_pair_production,
        ]

    # Shuffle to ensure variety, then duplicate to 10 slots for the queue
    shuffled = random.sample(pool, len(pool))
    return (shuffled * (10 // len(shuffled) + 1))[:10]

# ---------- MAIN GENERATOR ----------
def alevel_physics_particles(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, options, correct = pe_mcq_particles()
        return make_problem(q, s, hint, difficulty, marks, 'alevel', 'physics', 'particles',
                            options=options, correct_answer=correct)
    variants = alevel_physics_particles_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)
    return variant(difficulty, mode)