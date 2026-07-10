from pathlib import Path

STYLE_SUMMARY = 'style="cursor:pointer; padding:14px 18px; background:var(--color-surface-2); border-radius:var(--radius); font-weight:600; font-size:1.05rem; margin-bottom:4px;"'
STYLE_DIV = 'style="padding:16px; background:var(--color-surface); border-radius:0 0 var(--radius) var(--radius); margin-bottom:12px;"'
BADGE_ALL = '<span style="font-size:0.65rem; margin-left:8px; background:#e8f4fd; color:#1a6fa8; padding:2px 6px; border-radius:10px;">All Exam Boards</span>'
BADGE_PROB = '<span style="font-size:0.65rem; margin-left:8px; background:#e8f7ec; color:#2d6a35; padding:2px 6px; border-radius:10px;">Problem Solving</span>'
BADGE_HIGHER = '<span style="font-size:0.65rem; margin-left:8px; background:#fef4e8; color:#8a5300; padding:2px 6px; border-radius:10px;">Higher Skill</span>'


def section(i, title, paragraphs, badge=BADGE_ALL, open_first=False):
    open_attr = ' open' if open_first else ''
    body = '\n'.join(f'      <p>{p}</p>' for p in paragraphs)
    return f'''  <details class="lesson-section"{open_attr}>
    <summary {STYLE_SUMMARY}>
      {i}. {title}
      {badge}
    </summary>
    <div {STYLE_DIV}>
{body}
    </div>
  </details>'''


def page(title, sections):
    return f'''{{% extends "base.html" %}}
{{% block title %}}{title} – GCSE Mathematics{{% endblock %}}

{{% block content %}}
<div style="max-width:860px; margin:0 auto; padding:0 16px;">

  <h1>{title}</h1>
  <p style="color:var(--text-muted);">GCSE Mathematics – Foundation and Higher Tier · All Exam Boards</p>
{chr(10).join(sections)}

</div>
{{% endblock %}}
'''

