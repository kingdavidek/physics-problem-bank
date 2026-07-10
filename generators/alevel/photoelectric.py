"""A-level physics — photoelectric effect and wave–particle duality."""
import random
import math

from generators.shared.utils import make_problem
from generators.alevel.physics_common import _sample_variants
from generators.shared.variant_utils import pick_named_variant


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
    variant = pick_named_variant(variants, variant_name)
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
    hint = r"Multiply by \( 1.60 \times 10^{-19} \)."
    return q, s, hint, 2


def _pe_found_convert_j_to_ev():
    phi_ev = random.choice([1.9, 2.2, 2.5, 2.8])
    phi_j = phi_ev * 1.60e-19
    q = rf"""A work function is \( {phi_j:.3g} \, \text{{J}} \).
Convert this value to electronvolts."""
    s = rf"""Use \( 1 \, \text{{eV}} = 1.60 \times 10^{{-19}} \, \text{{J}} \).<br>
\( \phi = \frac{{{phi_j:.3g}}}{{1.60 \times 10^{{-19}}}} \)<br>
\( \phi = \boxed{{{phi_ev:.3g} \, \text{{eV}}}} \)"""
    hint = r"Divide by \( 1.60 \times 10^{-19} \)."
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
    hint = r"Compare the work functions using \( E_k = hf - \phi \)."
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
    q = r"""A graph of stopping potential \(V_s\) against frequency \(f\) is plotted for a metal.
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

    if mode == 'mcq':
        return [pe_mcq] * 10

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

    seen = {}
    for fn in difficult + exam_difficult:
        seen[fn.__name__] = fn
    queue = list(seen.values())
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
            "hint": r"At the stopping potential, \(eV_s = K_\text{max}\)."
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
            "hint": r"Einstein's equation: \(K_\text{max} = hf - \phi\); the gradient is h."
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




