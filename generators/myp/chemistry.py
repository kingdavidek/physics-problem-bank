import random
from generators.shared.utils import make_problem




# ================================================================
# MYP CHEMISTRY — THERMOCHEMISTRY — MAIN GENERATOR
# ================================================================
def myp_chemistry_energy_changes_and_rates(difficulty, mode):

    if difficulty == 'foundational':
        variant = random.choice([
            _thermo_found_classify_reaction,
            _thermo_found_temperature_change,
            _thermo_found_bond_breaking_making,
            _thermo_found_delta_h_sign,
            _thermo_found_activation_energy_definition,
            _thermo_found_catalyst_effect,
            _thermo_found_everyday_examples,
            _thermo_found_collision_theory_basics,
            _thermo_found_reversible_symbol,
            _thermo_found_rate_factors_state,
        ])
    elif difficulty == 'intermediate':
        variant = random.choice([
            _thermo_inter_calorimetry_basic,
            _thermo_inter_calorimetry_find_temp,
            _thermo_inter_bond_energy_simple,
            _thermo_inter_energy_profile_read,
            _thermo_inter_collision_theory_temperature,
            _thermo_inter_collision_theory_concentration,
            _thermo_inter_surface_area,
            _thermo_inter_calorimetry_error,
            _thermo_inter_reversible_equilibrium,
            _thermo_inter_enthalpy_table,
        ])
    else:
        variant = random.choice([
            _thermo_diff_bond_energy_multistep,
            _thermo_diff_calorimetry_per_mole,
            _thermo_diff_energy_profile_catalyst,
            _thermo_diff_multistep_calorimetry,
            _thermo_diff_rate_explain_all_factors,
            _thermo_diff_le_chatelier_qualitative,
            _thermo_diff_enthalpy_profile_draw,
            _thermo_diff_bond_energy_evaluate,
            _thermo_diff_equilibrium_closed_system,
            _thermo_diff_full_experiment_design,
        ])

    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'myp', 'chemistry', 'energy_changes_and_rates')



# -----------------------------------------------
# MYP Chemistry — Redox
# -----------------------------------------------
def myp_chemistry_redox(difficulty, mode):

    if difficulty == 'foundational':
        # Identify oxidation or reduction from electron transfer description
        scenarios = [
            ("magnesium loses 2 electrons to form Mg²⁺",
             "oxidation",
             "Oxidation is the loss of electrons. Magnesium loses electrons, so it is oxidised.",
             "Mg"),
            ("chlorine gains 1 electron to form Cl⁻",
             "reduction",
             "Reduction is the gain of electrons. Chlorine gains electrons, so it is reduced.",
             "Cl"),
            ("iron loses 3 electrons to form Fe³⁺",
             "oxidation",
             "Oxidation is the loss of electrons. Iron loses electrons, so it is oxidised.",
             "Fe"),
            ("oxygen gains 2 electrons to form O²⁻",
             "reduction",
             "Reduction is the gain of electrons. Oxygen gains electrons, so it is reduced.",
             "O"),
        ]
        scenario, answer, explanation, _ = random.choice(scenarios)
        q = rf"""State whether the following represents oxidation or reduction, and justify your answer:<br><br>
        <em>{scenario}</em>"""
        s = rf"This is <strong>{answer}</strong>. {explanation}<br><br>Remember: <strong>OIL RIG</strong> — Oxidation Is Loss, Reduction Is Gain."
        hint = r"""
            <strong>OIL RIG</strong><br>
            <strong>O</strong>xidation <strong>I</strong>s <strong>L</strong>oss of electrons<br>
            <strong>R</strong>eduction <strong>I</strong>s <strong>G</strong>ain of electrons<br>
            Ask yourself: is the species losing or gaining electrons?
        """
        marks = 2

    elif difficulty == 'intermediate':
        # Assign oxidation numbers to elements in a compound
        compounds = [
            {
                'formula': r'H_2O',
                'name': 'water',
                'elements': [('H', +1, 2), ('O', -2, 1)],
                'rules': 'H is +1 in compounds. O is −2 in compounds.'
            },
            {
                'formula': r'SO_4^{2-}',
                'name': 'sulfate ion',
                'elements': [('O', -2, 4), ('S', +6, 1)],
                'rules': 'O is −2. The ion has charge −2, so: S + 4(−2) = −2, giving S = +6.'
            },
            {
                'formula': r'NO_3^-',
                'name': 'nitrate ion',
                'elements': [('O', -2, 3), ('N', +5, 1)],
                'rules': 'O is −2. The ion has charge −1, so: N + 3(−2) = −1, giving N = +5.'
            },
            {
                'formula': r'CO_2',
                'name': 'carbon dioxide',
                'elements': [('O', -2, 2), ('C', +4, 1)],
                'rules': 'O is −2. Molecule is neutral, so: C + 2(−2) = 0, giving C = +4.'
            },
        ]
        c = random.choice(compounds)
        target = c['elements'][-1]  # ask about the less obvious element
        element, ox_num, _ = target
        sign = '+' if ox_num > 0 else ''
        q = rf"""Assign the oxidation number to <strong>{element}</strong> in \( {c['formula']} \) ({c['name']})."""
        s = rf"The oxidation number of {element} in \( {c['formula']} \) is <strong>{sign}{ox_num}</strong>.<br><br>{c['rules']}"
        hint = r"""
            <strong>Rules for Oxidation Numbers</strong><br>
            <ul style="margin:8px 0; padding-left:18px;">
                <li>Free elements = 0</li>
                <li>O in compounds = −2 (except peroxides)</li>
                <li>H in compounds = +1 (except metal hydrides)</li>
                <li>Sum of oxidation numbers = overall charge of species</li>
            </ul>
            Use the known values to calculate the unknown one algebraically.
        """
        marks = 3

    else:  # difficult
        # Identify oxidising agent, reducing agent, and what is oxidised/reduced
        reactions = [
            {
                'equation': r'Mg + CuSO_4 \rightarrow MgSO_4 + Cu',
                'oxidised': 'Mg (0 → +2, loses electrons)',
                'reduced': 'Cu (from +2 → 0, gains electrons)',
                'ox_agent': 'CuSO₄ (the copper ion accepts electrons)',
                'red_agent': 'Mg (donates electrons)',
            },
            {
                'equation': r'Zn + 2HCl \rightarrow ZnCl_2 + H_2',
                'oxidised': 'Zn (0 → +2, loses electrons)',
                'reduced': 'H (from +1 → 0, gains electrons)',
                'ox_agent': 'HCl (hydrogen ions accept electrons)',
                'red_agent': 'Zn (donates electrons)',
            },
            {
                'equation': r'Fe + 2AgNO_3 \rightarrow Fe(NO_3)_2 + 2Ag',
                'oxidised': 'Fe (0 → +2, loses electrons)',
                'reduced': 'Ag (from +1 → 0, gains electrons)',
                'ox_agent': 'AgNO₃ (silver ions accept electrons)',
                'red_agent': 'Fe (donates electrons)',
            },
        ]
        r = random.choice(reactions)
        q = rf"""For the following redox reaction, identify:
        <ol style="margin-top:10px;">
            <li>Which species is oxidised and which is reduced</li>
            <li>The oxidising agent and the reducing agent</li>
        </ol>
        \[ {r['equation']} \]"""
        s = rf"""<strong>Oxidised:</strong> {r['oxidised']}<br>
        <strong>Reduced:</strong> {r['reduced']}<br><br>
        <strong>Oxidising agent:</strong> {r['ox_agent']}<br>
        <strong>Reducing agent:</strong> {r['red_agent']}<br><br>
        <em>Remember: the oxidising agent causes oxidation by accepting electrons — and is itself reduced.
        The reducing agent causes reduction by donating electrons — and is itself oxidised.</em>"""
        hint = r"""
            <strong>Oxidising and Reducing Agents</strong><br>
            Track the oxidation numbers of each element:<br>
            <ul style="margin:8px 0; padding-left:18px;">
                <li>If oxidation number <strong>increases</strong> → oxidation → that species is the <strong>reducing agent</strong></li>
                <li>If oxidation number <strong>decreases</strong> → reduction → that species is the <strong>oxidising agent</strong></li>
            </ul>
            The oxidising agent <em>accepts</em> electrons. The reducing agent <em>donates</em> electrons.
        """
        marks = 5

    return make_problem(q, s, hint, difficulty, marks, 'myp', 'chemistry', 'redox')




