# topics_data.py

TOPIC_CONTENT = {
    ('gcse', 'physics', 'forces'): {
        'title': 'GCSE Physics — Forces',
        'summary': (
            "Newton's Second Law states that the resultant force on an object equals "
            "its mass multiplied by its acceleration."
        ),
        'formulae': [
            r'F = ma',
            r'F_{\text{net}} = F_{\text{applied}} - F_{\text{friction}}',
        ],
        'tips': [
            "Always identify the resultant (net) force before applying F = ma.",
            "Check units: force in Newtons (N), mass in kg, acceleration in m/s².",
            "In multi-step problems, find the net force first, then apply Newton's Second Law.",
        ],
        'generate_url': '/?level=gcse&subject=physics&topic=forces',
    },

    ('gcse', 'maths', 'algebra'): {
        'title': 'GCSE Maths — Algebra',
        'summary': (
            "Algebra involves solving equations by isolating the unknown variable "
            "using inverse operations."
        ),
        'formulae': [
            r'ax + b = c \Rightarrow x = \frac{c - b}{a}',
            r'x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}',
        ],
        'tips': [
            "For linear equations, use inverse operations to isolate x.",
            "Always check your answer by substituting back into the original equation.",
            "For quadratics, try factorising first — use the formula only if needed.",
        ],
        'generate_url': '/?level=gcse&subject=maths&topic=algebra',
    },

    ('gcse', 'maths', 'simultaneous_equations'): {
        'title': 'GCSE Maths — Simultaneous Equations',
        'summary': (
            "Solve two linear equations at once using elimination or substitution. "
            "Find the values of x and y that satisfy both equations — the point where two lines cross."
        ),
        'key_ideas': [
            "A simultaneous solution is one pair of values that makes both equations true at the same time.",
            "Elimination is usually quickest when the coefficients of one variable already match, or can be made to match by multiplying one equation.",
            "Substitution is useful when one equation already says something like y = 2x + 1 or x = 3y - 4.",
        ],
        'method_sections': [
            {
                'title': 'Elimination — step by step',
                'steps': [
                    r'Label the equations (1) and (2). Check whether the \(x\)-terms or \(y\)-terms already match, or are opposites (e.g. \(+2y\) and \(-2y\)).',
                    r'If they do not match, multiply one or both equations so that one variable has the same coefficient in both (e.g. multiply (1) by 2 so both have \(4x\)).',
                    r'Add the equations if the matching terms have opposite signs (e.g. \(+3y\) and \(-3y\)). Subtract if they have the same sign.',
                    r'This removes one variable. Solve the remaining equation to find the first unknown.',
                    r'Substitute that value back into either original equation to find the second unknown.',
                    r'Write the answer as \(x = \ldots,\; y = \ldots\) and check in both originals.',
                ],
            },
            {
                'title': 'Substitution — step by step',
                'steps': [
                    r'Pick the equation where one variable is already isolated (e.g. \(y = 2x + 1\)) or rearrange one equation to make that easy.',
                    r'Replace that variable in the <em>other</em> equation with the expression. You now have one equation in one unknown.',
                    r'Solve for that unknown.',
                    r'Substitute back into the rearranged equation (not necessarily the harder one) to find the second value.',
                    r'Check both values satisfy both original equations.',
                ],
            },
        ],
        'method_mcq': {
            'question': r'For \(x + y = 10\) and \(x - y = 4\), which operation removes \(x\) in one step?',
            'options': [
                {'letter': 'A', 'text': r'Add the equations'},
                {'letter': 'B', 'text': r'Subtract the second from the first'},
                {'letter': 'C', 'text': r'Multiply the first equation by 2'},
                {'letter': 'D', 'text': r'Divide both equations by 2'},
            ],
            'correct': 'A',
            'hint': r'Adding gives \(2x = 14\), so \(x = 7\). Then substitute to find \(y\).',
        },
        'formulae': [
            r'\text{Elimination: add or subtract equations to remove } x \text{ or } y',
            r'\text{Substitution: replace one variable using the other equation}',
        ],
        'worked_examples': [
            {
                'title': 'Example: elimination',
                'question': r'Solve \(2x + y = 11\) and \(x + y = 7\).',
                'working': (
                    r'Subtract the second equation from the first:<br>'
                    r'\((2x + y) - (x + y) = 11 - 7\), so \(x = 4\).<br>'
                    r'Substitute into \(x + y = 7\): \(4 + y = 7\), so \(y = 3\).<br>'
                    r'<strong>Solution: \(x = 4,\; y = 3\)</strong>.'
                ),
            },
        ],
        'tips': [
            "Check if one variable already has the same (or opposite) coefficient — then eliminate.",
            "If y = … is given, substitute straight into the second equation.",
            "Always find both x and y unless the question asks for only one.",
            "Check your answer in both original equations.",
        ],
        'generate_url': '/?level=gcse&subject=maths&topic=simultaneous_equations',
    },

    ('gcse', 'maths', 'completing_the_square'): {
        'title': 'GCSE Maths — Completing the Square',
        'summary': (
            "Rewrite quadratics as (x + p)² + k to solve equations, find turning points, "
            "and sketch parabolas. A key Higher-tier algebra skill."
        ),
        'key_ideas': [
            "Completing the square rewrites a quadratic to make the square part visible. This is helpful because a square is always zero or positive.",
            r"For \(x^2 + bx + c\), halve the coefficient of \(x\). That half becomes the number inside the bracket.",
            "The completed form also shows the turning point of the graph without needing to draw it.",
        ],
        'method_sections': [
            {
                'title': r'How to complete the square for \(x^2 + bx + c\)',
                'steps': [
                    r'Write down half of the coefficient of \(x\). Call this number \(p\). For \(x^2 + 6x + 4\), half of 6 is \(p = 3\).',
                    r'Write \((x + p)^2\) and expand it in your head: \((x + p)^2 = x^2 + 2px + p^2\). So \((x + 3)^2 = x^2 + 6x + 9\).',
                    r'Compare the constant you get from expanding (\(p^2\)) with the constant in the original (\(c\)). Here you have \(+9\) but need \(+4\), so you are \(5\) too high.',
                    r'Adjust: subtract the extra amount. \(x^2 + 6x + 4 = (x + 3)^2 - 5\). In general: \(x^2 + bx + c = (x + p)^2 + (c - p^2)\) where \(p = \dfrac{b}{2}\).',
                    r'If the \(x^2\) coefficient is not 1 (e.g. \(2x^2 + \ldots\)), factor 2 out of the \(x\)-terms first, complete the square inside the bracket, then multiply back.',
                ],
            },
            {
                'title': 'How to solve a quadratic by completing the square',
                'steps': [
                    r'Rearrange so the squared part and \(x\)-terms are on one side and the number is on the other (e.g. \(x^2 + 6x = 5\)).',
                    r'Complete the square on the left-hand side, remembering to add the same adjustment to the right-hand side.',
                    r'Write the left as \((x + p)^2 = \text{number}\).',
                    r'Take the square root of both sides — do not forget \(\pm\): \(x + p = \pm\sqrt{\text{number}}\).',
                    r'Solve for \(x\). If the right-hand side is negative after rearranging, there are no real solutions.',
                ],
            },
            {
                'title': r'How to read the turning point from \((x + p)^2 + k\)',
                'steps': [
                    r'A square \((x + p)^2\) is never negative: it is smallest when \(x + p = 0\), i.e. when \(x = -p\).',
                    r'At that \(x\)-value, the square equals 0, so \(y = k\). The turning point is \((-p,\; k)\).',
                    r'For \(y = (x + 3)^2 - 5\): minimum at \(x = -3\), \(y = -5\), so turning point \((-3,\; -5)\).',
                    r'If the \(x^2\) coefficient is negative, the parabola opens downward and \((-p,\; k)\) is a maximum instead.',
                ],
            },
        ],
        'method_mcq': {
            'question': r'Write \(x^2 + 6x + 4\) in completed-square form.',
            'options': [
                {'letter': 'A', 'text': r'\((x + 3)^2 + 5\)'},
                {'letter': 'B', 'text': r'\((x + 3)^2 - 5\)'},
                {'letter': 'C', 'text': r'\((x + 6)^2 - 32\)'},
                {'letter': 'D', 'text': r'\((x + 3)^2 + 9\)'},
            ],
            'correct': 'B',
            'hint': r'Half of 6 is 3. \((x+3)^2 = x^2 + 6x + 9\), but you need \(+4\), so subtract 5.',
        },
        'formulae': [
            r'x^2 + bx + c \;\Rightarrow\; \left(x + \frac{b}{2}\right)^2 + \left(c - \frac{b^2}{4}\right)',
            r'(x + p)^2 + k \text{ has minimum } y = k \text{ at } x = -p \text{ (when coefficient of } x^2 \text{ is positive)}',
        ],
        'worked_examples': [
            {
                'title': 'Example: rewrite a quadratic',
                'question': r'Complete the square for \(x^2 + 6x + 4\).',
                'working': (
                    r'Half of 6 is 3, so start with \((x + 3)^2\).<br>'
                    r'\((x + 3)^2 = x^2 + 6x + 9\).<br>'
                    r'We need \(+4\), not \(+9\), so subtract 5:<br>'
                    r'<strong>\(x^2 + 6x + 4 = (x + 3)^2 - 5\)</strong>.'
                ),
            },
        ],
        'tips': [
            "Halve the coefficient of x — that is p.",
            "Subtract p² from the constant term to get k.",
            "To solve, move the number to the other side before completing the square.",
            "The constant k in (x + p)² + k is the turning-point y-value.",
        ],
        'generate_url': '/?level=gcse&subject=maths&topic=completing_the_square',
    },

    ('gcse', 'maths', 'quadratic_simultaneous_equations'): {
        'title': 'GCSE Maths — Quadratic Simultaneous Equations',
        'summary': (
            "Solve a linear equation and a quadratic (usually a parabola and a straight line) "
            "together. Substitute the line into the curve, factorise, then find both (x, y) pairs."
        ),
        'key_ideas': [
            r"A simultaneous solution is a pair \((x, y)\) that satisfies both equations — on a graph, it is where the line meets the parabola.",
            r"One equation is usually linear (\(y = ax + b\)) and the other quadratic (\(y = x^2\) or similar). Substitution is the standard method.",
            r"Substituting gives one quadratic equation in \(x\). You often get two \(x\)-values, so two solution points \((x, y)\).",
            r"Each solution point must work in <em>both</em> equations. Check by substituting your \(x\) and \(y\) back in.",
        ],
        'method_sections': [
            {
                'title': 'How to solve — substitution step by step',
                'steps': [
                    r'Label the equations, e.g. \(y = x^2\) as (1) and \(y = x + 2\) as (2).',
                    r'Both equations equal \(y\), so set the right-hand sides equal: \(x^2 = x + 2\). (Substitute the <em>linear</em> equation into the <em>quadratic</em>.)',
                    r'Rearrange to make one side zero: \(x^2 - x - 2 = 0\).',
                    r'Solve the quadratic — factorise if possible, or use the quadratic formula.',
                    r'You get two \(x\)-values (usually). For each \(x\), find \(y\) by substituting into the <em>easier</em> equation (often the line).',
                    r'Write both solution pairs: e.g. \((2, 4)\) and \((-1, 1)\). Check each pair in both originals.',
                ],
            },
            {
                'title': r'How to find \(y\) once you know \(x\)',
                'steps': [
                    r'After factorising, you might have \(x = 2\) or \(x = -1\).',
                    r'Use the line \(y = x + 2\) (simpler than squaring): when \(x = 2\), \(y = 4\); when \(x = -1\), \(y = 1\).',
                    r'You could also use \(y = x^2\) — you must get the same \(y\) each time. If not, recheck your \(x\)-values.',
                    r'Present answers as coordinate pairs \((x, y)\), not just separate lists of \(x\) and \(y\) values.',
                ],
            },
            {
                'title': 'How many solutions are there?',
                'steps': [
                    r'On a graph, count where the line crosses the parabola: <strong>0</strong>, <strong>1</strong> (tangent), or <strong>2</strong> intersections.',
                    r'Algebraically, after rearranging you get a quadratic in \(x\). Two distinct real roots → two solution pairs.',
                    r'If the quadratic has equal roots (discriminant \(= 0\)), the line is a tangent → one solution.',
                    r'If there are no real roots (discriminant \(< 0\)), the line does not meet the curve → no solutions.',
                ],
            },
        ],
        'method_mcq': {
            'question': r'Solve \(y = x^2\) and \(y = x + 2\). After substitution, which quadratic in \(x\) do you get (equal to 0)?',
            'options': [
                {'letter': 'A', 'text': r'\(x^2 + x - 2 = 0\)'},
                {'letter': 'B', 'text': r'\(x^2 - x - 2 = 0\)'},
                {'letter': 'C', 'text': r'\(x^2 + x + 2 = 0\)'},
                {'letter': 'D', 'text': r'\(2x^2 - x - 2 = 0\)'},
            ],
            'correct': 'B',
            'hint': r'Set \(x^2 = x + 2\), then move all terms to one side: \(x^2 - x - 2 = 0\).',
        },
        'formulae': [
            r'y = x^2 \text{ and } y = ax + b \Rightarrow x^2 = ax + b',
            r'\text{Rearrange: } x^2 - ax - b = 0 \text{ then factorise or use the formula}',
        ],
        'worked_examples': [
            {
                'title': 'Example: parabola and straight line',
                'question': r'Solve \(y = x^2\) and \(y = x + 2\).',
                'working': (
                    r'Substitute the line into the parabola: \(x^2 = x + 2\).<br>'
                    r'Rearrange: \(x^2 - x - 2 = 0\).<br>'
                    r'Factorise: \((x - 2)(x + 1) = 0\), so \(x = 2\) or \(x = -1\).<br>'
                    r'When \(x = 2\): \(y = 2 + 2 = 4\). When \(x = -1\): \(y = -1 + 2 = 1\).<br>'
                    r'<strong>Solutions: \((2, 4)\) and \((-1, 1)\)</strong>.'
                ),
            },
        ],
        'tips': [
            "Substitute the linear equation into the quadratic — you get one equation in x.",
            "You usually get two x-values and two solution points (x, y).",
            "Find y by substituting each x back into the easier equation (often the line).",
            "On a graph, solutions are where the line crosses the parabola.",
        ],
        'generate_url': '/?level=gcse&subject=maths&topic=quadratic_simultaneous_equations',
    },

    ('gcse', 'maths', 'graphical_simultaneous_equations'): {
        'title': 'GCSE Maths — Graphical Simultaneous Equations',
        'summary': (
            "Solve or interpret simultaneous equations using graphs: where two lines cross, "
            "where a line meets a parabola, and when there is no solution (parallel lines)."
        ),
        'key_ideas': [
            "A graph shows all the points that satisfy an equation. A crossing point satisfies both equations, so it is the simultaneous solution.",
            "Two straight lines can cross once, be parallel with no solution, or lie on top of each other with infinitely many solutions.",
            "A straight line and a quadratic curve can meet twice, once, or not at all depending on the shape and position of the graphs.",
        ],
        'method_sections': [
            {
                'title': 'How to find a solution from a graph',
                'steps': [
                    r'Draw or use the given graphs of both equations on the same axes, with the same scale on \(x\) and \(y\).',
                    r'Find where the graphs cross. Each crossing is one simultaneous solution.',
                    r'Read the \(x\)-coordinate first (across), then the \(y\)-coordinate (up). Write as \((x,\; y)\).',
                    r'If asked for \(x\) and \(y\) separately, split the coordinates: solution \(x = \ldots,\; y = \ldots\).',
                    r'Check your reading by confirming the point lies on both lines or curves.',
                ],
            },
            {
                'title': 'How to decide how many solutions there are',
                'steps': [
                    r'Two straight lines: if they have the same gradient but different intercepts, they are parallel → <strong>0</strong> solutions.',
                    r'Two straight lines with different gradients cross once → <strong>1</strong> solution.',
                    r'If one line lies exactly on top of the other, every point on the line works → <strong>infinitely many</strong> solutions.',
                    r'A line and a parabola: count the crossing points — <strong>0</strong>, <strong>1</strong> (tangent), or <strong>2</strong> intersections.',
                    r'Algebra and graphs should agree: two crossings on the graph means two \((x,\; y)\) pairs algebraically.',
                ],
            },
        ],
        'method_mcq': {
            'question': r'Two straight lines have the same gradient but different \(y\)-intercepts. How many simultaneous solutions are there?',
            'options': [
                {'letter': 'A', 'text': r'0'},
                {'letter': 'B', 'text': r'1'},
                {'letter': 'C', 'text': r'2'},
                {'letter': 'D', 'text': r'Infinitely many'},
            ],
            'correct': 'A',
            'hint': r'Same gradient means the lines are parallel and never meet.',
        },
        'formulae': [
            r'\text{Intersection point } (x, y) \text{ satisfies both equations}',
            r'\text{Parallel lines (same gradient)} \Rightarrow \text{no solution}',
        ],
        'worked_examples': [
            {
                'title': 'Example: read an intersection',
                'question': r'Two graphs cross at \((2, 5)\). What is the solution of the simultaneous equations?',
                'working': (
                    r'The crossing point gives the values that make both equations true.<br>'
                    r'Read coordinates as \(x\) first, then \(y\).<br>'
                    r'<strong>Solution: \(x = 2,\; y = 5\)</strong>.'
                ),
            },
        ],
        'tips': [
            "Read the crossing point carefully — x first, then y.",
            "Two crossings of a line and y = x² mean two solution pairs.",
            "If lines are parallel on the graph, there is no simultaneous solution.",
            "Check your algebraic answer lies on both graphs.",
        ],
        'generate_url': '/?level=gcse&subject=maths&topic=graphical_simultaneous_equations',
    },

    ('gcse', 'maths', 'changing_the_subject'): {
        'title': 'GCSE Maths — Changing the Subject',
        'summary': (
            "Rearrange formulae so a chosen letter stands alone on one side. "
            "Use the same balance rules as solving equations — undo operations in reverse order."
        ),
        'key_ideas': [
            "Changing the subject means making a different letter the main variable by getting it on its own.",
            "Whatever operation is done to the subject, undo it using inverse operations on both sides.",
            "If the subject appears inside a bracket, denominator, square, or square root, clear those structures step by step rather than trying to move everything at once.",
        ],
        'method_sections': [
            {
                'title': 'How to rearrange a formula — step by step',
                'steps': [
                    r'<strong>Identify the subject.</strong> Decide which letter should end up alone on one side. '
                    r'<em>Example:</em> “Make \(x\) the subject of \(y = 3x + 5\)” → the subject we want is \(x\).',
                    r'<strong>Spot what is done to the subject.</strong> Read the formula and list the operations in order. '
                    r'<em>Example:</em> in \(y = 3x + 5\), the \(x\) is multiplied by 3, then 5 is added.',
                    r'<strong>Undo in reverse order.</strong> Start with the last operation that was done. '
                    r'<em>Example:</em> because 5 was added last, subtract 5 first: \(y - 5 = 3x\). Then undo the multiply by 3: divide both sides by 3.',
                    r'<strong>Do the same to both sides.</strong> Every step must keep the formula balanced. '
                    r'<em>Example:</em> subtract 5 from <em>both</em> sides to get \(y - 5 = 3x\), not just from one side.',
                    r'<strong>Write the final answer.</strong> Put the new subject on the left. '
                    r'<em>Example:</em> \(x = \dfrac{y - 5}{3}\).',
                ],
            },
            {
                'title': 'How to deal with squares, roots, and fractions',
                'steps': [
                    r'<strong>Fractions:</strong> if the subject is in a denominator, multiply both sides by that denominator first. '
                    r'<em>Example:</em> \(v = \dfrac{d}{t}\) → multiply by \(t\): \(vt = d\).',
                    r'<strong>Squares:</strong> divide to isolate the squared term, then square-root both sides. '
                    r'<em>Example:</em> \(A = \pi r^2\) → divide by \(\pi\): \(\dfrac{A}{\pi} = r^2\) → square root: \(r = \sqrt{\dfrac{A}{\pi}}\).',
                    r'<strong>Square roots:</strong> square both sides to remove the root. '
                    r'<em>Example:</em> \(d = \sqrt{x}\) → square both sides: \(d^2 = x\).',
                    r'<strong>Subject on both sides:</strong> collect subject terms on one side, factorise, then divide. '
                    r'<em>Example:</em> \(y = 2x + 3x + 4\) → \(y - 4 = 5x\) → \(x = \dfrac{y - 4}{5}\).',
                ],
            },
        ],
        'method_mcq': {
            'question': r'Make \(x\) the subject of \(y = 3x + 5\).',
            'options': [
                {'letter': 'A', 'text': r'\(x = 3y + 5\)'},
                {'letter': 'B', 'text': r'\(x = \dfrac{y - 5}{3}\)'},
                {'letter': 'C', 'text': r'\(x = \dfrac{y + 5}{3}\)'},
                {'letter': 'D', 'text': r'\(x = y - 5\)'},
            ],
            'correct': 'B',
            'hint': r'Subtract 5 from both sides, then divide by 3.',
        },
        'formulae': [
            r'y = mx + c \Rightarrow x = \dfrac{y - c}{m}',
            r'A = \pi r^2 \Rightarrow r = \sqrt{\dfrac{A}{\pi}}',
        ],
        'worked_examples': [
            {
                'title': 'Example: make x the subject',
                'question': r'Make \(x\) the subject of \(y = 3x + 5\).',
                'working': (
                    r'Subtract 5 from both sides: \(y - 5 = 3x\).<br>'
                    r'Divide both sides by 3:<br>'
                    r'<strong>\(x = \dfrac{y - 5}{3}\)</strong>.'
                ),
            },
        ],
        'tips': [
            "Identify what is 'done to' the subject — undo it on both sides.",
            "For y = mx + c, subtract c before dividing by m.",
            "With squares, divide first then take the square root.",
            "With fractions, multiply by the denominator to clear it.",
        ],
        'generate_url': '/?level=gcse&subject=maths&topic=changing_the_subject',
    },

    ('gcse', 'maths', 'functions'): {
        'title': 'GCSE Maths — Functions',
        'summary': (
            "Use function notation f(x): substitute inputs, find outputs, compose functions "
            "f(g(x)), and find simple inverse functions."
        ),
        'key_ideas': [
            r"A function is a rule that takes an input \(x\) and gives one output. \(f(x)\) means 'apply the rule \(f\) to \(x\)'.",
            r"\(f(3)\) is the output when the input is 3 — it is not 'f times 3'.",
            r"A composite function \(f(g(x))\) means: work out \(g(x)\) first, then apply \(f\) to that result.",
            r"The inverse function \(f^{-1}\) undoes \(f\): if \(f(2) = 7\) then \(f^{-1}(7) = 2\).",
        ],
        'method_sections': [
            {
                'title': r'How to evaluate \(f(x)\)',
                'steps': [
                    r'Read the rule for \(f\), e.g. \(f(x) = 2x + 3\).',
                    r'Replace every \(x\) in the rule with the input number (use brackets if the input is negative).',
                    r'Calculate step by step. For \(f(4)\): \(f(4) = 2(4) + 3 = 11\).',
                    r'The result is the output. You can also solve \(f(x) = k\) by setting the rule equal to \(k\) and solving for \(x\).',
                ],
            },
            {
                'title': 'How to work out a composite function',
                'steps': [
                    r'For \(f(g(x))\), always start with the <em>inner</em> function \(g\). Write down \(g(x)\) in full.',
                    r'Substitute that entire expression into \(f\) in place of \(x\).',
                    r'Simplify. Example: \(f(x) = 2x + 1\), \(g(x) = x + 3\). Then \(g(2) = 5\), so \(f(g(2)) = f(5) = 11\).',
                    r'For \(g(f(x))\), the order reverses — apply \(f\) first, then \(g\). Order matters.',
                ],
            },
            {
                'title': 'How to find an inverse function',
                'steps': [
                    r'Write \(y = f(x)\) using the rule (e.g. \(y = 3x - 2\)).',
                    r'Swap \(x\) and \(y\) so the output becomes the input: \(x = 3y - 2\).',
                    r'Rearrange to make \(y\) the subject — this new \(y\) is \(f^{-1}(x)\).',
                    r'Check: \(f\) and \(f^{-1}\) should undo each other (e.g. \(f(4) = 10\) and \(f^{-1}(10) = 4\)).',
                ],
            },
        ],
        'method_mcq': {
            'question': r'If \(f(x) = 3x - 2\), what is \(f(5)\)?',
            'options': [
                {'letter': 'A', 'text': r'7'},
                {'letter': 'B', 'text': r'11'},
                {'letter': 'C', 'text': r'13'},
                {'letter': 'D', 'text': r'15'},
            ],
            'correct': 'C',
            'hint': r'Substitute \(x = 5\): \(3(5) - 2 = 13\).',
        },
        'worked_examples': [
            {
                'title': 'Example: composite function',
                'question': r'\(f(x) = 2x + 1\) and \(g(x) = x + 3\). Find \(f(g(2))\).',
                'working': (
                    r'Work out the inner function first: \(g(2) = 2 + 3 = 5\).<br>'
                    r'Apply \(f\) to that result: \(f(5) = 2(5) + 1 = 11\).<br>'
                    r'<strong>\(f(g(2)) = 11\)</strong>.'
                ),
            },
        ],
        'formulae': [
            r'f(a) \text{ means substitute } x = a \text{ into the rule}',
            r'f(g(x)) \text{ means apply } g \text{ first, then } f',
        ],
        'tips': [
            "f(3) is an output, not ‘f times 3’.",
            "For f(g(x)), always work out g(x) before applying f.",
            "The inverse f⁻¹ undoes f — swap y and x, then rearrange.",
            "Check invalid inputs (e.g. x = 0 for 1/x).",
        ],
        'generate_url': '/?level=gcse&subject=maths&topic=functions',
    },

    ('gcse', 'maths', 'algebraic_fractions'): {
        'title': 'GCSE Maths — Algebraic Fractions',
        'summary': (
            "Simplify, add, subtract, multiply and divide fractions that contain algebra. "
            "Factorise and cancel common factors, then use common denominators."
        ),
        'key_ideas': [
            "Algebraic fractions behave like number fractions: you still need common denominators for addition and subtraction.",
            "Before cancelling, factorise fully. You can only cancel a whole factor, not part of a sum.",
            r"Some values of \(x\) may be excluded because they make a denominator zero, even if the expression later simplifies.",
        ],
        'method_sections': [
            {
                'title': 'How to simplify by cancelling',
                'steps': [
                    r'Factorise the numerator and denominator fully (look for common factors, difference of two squares, or quadratics).',
                    r'Identify factors that appear in <em>both</em> top and bottom. You can only cancel whole bracketed factors — never cancel individual terms inside a sum.',
                    r'Cross out the common factor. Write the simplified expression and state any values of \(x\) that would have made the original denominator zero.',
                    r'Example: \(\dfrac{x^2 - 9}{x - 3} = \dfrac{(x-3)(x+3)}{x-3} = x + 3\), with \(x \neq 3\).',
                ],
            },
            {
                'title': 'How to add or subtract algebraic fractions',
                'steps': [
                    r'If the denominators are already the same, add or subtract the numerators and keep the denominator: \(\dfrac{a}{d} \pm \dfrac{b}{d} = \dfrac{a \pm b}{d}\).',
                    r'If denominators differ, find the lowest common denominator (LCD) — often the product of the two denominators, or a factorised form.',
                    r'Convert each fraction to an equivalent fraction with the LCD.',
                    r'Add or subtract the numerators, then simplify the result if possible.',
                ],
            },
            {
                'title': 'How to multiply or divide',
                'steps': [
                    r'<strong>Multiply:</strong> multiply numerators together and denominators together, then cancel common factors before expanding if possible.',
                    r'<strong>Divide:</strong> flip the second fraction (use its reciprocal), then multiply as above.',
                    r'Factorise before multiplying — it is usually easier to cancel first than to expand a large product.',
                ],
            },
        ],
        'method_mcq': {
            'question': r'Simplify \(\dfrac{x^2 - 9}{x - 3}\).',
            'options': [
                {'letter': 'A', 'text': r'\(x - 3\)'},
                {'letter': 'B', 'text': r'\(x + 3\)'},
                {'letter': 'C', 'text': r'\(x^2 + 3\)'},
                {'letter': 'D', 'text': r'\(3\)'},
            ],
            'correct': 'B',
            'hint': r'Factorise \(x^2 - 9 = (x-3)(x+3)\), then cancel the common factor \(x - 3\) (\(x \neq 3\)).',
        },
        'formulae': [
            r'\dfrac{a}{x} + \dfrac{b}{x} = \dfrac{a + b}{x}',
            r'\dfrac{x^2 - c^2}{x - c} = x + c \quad (x \neq c)',
        ],
        'worked_examples': [
            {
                'title': 'Example: factorise before cancelling',
                'question': r'Simplify \(\dfrac{x^2 - 9}{x - 3}\).',
                'working': (
                    r'Factorise the numerator as a difference of two squares:<br>'
                    r'\(x^2 - 9 = (x - 3)(x + 3)\).<br>'
                    r'\(\dfrac{x^2 - 9}{x - 3} = \dfrac{(x - 3)(x + 3)}{x - 3}\).<br>'
                    r'Cancel the common factor \(x - 3\): <strong>\(x + 3\)</strong>, with \(x \neq 3\).'
                ),
            },
        ],
        'tips': [
            "Factorise numerator and denominator before cancelling.",
            "Only cancel factors that appear in both top and bottom.",
            "For adding, find the lowest common denominator.",
            "When solving equations, multiply through by the denominator and check excluded values.",
        ],
        'generate_url': '/?level=gcse&subject=maths&topic=algebraic_fractions',
    },

    ('gcse', 'maths', 'algebraic_proof'): {
        'title': 'GCSE Maths — Algebraic Proof',
        'summary': (
            "Prove results for all integers using algebra: even and odd forms, "
            "consecutive integers, factorising, and counterexamples."
        ),
        'formulae': [
            r'\text{Even: } 2n \qquad \text{Odd: } 2n + 1',
            r'n(n+1) \text{ is always even (consecutive integers)}',
        ],
        'tips': [
            "Let n be any integer — do not pick one number to test.",
            "Expand, factorise, then explain using 2n or 2n+1.",
            "To disprove “always true”, give one counterexample.",
            "End with a clear conclusion: “hence always even”, etc.",
        ],
        'generate_url': '/?level=gcse&subject=maths&topic=algebraic_proof',
    },

    ('gcse', 'cs', 'data_rep'): {
        'title': 'GCSE Computer Science — Fundamentals of Data Representation',
        'summary': (
            "Computers store all data as binary — sequences of 1s and 0s. "
            "Understanding how to convert between binary and denary, and how binary "
            "addition works, is fundamental to GCSE Computer Science."
        ),
        'formulae': [
            r'\text{Place values: } 128, 64, 32, 16, 8, 4, 2, 1',
            r'\text{Max 8-bit value: } 2^8 - 1 = 255',
            r'\text{Overflow occurs when result} > 255',
        ],
        'tips': [
            "Always write out the place value table before converting.",
            "For binary addition, work right to left — 1+1 = 10 in binary.",
            "Overflow happens when your result needs more than 8 bits.",
            "To convert binary to denary, add only the place values with a 1 above them.",
        ],
        'generate_url': '/?level=gcse&subject=cs&topic=data_rep',
    },

    ('myp', 'chemistry', 'energy_changes_and_rates'): {
        'title': 'MYP Chemistry — Energy Changes and Rates',
        'summary': 'Energy changes, calorimetry, bond energies, and factors affecting reaction rates.',
        'formulae': [],
        'tips': [],
        'generate_url': '/?level=myp&subject=chemistry&topic=energy_changes_and_rates',
    },

    ('myp', 'chemistry', 'redox'): {
        'title': 'MYP Chemistry — Redox Reactions',
        'summary': (
            "Redox reactions involve the transfer of electrons. "
            "Oxidation is loss of electrons, and reduction is gain of electrons."
        ),
        'formulae': [
            r'\text{OIL RIG: Oxidation Is Loss, Reduction Is Gain}',
            r'\text{Sum of oxidation numbers} = \text{overall charge of species}',
            r'\text{Free elements always have oxidation number} = 0',
        ],
        'tips': [
            "The oxidising agent accepts electrons and is itself reduced.",
            "The reducing agent donates electrons and is itself oxidised.",
            "Oxygen is usually −2 in compounds, except in peroxides where it is −1.",
            "Hydrogen is usually +1 in compounds, except in metal hydrides where it is −1.",
        ],
        'generate_url': '/?level=myp&subject=chemistry&topic=redox',
    },

    ('alevel', 'physics', 'magnetism'): {
        'title': 'A-Level Physics — Magnetic Fields',
        'summary': (
            "Magnetic fields exert forces on current-carrying conductors and moving charges. "
            "Charged particles can move in circular paths in uniform magnetic fields."
        ),
        'formulae': [
            r'F = BIL\sin\theta',
            r'F = BQv',
            r'r = \frac{mv}{BQ}',
            r'T = \frac{2\pi m}{BQ}',
            r'V_H = \frac{BI}{nQt}',
        ],
        'tips': [
            "F = BIL sinθ is maximum when the conductor is perpendicular to the field.",
            "A magnetic force changes direction but does no work, so speed stays constant.",
            "For circular motion, equate magnetic force and centripetal force: BQv = mv^2/r.",
            "Hall voltage increases when charge carrier density n is smaller.",
            "In a velocity selector, electric and magnetic forces balance to give v = E/B.",
        ],
        'generate_url': '/?level=alevel&subject=physics&topic=magnetism',
    },
}