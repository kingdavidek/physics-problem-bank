"""Shared European School Integrated Science helpers and curriculum manifest."""
from models.svg_kit import PALETTE, shape_label, svg

# Machine-readable depth for registered modules. Tests compare this with
# lesson templates and topic_registry — do not assume a global 6–7 rule.
SYLLABUS_MODULES = {
    "1.1.1": {
        "slug": "what_is_science",
        "name": "What Is Science?",
        "year": "s1",
        "unit_code": "1.1",
        "unit_name": "Science Lab",
        "order": 1,
        "sections": 5,
        "checkpoints": 4,
        "objectives": (
            "Distinguish scientific knowledge from opinion or authority",
            "Explain why claims need public, testable evidence",
            "Describe reproducibility and why repeats matter",
            "Explain peer critique as a check on methods and conclusions",
            "Recognise scientific explanations as provisional",
        ),
    },
    "1.1.2": {
        "slug": "measurement",
        "name": "Measurement and SI Units",
        "year": "s1",
        "unit_code": "1.1",
        "unit_name": "Science Lab",
        "order": 2,
        "sections": 6,
        "checkpoints": 7,
        "objectives": (
            "Explain why scientists use universal SI units",
            "Recall SI base units for length, mass, time, temperature and current",
            "Use SI prefixes from nano to giga",
            "Convert between SI units and prefixes",
            "Describe calibration of a measuring instrument",
            "Distinguish accuracy, precision, random error and systematic error",
            "Read analogue scales and summarise repeated measurements",
        ),
    },
    "1.1.3": {
        "slug": "science_lab",
        "name": "The Science Laboratory",
        "year": "s1",
        "unit_code": "1.1",
        "unit_name": "Science Lab",
        "order": 3,
        "sections": 8,
        "checkpoints": 7,
        "objectives": (
            "Choose a measuring instrument that matches the quantity",
            "Apply laboratory safety rules and hazard controls",
            "Read a simple technical drawing of apparatus",
            "Identify independent, dependent and control variables",
            "Plan a controlled (fair) investigation",
            "Describe ways to reduce error in practical work",
            "Record results so someone else can repeat the method",
        ),
    },
    "1.2.1": {
        "slug": "food_formulas",
        "name": "Food Formulas: Molecules of Life",
        "year": "s1",
        "unit_code": "1.2",
        "unit_name": "Food",
        "order": 4,
        "sections": 5,
        "checkpoints": 5,
        "objectives": (
            "Explain why water matters in food and living things",
            "Identify proteins and typical food sources",
            "Identify fats and typical food sources",
            "Identify carbohydrates and typical food sources",
            "Distinguish plant and animal contributions to a diet",
        ),
    },
    "1.2.2": {
        "slug": "water_substances",
        "name": "Water and Other Substances",
        "year": "s1",
        "unit_code": "1.2",
        "unit_name": "Food",
        "order": 5,
        "sections": 6,
        "checkpoints": 6,
        "objectives": (
            "Describe particle arrangements in solid, liquid and gas",
            "Name melting, boiling, freezing, evaporation and condensation",
            "Distinguish a mixture from a pure substance",
            "Choose a separation method that matches the mixture",
            "Explain why mixed volumes are not always additive",
            "Describe water as a solvent in food and the kitchen",
        ),
    },
    "1.2.3": {
        "slug": "cooking_heat",
        "name": "Basic Cooking: Heat",
        "year": "s1",
        "unit_code": "1.2",
        "unit_name": "Food",
        "order": 6,
        "sections": 6,
        "checkpoints": 6,
        "objectives": (
            "Describe conduction through solids such as a pan",
            "Describe convection in fluids such as water or air",
            "Describe radiation from a grill or hot surface",
            "Match a cooking method to the main heat transfer",
            "Explain denaturing of proteins with heat",
            "Describe browning as a chemical change in cooking",
        ),
    },
    "1.2.4": {
        "slug": "cooking_acid",
        "name": "Basic Cooking: Acid",
        "year": "s1",
        "unit_code": "1.2",
        "unit_name": "Food",
        "order": 7,
        "sections": 5,
        "checkpoints": 4,
        "objectives": (
            "Link sour taste to acids in food",
            "Use pH and indicators to tell acid from alkali",
            "Explain acid cooking such as ceviche-style denaturing",
            "Explain how acid can help preserve food",
        ),
    },
    "1.2.5": {
        "slug": "cooking_salt",
        "name": "Basic Cooking: Salt",
        "year": "s1",
        "unit_code": "1.2",
        "unit_name": "Food",
        "order": 8,
        "sections": 5,
        "checkpoints": 5,
        "objectives": (
            "Recognise salt as an inorganic mineral used in food",
            "Describe a solution of salt in water",
            "Compare concentrations using amount in a volume",
            "Describe crystallisation when water evaporates",
            "Explain how salt can help preserve food",
        ),
    },
    "1.2.6": {
        "slug": "cooking_fermentation",
        "name": "Basic Cooking: Fermentation",
        "year": "s1",
        "unit_code": "1.2",
        "unit_name": "Food",
        "order": 9,
        "sections": 6,
        "checkpoints": 5,
        "objectives": (
            "Identify microorganisms used in food fermentation",
            "Describe yeast fermentation producing carbon dioxide and alcohol",
            "Describe lactic bacterial fermentation in yoghurt and pickles",
            "Explain fermentation as useful, controlled spoilage",
            "Name conditions that microorganisms need",
        ),
    },
    "1.2.7": {
        "slug": "nutrition",
        "name": "Nutrition and Food Information",
        "year": "s1",
        "unit_code": "1.2",
        "unit_name": "Food",
        "order": 10,
        "sections": 10,
        "checkpoints": 9,
        "objectives": (
            "Describe a balanced diet using food groups",
            "Link named deficiencies to missing nutrients",
            "Distinguish allergy from intolerance",
            "Describe obesity as a health condition linked to energy balance",
            "Describe eating disorders as health conditions needing qualified care",
            "Read energy and ingredient information on a label",
            "Convert between kilojoules and kilocalories at S1 level",
            "Explain why additives are listed on labels",
            "Critique a marketing claim using evidence",
        ),
    },
    "1.2.8": {
        "slug": "healthy_meal_project",
        "name": "Project: A Healthy Meal",
        "year": "s1",
        "unit_code": "1.2",
        "unit_name": "Food",
        "order": 11,
        "sections": 4,
        "checkpoints": 4,
        "objectives": (
            "Plan an evidence-based classroom meal using food-group knowledge",
            "Apply kitchen hygiene and safety rules",
            "Follow a method another group could repeat",
            "Present and reflect on evidence, not on personal eating habits",
        ),
    },
    "1.3.1": {
        "slug": "movement",
        "name": "Movement",
        "year": "s1",
        "unit_code": "1.3",
        "unit_name": "Sports",
        "order": 12,
        "sections": 6,
        "checkpoints": 7,
        "objectives": (
            "Measure distance and time in a movement investigation",
            "Define average speed as distance divided by time",
            "Use v = d/t with consistent SI units",
            "Convert units of distance and time used in speed",
            "Read distance and time from a distance–time graph",
            "Link the slope of a distance–time graph to speed, including rest",
        ),
    },
    "1.3.2": {
        "slug": "forces_sport",
        "name": "Forces in Sport",
        "year": "s1",
        "unit_code": "1.3",
        "unit_name": "Sports",
        "order": 13,
        "sections": 8,
        "checkpoints": 7,
        "objectives": (
            "Describe the effects of a force on motion or shape",
            "Describe forces as interactions between objects",
            "Use the newton as the unit of force",
            "Describe friction in sport, including helpful and slowing effects",
            "Distinguish mass from weight",
            "Locate the idea of centre of gravity and stability",
            "Describe equilibrium as balanced forces",
        ),
    },
    "1.3.3": {
        "slug": "breathing",
        "name": "Breathing, Respiration and Circulation",
        "year": "s1",
        "unit_code": "1.3",
        "unit_name": "Sports",
        "order": 14,
        "sections": 8,
        "checkpoints": 7,
        "objectives": (
            "Name the main gases in air",
            "Compare inhaled and exhaled air",
            "Describe respiration as cells using oxygen to release energy from food",
            "Measure pulse as a clue to heart rate",
            "Describe the heart pumping blood that carries oxygen",
            "Link breathing, blood and muscle work in sport",
            "Describe pressure and buoyancy in water sport at S1 level",
        ),
    },
    "1.3.4": {
        "slug": "sport_health",
        "name": "Sport and Health",
        "year": "s1",
        "unit_code": "1.3",
        "unit_name": "Sports",
        "order": 15,
        "sections": 7,
        "checkpoints": 6,
        "objectives": (
            "Identify the skeleton as support and protection",
            "Describe joints as places bones meet and move",
            "Describe antagonistic muscle pairs",
            "Apply injury, infection and UV protection ideas in sport",
            "Explain why some drugs are banned or unsafe in sport",
            "Link sweating, water and minerals to keeping cool in exercise",
        ),
    },
    "1.4.1": {
        "slug": "puberty_maturity",
        "name": "Puberty and Sexual Maturity",
        "year": "s1",
        "unit_code": "1.4",
        "unit_name": "Puberty",
        "order": 16,
        "sections": 5,
        "checkpoints": 4,
        "objectives": (
            "Describe typical physical changes at puberty in third-person language",
            "Describe typical emotional and social changes without personal disclosure",
            "Identify hormones as chemical messengers that help trigger puberty",
            "Explain that timing of puberty varies and that this is normal",
        ),
    },
    "1.4.2": {
        "slug": "reproductive_anatomy",
        "name": "Human Reproductive Anatomy",
        "year": "s1",
        "unit_code": "1.4",
        "unit_name": "Puberty",
        "order": 17,
        "sections": 6,
        "checkpoints": 5,
        "objectives": (
            "Label main female reproductive structures on an educational schematic",
            "Label main male reproductive structures and the shared urinary idea",
            "Name gametes: egg and sperm",
            "Outline the menstrual cycle as a repeating sequence",
            "Describe fertilisation as egg and sperm joining",
        ),
    },
    "1.4.3": {
        "slug": "pregnancy_sexual_health",
        "name": "Pregnancy and Sexual Health",
        "year": "s1",
        "unit_code": "1.4",
        "unit_name": "Puberty",
        "order": 18,
        "sections": 8,
        "checkpoints": 7,
        "objectives": (
            "Describe how sperm can meet an egg after sexual intercourse, in clinical language",
            "Describe pregnancy as development after fertilisation",
            "Outline fetal development and birth at S1 level",
            "Explain contraception as methods that reduce the chance of pregnancy",
            "Describe STIs as infections that can spread through sexual contact",
            "State that sexual identity and orientation vary, without asking pupils to disclose",
            "Describe consent, communication and healthy relationships using third-person scenarios",
        ),
    },
    "2.1.1": {
        "slug": "solar_system",
        "name": "The Solar System",
        "year": "s2",
        "unit_code": "2.1",
        "unit_name": "Universe",
        "order": 19,
        "sections": 9,
        "checkpoints": 8,
        "objectives": (
            "Distinguish rotation of a planet from its revolution around the Sun",
            "Explain seasons using the tilt of Earth's axis",
            "Describe the Moon as a satellite that we see by reflected sunlight",
            "Order planets and other Solar System bodies by a simple scale idea",
            "Use an astronomical unit as a Solar System distance scale",
            "Describe the universe as ancient and expanding, using public evidence",
            "Compare geocentric and heliocentric models using evidence, not authority",
        ),
    },
    "2.1.2": {
        "slug": "light_telescopes",
        "name": "Light and Telescopes",
        "year": "s2",
        "unit_code": "2.1",
        "unit_name": "Universe",
        "order": 20,
        "sections": 9,
        "checkpoints": 8,
        "objectives": (
            "Describe light as travelling in straight lines at a very high speed",
            "Explain a light-year as a distance, not a time",
            "Use ray ideas for shadows",
            "Link Moon phases and eclipses to relative positions of Sun, Earth and Moon",
            "Describe reflection with equal angles of incidence and reflection",
            "Describe refraction as a change of direction when light enters a new medium",
            "Describe colour as light that a surface reflects or a filter transmits",
            "Match a lens or telescope to gathering and focusing light",
        ),
    },
    "2.1.3": {
        "slug": "life_earth_elsewhere",
        "name": "Life on Earth and Elsewhere",
        "year": "s2",
        "unit_code": "2.1",
        "unit_name": "Universe",
        "order": 21,
        "sections": 5,
        "checkpoints": 4,
        "objectives": (
            "List requirements often used for life as we know it (energy, liquid water, chemicals)",
            "Describe early Earth and LUCA as evidence-based scientific models",
            "Distinguish a testable claim about extraterrestrial life from a rumour",
            "Explain why travel and habitation beyond Earth are tightly constrained",
        ),
    },
    "2.1.4": {
        "slug": "atoms_molecules",
        "name": "Atoms and Molecules",
        "year": "s2",
        "unit_code": "2.1",
        "unit_name": "Universe",
        "order": 22,
        "sections": 7,
        "checkpoints": 7,
        "objectives": (
            "Describe matter as made of particles that are always there",
            "Distinguish an element (one type of atom) from a mixture",
            "Read simple chemical symbols as names of elements",
            "Describe a molecule as atoms joined together",
            "Describe a reaction as rearrangement of atoms, not creation from nothing",
            "Write a simple word equation for a familiar reaction",
            "Explain that atom counts are conserved in a closed reaction story",
        ),
    },
    "2.2.1": {
        "slug": "healthy_living",
        "name": "Healthy Living",
        "year": "s2",
        "unit_code": "2.2",
        "unit_name": "Health",
        "order": 23,
        "sections": 6,
        "checkpoints": 5,
        "objectives": (
            "Describe a balanced diet as a mix of needs over time, without ranking classmates",
            "Link regular physical activity to health using public evidence, not body surveys",
            "Describe mental health as part of health and signpost qualified support",
            "Describe the microbiome as living microorganisms that interact with the body",
            "Describe respectful relationships and screen-time management as health ideas",
        ),
    },
    "2.2.2": {
        "slug": "infectious_disease",
        "name": "Infectious Disease and Immunity",
        "year": "s2",
        "unit_code": "2.2",
        "unit_name": "Health",
        "order": 24,
        "sections": 9,
        "checkpoints": 8,
        "objectives": (
            "Distinguish bacteria and viruses as different kinds of pathogen",
            "Describe transmission routes without asking who has been ill",
            "Order a simple chain of infection: source, route, new host",
            "Describe immunity as the body's learned or innate defence",
            "Explain vaccination as training immunity using a safe exposure",
            "Explain why antibiotics do not treat viruses and why resistance matters",
            "Read a simple outbreak table or bar sketch",
            "Link sanitation and hygiene to reducing spread",
        ),
    },
    "2.2.3": {
        "slug": "noninfectious_disease",
        "name": "Noninfectious and Environmental Disease",
        "year": "s2",
        "unit_code": "2.2",
        "unit_name": "Health",
        "order": 25,
        "sections": 7,
        "checkpoints": 6,
        "objectives": (
            "Distinguish infectious from noninfectious disease",
            "Give examples of inherited or long-term systemic conditions",
            "Link some diseases to nutrient deficiency using public evidence",
            "Link some diseases to pollution or occupation using public evidence",
            "Describe mental illness as a health condition that can be supported",
            "Describe treatment and support as clinical, not a classmate ranking",
        ),
    },
    "2.2.4": {
        "slug": "dependence_addiction",
        "name": "Pleasure, Dependence and Addiction",
        "year": "s2",
        "unit_code": "2.2",
        "unit_name": "Health",
        "order": 26,
        "sections": 6,
        "checkpoints": 5,
        "objectives": (
            "Distinguish ordinary pleasure from dependence",
            "Describe substance dependence using third-person scenarios",
            "Describe behavioural dependence using third-person scenarios",
            "Name social and risk factors without asking pupils to confess use",
            "Describe harm and support routes (trusted adult, qualified help)",
        ),
    },
    "2.2.5": {
        "slug": "tobacco",
        "name": "Tobacco, Nicotine and Vaping",
        "year": "s2",
        "unit_code": "2.2",
        "unit_name": "Health",
        "order": 27,
        "sections": 6,
        "checkpoints": 5,
        "objectives": (
            "Link tobacco use to disease and premature death using public evidence",
            "Describe nicotine as addictive and initiation as a health risk",
            "Critique industry marketing as a source that is not independent evidence",
            "Describe vaping as still uncertain and not a harmless swap",
            "Describe prevention as reducing uptake, not a pupil confession",
        ),
    },
    "2.3.1": {
        "slug": "vision",
        "name": "Vision",
        "year": "s2",
        "unit_code": "2.3",
        "unit_name": "Senses",
        "order": 28,
        "sections": 7,
        "checkpoints": 6,
        "objectives": (
            "Label cornea or lens, retina and the path toward the brain on a schematic",
            "Describe the eye as forming an image using refraction by the lens",
            "Describe accommodation as changing lens shape for near or far",
            "Distinguish near-sight and far-sight as focusing errors in this S2 model",
            "Explain stereo depth as two slightly different views",
            "Describe illusions as the brain's interpretation, not a broken instrument only",
        ),
    },
    "2.3.2": {
        "slug": "hearing",
        "name": "Hearing",
        "year": "s2",
        "unit_code": "2.3",
        "unit_name": "Senses",
        "order": 29,
        "sections": 7,
        "checkpoints": 6,
        "objectives": (
            "Label outer, middle and inner ear on a schematic",
            "Describe sound as vibration that needs a medium",
            "Link pitch and loudness to simple acoustic ideas",
            "Explain stereo localisation using two ears",
            "Describe hearing aids as tools that help; this app does not store whose ears they are",
            "Describe auditory illusions as interpretation, not a class hearing test",
        ),
    },
    "2.3.3": {
        "slug": "touch",
        "name": "Touch",
        "year": "s2",
        "unit_code": "2.3",
        "unit_name": "Senses",
        "order": 30,
        "sections": 5,
        "checkpoints": 4,
        "objectives": (
            "Name touch receptor types at S2 level (pressure, pain, temperature)",
            "Link receptor density to how well a region can tell two points apart",
            "Describe temperature perception as a receptor idea, not a body ranking",
            "Plan a teacher-approved two-point mapping with consent, not a survey of the class",
        ),
    },
    "2.3.4": {
        "slug": "smell",
        "name": "Smell",
        "year": "s2",
        "unit_code": "2.3",
        "unit_name": "Senses",
        "order": 31,
        "sections": 4,
        "checkpoints": 4,
        "objectives": (
            "Describe smell receptors as detecting a range of airborne chemicals",
            "Categorise smells with public examples, not a private odour list",
            "Explain that context changes what a smell is taken to mean",
            "State that perception can differ without ranking classmates",
        ),
    },
    "2.3.5": {
        "slug": "taste",
        "name": "Taste",
        "year": "s2",
        "unit_code": "2.3",
        "unit_name": "Senses",
        "order": 32,
        "sections": 4,
        "checkpoints": 4,
        "objectives": (
            "Name the five tastes used in this S2 model",
            "Describe taste–smell interaction using a fictional blocked-nose case",
            "Explain colour and context effects on what a food is judged to be",
            "Outline a controlled classroom tasting only with teacher rules and no force",
        ),
    },
    "2.3.6": {
        "slug": "proprioception_balance",
        "name": "Proprioception and Balance",
        "year": "s2",
        "unit_code": "2.3",
        "unit_name": "Senses",
        "order": 33,
        "sections": 5,
        "checkpoints": 4,
        "objectives": (
            "Describe proprioception as sensing body position without looking",
            "Describe balance as keeping the body oriented against a fall",
            "Link semicircular canals to detecting rotation of the head",
            "Explain that canals, vision and proprioception work together",
        ),
    },
    "2.3.7": {
        "slug": "interoception",
        "name": "Interoception",
        "year": "s2",
        "unit_code": "2.3",
        "unit_name": "Senses",
        "order": 34,
        "sections": 4,
        "checkpoints": 4,
        "objectives": (
            "Describe interoception as sensing internal states such as hunger or heartbeat",
            "Explain that the same signal can be interpreted in more than one way",
            "Link interpretation to wellbeing ideas without a mood survey",
            "Signpost that personal distress is for a trusted adult, not this app",
        ),
    },
    "2.3.8": {
        "slug": "nonhuman_senses",
        "name": "Nonhuman Senses",
        "year": "s2",
        "unit_code": "2.3",
        "unit_name": "Senses",
        "order": 35,
        "sections": 7,
        "checkpoints": 6,
        "objectives": (
            "Describe UV or IR sensing as light humans do not see the same way",
            "Describe polarised-light sensing with a public animal example",
            "Describe electromagnetic sensing in some animals as a model, not a superpower quiz",
            "Explain echolocation as using returning sound",
            "Distinguish infrasound and ultrasound from the human hearing band in this model",
            "Link chemical senses and technology (for example a sensor) to the same idea of detecting a signal",
        ),
    },
    "3.1.1": {
        "slug": "force_work_machines",
        "name": "Force, Work and Simple Machines",
        "year": "s3",
        "unit_code": "3.1",
        "unit_name": "Machines",
        "order": 36,
        "sections": 8,
        "checkpoints": 8,
        "objectives": (
            "Describe a force as a vector model of a push or pull",
            "Name simple machine types used in this S3 model (lever, pulley, ramp)",
            "Describe a lever as effort, fulcrum and load",
            "Explain the force–distance trade-off of a simple machine",
            "Calculate work as W = Fd in joules when force and distance are along the same line",
            "Describe a body lever with a fictional case, not a private joint map",
            "State that this lesson does not claim power calculations",
            "Use the schematic to label effort, fulcrum and load",
        ),
    },
    "3.1.2": {
        "slug": "energy",
        "name": "Energy",
        "year": "s3",
        "unit_code": "3.1",
        "unit_name": "Machines",
        "order": 37,
        "sections": 9,
        "checkpoints": 8,
        "objectives": (
            "Name energy forms used in this S3 model",
            "Describe energy as transformed from one form to another",
            "Describe energy as transferred from one store or place to another",
            "Explain that some energy is wasted as less useful forms such as thermal",
            "Read a Sankey-style split of useful and wasted energy",
            "Compare food and appliance energy uses with public data, not a private diary",
            "Link energy sources to impacts without ranking households",
            "State conservation of energy as a model: it is not created or destroyed",
        ),
    },
    "3.1.3": {
        "slug": "electrostatics",
        "name": "Electrostatics",
        "year": "s3",
        "unit_code": "3.1",
        "unit_name": "Machines",
        "order": 38,
        "sections": 6,
        "checkpoints": 6,
        "objectives": (
            "Describe charging by friction or contact in this S3 model",
            "Distinguish two kinds of charge that attract or repel",
            "Describe transfer and induction as ways charge can be rearranged",
            "Explain grounding and insulators as safety and materials ideas",
            "Link charge to a simple atomic model (electrons can move)",
            "Describe sparks and lightning as discharge, with classroom safety",
        ),
    },
    "3.1.4": {
        "slug": "electric_current",
        "name": "Electric Current and Circuits",
        "year": "s3",
        "unit_code": "3.1",
        "unit_name": "Machines",
        "order": 39,
        "sections": 9,
        "checkpoints": 8,
        "objectives": (
            "Describe a complete circuit as a loop that allows current",
            "Describe a series circuit as one path",
            "Describe a parallel circuit as more than one path",
            "Distinguish conventional current from electron flow in this teaching model",
            "Name conductors and insulators with public examples",
            "Describe heating, lighting and magnetic effects of current",
            "Read meters qualitatively; this lesson does not claim V = IR calculations",
            "State electrical safety rules for the classroom, not a home inspection",
        ),
    },
    "3.1.5": {
        "slug": "magnetism",
        "name": "Magnetism and Electromagnetism",
        "year": "s3",
        "unit_code": "3.1",
        "unit_name": "Machines",
        "order": 40,
        "sections": 8,
        "checkpoints": 7,
        "objectives": (
            "Describe magnetic poles that attract or repel",
            "Classify materials as magnetic or not in this S3 model",
            "Describe magnetisation as aligning or making a magnet",
            "Read a schematic field between poles",
            "Describe an electromagnet as a current-made magnet that can be switched",
            "Link Earth, a compass and magnetotaxis as public models, not a pupil ranking",
            "Use field ideas without claiming a stored 'whose magnet is strongest' league",
        ),
    },
    "3.1.6": {
        "slug": "robotics_project",
        "name": "Project: Build a Simple Robot",
        "year": "s3",
        "unit_code": "3.1",
        "unit_name": "Machines",
        "order": 41,
        "sections": 5,
        "checkpoints": 5,
        "objectives": (
            "Write requirements for a classroom robot that another group could test",
            "Choose simple machines that match the requirements",
            "Plan electromagnetism or electronics only with teacher-approved parts",
            "Describe a classroom program as sense–decide–act, not a private code upload",
            "Iterate after a test and present evidence; the physical robot is not auto-graded here",
        ),
    },
    "3.2.1": {
        "slug": "food_environment",
        "name": "Human Nutrition and the Environment",
        "year": "s3",
        "unit_code": "3.2",
        "unit_name": "Living Earth",
        "order": 42,
        "sections": 8,
        "checkpoints": 7,
        "objectives": (
            "Describe greenhouse gases in the atmosphere as a public climate idea",
            "Link climate change to public evidence, not a household interrogation",
            "Describe land use and biodiversity as effects of food systems",
            "Order a food lifecycle from produce to waste with public examples",
            "Describe food waste as a system idea, not a private plate survey",
            "Read a footprint idea from public data, not a live family diary",
            "Outline sustainable choices as public options the class can discuss",
        ),
    },
    "3.2.2": {
        "slug": "ecosystems_cycles",
        "name": "Ecosystems, Matter and Energy",
        "year": "s3",
        "unit_code": "3.2",
        "unit_name": "Living Earth",
        "order": 43,
        "sections": 9,
        "checkpoints": 8,
        "objectives": (
            "Describe an ecosystem as living things and their surroundings in this model",
            "Outline the water cycle with public stages",
            "Outline the carbon cycle with public stages",
            "Name trophic roles: producer, consumer, decomposer",
            "Describe energy and matter flows in a simple web",
            "Read a pyramid or web schematic without ranking classmates as animals",
            "Link photosynthesis and respiration as word-equation ideas at S3",
        ),
    },
    "3.2.3": {
        "slug": "ecosystem_characteristics",
        "name": "Ecosystem Characteristics",
        "year": "s3",
        "unit_code": "3.2",
        "unit_name": "Living Earth",
        "order": 44,
        "sections": 8,
        "checkpoints": 7,
        "objectives": (
            "Critique a simple trophic model as incomplete, not the whole ecosystem",
            "Give abiotic factor examples (light, temperature, water) from public cases",
            "Give biotic factor examples (competition, feeding) from public cases",
            "Describe a classroom measurement of an abiotic factor with teacher rules",
            "Describe activity and thermoregulation as public animal examples",
            "Outline a survey method another group could repeat",
            "State that this page does not replace a field visit",
        ),
    },
    "3.2.4": {
        "slug": "classification_biodiversity",
        "name": "Classification and Biodiversity",
        "year": "s3",
        "unit_code": "3.2",
        "unit_name": "Living Earth",
        "order": 45,
        "sections": 9,
        "checkpoints": 8,
        "objectives": (
            "Describe a species as a grouping idea used in this S3 model",
            "Use grouping features that another pupil could check",
            "Follow a dichotomous key on a public example, not a private collection",
            "Describe taxonomy and Linnaeus as a historical grouping system",
            "State common descent as a scientific model, not a class ranking",
            "Name broad groups used in this lesson",
            "Link biodiversity loss to public evidence and sustainability ideas",
        ),
    },
    "3.2.5": {
        "slug": "ecology_field_project",
        "name": "Project: An Ecological Field Study",
        "year": "s3",
        "unit_code": "3.2",
        "unit_name": "Living Earth",
        "order": 46,
        "sections": 6,
        "checkpoints": 6,
        "objectives": (
            "Write a field question another group could test",
            "Plan risk with the teacher's assessment, not a home-garden photo harvest",
            "Choose a sampling idea such as a quadrat that the teacher approves",
            "Record method and data with units so another group could repeat them",
            "Analyse the pattern with numbers from the table",
            "Present and reflect; the field product is not auto-graded here",
        ),
    },
}