# -----------------------------------------------
# MYP CHEMISTRY — Energy Changes and Rates of Reaction
# -----------------------------------------------

# --- FOUNDATIONAL (10 variants) ---

def _thermo_found_classify_reaction():
    """Classify a reaction as exothermic or endothermic from description"""
    reactions = [
        ("burning methane gas", "exothermic",
         "Combustion releases energy to the surroundings — the flame heats the air around it. ΔH is negative."),
        ("photosynthesis in a plant", "endothermic",
         "Photosynthesis absorbs energy from sunlight to build glucose. ΔH is positive."),
        ("a hand warmer getting hot", "exothermic",
         "The oxidation of iron in a hand warmer releases heat to the surroundings. ΔH is negative."),
        ("a sports injury cold pack getting cold", "endothermic",
         "Dissolving ammonium nitrate absorbs heat from the surroundings, causing the temperature to drop. ΔH is positive."),
        ("neutralisation of hydrochloric acid with sodium hydroxide", "exothermic",
         "Neutralisation reactions always release energy to the surroundings. ΔH is negative."),
        ("thermal decomposition of calcium carbonate", "endothermic",
         "Thermal decomposition requires continuous heating — energy is absorbed from the surroundings. ΔH is positive."),
        ("respiration in a cell", "exothermic",
         "Cellular respiration releases energy stored in glucose molecules. ΔH is negative."),
        ("citric acid reacting with sodium hydrogen carbonate", "endothermic",
         "The mixture cools down — energy is absorbed from the surroundings. ΔH is positive."),
    ]
    reaction, answer, explanation = random.choice(reactions)
    q = rf"Classify the following as <strong>exothermic</strong> or <strong>endothermic</strong>, and justify your answer:<br><br><em>{reaction}</em>"
    s = rf"This reaction is <strong>{answer}</strong>. {explanation}"
    hint = r"""
        <strong>Exothermic vs Endothermic</strong><br>
        Exothermic → surroundings get <em>warmer</em> → ΔH is <strong>negative</strong><br>
        Endothermic → surroundings get <em>cooler</em> → ΔH is <strong>positive</strong>
    """
    return q, s, hint, 2

def _thermo_found_temperature_change():
    """Predict temperature change direction from reaction type"""
    scenarios = [
        ("An exothermic reaction takes place in a beaker of water.",
         "increases", "The reaction releases energy to the surroundings. The water gains heat, so its temperature rises."),
        ("An endothermic reaction occurs in a test tube.",
         "decreases", "The reaction absorbs energy from the surroundings. The surroundings lose heat, so the temperature falls."),
        ("Combustion of ethanol heats 200 cm³ of water.",
         "increases", "Combustion is exothermic — it releases heat to the surroundings, warming the water."),
        ("Ammonium nitrate is dissolved in water in a polystyrene cup.",
         "decreases", "Dissolving ammonium nitrate is endothermic — it absorbs heat from the water, cooling it down."),
    ]
    scenario, change, explanation = random.choice(scenarios)
    q = rf"{scenario}<br><br>State whether the temperature of the water <strong>increases</strong> or <strong>decreases</strong>, and explain why."
    s = rf"The temperature <strong>{change}</strong>. {explanation}"
    hint = "Exothermic → temperature rises. Endothermic → temperature falls."
    return q, s, hint, 2

def _thermo_found_bond_breaking_making():
    """Foundational: correct the common misconception about bond breaking"""
    q = r"""A student writes: <em>"Breaking chemical bonds releases energy."</em><br><br>
    Is this statement correct? Explain your answer using the terms <strong>bond breaking</strong> and <strong>bond making</strong>."""
    s = r"""The statement is <strong>incorrect</strong>.<br><br>
    <strong>Bond breaking</strong> is endothermic — it <em>requires</em> energy to pull atoms apart.<br>
    <strong>Bond making</strong> is exothermic — it <em>releases</em> energy as new bonds form.<br><br>
    Whether the overall reaction is exo- or endothermic depends on the balance:
    if more energy is released making bonds than is needed to break them, the reaction is exothermic overall."""
    hint = r"""
        Remember:<br>
        Breaking bonds = energy <strong>IN</strong> (endothermic)<br>
        Making bonds = energy <strong>OUT</strong> (exothermic)
    """
    return q, s, hint, 3

def _thermo_found_delta_h_sign():
    """Identify sign of ΔH from context"""
    examples = [
        ("a reaction that releases heat to the surroundings", "negative (−)",
         "Exothermic reactions transfer energy to the surroundings. The products have less energy than the reactants, so ΔH < 0."),
        ("a reaction that absorbs heat from the surroundings", "positive (+)",
         "Endothermic reactions take in energy from the surroundings. The products have more energy than the reactants, so ΔH > 0."),
        ("the combustion of propane in a gas hob", "negative (−)",
         "Combustion is exothermic — it releases heat. ΔH is negative."),
        ("the thermal decomposition of copper carbonate on heating", "positive (+)",
         "Thermal decomposition requires a continuous energy input. ΔH is positive."),
    ]
    ex, sign, explanation = random.choice(examples)
    q = rf"State the sign of ΔH for the following, and explain your reasoning:<br><br><em>{ex}</em>"
    s = rf"ΔH is <strong>{sign}</strong>. {explanation}"
    hint = "ΔH negative = exothermic (energy released). ΔH positive = endothermic (energy absorbed)."
    return q, s, hint, 2

def _thermo_found_activation_energy_definition():
    """Define activation energy and relate to energy profile"""
    q = r"""(a) Define the term <em>activation energy</em>.<br>
    (b) On an energy profile diagram, where is the activation energy shown?<br>
    (c) Explain why a reaction with a very high activation energy tends to be slow."""
    s = r"""(a) Activation energy (E<sub>a</sub>) is the <strong>minimum energy</strong> that colliding particles must possess for a reaction to occur.<br><br>
    (b) On an energy profile, E<sub>a</sub> is the energy difference between the <strong>reactants</strong> and the <strong>peak</strong> (transition state) of the curve.<br><br>
    (c) A high activation energy means that only a small proportion of collisions involve particles with sufficient energy to react.
    Fewer successful collisions per second means the reaction proceeds more slowly."""
    hint = "Activation energy = energy gap from reactants to the peak. Higher peak = fewer successful collisions = slower reaction."
    return q, s, hint, 3

