from pathlib import Path

OUT = Path('/home/ubuntu')


def section(title, badge, body, open_first=False):
    open_attr = ' open' if open_first else ''
    return f'''  <details class="lesson-section"{open_attr}>
    <summary style="cursor:pointer; padding:14px 18px; background:var(--color-surface-2); border-radius:var(--radius); font-weight:600; font-size:1.05rem; margin-bottom:4px;">
      {title}
      <span style="font-size:0.65rem; margin-left:8px; background:{badge[0]}; color:{badge[1]}; padding:2px 6px; border-radius:10px;">{badge[2]}</span>
    </summary>
    <div style="padding:16px; background:var(--color-surface); border-radius:0 0 var(--radius) var(--radius); margin-bottom:12px;">
{body}
    </div>
  </details>\n'''


def lesson(filename, title, sections):
    blue = ('#e8f4fd', '#1a6fa8', 'All Exam Boards')
    content = [f'''{{% extends "base.html" %}}
{{% block title %}}{title} – GCSE Mathematics{{% endblock %}}

{{% block content %}}
<div style="max-width:860px; margin:0 auto; padding:0 16px;">

  <h1>{title}</h1>
  <p style="color:var(--text-muted);">GCSE Mathematics – Foundation and Higher Tier · All Exam Boards</p>
''']
    for i, (heading, badge, body) in enumerate(sections, start=1):
        content.append(section(f'{i}. {heading}', badge or blue, body, i == 1))
    content.append('''
</div>
{% endblock %}
''')
    (OUT / filename).write_text(''.join(content), encoding='utf-8')

blue = ('#e8f4fd', '#1a6fa8', 'All Exam Boards')
orange = ('#fef4e8', '#8a5300', 'Higher Skill')
green = ('#e8f7ec', '#2d6a35', 'Problem Solving')

lesson('gcse_maths_geometry_angles_lesson.html', 'Geometry and Angles', [
('Angle Basics', blue, '''      <p>An <strong>angle</strong> measures a turn and is measured in degrees. A right angle is \(90^\circ\), a straight line is \(180^\circ\), and a full turn is \(360^\circ\).</p>
      <p>Angles at a point add to \(360^\circ\). Angles on a straight line add to \(180^\circ\). Vertically opposite angles are equal.</p>
      <div style="text-align:center;margin:16px 0;"><svg width="420" height="140" viewBox="0 0 420 140" style="background:#f9f8f5; border-radius:8px; max-width:100%;"><line x1="55" y1="90" x2="365" y2="90" stroke="#555" stroke-width="3"/><line x1="210" y1="90" x2="295" y2="35" stroke="#01696f" stroke-width="3"/><path d="M250 90 A40 40 0 0 0 235 58" fill="none" stroke="#a13544" stroke-width="3"/><text x="250" y="72" font-size="14">x</text><text x="205" y="120" text-anchor="middle" font-size="13">Angles on a straight line total 180°</text></svg></div>
      <p><strong>Exam tip:</strong> Always write the angle fact you used, such as "angles on a straight line add to 180°".</p>'''),
('Angles in Parallel Lines', blue, '''      <p>When two parallel lines are crossed by a transversal, special angle pairs are formed. <strong>Corresponding angles</strong> are equal, <strong>alternate angles</strong> are equal, and <strong>co-interior angles</strong> add to \(180^\circ\).</p>
      <p>These facts are often used together with angles on a straight line or angles around a point.</p>
      <p><strong>Common mistake:</strong> Do not assume lines are parallel unless the diagram marks them with arrows or the question states they are parallel.</p>'''),
('Angles in Triangles', blue, '''      <p>The angles inside a triangle always add to \(180^\circ\). An isosceles triangle has two equal sides and therefore two equal base angles.</p>
      <p>The exterior angle of a triangle is equal to the sum of the two opposite interior angles.</p>
      <p style="text-align:center;">\(a+b+c=180^\circ\)</p>'''),
('Angles in Polygons', blue, '''      <p>The sum of interior angles in an \(n\)-sided polygon is \((n-2)\times180^\circ\). For a regular polygon, divide this total by \(n\) to find each interior angle.</p>
      <p>Exterior angles of any polygon add to \(360^\circ\). For a regular polygon, each exterior angle is \(360^\circ\div n\).</p>
      <p><strong>Exam tip:</strong> Exterior angles are often the fastest way to solve regular polygon questions.</p>'''),
('Bearings', green, '''      <p>A <strong>bearing</strong> is an angle measured clockwise from north and is written with three digits, such as \(047^\circ\) or \(128^\circ\).</p>
      <p>Bearings questions often combine angle facts, parallel north lines, and triangle angle sums.</p>
      <p><strong>Common mistake:</strong> Always measure bearings from the north line at the starting point, not from the destination.</p>'''),
('Constructions and Loci', blue, '''      <p>Constructions use a ruler and compass to draw accurate geometric objects. Common constructions include perpendicular bisectors, angle bisectors, and triangles from given side lengths.</p>
      <p>A <strong>locus</strong> is a set of points satisfying a rule. Points a fixed distance from one point form a circle; points equidistant from two points lie on the perpendicular bisector.</p>'''),
('Congruence', orange, '''      <p>Two shapes are <strong>congruent</strong> if they are the same shape and size. Congruent triangles can be proven using SSS, SAS, ASA, RHS, or equivalent angle-side information.</p>
      <p>Congruence questions require precise reasoning. Matching sides and angles must be identified clearly.</p>'''),
('Geometric Proof', orange, '''      <p>Geometric proof means using known angle and shape facts to justify a conclusion. A good proof states each fact and links it logically to the next step.</p>
      <p>For example, if two alternate angles are equal, then the lines may be parallel. If the angles in a quadrilateral add to \(360^\circ\), a missing angle can be found by subtraction.</p>''')
])