lessons = {
    'gcse_maths_equations_inequalities_lesson.html': page('Equations and Inequalities', [
        section(1, 'Solving One-Step and Two-Step Equations', [
            'An equation says that two expressions are equal. To solve it, use inverse operations to isolate the unknown.',
            'For example, if \\(3x+4=19\\), subtract 4 from both sides and then divide by 3 to get \\(x=5\\).'
        ], open_first=True),
        section(2, 'Equations with Brackets', [
            'When an equation contains brackets, expand the brackets first unless there is a quicker common-factor method.',
            'For example, \\(2(x+5)=18\\) can be solved by dividing by 2 first, or by expanding to \\(2x+10=18\\).'
        ]),
        section(3, 'Unknowns on Both Sides', [
            'If the unknown appears on both sides, collect the unknown terms on one side and the number terms on the other.',
            'For example, \\(5x+2=2x+17\\) becomes \\(3x=15\\), so \\(x=5\\).'
        ]),
        section(4, 'Formulae and Rearranging', [
            'A formula links two or more variables. Rearranging means making a different variable the subject.',
            'Use the same inverse-operation logic as equation solving, but keep letters instead of numbers.'
        ], BADGE_PROB),
        section(5, 'Linear Inequalities', [
            'Inequalities use symbols such as \\(>\\), \\(<\\), \\(\\ge\\), and \\(\\le\\). Solve them like equations, keeping the inequality symbol throughout.',
            'If you multiply or divide both sides by a negative number, reverse the inequality sign.'
        ]),
        section(6, 'Representing Inequalities', [
            'Inequality solutions can be shown on a number line. An open circle means the endpoint is not included, while a filled circle means it is included.',
            'For example, \\(x>3\\) has an open circle at 3 and an arrow to the right.'
        ]),
        section(7, 'Simultaneous Equations', [
            'Simultaneous equations are two equations solved at the same time. Elimination is often used when coefficients can be made equal.',
            'After finding one variable, substitute it back into either original equation to find the other variable.'
        ], BADGE_HIGHER),
        section(8, 'Quadratic Equations', [
            'A quadratic equation contains an \\(x^2\\) term. Many GCSE quadratics can be solved by factorising.',
            'For example, \\(x^2+5x+6=0\\) factorises to \\((x+2)(x+3)=0\\), so \\(x=-2\\) or \\(x=-3\\).'
        ], BADGE_HIGHER),
    ]),
    'gcse_maths_sequences_lesson.html': page('Sequences', [
        section(1, 'What Is a Sequence?', [
            'A sequence is an ordered list of numbers or terms. Each term has a position number.',
            'The first term is the term in position 1, the second term is in position 2, and so on.'
        ], open_first=True),
        section(2, 'Term-to-Term Rules', [
            'A term-to-term rule tells you how to get from one term to the next. Common rules include adding, subtracting, multiplying, or dividing.',
            'For example, the sequence 4, 7, 10, 13 has the term-to-term rule “add 3”.'
        ]),
        section(3, 'Linear Sequences', [
            'A linear sequence has a constant difference between consecutive terms. Its nth term has the form \\(an+b\\).',
            'The coefficient of \\(n\\) is the common difference.'
        ]),
        section(4, 'Finding the nth Term', [
            'To find the nth term of a linear sequence, first identify the common difference. Then compare the sequence with the matching times table.',
            'For example, 5, 8, 11, 14 has common difference 3, so start with \\(3n\\). Since \\(3n\\) gives 3, 6, 9, 12, add 2 to get \\(3n+2\\).'
        ]),
        section(5, 'Using the nth Term', [
            'Once you know the nth term, substitute the position number to find any term in the sequence.',
            'If the nth term is \\(4n-1\\), the 10th term is \\(4(10)-1=39\\).'
        ]),
        section(6, 'Checking Whether a Number Is in a Sequence', [
            'To check whether a value is in a sequence, set the nth term equal to that value and solve for \\(n\\).',
            'If \\(n\\) is a positive whole number, the value is in the sequence.'
        ], BADGE_PROB),
        section(7, 'Quadratic Sequences', [
            'A quadratic sequence has constant second differences. Its nth term includes an \\(n^2\\) term.',
            'The coefficient of \\(n^2\\) is half the constant second difference.'
        ], BADGE_HIGHER),
        section(8, 'Special Sequences', [
            'GCSE questions may include square numbers, cube numbers, triangular numbers, powers of 2, and Fibonacci-type sequences.',
            'Recognising these patterns can make non-linear sequence questions much quicker.'
        ], BADGE_HIGHER),
    ]),
    'gcse_maths_transformations_lesson.html': page('Transformations', [
        section(1, 'What Is a Transformation?', [
            'A transformation changes the position, size, or orientation of a shape. GCSE transformations include translation, reflection, rotation, and enlargement.',
            'The original shape is called the object. The transformed shape is called the image.'
        ], open_first=True),
        section(2, 'Translations', [
            'A translation moves every point by the same vector. The shape does not change size or orientation.',
            'For example, the vector \\(\\begin{pmatrix}3\\\\-2\\end{pmatrix}\\) means move 3 right and 2 down.'
        ]),
        section(3, 'Reflections', [
            'A reflection flips a shape in a mirror line. The image is the same distance from the mirror line as the object.',
            'Common mirror lines include \\(x=0\\), \\(y=0\\), \\(x=a\\), \\(y=a\\), and sometimes \\(y=x\\).'
        ]),
        section(4, 'Rotations', [
            'A rotation turns a shape around a centre of rotation. You must state the angle, direction, and centre.',
            'Common GCSE rotations are 90°, 180°, and 270° clockwise or anticlockwise.'
        ]),
        section(5, 'Enlargements', [
            'An enlargement changes the size of a shape by a scale factor from a centre of enlargement.',
            'A scale factor greater than 1 makes the image larger. A scale factor between 0 and 1 makes it smaller.'
        ]),
        section(6, 'Negative Scale Factors', [
            'A negative scale factor enlarges the shape through the centre of enlargement and places the image on the opposite side.',
            'Negative enlargements are usually Higher Tier questions and require careful counting from the centre.'
        ], BADGE_HIGHER),
        section(7, 'Describing Transformations', [
            'When describing a transformation, include all necessary information. For a reflection, give the mirror line. For a rotation, give the centre, angle, and direction.',
            'For an enlargement, give the centre and scale factor. For a translation, give the vector.'
        ], BADGE_PROB),
        section(8, 'Combined Transformations', [
            'A combined transformation applies more than one transformation in order. The order can matter, especially for rotations and translations.',
            'Work one transformation at a time and label intermediate images if needed.'
        ], BADGE_HIGHER),
    ]),
}

for filename, html in lessons.items():
    Path('/home/ubuntu/' + filename).write_text(html, encoding='utf-8')

print('Batch 2 lesson templates written.')