def _thermo_found_catalyst_effect():
    """Effect of catalyst on activation energy and energy profile"""
    q = r"""A catalyst is added to a chemical reaction.<br>
    (a) What effect does the catalyst have on the activation energy?<br>
    (b) Does the catalyst change the enthalpy change (ΔH) of the reaction? Explain.<br>
    (c) Give one real-world example of a catalyst in use."""
    s = r"""(a) The catalyst <strong>lowers</strong> the activation energy by providing an alternative reaction pathway.<br><br>
    (b) <strong>No</strong> — the catalyst does not change ΔH. The energy levels of the reactants and products remain the same;
    only the height of the peak (activation energy) is reduced.<br><br>
    (c) Any valid example: iron in the Haber process (making ammonia), enzymes in biological reactions,
    platinum in catalytic converters in cars."""
    hint = "A catalyst lowers Eₐ but leaves reactant and product energy levels — and therefore ΔH — unchanged."
    return q, s, hint, 3

def _thermo_found_everyday_examples():
    """Match everyday reactions to exo/endo with explanation"""
    pairs = [
        ("Hand warmers", "exothermic", "They release heat — that is the whole point of them."),
        ("Cold packs used for sports injuries", "endothermic", "They absorb heat from the skin, causing a cooling effect."),
        ("A gas cooker flame", "exothermic", "Combustion releases energy as heat and light."),
        ("Baking a cake in an oven", "endothermic", "The cake absorbs heat energy from the oven to undergo chemical changes."),
    ]
    item, answer, explanation = random.choice(pairs)
    q = rf"State whether <strong>{item}</strong> involve(s) an exothermic or endothermic process. Justify your answer."
    s = rf"<strong>{answer.title()}.</strong> {explanation}"
    hint = "Think about the direction of heat flow: is heat going into or out of the system?"
    return q, s, hint, 2

def _thermo_found_collision_theory_basics():
    """State the conditions for a successful collision"""
    q = r"""State the <strong>three conditions</strong> that must be met for a collision between particles to result in a chemical reaction."""
    s = r"""For a collision to be successful (i.e. to result in a reaction), particles must:<br>
    <ol style="margin-top:8px; padding-left:20px;">
        <li>Actually <strong>collide</strong> with each other</li>
        <li>Have sufficient <strong>energy</strong> — equal to or greater than the activation energy (E<sub>a</sub>)</li>
        <li>Collide with the correct <strong>orientation</strong> (the reactive parts of the molecules must face each other)</li>
    </ol>
    Only a small fraction of all collisions meet all three conditions — these are called <strong>successful collisions</strong>."""
    hint = "The three conditions: collide, sufficient energy (≥ Eₐ), correct orientation."
    return q, s, hint, 3

def _thermo_found_reversible_symbol():
    """Interpret the ⇌ symbol and define dynamic equilibrium"""
    q = r"""The following equation uses a special symbol:<br><br>
    \[ \text{N}_2(g) + 3\text{H}_2(g) \rightleftharpoons 2\text{NH}_3(g) \]
    (a) What does the symbol ⇌ tell you about this reaction?<br>
    (b) What is meant by <em>dynamic equilibrium</em>?<br>
    (c) State one condition required for equilibrium to be reached."""
    s = r"""(a) The ⇌ symbol indicates that the reaction is <strong>reversible</strong> — the products can react to re-form the reactants.<br><br>
    (b) Dynamic equilibrium is the state in which the <strong>forward and reverse reactions occur at the same rate</strong>,
    so the concentrations of reactants and products remain constant — even though both reactions are still happening.<br><br>
    (c) The reaction must occur in a <strong>closed system</strong> — no substances can enter or leave."""
    hint = "Dynamic ≠ static. Both reactions still occur; they just happen at equal rates."
    return q, s, hint, 3

def _thermo_found_rate_factors_state():
    """State factors that affect rate of reaction"""
    q = r"""State <strong>four factors</strong> that can affect the rate of a chemical reaction, and for each one, state whether increasing it speeds up or slows down the reaction."""
    s = r"""<table style="width:100%; border-collapse:collapse; margin-top:8px;">
    <tr style="background:#f0fafa;"><th style="padding:8px; text-align:left; border:1px solid #ddd;">Factor</th><th style="padding:8px; text-align:left; border:1px solid #ddd;">Effect of increasing</th></tr>
    <tr><td style="padding:8px; border:1px solid #ddd;">Temperature</td><td style="padding:8px; border:1px solid #ddd;">Speeds up — particles have more energy, more successful collisions</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd;">Concentration</td><td style="padding:8px; border:1px solid #ddd;">Speeds up — more particles per unit volume, more frequent collisions</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd;">Surface area</td><td style="padding:8px; border:1px solid #ddd;">Speeds up — more reactant particles exposed, more collisions possible</td></tr>
    <tr><td style="padding:8px; border:1px solid #ddd;">Catalyst</td><td style="padding:8px; border:1px solid #ddd;">Speeds up — lowers activation energy, more collisions are successful</td></tr>
    </table>"""
    hint = "Temperature, concentration, surface area, catalyst — all increase rate when increased/added."
    return q, s, hint, 4


# --- INTERMEDIATE (10 variants) ---

def _thermo_inter_calorimetry_basic():
    """q = mcΔT calculation"""
    m = random.choice([50, 100, 150, 200, 250])
    T_i = random.randint(18, 22)
    T_f = random.randint(T_i + 8, T_i + 30)
    dT = T_f - T_i
    q_val = round(m * 4.18 * dT / 1000, 2)
    q = rf"""A student heats \( {m} \, \text{{g}} \) of water in a calorimetry experiment.
    The temperature rises from \( {T_i}°\text{{C}} \) to \( {T_f}°\text{{C}} \).
    Using \( q = mc\Delta T \) where \( c = 4.18 \, \text{{J g}}^{{-1}} \text{{°C}}^{{-1}} \),
    calculate the heat energy transferred. Give your answer in kJ."""
    s = rf"""\( \Delta T = {T_f} - {T_i} = {dT}°\text{{C}} \)<br>
    \( q = {m} \times 4.18 \times {dT} = {round(m * 4.18 * dT, 1)} \, \text{{J}} \)<br>
    \( q = \boxed{{{q_val}}} \, \text{{kJ}} \)"""
    hint = r"""
        \[ q = mc\Delta T \]
        Then divide by 1000 to convert J → kJ.
    """
    return q, s, hint, 3