lesson('gcse_maths_mensuration_lesson.html', 'Mensuration', [
('Perimeter and Area', blue, '''      <p><strong>Perimeter</strong> is the distance around a 2D shape. <strong>Area</strong> is the amount of surface inside a 2D shape.</p>
      <p>For rectangles, area is length multiplied by width. For triangles, area is \(\frac{1}{2}\times\text{base}\times\text{height}\). For parallelograms, area is base multiplied by perpendicular height.</p>
      <p><strong>Exam tip:</strong> Make sure the height used in area formulae is perpendicular to the base.</p>'''),
('Compound Shapes', blue, '''      <p>A compound shape is made from two or more simple shapes. Split the shape into rectangles, triangles, trapezia, or circles, then add or subtract areas as needed.</p>
      <p>Missing side lengths are often found by subtracting known lengths from a total length.</p>'''),
('Circles', blue, '''      <p>For a circle with radius \(r\), the circumference is \(2\pi r\) and the area is \(\pi r^2\). If the diameter is given, halve it to find the radius.</p>
      <div style="text-align:center;margin:16px 0;"><svg width="240" height="160" viewBox="0 0 240 160" style="background:#f9f8f5; border-radius:8px; max-width:100%;"><circle cx="120" cy="80" r="52" fill="none" stroke="#01696f" stroke-width="4"/><line x1="120" y1="80" x2="172" y2="80" stroke="#a13544" stroke-width="3"/><text x="146" y="72" font-size="14">r</text><text x="120" y="148" text-anchor="middle" font-size="13">Area = πr²</text></svg></div>'''),
('Sectors and Arcs', orange, '''      <p>A sector is a fraction of a circle. If the angle at the centre is \(\theta\), then sector area is \(\frac{\theta}{360}\times\pi r^2\), and arc length is \(\frac{\theta}{360}\times2\pi r\).</p>
      <p><strong>Common mistake:</strong> Arc length is only the curved edge, while perimeter of a sector includes the two radii as well.</p>'''),
('Volume of Prisms', blue, '''      <p>A prism has the same cross-section all the way through. The volume of a prism is:</p>
      <p style="text-align:center;">\(\text{Volume}=\text{area of cross-section}\times\text{length}\)</p>
      <p>This works for cuboids, triangular prisms, cylinders, and other prisms.</p>'''),
('Surface Area', blue, '''      <p><strong>Surface area</strong> is the total area of all outside faces of a 3D shape. For cuboids, find the areas of the three pairs of opposite faces and add them.</p>
      <p>For cylinders, surface area combines two circular ends with the curved surface area.</p>'''),
('Cones, Spheres and Pyramids', orange, '''      <p>Higher GCSE questions may use formulae for cones, spheres, and pyramids. Read the formula sheet carefully and substitute values accurately.</p>
      <p>Common formulae include sphere volume \(\frac{4}{3}\pi r^3\), sphere surface area \(4\pi r^2\), cone volume \(\frac{1}{3}\pi r^2h\), and pyramid volume \(\frac{1}{3}\times\text{base area}\times\text{height}\).</p>'''),
('Bounds and Units', green, '''      <p>Mensuration often involves units and bounds. Convert units before calculating, especially between cm, m, cm², m², cm³, and m³.</p>
      <p>When measurements are rounded, upper and lower bounds can be used to find maximum or minimum possible areas and volumes.</p>''')
])