# Classroom IBL support pages (not syllabus module slugs; not in TOPICS).
IBL_PAGES = {
    "s1_lab": {
        "title": "Classroom investigation: a controlled measurement",
        "year": "s1",
        "unit_code": "1.1",
        "unit_name": "Science Lab",
        "template": "eursc_science_ibl_s1_lab.html",
        "related": ("what_is_science", "measurement", "science_lab"),
        "sections": 6,
    },
    "s1_food": {
        "title": "Classroom investigation: a healthy meal",
        "year": "s1",
        "unit_code": "1.2",
        "unit_name": "Food",
        "template": "eursc_science_ibl_s1_food.html",
        "related": (
            "food_formulas",
            "nutrition",
            "cooking_fermentation",
            "healthy_meal_project",
        ),
        "sections": 6,
    },
    "s2_light": {
        "title": "Classroom investigation: light and a simple telescope",
        "year": "s2",
        "unit_code": "2.1",
        "unit_name": "Universe",
        "template": "eursc_science_ibl_s2_light.html",
        "related": ("solar_system", "light_telescopes"),
        "sections": 6,
    },
    "s2_disease": {
        "title": "Classroom investigation: a disease-spread model",
        "year": "s2",
        "unit_code": "2.2",
        "unit_name": "Health",
        "template": "eursc_science_ibl_s2_disease.html",
        "related": ("healthy_living", "infectious_disease"),
        "sections": 6,
    },
    "s3_robot": {
        "title": "Classroom investigation: a simple robot",
        "year": "s3",
        "unit_code": "3.1",
        "unit_name": "Machines",
        "template": "eursc_science_ibl_s3_robot.html",
        "related": (
            "force_work_machines",
            "electric_current",
            "magnetism",
            "robotics_project",
        ),
        "sections": 6,
    },
    "s3_field": {
        "title": "Classroom investigation: an ecological field study",
        "year": "s3",
        "unit_code": "3.2",
        "unit_name": "Living Earth",
        "template": "eursc_science_ibl_s3_field.html",
        "related": (
            "ecosystems_cycles",
            "ecosystem_characteristics",
            "classification_biodiversity",
            "ecology_field_project",
        ),
        "sections": 6,
    },
}