def _thermo_inter_calorimetry_find_temp():
    """Rearrange q = mcΔT to find final temperature"""
    m = random.choice([100, 150, 200])
    T_i = random.randint(18, 25)
    q_kj = round(random.uniform(2.0, 12.0), 1)
    q_j = q_kj * 1000
    dT = round(q_j / (m * 4.18), 1)
    T_f = round(T_i + dT, 1)
    q = rf"""\( {q_kj} \, \text{{kJ}} \) of heat energy is transferred to \( {m} \, \text{{g}} \) of water at \( {T_i}°\text{{C}} \).
    Calculate the final temperature of the water. (\( c = 4.18 \, \text{{J g}}^{{-1}} \text{{°C}}^{{-1}} \))"""
    s = rf"""Convert to joules: \( q = {q_kj} \times 1000 = {q_j} \, \text{{J}} \)<br>
    Rearrange: \( \Delta T = \frac{{q}}{{mc}} = \frac{{{q_j}}}{{{m} \times 4.18}} = {dT}°\text{{C}} \)<br>
    \( T_f = {T_i} + {dT} = \boxed{{{T_f}}}°\text{{C}} \)"""
    hint = r"""
        Rearrange \( q = mc\Delta T \) to find \( \Delta T \):
        \[ \Delta T = \frac{q}{mc} \]
        Then \( T_f = T_i + \Delta T \)
    """
    return q, s, hint, 3

def _thermo_inter_bond_energy_simple():
    """ΔH from bond energies — simple 2-bond reaction"""
    problems = [
        {
            'equation': r'H_2 + F_2 \rightarrow 2HF',
            'broken': [('H–H', 436, 1), ('F–F', 158, 1)],
            'made': [('H–F', 568, 2)],
        },
        {
            'equation': r'H_2 + Cl_2 \rightarrow 2HCl',
            'broken': [('H–H', 436, 1), ('Cl–Cl', 243, 1)],
            'made': [('H–Cl', 432, 2)],
        },
        {
            'equation': r'H_2 + Br_2 \rightarrow 2HBr',
            'broken': [('H–H', 436, 1), ('Br–Br', 193, 1)],
            'made': [('H–Br', 366, 2)],
        },
    ]
    p = random.choice(problems)
    energy_in  = sum(e * n for _, e, n in p['broken'])
    energy_out = sum(e * n for _, e, n in p['made'])
    dH = energy_in - energy_out
    direction = "exothermic" if dH < 0 else "endothermic"
    bond_table = "".join([
        f"<tr><td style='padding:6px 12px;border:1px solid #ddd;'>{name}</td>"
        f"<td style='padding:6px 12px;border:1px solid #ddd;'>{e}</td></tr>"
        for name, e, _ in p['broken'] + p['made']
    ])
    q = rf"""Use bond energies to calculate \( \Delta H \) for:
    \[ {p['equation']} \]
    <table style="margin:10px 0;border-collapse:collapse;">
    <tr style="background:#f0fafa;"><th style="padding:6px 12px;border:1px solid #ddd;">Bond</th>
    <th style="padding:6px 12px;border:1px solid #ddd;">Energy (kJ mol⁻¹)</th></tr>
    {bond_table}
    </table>
    State whether the reaction is exothermic or endothermic."""
    broken_str = " + ".join([f"{n} × {name} ({e}) = {n*e} kJ" for name, e, n in p['broken']])
    made_str   = " + ".join([f"{n} × {name} ({e}) = {n*e} kJ" for name, e, n in p['made']])
    s = rf"""Bonds broken: {broken_str} → Total = {energy_in} kJ<br>
    Bonds made: {made_str} → Total = {energy_out} kJ<br><br>
    \( \Delta H = {energy_in} - {energy_out} = \boxed{{{dH}}} \, \text{{kJ mol}}^{{-1}} \)<br>
    This reaction is <strong>{direction}</strong>."""
    hint = r"""
        \[ \Delta H = \sum E_{\text{bonds broken}} - \sum E_{\text{bonds made}} \]
        Negative result = exothermic. Positive result = endothermic.
    """
    return q, s, hint, 4

def _thermo_inter_energy_profile_read():
    """Read and interpret an energy profile SVG"""
    exo = random.choice([True, False])
    e_react = random.randint(40, 80)
    e_prod  = (e_react - random.randint(10, 30)) if exo else (e_react + random.randint(10, 30))
    e_peak  = max(e_react, e_prod) + random.randint(20, 50)
    dH = e_prod - e_react
    ea = e_peak - e_react

    # SVG energy profile
    def ey(e): return int(200 - (e / 150) * 160)
    r_y = ey(e_react); p_y = ey(e_prod); pk_y = ey(e_peak)

    svg = rf"""
    <svg width="320" height="220" style="margin:14px 0;border:1px solid #ddd;border-radius:6px;background:#fafafa;">
        <line x1="30" y1="10" x2="30" y2="200" stroke="#333" stroke-width="2"/>
        <line x1="30" y1="200" x2="300" y2="200" stroke="#333" stroke-width="2"/>
        <text x="8" y="110" font-size="11" fill="#555" transform="rotate(-90,8,110)" text-anchor="middle">Energy (kJ)</text>
        <text x="165" y="218" font-size="11" fill="#555" text-anchor="middle">Reaction progress →</text>
        <!-- Reactant line -->
        <line x1="40" y1="{r_y}" x2="90" y2="{r_y}" stroke="#01696f" stroke-width="2.5"/>
        <text x="65" y="{r_y - 6}" font-size="10" fill="#01696f" text-anchor="middle">Reactants</text>
        <!-- Product line -->
        <line x1="220" y1="{p_y}" x2="290" y2="{p_y}" stroke="#01696f" stroke-width="2.5"/>
        <text x="255" y="{p_y - 6}" font-size="10" fill="#01696f" text-anchor="middle">Products</text>
        <!-- Curve peak -->
        <path d="M90,{r_y} Q165,{pk_y - 20} 220,{p_y}" fill="none" stroke="#01696f" stroke-width="2.5"/>
        <circle cx="155" cy="{pk_y}" r="4" fill="#a02020"/>
        <text x="160" y="{pk_y - 8}" font-size="10" fill="#a02020">‡</text>
        <!-- ΔH arrow -->
        <line x1="270" y1="{r_y}" x2="270" y2="{p_y}" stroke="#856404" stroke-width="1.5" stroke-dasharray="4,3"/>
        <text x="282" y="{int((r_y + p_y)/2) + 4}" font-size="10" fill="#856404">ΔH</text>
    </svg>"""

    direction_str = "exothermic" if exo else "endothermic"
    q = rf"""The diagram below shows an energy profile for a chemical reaction.<br>{svg}<br>
    (a) Is this reaction exothermic or endothermic? Justify your answer using the diagram.<br>
    (b) On the diagram, where would you mark the activation energy (E<sub>a</sub>)?<br>
    (c) The approximate values are: reactants = {e_react} kJ, products = {e_prod} kJ, peak = {e_peak} kJ.
    Calculate ΔH and E<sub>a</sub>."""
    s = rf"""(a) The reaction is <strong>{direction_str}</strong>. The products are at a
    {'lower' if exo else 'higher'} energy level than the reactants, so energy is
    {'released to' if exo else 'absorbed from'} the surroundings.<br><br>
    (b) E<sub>a</sub> is shown by the gap between the <strong>reactants</strong> and the <strong>peak</strong> (‡) of the curve.<br><br>
    (c) \( \Delta H = {e_prod} - {e_react} = \boxed{{{dH}}} \, \text{{kJ mol}}^{{-1}} \)<br>
    \( E_a = {e_peak} - {e_react} = \boxed{{{ea}}} \, \text{{kJ mol}}^{{-1}} \)"""
    hint = "ΔH = products − reactants. Eₐ = peak − reactants."
    return q, s, hint, 4