lesson('gcse_maths_graphs_lesson.html', 'Graphs', [
('Coordinates and Axes', blue, '''      <p>Coordinates are written as \((x,y)\). The \(x\)-coordinate tells you how far across to go, and the \(y\)-coordinate tells you how far up or down to go.</p>
      <p>The origin is \((0,0)\). Points in different quadrants may have positive or negative coordinates.</p>'''),
('Straight-Line Graphs', blue, '''      <p>A straight-line graph usually has equation \(y=mx+c\), where \(m\) is the gradient and \(c\) is the y-intercept.</p>
      <p>The y-intercept is where the graph crosses the y-axis. The gradient describes how steep the line is.</p>
      <p style="text-align:center;">\(\text{gradient}=\frac{\text{change in }y}{\text{change in }x}\)</p>'''),
('Plotting Linear Graphs', blue, '''      <p>To plot a linear graph, choose values of \(x\), calculate the matching values of \(y\), plot the points, and draw a straight line through them.</p>
      <p>For example, for \(y=2x+1\), when \(x=0\), \(y=1\); when \(x=2\), \(y=5\).</p>'''),
('Gradient and Intercept', blue, '''      <p>In \(y=mx+c\), the gradient is the coefficient of \(x\). A positive gradient slopes upwards from left to right, while a negative gradient slopes downwards.</p>
      <p>Parallel lines have the same gradient. This fact is useful for finding missing equations.</p>'''),
('Real-Life Graphs', green, '''      <p>Real-life graphs show quantities such as distance, time, speed, cost, or temperature. The gradient often has a real meaning, such as speed on a distance-time graph.</p>
      <p>Horizontal sections usually mean no change. On a distance-time graph, a horizontal line means the object is stationary.</p>'''),
('Quadratic Graphs', orange, '''      <p>A quadratic graph has a squared term, such as \(y=x^2+3x+2\). Its graph is a curve called a parabola.</p>
      <p>Quadratic graphs can be used to estimate roots, turning points, and solutions to equations.</p>'''),
('Cubic and Reciprocal Graphs', orange, '''      <p>Higher GCSE includes recognising cubic and reciprocal graphs. Cubic graphs include an \(x^3\) term and often have an S-like shape. Reciprocal graphs such as \(y=\frac{1}{x}\) have asymptotes and separate branches.</p>
      <p>Recognising the shape helps you match equations to graphs.</p>'''),
('Solving Equations with Graphs', orange, '''      <p>Graphs can be used to solve equations approximately. The solution is found where two graphs intersect, or where one graph crosses a given line.</p>
      <p>For example, solutions to \(x^2=2x+3\) are the x-coordinates where \(y=x^2\) and \(y=2x+3\) intersect.</p>''')
])

print('Batch 1 lesson templates written.')