SI_BASE_UNITS = (
    ("metre", "m", "length"),
    ("kilogram", "kg", "mass"),
    ("second", "s", "time"),
    ("ampere", "A", "electric current"),
    ("kelvin", "K", "temperature"),
    ("mole", "mol", "amount of substance"),
    ("candela", "cd", "luminous intensity"),
)

SI_PREFIXES = (
    ("giga", "G", "10^9", 1_000_000_000),
    ("mega", "M", "10^6", 1_000_000),
    ("kilo", "k", "10^3", 1_000),
    ("centi", "c", "10^-2", 0.01),
    ("milli", "m", "10^-3", 0.001),
    ("micro", "µ", "10^-6", 0.000001),
    ("nano", "n", "10^-9", 0.000000001),
)


def ruler_scale(reading_cm, *, span_cm=8, title=None, max_width=360):
    """Analogue centimetre ruler with a pointer at ``reading_cm``."""
    p = PALETTE
    left, right, axis_y = 28, 372, 52
    span = float(span_cm)
    reading = float(reading_cm)

    def x_at(cm):
        return left + (float(cm) / span) * (right - left)

    def body(_ids):
        parts = [
            f'<line x1="{left}" y1="{axis_y}" x2="{right}" y2="{axis_y}" '
            f'stroke="{p["ink"]}" stroke-width="2.5" stroke-linecap="round"/>'
        ]
        for i in range(int(span) + 1):
            x = x_at(i)
            parts.append(
                f'<line x1="{x:.1f}" y1="{axis_y - 18}" x2="{x:.1f}" y2="{axis_y + 18}" '
                f'stroke="{p["ink"]}" stroke-width="2"/>'
            )
            parts.append(shape_label(x, axis_y + 36, str(i)))
            if i < span:
                for tenth in range(1, 10):
                    xt = x_at(i + tenth / 10)
                    tick_h = 11 if tenth == 5 else 6
                    parts.append(
                        f'<line x1="{xt:.1f}" y1="{axis_y - tick_h}" '
                        f'x2="{xt:.1f}" y2="{axis_y + tick_h}" '
                        f'stroke="{p["ink_muted"]}" stroke-width="1"/>'
                    )
        px = x_at(reading)
        parts.append(
            f'<polygon points="{px:.1f},{axis_y - 22} {px - 8:.1f},{axis_y - 40} '
            f'{px + 8:.1f},{axis_y - 40}" fill="{p["measure"]}"/>'
        )
        parts.append(shape_label((left + right) / 2, 108, "cm"))
        return "".join(parts)

    desc = (
        f"A centimetre scale from 0 to {int(span)} with a pointer at {reading} cm."
    )
    return svg(
        400,
        124,
        title=title or "Reading a centimetre scale",
        desc=desc,
        body=body,
        max_width=max_width,
        variant="wide",
    )