def _thermo_inter_collision_theory_temperature():
    """Explain why temperature increases rate using collision theory"""
    q = r"""Explain, using collision theory, why <strong>increasing the temperature</strong> of a reaction increases its rate."""
    s = r"""Increasing temperature gives particles more <strong>kinetic energy</strong>.<br><br>
    This has two effects:
    <ol style="margin-top:8px; padding-left:20px;">
        <li>Particles move <strong>faster</strong>, so collisions occur more <strong>frequently</strong>.</li>
        <li>A greater <strong>proportion</strong> of collisions now have energy equal to or greater than the activation energy (E<sub>a</sub>).</li>
    </ol>
    Both effects increase the number of <strong>successful collisions</strong> per second, so the reaction rate increases."""
    hint = "Focus on TWO effects: more frequent collisions AND more collisions exceeding Eₐ."
    return q, s, hint, 3

def _thermo_inter_collision_theory_concentration():
    """Explain why concentration increases rate"""
    q = r"""A student increases the concentration of hydrochloric acid in a reaction with zinc.<br>
    Explain, using collision theory, why this increases the rate of reaction."""
    s = r"""Increasing concentration means there are <strong>more particles per unit volume</strong>.<br><br>
    With more particles in the same space, collisions between zinc and acid particles become
    <strong>more frequent</strong>. More collisions per second means more successful collisions per second,
    so the rate of reaction increases."""
    hint = "More particles per unit volume → more frequent collisions → faster reaction."
    return q, s, hint, 3

def _thermo_inter_surface_area():
    """Surface area and rate — marble chip experiment"""
    q = r"""A student investigates the rate of reaction between marble chips (calcium carbonate) and hydrochloric acid.
    The experiment is repeated using the same mass of marble but ground into a fine powder.<br><br>
    (a) Predict how the rate of reaction changes when powder is used instead of chips.<br>
    (b) Explain this change using the idea of surface area and collision frequency.<br>
    (c) State one variable the student should keep constant to make this a fair test."""
    s = r"""(a) The rate of reaction <strong>increases</strong> when powder is used.<br><br>
    (b) Grinding the marble into powder <strong>increases the surface area</strong> exposed to the acid.
    More marble particles are available at the surface for collisions with acid particles,
    increasing the <strong>collision frequency</strong>. More frequent collisions means more successful
    collisions per second, so the rate increases.<br><br>
    (c) Any one of: concentration of acid, temperature, total mass of marble, volume of acid."""
    hint = "Surface area ↑ → more particles exposed → collision frequency ↑ → rate ↑"
    return q, s, hint, 4

def _thermo_inter_calorimetry_error():
    """Sources of error in calorimetry — evaluation question"""
    q = r"""A student measures the enthalpy change of combustion of ethanol using a spirit burner and a copper calorimeter.
    Their calculated value of ΔH is much less negative than the accepted value.<br><br>
    (a) Suggest <strong>two sources of error</strong> in this experiment that could explain the discrepancy.<br>
    (b) For each source of error, suggest an improvement to the experimental method."""
    s = r"""<strong>Source of error 1:</strong> Heat lost to the surroundings (most significant error).<br>
    <em>Improvement:</em> Insulate the calorimeter with a draught shield and lagging to reduce heat loss.<br><br>
    <strong>Source of error 2:</strong> Incomplete combustion of the ethanol.<br>
    <em>Improvement:</em> Ensure adequate oxygen supply; use a lid to extinguish the flame cleanly.<br><br>
    <em>Other acceptable answers:</em> Assuming the specific heat capacity of the solution equals pure water;
    not accounting for the heat capacity of the copper calorimeter itself."""
    hint = "Think about where the energy could be going that you are not measuring. Heat loss to surroundings is almost always the biggest source of error."
    return q, s, hint, 4

def _thermo_inter_reversible_equilibrium():
    """Describe dynamic equilibrium and closed system requirement"""
    q = r"""The reaction between nitrogen and hydrogen to form ammonia is reversible:
    \[ \text{N}_2(g) + 3\text{H}_2(g) \rightleftharpoons 2\text{NH}_3(g) \]
    (a) What does the ⇌ symbol indicate?<br>
    (b) Explain what is meant by <em>dynamic equilibrium</em>.<br>
    (c) Why can this equilibrium only be reached in a closed system?"""
    s = r"""(a) The ⇌ symbol shows the reaction is <strong>reversible</strong> — products can react to re-form the reactants.<br><br>
    (b) Dynamic equilibrium is reached when the <strong>rate of the forward reaction equals the rate of the reverse reaction</strong>.
    Concentrations of reactants and products remain constant, but both reactions continue to occur simultaneously.<br><br>
    (c) In an open system, products could escape (e.g. ammonia gas leaving the container).
    This would prevent the reverse reaction from occurring at the same rate as the forward reaction,
    so equilibrium could never be established."""
    hint = "Dynamic = still happening, just balanced. Closed system = nothing escapes."
    return q, s, hint, 4

def _thermo_inter_enthalpy_table():
    """Read ΔH from context and interpret sign"""
    reactions = [
        (r"CH_4 + 2O_2 \rightarrow CO_2 + 2H_2O", -890, "exothermic",
         "The negative value shows energy is released to the surroundings. This is combustion — it produces heat."),
        (r"CaCO_3 \rightarrow CaO + CO_2", +178, "endothermic",
         "The positive value shows energy is absorbed from the surroundings. Heating is required to decompose calcium carbonate."),
        (r"H_2 + \frac{1}{2}O_2 \rightarrow H_2O", -286, "exothermic",
         "Negative ΔH confirms energy is released. Hydrogen combustion is strongly exothermic."),
    ]
    rxn, dH, direction, explanation = random.choice(reactions)
    sign = '+' if dH > 0 else ''
    q = rf"""The enthalpy change for the following reaction is \( \Delta H = {sign}{dH} \, \text{{kJ mol}}^{{-1}} \):<br>
    \[ {rxn} \]
    (a) Is this reaction exothermic or endothermic?<br>
    (b) What does the sign of ΔH tell you about the energy of the products compared to the reactants?"""
    s = rf"""(a) The reaction is <strong>{direction}</strong>.<br><br>
    (b) {explanation}<br>
    The {'products have less energy than the reactants (ΔH negative)' if dH < 0 else 'products have more energy than the reactants (ΔH positive)'}."""
    hint = "ΔH negative → products lower energy → exothermic. ΔH positive → products higher energy → endothermic."
    return q, s, hint, 3


# --- DIFFICULT (10 variants) ---