def lab_bench(*, title=None, max_width=360):
    """Simple labelled bench: heat, beaker of water, thermometer."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<rect x="24" y="88" width="352" height="14" rx="2" '
                f'fill="{p["ink_line"]}"/>',
                f'<rect x="48" y="58" width="70" height="30" rx="4" '
                f'fill="{p["measure"]}"/>',
                f'<rect x="58" y="48" width="50" height="12" rx="2" '
                f'fill="{p["measure"]}"/>',
                shape_label(83, 118, "A"),
                f'<path d="M150 40 h70 v50 h-70 z" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                f'<path d="M158 58 h54 v24 h-54 z" fill="{p["brand"]}"/>',
                shape_label(185, 118, "B"),
                f'<line x1="268" y1="28" x2="268" y2="86" '
                f'stroke="{p["ink"]}" stroke-width="3" stroke-linecap="round"/>',
                f'<circle cx="268" cy="90" r="10" fill="{p["xp"]}"/>',
                shape_label(268, 118, "C"),
            ]
        )

    return svg(
        400,
        140,
        title=title or "Laboratory bench with three labelled objects",
        desc=(
            "A lab bench. A is a heat source, B is a beaker of liquid, "
            "and C is a thermometer standing in the liquid."
        ),
        body=body,
        max_width=max_width,
        variant="wide",
    )


def particle_states(*, title=None, max_width=360):
    """Three labelled boxes: A solid, B liquid, C gas."""
    p = PALETTE

    def _box(x, packed, title_letter):
        parts = [
            f'<rect x="{x}" y="18" width="110" height="90" rx="6" fill="{p["brand_soft"]}" '
            f'stroke="{p["brand"]}" stroke-width="2"/>'
        ]
        if packed == "solid":
            coords = (
                (x + 28, 40), (x + 52, 40), (x + 76, 40),
                (x + 28, 64), (x + 52, 64), (x + 76, 64),
                (x + 40, 88), (x + 64, 88),
            )
        elif packed == "liquid":
            coords = (
                (x + 30, 48), (x + 55, 42), (x + 78, 52),
                (x + 36, 70), (x + 60, 66), (x + 82, 74), (x + 48, 88),
            )
        else:
            coords = (
                (x + 28, 36), (x + 78, 44), (x + 48, 62),
                (x + 86, 78), (x + 34, 88),
            )
        for cx, cy in coords:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{p["brand"]}"/>')
        parts.append(shape_label(x + 55, 124, title_letter))
        return "".join(parts)

    def body(_ids):
        return _box(24, "solid", "A") + _box(145, "liquid", "B") + _box(266, "gas", "C")

    return svg(
        400,
        140,
        title=title or "Particle arrangements in three states",
        desc="A is a solid with packed particles, B is a liquid, and C is a gas with particles far apart.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def ph_scale(*, title=None, max_width=360):
    """Horizontal pH bar with acid, 7, and alkali labelled."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<rect x="30" y="48" width="120" height="22" rx="4" fill="{p["measure"]}"/>',
                f'<rect x="150" y="48" width="100" height="22" rx="4" fill="{p["brand_soft"]}"/>',
                f'<rect x="250" y="48" width="120" height="22" rx="4" fill="{p["xp"]}"/>',
                f'<line x1="200" y1="40" x2="200" y2="78" stroke="{p["ink"]}" stroke-width="2"/>',
                shape_label(90, 96, "A"),
                shape_label(200, 96, "B"),
                shape_label(310, 96, "C"),
                shape_label(90, 28, "acid"),
                shape_label(200, 28, "pH 7"),
                shape_label(310, 28, "alkali"),
            ]
        )

    return svg(
        400,
        120,
        title=title or "pH scale with acid, neutral and alkali",
        desc="A marks the acid side, B marks pH 7 in the middle, and C marks the alkali side.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def distance_time_graph(*, title=None, max_width=360):
    """Distance–time sketch: A moving, B rest, C moving again."""
    p = PALETTE
    ox, oy = 48, 108
    top, right = 28, 360

    def body(_ids):
        return "".join(
            [
                f'<line x1="{ox}" y1="{oy}" x2="{right}" y2="{oy}" '
                f'stroke="{p["ink"]}" stroke-width="2" stroke-linecap="round"/>',
                f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{top}" '
                f'stroke="{p["ink"]}" stroke-width="2" stroke-linecap="round"/>',
                f'<polyline points="{ox},{oy} 150,48 230,48 330,28" fill="none" '
                f'stroke="{p["brand"]}" stroke-width="3" stroke-linecap="round" '
                f'stroke-linejoin="round"/>',
                shape_label(100, 92, "A"),
                shape_label(190, 68, "B"),
                shape_label(290, 52, "C"),
                shape_label(200, 128, "time"),
                shape_label(22, 68, "d"),
            ]
        )

    return svg(
        400,
        148,
        title=title or "Distance–time graph with three labelled parts",
        desc="A is a sloping line (moving), B is a flat line (rest), and C is a slope again (moving).",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def force_pair(*, title=None, max_width=360):
    """Two boxes pushing: A left-to-right, B right-to-left."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<rect x="70" y="40" width="90" height="50" rx="6" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                f'<rect x="240" y="40" width="90" height="50" rx="6" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                f'<line x1="165" y1="65" x2="228" y2="65" stroke="{p["measure"]}" '
                f'stroke-width="3" marker-end="none"/>',
                f'<polygon points="228,65 214,58 214,72" fill="{p["measure"]}"/>',
                f'<polygon points="172,65 186,58 186,72" fill="{p["xp"]}"/>',
                shape_label(115, 118, "A"),
                shape_label(285, 118, "B"),
            ]
        )

    return svg(
        400,
        140,
        title=title or "Two objects pushing on each other",
        desc="Box A pushes right on box B. Box B pushes left on box A with a matching interaction.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def circulation_boxes(*, title=None, max_width=360):
    """A heart, B lungs, C body tissues — schematic boxes only."""
    p = PALETTE

    def _box(x, letter, caption):
        return "".join(
            [
                f'<rect x="{x}" y="28" width="100" height="64" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                shape_label(x + 50, 64, letter),
                shape_label(x + 50, 114, caption),
            ]
        )

    def body(_ids):
        return _box(28, "A", "heart") + _box(150, "B", "lungs") + _box(272, "C", "body")

    return svg(
        400,
        140,
        title=title or "Circulation schematic with three labelled organs",
        desc="A is the heart, B is the lungs, and C is body tissue. Educational boxes only.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def antagonistic_pair(*, title=None, max_width=360):
    """Bone with muscle A above and muscle B below."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<rect x="60" y="62" width="280" height="14" rx="4" fill="{p["ink_line"]}"/>',
                f'<ellipse cx="160" cy="40" rx="70" ry="18" fill="{p["measure"]}"/>',
                f'<ellipse cx="240" cy="98" rx="70" ry="18" fill="{p["xp"]}"/>',
                shape_label(160, 24, "A"),
                shape_label(240, 128, "B"),
            ]
        )

    return svg(
        400,
        148,
        title=title or "Antagonistic muscles on a bone",
        desc="A is the muscle above the bone. B is the muscle below. They pull in opposite ways.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def organ_labels(*, title=None, max_width=360):
    """Schematic labelled boxes: A ovary, B uterus, C testis. Not a realistic drawing."""
    p = PALETTE

    def _box(x, letter, caption):
        return "".join(
            [
                f'<rect x="{x}" y="24" width="108" height="70" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                shape_label(x + 54, 58, letter),
                shape_label(x + 54, 114, caption),
            ]
        )

    def body(_ids):
        return _box(20, "A", "ovary") + _box(146, "B", "uterus") + _box(272, "C", "testis")

    return svg(
        400,
        140,
        title=title or "Educational labels for reproductive organs",
        desc="A is an ovary, B is a uterus, and C is a testis. Schematic boxes, not a realistic image.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def earth_sun_moon(*, title=None, max_width=360):
    """Schematic: A Sun, B Earth, C Moon."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<circle cx="70" cy="64" r="28" fill="{p["xp"]}"/>',
                shape_label(70, 112, "A"),
                f'<circle cx="200" cy="64" r="16" fill="{p["brand"]}"/>',
                shape_label(200, 112, "B"),
                f'<circle cx="310" cy="48" r="10" fill="{p["ink_muted"]}"/>',
                shape_label(310, 112, "C"),
            ]
        )

    return svg(
        400,
        136,
        title=title or "Sun, Earth and Moon schematic",
        desc="A is the Sun, B is the Earth, and C is the Moon. Sizes are not to scale.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def reflection_rays(*, title=None, max_width=360):
    """A incident ray, B reflected ray, C the mirror line."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<line x1="40" y1="100" x2="360" y2="100" stroke="{p["ink"]}" stroke-width="3"/>',
                f'<line x1="200" y1="100" x2="200" y2="28" stroke="{p["ink_muted"]}" '
                f'stroke-width="1.5" stroke-dasharray="4 4"/>',
                f'<line x1="70" y1="36" x2="200" y2="100" stroke="{p["brand"]}" stroke-width="3"/>',
                f'<polygon points="200,100 186,90 194,86" fill="{p["brand"]}"/>',
                f'<line x1="200" y1="100" x2="330" y2="36" stroke="{p["measure"]}" stroke-width="3"/>',
                f'<polygon points="330,36 316,42 322,50" fill="{p["measure"]}"/>',
                shape_label(100, 52, "A"),
                shape_label(300, 52, "B"),
                shape_label(200, 122, "C"),
            ]
        )

    return svg(
        400,
        140,
        title=title or "Reflection at a mirror",
        desc="A is the incident ray, B is the reflected ray, and C is the mirror surface.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def atom_molecule_boxes(*, title=None, max_width=360):
    """A one atom, B a two-atom molecule, C a mixed jumble."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<rect x="20" y="20" width="110" height="80" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                f'<circle cx="75" cy="60" r="14" fill="{p["brand"]}"/>',
                shape_label(75, 118, "A"),
                f'<rect x="145" y="20" width="110" height="80" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                f'<circle cx="178" cy="60" r="12" fill="{p["brand"]}"/>',
                f'<circle cx="212" cy="60" r="12" fill="{p["measure"]}"/>',
                shape_label(200, 118, "B"),
                f'<rect x="270" y="20" width="110" height="80" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                f'<circle cx="292" cy="42" r="8" fill="{p["brand"]}"/>',
                f'<circle cx="328" cy="50" r="8" fill="{p["xp"]}"/>',
                f'<circle cx="310" cy="78" r="8" fill="{p["measure"]}"/>',
                f'<circle cx="348" cy="80" r="8" fill="{p["brand"]}"/>',
                shape_label(325, 118, "C"),
            ]
        )

    return svg(
        400,
        140,
        title=title or "Atom, molecule and mixed particles",
        desc="A is a single atom, B is two atoms joined as a molecule, and C is a mixed jumble of different particles.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def habit_bars(*, title=None, max_width=360):
    """A sleep, B activity, C screen time as schematic bars."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<rect x="40" y="28" width="70" height="80" rx="6" fill="{p["brand"]}"/>',
                shape_label(75, 128, "A"),
                f'<rect x="165" y="58" width="70" height="50" rx="6" fill="{p["xp"]}"/>',
                shape_label(200, 128, "B"),
                f'<rect x="290" y="88" width="70" height="20" rx="6" fill="{p["measure"]}"/>',
                shape_label(325, 128, "C"),
            ]
        )

    return svg(
        400,
        148,
        title=title or "Sleep, activity and screen-time bars",
        desc="A is a tall sleep bar, B is a medium activity bar, and C is a short screen-time bar. Not a ranking of classmates.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def infection_chain(*, title=None, max_width=360):
    """A source, B route, C new host."""
    p = PALETTE

    def _box(x, letter):
        return "".join(
            [
                f'<rect x="{x}" y="24" width="100" height="64" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                shape_label(x + 50, 112, letter),
            ]
        )

    def body(_ids):
        return "".join(
            [
                _box(20, "A"),
                f'<line x1="120" y1="56" x2="148" y2="56" stroke="{p["ink"]}" stroke-width="3"/>',
                f'<polygon points="148,56 136,50 136,62" fill="{p["ink"]}"/>',
                _box(150, "B"),
                f'<line x1="250" y1="56" x2="278" y2="56" stroke="{p["ink"]}" stroke-width="3"/>',
                f'<polygon points="278,56 266,50 266,62" fill="{p["ink"]}"/>',
                _box(280, "C"),
            ]
        )

    return svg(
        400,
        132,
        title=title or "Chain of infection schematic",
        desc="A is the source, B is the route of transmission, and C is a new host.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def outbreak_bars(*, title=None, max_width=360):
    """A 2 cases, B 4 cases, C 8 cases on three days."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<rect x="50" y="88" width="70" height="20" rx="4" fill="{p["brand"]}"/>',
                shape_label(85, 128, "A"),
                f'<rect x="165" y="68" width="70" height="40" rx="4" fill="{p["xp"]}"/>',
                shape_label(200, 128, "B"),
                f'<rect x="280" y="28" width="70" height="80" rx="4" fill="{p["measure"]}"/>',
                shape_label(315, 128, "C"),
            ]
        )

    return svg(
        400,
        148,
        title=title or "Outbreak cases on three days",
        desc="A is 2 cases, B is 4 cases, and C is 8 cases. A classroom model, not a real outbreak.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def eye_boxes(*, title=None, max_width=360):
    """A lens, B retina, C path toward the brain."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<ellipse cx="90" cy="56" rx="54" ry="40" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                f'<ellipse cx="70" cy="56" rx="10" ry="18" fill="{p["brand"]}"/>',
                shape_label(70, 118, "A"),
                f'<path d="M128 36 Q148 56 128 76" fill="none" stroke="{p["measure"]}" '
                f'stroke-width="3"/>',
                shape_label(148, 118, "B"),
                f'<line x1="150" y1="56" x2="310" y2="56" stroke="{p["ink"]}" stroke-width="3"/>',
                f'<polygon points="310,56 296,50 296,62" fill="{p["ink"]}"/>',
                shape_label(250, 118, "C"),
            ]
        )

    return svg(
        400,
        140,
        title=title or "Eye schematic: lens, retina and path",
        desc="A is the lens, B is the retina, and C is the path of signals toward the brain. Schematic only.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def ear_boxes(*, title=None, max_width=360):
    """A outer ear, B middle ear, C inner ear."""
    p = PALETTE

    def _box(x, letter):
        return "".join(
            [
                f'<rect x="{x}" y="24" width="100" height="64" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                shape_label(x + 50, 112, letter),
            ]
        )

    def body(_ids):
        return "".join(
            [
                _box(20, "A"),
                f'<line x1="120" y1="56" x2="148" y2="56" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(150, "B"),
                f'<line x1="250" y1="56" x2="278" y2="56" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(280, "C"),
            ]
        )

    return svg(
        400,
        132,
        title=title or "Ear schematic: outer, middle and inner",
        desc="A is the outer ear, B is the middle ear, and C is the inner ear. Schematic boxes, not a realistic drawing.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def canal_boxes(*, title=None, max_width=360):
    """Three semicircular-canal loops labelled A B C."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<circle cx="80" cy="56" r="28" fill="none" stroke="{p["brand"]}" stroke-width="4"/>',
                shape_label(80, 112, "A"),
                f'<circle cx="200" cy="56" r="28" fill="none" stroke="{p["xp"]}" stroke-width="4"/>',
                shape_label(200, 112, "B"),
                f'<circle cx="320" cy="56" r="28" fill="none" stroke="{p["measure"]}" stroke-width="4"/>',
                shape_label(320, 112, "C"),
            ]
        )

    return svg(
        400,
        132,
        title=title or "Three semicircular canals",
        desc="A, B and C are three looped canals that detect rotation in different planes. Schematic rings, not a realistic inner ear.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def lever_boxes(*, title=None, max_width=360):
    """A effort, B fulcrum, C load."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<line x1="40" y1="56" x2="360" y2="56" stroke="{p["ink"]}" stroke-width="6"/>',
                f'<polygon points="200,56 184,88 216,88" fill="{p["brand"]}"/>',
                f'<circle cx="70" cy="40" r="12" fill="{p["measure"]}"/>',
                f'<rect x="320" y="28" width="28" height="28" fill="{p["xp"]}"/>',
                shape_label(70, 118, "A"),
                shape_label(200, 118, "B"),
                shape_label(334, 118, "C"),
            ]
        )

    return svg(
        400,
        140,
        title=title or "Lever: effort, fulcrum and load",
        desc="A is the effort, B is the fulcrum, and C is the load. Schematic bar, not a realistic machine.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def sankey_bars(*, title=None, max_width=360):
    """A input, B useful output, C wasted output."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<rect x="24" y="28" width="80" height="72" fill="{p["brand"]}"/>',
                shape_label(64, 118, "A"),
                f'<rect x="160" y="28" width="80" height="44" fill="{p["measure"]}"/>',
                shape_label(200, 118, "B"),
                f'<rect x="296" y="28" width="80" height="24" fill="{p["xp"]}"/>',
                shape_label(336, 118, "C"),
            ]
        )

    return svg(
        400,
        140,
        title=title or "Sankey-style energy split",
        desc="A is the energy input, B is the useful output, and C is the wasted output. Schematic bars, not a measured appliance.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def charge_pair(*, title=None, max_width=360):
    """A one charge, B the other charge."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<circle cx="120" cy="56" r="32" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="3"/>',
                shape_label(120, 118, "A"),
                f'<circle cx="280" cy="56" r="32" fill="{p["brand_soft"]}" '
                f'stroke="{p["measure"]}" stroke-width="3"/>',
                shape_label(280, 118, "B"),
            ]
        )

    return svg(
        400,
        140,
        title=title or "Two kinds of charge",
        desc="A and B are two opposite charges in this schematic. Opposite charges attract; like charges repel.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def circuit_boxes(*, title=None, max_width=360):
    """A cell, B lamp, C switch in a series loop."""
    p = PALETTE

    def _box(x, letter):
        return "".join(
            [
                f'<rect x="{x}" y="24" width="90" height="56" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                shape_label(x + 45, 112, letter),
            ]
        )

    def body(_ids):
        return "".join(
            [
                _box(30, "A"),
                f'<line x1="120" y1="52" x2="148" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(150, "B"),
                f'<line x1="240" y1="52" x2="268" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(270, "C"),
            ]
        )

    return svg(
        400,
        132,
        title=title or "Series circuit boxes: cell, lamp, switch",
        desc="A is the cell, B is the lamp, and C is the switch. Schematic boxes in one path, not a realistic drawing.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def magnet_poles(*, title=None, max_width=360):
    """A north, B south, C field region between them."""
    p = PALETTE

    def body(_ids):
        return "".join(
            [
                f'<rect x="40" y="28" width="70" height="56" rx="6" fill="{p["brand"]}"/>',
                shape_label(75, 118, "A"),
                f'<path d="M120 40 Q200 8 280 40" fill="none" stroke="{p["measure"]}" '
                f'stroke-width="3"/>',
                f'<path d="M120 72 Q200 104 280 72" fill="none" stroke="{p["measure"]}" '
                f'stroke-width="3"/>',
                shape_label(200, 118, "C"),
                f'<rect x="290" y="28" width="70" height="56" rx="6" fill="{p["xp"]}"/>',
                shape_label(325, 118, "B"),
            ]
        )

    return svg(
        400,
        140,
        title=title or "Magnet poles and field region",
        desc="A is one pole, B is the other pole, and C is the field region between them. Schematic only.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def lifecycle_boxes(*, title=None, max_width=360):
    """A produce, B use, C waste."""
    p = PALETTE

    def _box(x, letter):
        return "".join(
            [
                f'<rect x="{x}" y="24" width="90" height="56" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                shape_label(x + 45, 112, letter),
            ]
        )

    def body(_ids):
        return "".join(
            [
                _box(30, "A"),
                f'<line x1="120" y1="52" x2="148" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(150, "B"),
                f'<line x1="240" y1="52" x2="268" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(270, "C"),
            ]
        )

    return svg(
        400,
        132,
        title=title or "Food lifecycle: produce, use, waste",
        desc="A is produce, B is use, and C is waste. Schematic boxes, not a private plate survey.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def trophic_boxes(*, title=None, max_width=360):
    """A producer, B consumer, C decomposer."""
    p = PALETTE

    def _box(x, letter):
        return "".join(
            [
                f'<rect x="{x}" y="24" width="90" height="56" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                shape_label(x + 45, 112, letter),
            ]
        )

    def body(_ids):
        return "".join(
            [
                _box(30, "A"),
                f'<line x1="120" y1="52" x2="148" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(150, "B"),
                f'<line x1="240" y1="52" x2="268" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(270, "C"),
            ]
        )

    return svg(
        400,
        132,
        title=title or "Trophic roles: producer, consumer, decomposer",
        desc="A is a producer, B is a consumer, and C is a decomposer. Schematic only, not a classmate ranking.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def factor_boxes(*, title=None, max_width=360):
    """A abiotic, B biotic, C survey."""
    p = PALETTE

    def _box(x, letter):
        return "".join(
            [
                f'<rect x="{x}" y="24" width="90" height="56" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                shape_label(x + 45, 112, letter),
            ]
        )

    def body(_ids):
        return "".join(
            [
                _box(30, "A"),
                f'<line x1="120" y1="52" x2="148" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(150, "B"),
                f'<line x1="240" y1="52" x2="268" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(270, "C"),
            ]
        )

    return svg(
        400,
        132,
        title=title or "Abiotic, biotic and a survey",
        desc="A is an abiotic factor, B is a biotic factor, and C is a survey step. Schematic only.",
        body=body,
        max_width=max_width,
        variant="wide",
    )


def key_boxes(*, title=None, max_width=360):
    """A first couplet, B second couplet, C named group."""
    p = PALETTE

    def _box(x, letter):
        return "".join(
            [
                f'<rect x="{x}" y="24" width="90" height="56" rx="8" fill="{p["brand_soft"]}" '
                f'stroke="{p["brand"]}" stroke-width="2"/>',
                shape_label(x + 45, 112, letter),
            ]
        )

    def body(_ids):
        return "".join(
            [
                _box(30, "A"),
                f'<line x1="120" y1="52" x2="148" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(150, "B"),
                f'<line x1="240" y1="52" x2="268" y2="52" stroke="{p["ink"]}" stroke-width="3"/>',
                _box(270, "C"),
            ]
        )

    return svg(
        400,
        132,
        title=title or "Dichotomous key: couplet, couplet, group",
        desc="A is the first couplet, B is the second couplet, and C is the named group. Public example, not a private collection.",
        body=body,
        max_width=max_width,
        variant="wide",
    )