def _thermo_diff_bond_energy_multistep():
    """Multi-bond ΔH calculation with full working"""
    problems = [
        {
            'equation': r'CH_4 + 2O_2 \rightarrow CO_2 + 2H_2O',
            'broken': [('C–H', 413, 4), ('O=O', 498, 2)],
            'made':   [('C=O', 805, 2), ('O–H', 463, 4)],
        },
        {
            'equation': r'N_2 + 3H_2 \rightarrow 2NH_3',
            'broken': [('N≡N', 945, 1), ('H–H', 436, 3)],
            'made':   [('N–H', 391, 6)],
        },
        {
            'equation': r'C_2H_4 + H_2 \rightarrow C_2H_6',
            'broken': [('C=C', 614, 1), ('H–H', 436, 1)],
            'made':   [('C–C', 347, 1), ('C–H', 413, 2)],
        },
    ]
    p = random.choice(problems)
    energy_in  = sum(e * n for _, e, n in p['broken'])
    energy_out = sum(e * n for _, e, n in p['made'])
    dH = energy_in - energy_out
    direction = "exothermic" if dH < 0 else "endothermic"

    all_bonds = p['broken'] + p['made']
    bond_table = "".join([
        f"<tr><td style='padding:5px 10px;border:1px solid #ddd;'>{name}</td>"
        f"<td style='padding:5px 10px;border:1px solid #ddd;'>{e}</td></tr>"
        for name, e, _ in all_bonds
    ])
    broken_lines = "<br>".join([f"{n} × {name} = {n}×{e} = {n*e} kJ" for name, e, n in p['broken']])
    made_lines   = "<br>".join([f"{n} × {name} = {n}×{e} = {n*e} kJ" for name, e, n in p['made']])

    q = rf"""Use bond energies to calculate \( \Delta H \) for the following reaction:
    \[ {p['equation']} \]
    <table style="margin:10px 0;border-collapse:collapse;">
    <tr style="background:#f0fafa;">
    <th style="padding:5px 10px;border:1px solid #ddd;">Bond</th>
    <th style="padding:5px 10px;border:1px solid #ddd;">Bond energy (kJ mol⁻¹)</th></tr>
    {bond_table}
    </table>
    State whether the reaction is exothermic or endothermic and explain what this means in terms of bond energies."""

    s = rf"""<strong>Step 1 — Bonds broken (energy in):</strong><br>
    {broken_lines}<br>
    <strong>Total energy in = {energy_in} kJ</strong><br><br>
    <strong>Step 2 — Bonds made (energy out):</strong><br>
    {made_lines}<br>
    <strong>Total energy out = {energy_out} kJ</strong><br><br>
    <strong>Step 3:</strong> \( \Delta H = {energy_in} - {energy_out} = \boxed{{{dH}}} \, \text{{kJ mol}}^{{-1}} \)<br><br>
    The reaction is <strong>{direction}</strong>. {'More energy is released forming bonds in the products than is needed to break bonds in the reactants.' if dH < 0 else 'More energy is needed to break bonds in the reactants than is released forming bonds in the products.'}"""
    hint = r"""
        \[ \Delta H = \sum E_{\text{bonds broken}} - \sum E_{\text{bonds made}} \]
        Count bonds carefully — multiply bond energy by number of moles of that bond.
    """
    return q, s, hint, 6

def _thermo_diff_calorimetry_per_mole():
    """Calculate ΔH per mole from calorimetry data"""
    m = random.choice([100, 150, 200])
    T_i = random.randint(18, 22)
    T_f = random.randint(T_i + 15, T_i + 40)
    dT = T_f - T_i
    q_j = round(m * 4.18 * dT, 0)
    q_kj = round(q_j / 1000, 2)
    moles = round(random.uniform(0.005, 0.020), 3)
    dH = round(-q_kj / moles, 1)  # negative because exothermic combustion
    q = rf"""A student burns a small amount of ethanol under a copper calorimeter containing \( {m} \, \text{{g}} \) of water.
    The temperature rises from \( {T_i}°\text{{C}} \) to \( {T_f}°\text{{C}} \).
    \( {moles} \, \text{{mol}} \) of ethanol was burned. (\( c = 4.18 \, \text{{J g}}^{{-1}} \text{{°C}}^{{-1}} \))<br><br>
    (a) Calculate the heat energy transferred to the water in kJ.<br>
    (b) Calculate \( \Delta H \) per mole of ethanol in kJ mol⁻¹.<br>
    (c) The accepted value of ΔH for ethanol combustion is −1367 kJ mol⁻¹. Suggest why your calculated value is less negative."""
    s = rf"""(a) \( q = mc\Delta T = {m} \times 4.18 \times {dT} = {q_j:.0f} \, \text{{J}} = \boxed{{{q_kj}}} \, \text{{kJ}} \)<br><br>
    (b) \( \Delta H = -\frac{{q}}{{\text{{moles}}}} = -\frac{{{q_kj}}}{{{moles}}} = \boxed{{{dH}}} \, \text{{kJ mol}}^{{-1}} \)<br>
    (Negative because combustion is exothermic.)<br><br>
    (c) The calculated value is less negative (smaller magnitude) because heat is lost to the surroundings
    during the experiment — the calorimeter is not perfectly insulated. Some energy from combustion
    heats the air and apparatus rather than the water."""
    hint = r"""
        (a) \( q = mc\Delta T \), convert to kJ.<br>
        (b) \( \Delta H = -q \div n \). Negative sign for exothermic.<br>
        (c) Think about where heat energy could be lost.
    """
    return q, s, hint, 6

def _thermo_diff_energy_profile_catalyst():
    """Energy profile with and without catalyst — SVG"""
    e_react = random.randint(40, 60)
    e_prod  = e_react - random.randint(15, 30)
    e_peak  = e_react + random.randint(35, 60)
    e_peak_cat = e_react + random.randint(10, 25)
    dH = e_prod - e_react
    ea = e_peak - e_react
    ea_cat = e_peak_cat - e_react

    def ey(e): return int(200 - (e / 150) * 160)
    r_y=ey(e_react); p_y=ey(e_prod); pk_y=ey(e_peak); pk_cat_y=ey(e_peak_cat)

    svg = rf"""
    <svg width="340" height="230" style="margin:14px 0;border:1px solid #ddd;border-radius:6px;background:#fafafa;">
        <line x1="30" y1="10" x2="30" y2="210" stroke="#333" stroke-width="2"/>
        <line x1="30" y1="210" x2="315" y2="210" stroke="#333" stroke-width="2"/>
        <text x="8" y="115" font-size="10" fill="#555" transform="rotate(-90,8,115)" text-anchor="middle">Energy</text>
        <text x="175" y="226" font-size="10" fill="#555" text-anchor="middle">Reaction progress →</text>
        <line x1="40" y1="{r_y}" x2="85" y2="{r_y}" stroke="#333" stroke-width="2"/>
        <text x="62" y="{r_y-6}" font-size="9" fill="#333" text-anchor="middle">Reactants</text>
        <line x1="235" y1="{p_y}" x2="305" y2="{p_y}" stroke="#333" stroke-width="2"/>
        <text x="270" y="{p_y-6}" font-size="9" fill="#333" text-anchor="middle">Products</text>
        <!-- Without catalyst -->
        <path d="M85,{r_y} Q165,{pk_y-15} 235,{p_y}" fill="none" stroke="#01696f" stroke-width="2" stroke-dasharray="6,3"/>
        <text x="168" y="{pk_y-18}" font-size="9" fill="#01696f" text-anchor="middle">Without catalyst</text>
        <!-- With catalyst -->
        <path d="M85,{r_y} Q165,{pk_cat_y-10} 235,{p_y}" fill="none" stroke="#a02020" stroke-width="2"/>
        <text x="168" y="{pk_cat_y-14}" font-size="9" fill="#a02020" text-anchor="middle">With catalyst</text>
    </svg>"""

    q = rf"""The energy profile below shows a reaction with and without a catalyst.<br>{svg}<br>
    The following data applies: Reactants = {e_react} kJ, Products = {e_prod} kJ,
    Peak without catalyst = {e_peak} kJ, Peak with catalyst = {e_peak_cat} kJ.<br><br>
    (a) Calculate ΔH for the reaction.<br>
    (b) Calculate E<sub>a</sub> without the catalyst and E<sub>a</sub> with the catalyst.<br>
    (c) Explain why the catalyst increases the reaction rate but does not change ΔH.<br>
    (d) Explain why the products line is at the same height in both curves."""
    s = rf"""(a) \( \Delta H = {e_prod} - {e_react} = \boxed{{{dH}}} \, \text{{kJ mol}}^{{-1}} \)
    ({'exothermic' if dH < 0 else 'endothermic'})<br><br>
    (b) Without catalyst: \( E_a = {e_peak} - {e_react} = \boxed{{{ea}}} \, \text{{kJ mol}}^{{-1}} \)<br>
    With catalyst: \( E_a = {e_peak_cat} - {e_react} = \boxed{{{ea_cat}}} \, \text{{kJ mol}}^{{-1}} \)<br><br>
    (c) The catalyst provides an <strong>alternative reaction pathway</strong> with lower activation energy.
    More collisions now have sufficient energy to react, so the rate increases.
    However, the catalyst does not change the energy levels of reactants or products —
    ΔH depends only on these, so it is unchanged.<br><br>
    (d) The products line is at the same height because the catalyst does not change
    the chemical identity of the products or their energy content."""
    hint = "ΔH = products − reactants (unchanged). Catalyst only lowers the peak."
    return q, s, hint, 6

def _thermo_diff_multistep_calorimetry():
    """Multi-step: calorimetry + moles + comparison to accepted value"""
    fuel = random.choice([
        ('methanol', 0.726, -726),
        ('propanol', 0.060, -2021),
    ])
    fuel_name, moles_burned, dH_accepted = fuel
    m = 200
    T_i = random.randint(18, 22)
    q_kj = round(abs(dH_accepted) * moles_burned * random.uniform(0.4, 0.65), 1)
    dT = round(q_kj * 1000 / (m * 4.18), 1)
    T_f = round(T_i + dT, 1)
    dH_calc = round(-q_kj / moles_burned, 0)
    percentage_error = round(abs((dH_calc - dH_accepted) / dH_accepted) * 100, 1)

    q = rf"""A student burns \( {moles_burned} \, \text{{mol}} \) of {fuel_name} and heats \( {m} \, \text{{g}} \)
    of water. The temperature rises from \( {T_i}°\text{{C}} \) to \( {T_f}°\text{{C}} \).<br><br>
    (a) Calculate the heat transferred to the water (in kJ).<br>
    (b) Calculate the experimental value of \( \Delta H \) in kJ mol⁻¹.<br>
    (c) The accepted value is \( {dH_accepted} \, \text{{kJ mol}}^{{-1}} \).
    Calculate the percentage error.<br>
    (d) Suggest two reasons why the experimental value differs from the accepted value."""
    s = rf"""(a) \( q = {m} \times 4.18 \times {dT} = {round(m*4.18*dT,1)} \, \text{{J}} = \boxed{{{q_kj}}} \, \text{{kJ}} \)<br><br>
    (b) \( \Delta H = -\frac{{{q_kj}}}{{{moles_burned}}} = \boxed{{{dH_calc:.0f}}} \, \text{{kJ mol}}^{{-1}} \)<br><br>
    (c) \( \% \text{{error}} = \frac{{|{dH_calc:.0f} - ({dH_accepted})|}}{{|{dH_accepted}|}} \times 100
    = \boxed{{{percentage_error}}} \% \)<br><br>
    (d) Heat lost to surroundings; incomplete combustion; heat absorbed by the calorimeter itself;
    draught affecting the flame."""
    hint = r"q = mcΔT → ΔH = −q/n → % error = |experimental − accepted| / |accepted| × 100"
    return q, s, hint, 7

def _thermo_diff_rate_explain_all_factors():
    """Extended response: explain all four rate factors with collision theory"""
    factor = random.choice(['temperature', 'concentration', 'surface area', 'catalyst'])
    explanations = {
        'temperature': (
            "increasing the temperature of the reaction mixture",
            r"""Increasing temperature gives particles more <strong>kinetic energy</strong>.<br>
            Two effects occur: (1) particles move faster, so the <strong>collision frequency increases</strong>;
            (2) a greater <strong>proportion of collisions now exceed the activation energy</strong> E<sub>a</sub>.
            Both effects increase the number of successful collisions per second, increasing the rate."""
        ),
        'concentration': (
            "increasing the concentration of a reactant in solution",
            r"""Increasing concentration means there are <strong>more particles per unit volume</strong>.
            This increases the <strong>collision frequency</strong> — particles are more likely to encounter
            each other in a given time. More collisions per second leads to more successful collisions,
            increasing the rate."""
        ),
        'surface area': (
            "increasing the surface area of a solid reactant",
            r"""Breaking a solid into smaller pieces <strong>exposes more particles at the surface</strong>.
            Only surface particles can collide with particles in solution. A greater surface area means
            <strong>more particles are available for collision</strong>, increasing collision frequency
            and therefore the rate of reaction."""
        ),
        'catalyst': (
            "adding a catalyst to the reaction",
            r"""A catalyst provides an <strong>alternative reaction pathway with a lower activation energy</strong>.
            This means a greater proportion of collisions now have sufficient energy to react successfully.
            The collision frequency is unchanged, but more collisions result in a reaction.
            The catalyst is not consumed — it can be used repeatedly."""
        ),
    }
    desc, answer = explanations[factor]
    q = rf"""Using collision theory, explain the effect of <strong>{desc}</strong> on the rate of reaction.<br><br>
    Your answer should refer to: particle collisions, activation energy, and successful collisions."""
    s = answer
    hint = f"Structure your answer: what changes physically → how this affects collision frequency and/or the proportion exceeding Eₐ → effect on successful collisions."
    return q, s, hint, 5

def _thermo_diff_le_chatelier_qualitative():
    """Qualitative Le Chatelier — predict equilibrium shift"""
    scenarios = [
        (
            r"\text{N}_2(g) + 3\text{H}_2(g) \rightleftharpoons 2\text{NH}_3(g)",
            "the concentration of N₂ is increased",
            "forward",
            "Adding more N₂ increases the concentration of a reactant. The system responds by shifting in the forward direction to reduce this excess — consuming N₂ and producing more NH₃."
        ),
        (
            r"\text{N}_2(g) + 3\text{H}_2(g) \rightleftharpoons 2\text{NH}_3(g)",
            "some NH₃ is removed from the system",
            "forward",
            "Removing a product decreases its concentration. The equilibrium shifts forward to replace it, consuming reactants and producing more NH₃."
        ),
        (
            r"\text{N}_2(g) + 3\text{H}_2(g) \rightleftharpoons 2\text{NH}_3(g)",
            "the temperature is increased (forward reaction is exothermic)",
            "reverse",
            "Increasing temperature favours the endothermic direction, which is the reverse reaction. The equilibrium shifts backward, producing less NH₃ and more N₂ and H₂."
        ),
    ]
    equation, change, direction, explanation = random.choice(scenarios)
    q = rf"""Consider the following equilibrium:
    \[ {equation} \]
    State the direction the equilibrium shifts if <strong>{change}</strong>.
    Explain your answer using Le Chatelier's Principle."""
    s = rf"""The equilibrium shifts in the <strong>{direction}</strong> direction.<br><br>
    {explanation}<br><br>
    <em>Le Chatelier's Principle states: if a system at equilibrium is subjected to a change,
    the equilibrium shifts to oppose that change.</em>"""
    hint = "Le Chatelier: the system always shifts to oppose the change applied to it."
    return q, s, hint, 4

def _thermo_diff_enthalpy_profile_draw():
    """Describe how to draw an energy profile given ΔH and Eₐ values"""
    e_react = random.randint(30, 60)
    ea = random.randint(25, 55)
    dH = -random.randint(15, 40)
    e_prod = e_react + dH
    e_peak = e_react + ea
    q = rf"""Sketch and label an energy profile diagram for an exothermic reaction where:<br>
    <ul style="margin-top:8px; padding-left:20px;">
        <li>The reactants have an energy of \( {e_react} \, \text{{kJ}} \)</li>
        <li>The activation energy \( E_a = {ea} \, \text{{kJ mol}}^{{-1}} \)</li>
        <li>\( \Delta H = {dH} \, \text{{kJ mol}}^{{-1}} \)</li>
    </ul>
    (a) On your diagram, clearly label: reactants, products, peak (‡), E<sub>a</sub>, and ΔH.<br>
    (b) Calculate the energy of the products and the peak."""
    s = rf"""(b) Products energy: \( {e_react} + ({dH}) = \boxed{{{e_prod}}} \, \text{{kJ}} \)<br>
    Peak energy: \( {e_react} + {ea} = \boxed{{{e_peak}}} \, \text{{kJ}} \)<br><br>
    The energy profile should show:<br>
    — Reactants ({e_react} kJ) on the left at a higher level than products ({e_prod} kJ)<br>
    — A peak ({e_peak} kJ) above both, with ‡ marked<br>
    — E<sub>a</sub> = gap from reactants to peak ({ea} kJ)<br>
    — ΔH = gap from reactants to products, shown with a downward arrow ({dH} kJ)"""
    hint = "Products energy = reactants + ΔH. Peak energy = reactants + Eₐ."
    return q, s, hint, 5

def _thermo_diff_bond_energy_evaluate():
    """Bond energy method — evaluate limitations"""
    q = r"""Bond energy calculations often give values that differ from experimentally measured values of ΔH.<br><br>
    (a) Explain why bond energy values are described as <em>average</em> values.<br>
    (b) Describe one limitation of using average bond energies to calculate ΔH.<br>
    (c) A student calculates ΔH = −432 kJ mol⁻¹ for a reaction. The experimentally measured value
    is −418 kJ mol⁻¹. Suggest why these values differ."""
    s = r"""(a) Bond energy values are averages because the <strong>exact energy of a bond depends on
    the molecular environment</strong> — the same type of bond (e.g. C–H) has slightly different
    energies in different molecules. The tabulated values are averages across many compounds.<br><br>
    (b) Because average bond energies are used rather than exact values for the specific molecules
    involved, the calculated ΔH is only an approximation. This introduces error into the result.<br><br>
    (c) The bond energy values used are averages, not the exact values for the bonds in this specific reaction.
    The difference (−432 vs −418 kJ mol⁻¹) reflects the gap between the average and actual bond energies."""
    hint = "Bond energies are averages — they don't exactly match any one molecule. That's the source of error."
    return q, s, hint, 4

def _thermo_diff_equilibrium_closed_system():
    """Explain why equilibrium requires a closed system with full reasoning"""
    q = r"""The thermal decomposition of ammonium chloride is reversible:
    \[ \text{NH}_4\text{Cl}(s) \rightleftharpoons \text{NH}_3(g) + \text{HCl}(g) \]
    (a) Explain what would happen if this reaction were carried out in an open container.<br>
    (b) Explain why dynamic equilibrium can only be reached in a closed system.<br>
    (c) State two observable features of a system at dynamic equilibrium."""
    s = r"""(a) In an open container, the gaseous products (NH₃ and HCl) would escape into the air.
    The reverse reaction could not take place because the products would no longer be present
    in sufficient concentration to recombine. The decomposition would go to completion.<br><br>
    (b) Dynamic equilibrium requires both the forward and reverse reactions to proceed simultaneously
    at equal rates. This is only possible if the products are retained — i.e. in a closed system
    where no matter can enter or leave.<br><br>
    (c) Any two of:<br>
    — Concentrations of reactants and products remain constant<br>
    — Both forward and reverse reactions are still occurring<br>
    — The system has no net change in composition"""
    hint = "Open system → products escape → reverse reaction cannot occur → no equilibrium."
    return q, s, hint, 5

def _thermo_diff_full_experiment_design():
    """Design a calorimetry experiment — extended response"""
    q = r"""A student wants to measure the enthalpy change of neutralisation when sodium hydroxide
    solution reacts with hydrochloric acid.<br><br>
    (a) Describe a method the student could use, including equipment and measurements to take.<br>
    (b) Write the equation they would use to calculate the heat transferred.<br>
    (c) Explain why the calculated value of ΔH is likely to be less negative than the true value.<br>
    (d) Suggest two modifications to improve the accuracy of the experiment."""
    s = r"""(a) <strong>Method:</strong><br>
    1. Measure 25 cm³ of HCl solution into a polystyrene cup using a measuring cylinder.<br>
    2. Record the initial temperature of the HCl with a thermometer.<br>
    3. Add 25 cm³ of NaOH solution (same concentration). Stir gently.<br>
    4. Record the maximum temperature reached.<br>
    5. Calculate ΔT = T<sub>final</sub> − T<sub>initial</sub>.<br><br>
    (b) \( q = mc\Delta T \), where m = total mass of solution (assume 50 g), c = 4.18 J g⁻¹ °C⁻¹.<br><br>
    (c) Heat is lost to the surroundings — the polystyrene cup is not a perfect insulator,
    and some heat heats the air and the thermometer rather than the solution.
    This means the measured ΔT is smaller than the true value, giving a less negative ΔH.<br><br>
    (d) Any two: use a lid on the cup to reduce heat loss; use a more accurate temperature probe
    (e.g. data logger); repeat the experiment and take an average; use a vacuum-insulated vessel."""
    hint = "Structure: equipment → measurements → calculation → sources of error → improvements."
    return q, s, hint, 6
