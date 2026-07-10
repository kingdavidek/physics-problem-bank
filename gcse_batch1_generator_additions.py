# ------------------------------------------------------------
# GCSE Maths Batch 1 – Geometry/Angles, Mensuration, Graphs
# Add this section to generators/gcse/maths.py
# Requires existing imports: random, math, make_problem
# ------------------------------------------------------------


def _b1_fmt(x, dp=2):
    if isinstance(x, int) or abs(x - int(x)) < 1e-10:
        return str(int(x))
    return f"{x:.{dp}f}".rstrip('0').rstrip('.')


def _b1_simp(a, b):
    g = math.gcd(abs(int(a)), abs(int(b)))
    return int(a)//g, int(b)//g


def _b1_options(correct, distractors):
    correct = str(correct)
    choices = [correct]
    for d in distractors:
        d = str(d)
        if d not in choices:
            choices.append(d)
    filler = 1
    while len(choices) < 4:
        candidate = str(filler * 10)
        if candidate not in choices:
            choices.append(candidate)
        filler += 1
    choices = choices[:4]
    random.shuffle(choices)
    letters = ['A', 'B', 'C', 'D']
    return [f"{letters[i]}  {choices[i]}" for i in range(4)], letters[choices.index(correct)]


def _b1_extract_answer(solution):
    if '<strong>' in solution:
        return solution.split('<strong>')[-1].split('</strong>')[0]
    return 'See solution'


def _b1_make_variant(name, func):
    def variant():
        return func()
    variant.__name__ = name
    variant.__qualname__ = name
    globals()[name] = variant
    return variant

# ============================================================
# GEOMETRY AND ANGLES
# ============================================================


def _geo_straight_line():
    x = random.randint(35, 145)
    ans = 180 - x
    q = rf"Two angles lie on a straight line. One angle is {x}°. Find the other angle."
    s = rf"Angles on a straight line add to 180°. Missing angle = 180 − {x} = <strong>{ans}°</strong>."
    return q, s, "Angles on a straight line add to 180°.", 1


def _geo_around_point():
    a, b, c = random.randint(30, 110), random.randint(40, 120), random.randint(20, 90)
    ans = 360 - a - b - c
    q = rf"Angles around a point are {a}°, {b}°, {c}° and x. Find x."
    s = rf"Angles around a point add to 360°. x = 360 − {a} − {b} − {c} = <strong>{ans}°</strong>."
    return q, s, "Angles around a point total 360°.", 2


def _geo_vertically_opposite():
    x = random.randint(25, 155)
    q = rf"Two straight lines cross. One angle is {x}°. Find the vertically opposite angle."
    s = rf"Vertically opposite angles are equal, so the angle is <strong>{x}°</strong>."
    return q, s, "Vertically opposite angles are equal.", 1


def _geo_triangle_missing():
    a, b = random.randint(35, 80), random.randint(40, 85)
    ans = 180 - a - b
    q = rf"A triangle has angles {a}°, {b}° and x. Find x."
    s = rf"Angles in a triangle add to 180°. x = 180 − {a} − {b} = <strong>{ans}°</strong>."
    return q, s, "Angles in a triangle total 180°.", 2


def _geo_isosceles():
    top = random.randint(30, 110)
    ans = (180 - top) / 2
    q = rf"An isosceles triangle has vertex angle {top}°. Find each base angle."
    s = rf"The two base angles are equal. Each base angle = (180 − {top}) ÷ 2 = <strong>{_b1_fmt(ans)}°</strong>."
    return q, s, "The two base angles in an isosceles triangle are equal.", 2


def _geo_exterior_triangle():
    a, b = random.randint(35, 75), random.randint(45, 85)
    q = rf"Two opposite interior angles of a triangle are {a}° and {b}°. Find the exterior angle."
    s = rf"The exterior angle equals the sum of the two opposite interior angles: {a}+{b} = <strong>{a+b}°</strong>."
    return q, s, "Exterior angle = sum of the two opposite interior angles.", 2


def _geo_parallel_corresponding():
    x = random.randint(35, 145)
    q = rf"Two parallel lines are cut by a transversal. A corresponding angle is {x}°. Find the matching corresponding angle."
    s = rf"Corresponding angles in parallel lines are equal, so the angle is <strong>{x}°</strong>."
    return q, s, "Corresponding angles are equal on parallel lines.", 1


def _geo_parallel_cointerior():
    x = random.randint(50, 130)
    ans = 180 - x
    q = rf"Two co-interior angles on parallel lines are {x}° and y. Find y."
    s = rf"Co-interior angles add to 180°. y = 180 − {x} = <strong>{ans}°</strong>."
    return q, s, "Co-interior angles add to 180°.", 2


def _geo_polygon_sum():
    n = random.randint(5, 10)
    ans = (n-2)*180
    q = rf"Find the sum of the interior angles of a {n}-sided polygon."
    s = rf"Interior angle sum = (n−2)×180 = ({n}−2)×180 = <strong>{ans}°</strong>."
    return q, s, "Use (n − 2) × 180°.", 2


def _geo_regular_interior():
    n = random.choice([5,6,8,9,10,12])
    ans = (n-2)*180/n
    q = rf"Find each interior angle of a regular {n}-sided polygon."
    s = rf"Interior angle sum = ({n}−2)×180 = {(n-2)*180}°. Divide by {n}: <strong>{_b1_fmt(ans)}°</strong>."
    return q, s, "For a regular polygon, all interior angles are equal.", 3


def _geo_regular_exterior():
    n = random.choice([5,6,8,9,10,12])
    ans = 360/n
    q = rf"Find each exterior angle of a regular {n}-sided polygon."
    s = rf"Exterior angles add to 360°. Each exterior angle = 360 ÷ {n} = <strong>{_b1_fmt(ans)}°</strong>."
    return q, s, "Exterior angles of any polygon add to 360°.", 2


def _geo_find_sides_from_exterior():
    ext = random.choice([24,30,36,40,45,60,72])
    n = int(360/ext)
    q = rf"Each exterior angle of a regular polygon is {ext}°. How many sides does it have?"
    s = rf"Number of sides = 360 ÷ exterior angle = 360 ÷ {ext} = <strong>{n}</strong>."
    return q, s, "For regular polygons, sides = 360 ÷ exterior angle.", 2


def _geo_bearing_reverse():
    b = random.randint(1, 179)
    ans = b + 180
    q = rf"The bearing of B from A is {b:03d}°. Find the bearing of A from B."
    s = rf"Reverse bearings differ by 180°. {b} + 180 = <strong>{ans:03d}°</strong>."
    return q, s, "Reverse bearings are 180° apart.", 2


def _geo_locus_circle():
    r = random.randint(3, 12)
    q = rf"Describe the locus of points exactly {r} cm from a fixed point P."
    s = rf"All points a fixed distance from one point form a circle. The locus is <strong>a circle with centre P and radius {r} cm</strong>."
    return q, s, "A fixed distance from one point gives a circle.", 1


def _geo_congruence_reason():
    q = "Two triangles have all three corresponding side lengths equal. Which congruence condition proves they are congruent?"
    s = "If all three corresponding sides are equal, the triangles are congruent by <strong>SSS</strong>."
    return q, s, "SSS means side-side-side.", 1

# ============================================================
# MENSURATION
# ============================================================


def _men_rectangle_area():
    l, w = random.randint(4, 20), random.randint(3, 15)
    q = rf"Find the area of a rectangle with length {l} cm and width {w} cm."
    s = rf"Area = length × width = {l}×{w} = <strong>{l*w} cm²</strong>."
    return q, s, "Area of a rectangle is length × width.", 1


def _men_rectangle_perimeter():
    l, w = random.randint(4, 20), random.randint(3, 15)
    q = rf"Find the perimeter of a rectangle with length {l} cm and width {w} cm."
    s = rf"Perimeter = 2(l+w) = 2({l}+{w}) = <strong>{2*(l+w)} cm</strong>."
    return q, s, "Add all outside edges.", 1


def _men_triangle_area():
    b, h = random.randint(6, 20), random.randint(4, 16)
    ans = b*h/2
    q = rf"Find the area of a triangle with base {b} cm and perpendicular height {h} cm."
    s = rf"Area = 1/2 × base × height = 1/2 × {b} × {h} = <strong>{_b1_fmt(ans)} cm²</strong>."
    return q, s, "Use the perpendicular height.", 2


def _men_parallelogram_area():
    b, h = random.randint(5, 18), random.randint(4, 14)
    q = rf"Find the area of a parallelogram with base {b} cm and perpendicular height {h} cm."
    s = rf"Area = base × perpendicular height = {b}×{h} = <strong>{b*h} cm²</strong>."
    return q, s, "Use perpendicular height, not slanted side.", 2


def _men_trapezium_area():
    a, b, h = random.randint(5, 12), random.randint(13, 25), random.randint(4, 12)
    ans = (a+b)*h/2
    q = rf"Find the area of a trapezium with parallel sides {a} cm and {b} cm, and height {h} cm."
    s = rf"Area = 1/2(a+b)h = 1/2({a}+{b})×{h} = <strong>{_b1_fmt(ans)} cm²</strong>."
    return q, s, "Add the parallel sides first.", 3


def _men_circle_area():
    r = random.randint(3, 12)
    ans = math.pi*r*r
    q = rf"Find the area of a circle with radius {r} cm. Give your answer to 1 decimal place."
    s = rf"Area = πr² = π×{r}² = <strong>{ans:.1f} cm²</strong>."
    return q, s, "Area of a circle is πr².", 2


def _men_circumference():
    r = random.randint(3, 12)
    ans = 2*math.pi*r
    q = rf"Find the circumference of a circle with radius {r} cm. Give your answer to 1 decimal place."
    s = rf"Circumference = 2πr = 2π×{r} = <strong>{ans:.1f} cm</strong>."
    return q, s, "Circumference is 2πr.", 2


def _men_sector_area():
    r = random.randint(4, 12)
    theta = random.choice([30,45,60,90,120,150])
    ans = theta/360*math.pi*r*r
    q = rf"Find the area of a sector with radius {r} cm and angle {theta}°. Give your answer to 1 decimal place."
    s = rf"Sector area = {theta}/360 × π×{r}² = <strong>{ans:.1f} cm²</strong>."
    return q, s, "A sector is a fraction of a circle.", 3


def _men_arc_length():
    r = random.randint(4, 12)
    theta = random.choice([30,45,60,90,120,150])
    ans = theta/360*2*math.pi*r
    q = rf"Find the arc length of a sector with radius {r} cm and angle {theta}°. Give your answer to 1 decimal place."
    s = rf"Arc length = {theta}/360 × 2π×{r} = <strong>{ans:.1f} cm</strong>."
    return q, s, "Arc length is the same fraction of the circumference.", 3


def _men_cuboid_volume():
    l,w,h = random.randint(3,12), random.randint(3,10), random.randint(3,9)
    q = rf"Find the volume of a cuboid measuring {l} cm by {w} cm by {h} cm."
    s = rf"Volume = length × width × height = {l}×{w}×{h} = <strong>{l*w*h} cm³</strong>."
    return q, s, "Volume of a cuboid is length × width × height.", 1


def _men_prism_volume():
    area, length = random.randint(12,60), random.randint(4,15)
    q = rf"A prism has cross-sectional area {area} cm² and length {length} cm. Find its volume."
    s = rf"Volume = cross-sectional area × length = {area}×{length} = <strong>{area*length} cm³</strong>."
    return q, s, "Volume of a prism is cross-sectional area × length.", 2


def _men_cylinder_volume():
    r,h = random.randint(3,9), random.randint(5,15)
    ans = math.pi*r*r*h
    q = rf"Find the volume of a cylinder with radius {r} cm and height {h} cm. Give your answer to 1 decimal place."
    s = rf"Volume = πr²h = π×{r}²×{h} = <strong>{ans:.1f} cm³</strong>."
    return q, s, "A cylinder is a circular prism.", 3


def _men_cuboid_surface_area():
    l,w,h = random.randint(3,10), random.randint(3,9), random.randint(3,8)
    ans = 2*(l*w + l*h + w*h)
    q = rf"Find the surface area of a cuboid measuring {l} cm by {w} cm by {h} cm."
    s = rf"Surface area = 2(lw+lh+wh) = 2({l*w}+{l*h}+{w*h}) = <strong>{ans} cm²</strong>."
    return q, s, "Add the areas of all six faces.", 3


def _men_sphere_volume():
    r = random.randint(3,8)
    ans = 4/3*math.pi*r**3
    q = rf"Find the volume of a sphere with radius {r} cm. Give your answer to 1 decimal place."
    s = rf"Volume = 4/3πr³ = 4/3π×{r}³ = <strong>{ans:.1f} cm³</strong>."
    return q, s, "Use the sphere volume formula from the formula sheet.", 3


def _men_unit_conversion_area():
    m2 = random.randint(2,12)
    q = rf"Convert {m2} m² into cm²."
    s = rf"Since 1 m = 100 cm, 1 m² = 100×100 = 10,000 cm². So {m2} m² = <strong>{m2*10000} cm²</strong>."
    return q, s, "Area scale factors are squared.", 2

# ============================================================
# GRAPHS
# ============================================================


def _gra_coordinate_quadrant():
    x, y = random.choice([-5,-4,-3,3,4,5]), random.choice([-5,-4,-3,3,4,5])
    if x > 0 and y > 0: qd = 'I'
    elif x < 0 and y > 0: qd = 'II'
    elif x < 0 and y < 0: qd = 'III'
    else: qd = 'IV'
    q = rf"Which quadrant contains the point ({x}, {y})?"
    s = rf"The signs of the coordinates are x {'positive' if x>0 else 'negative'} and y {'positive' if y>0 else 'negative'}, so the point is in quadrant <strong>{qd}</strong>."
    return q, s, "Use the signs of x and y.", 1


def _gra_substitute_linear():
    m,c,x = random.randint(2,6), random.randint(-5,8), random.randint(-3,7)
    y = m*x+c
    q = rf"For the graph y = {m}x + {c}, find y when x = {x}."
    s = rf"Substitute x = {x}: y = {m}×{x} + {c} = <strong>{y}</strong>."
    return q, s, "Substitute the x-value into the equation.", 1


def _gra_gradient_two_points():
    x1,y1 = random.randint(-3,3), random.randint(-4,4)
    m = random.randint(1,5)
    x2 = x1 + random.randint(2,6)
    y2 = y1 + m*(x2-x1)
    q = rf"Find the gradient of the line through ({x1}, {y1}) and ({x2}, {y2})."
    s = rf"Gradient = change in y ÷ change in x = ({y2}−{y1})/({x2}−{x1}) = {y2-y1}/{x2-x1} = <strong>{m}</strong>."
    return q, s, "Gradient is change in y divided by change in x.", 2


def _gra_y_intercept():
    m,c = random.randint(-5,5), random.randint(-8,8)
    if m == 0: m = 2
    q = rf"Find the y-intercept of the graph y = {m}x + {c}."
    s = rf"In y = mx + c, the y-intercept is c. Therefore the y-intercept is <strong>{c}</strong>."
    return q, s, "The y-intercept is the constant term in y = mx + c.", 1


def _gra_equation_from_gradient_intercept():
    m,c = random.randint(-5,5), random.randint(-8,8)
    if m == 0: m = 3
    q = rf"A straight line has gradient {m} and y-intercept {c}. Write its equation."
    s = rf"Use y = mx + c. The equation is <strong>y = {m}x + {c}</strong>."
    return q, s, "Use y = mx + c.", 2


def _gra_parallel_gradient():
    m,c = random.randint(-5,5), random.randint(-8,8)
    if m == 0: m = -2
    q = rf"A line is parallel to y = {m}x + {c}. What is its gradient?"
    s = rf"Parallel lines have the same gradient, so the gradient is <strong>{m}</strong>."
    return q, s, "Parallel lines have equal gradients.", 1


def _gra_table_linear():
    m,c = random.randint(2,5), random.randint(-4,6)
    xs = [-1,0,1,2]
    ys = [m*x+c for x in xs]
    q = rf"Complete the y-values for y = {m}x + {c} when x = -1, 0, 1, 2."
    s = rf"Substitute each x-value: y-values are <strong>{ys[0]}, {ys[1]}, {ys[2]}, {ys[3]}</strong>."
    return q, s, "Substitute each x-value into the equation.", 2


def _gra_distance_time_speed():
    distance, time = random.randint(20,120), random.choice([2,3,4,5,6])
    q = rf"On a distance-time graph, an object travels {distance} km in {time} hours. Find its speed."
    s = rf"Speed = distance ÷ time = {distance} ÷ {time} = <strong>{_b1_fmt(distance/time)} km/h</strong>."
    return q, s, "Gradient of a distance-time graph represents speed.", 2


def _gra_quadratic_substitute():
    a,b,c,x = 1, random.randint(-4,4), random.randint(-5,5), random.randint(-3,4)
    y = a*x*x + b*x + c
    q = rf"For y = x² + {b}x + {c}, find y when x = {x}."
    s = rf"Substitute x = {x}: y = {x}² + {b}×{x} + {c} = <strong>{y}</strong>."
    return q, s, "Substitute carefully, especially when x is negative.", 2


def _gra_root_from_factorised():
    r1, r2 = random.sample(range(-5,6),2)
    q = rf"Find the roots of y = (x - {r1})(x - {r2})."
    s = rf"Set each bracket to zero. x − {r1} = 0 gives x = {r1}, and x − {r2} = 0 gives x = {r2}. Roots: <strong>{r1} and {r2}</strong>."
    return q, s, "Roots occur when y = 0.", 2


def _gra_midpoint():
    x1,y1,x2,y2 = random.randint(-5,5), random.randint(-5,5), random.randint(-5,5), random.randint(-5,5)
    q = rf"Find the midpoint of ({x1}, {y1}) and ({x2}, {y2})."
    mx,my = (x1+x2)/2, (y1+y2)/2
    s = rf"Midpoint = (({x1}+{x2})/2, ({y1}+{y2})/2) = <strong>({_b1_fmt(mx)}, {_b1_fmt(my)})</strong>."
    return q, s, "Average the x-coordinates and average the y-coordinates.", 2


def _gra_line_intersection_simple():
    m1, c1, m2, c2 = 2, random.randint(-4,4), -1, random.randint(2,8)
    x = (c2-c1)/(m1-m2); y = m1*x+c1
    q = rf"Find the intersection of y = {m1}x + {c1} and y = {m2}x + {c2}."
    s = rf"Set the equations equal: {m1}x + {c1} = {m2}x + {c2}. Solving gives x = {_b1_fmt(x)}, then y = {_b1_fmt(y)}. Intersection: <strong>({_b1_fmt(x)}, {_b1_fmt(y)})</strong>."
    return q, s, "At an intersection, both equations have the same x and y.", 3


def _gra_reciprocal_value():
    k = random.choice([6,8,10,12,15,20])
    x = random.choice([2,3,4,5])
    q = rf"For y = {k}/x, find y when x = {x}."
    s = rf"Substitute x = {x}: y = {k} ÷ {x} = <strong>{_b1_fmt(k/x)}</strong>."
    return q, s, "Substitute into the reciprocal equation.", 1


def _gra_cubic_substitute():
    x = random.choice([-3,-2,-1,2,3])
    q = rf"For y = x³ − 2x, find y when x = {x}."
    y = x**3 - 2*x
    s = rf"Substitute x = {x}: y = {x}³ − 2×{x} = <strong>{y}</strong>."
    return q, s, "Cube the x-value, then subtract 2x.", 2


def _gra_region_inequality():
    c = random.randint(-3,5)
    q = rf"For the inequality y > x + {c}, should the boundary line be solid or dashed?"
    s = rf"Because the inequality is strict (> rather than ≥), the boundary line should be <strong>dashed</strong>."
    return q, s, "Strict inequalities use dashed boundary lines.", 1


def _b1_register(prefix, funcs):
    names = []
    for difficulty, flist in funcs.items():
        for i, func in enumerate(flist, 1):
            names.append(_b1_make_variant(f"_{prefix}_{difficulty}_{i:02d}", func))
    return names

_geo_found_funcs = [_geo_straight_line,_geo_around_point,_geo_vertically_opposite,_geo_triangle_missing,_geo_isosceles,_geo_exterior_triangle,_geo_parallel_corresponding,_geo_parallel_cointerior,_geo_polygon_sum,_geo_regular_exterior,_geo_locus_circle,_geo_congruence_reason,_geo_straight_line,_geo_triangle_missing,_geo_regular_exterior]
_geo_inter_funcs = [_geo_parallel_cointerior,_geo_polygon_sum,_geo_regular_interior,_geo_regular_exterior,_geo_find_sides_from_exterior,_geo_bearing_reverse,_geo_exterior_triangle,_geo_isosceles,_geo_around_point,_geo_parallel_corresponding,_geo_triangle_missing,_geo_congruence_reason,_geo_regular_interior,_geo_find_sides_from_exterior,_geo_bearing_reverse]
_geo_diff_funcs = [_geo_regular_interior,_geo_find_sides_from_exterior,_geo_bearing_reverse,_geo_congruence_reason,_geo_parallel_cointerior,_geo_polygon_sum,_geo_exterior_triangle,_geo_around_point,_geo_locus_circle,_geo_regular_exterior,_geo_regular_interior,_geo_find_sides_from_exterior,_geo_bearing_reverse,_geo_congruence_reason,_geo_parallel_cointerior]

_men_found_funcs = [_men_rectangle_area,_men_rectangle_perimeter,_men_triangle_area,_men_parallelogram_area,_men_circle_area,_men_circumference,_men_cuboid_volume,_men_prism_volume,_men_unit_conversion_area,_men_rectangle_area,_men_rectangle_perimeter,_men_triangle_area,_men_circle_area,_men_circumference,_men_cuboid_volume]
_men_inter_funcs = [_men_trapezium_area,_men_circle_area,_men_circumference,_men_sector_area,_men_arc_length,_men_prism_volume,_men_cylinder_volume,_men_cuboid_surface_area,_men_unit_conversion_area,_men_triangle_area,_men_parallelogram_area,_men_trapezium_area,_men_sector_area,_men_arc_length,_men_cylinder_volume]
_men_diff_funcs = [_men_sector_area,_men_arc_length,_men_cylinder_volume,_men_cuboid_surface_area,_men_sphere_volume,_men_unit_conversion_area,_men_trapezium_area,_men_prism_volume,_men_circle_area,_men_circumference,_men_sector_area,_men_arc_length,_men_cylinder_volume,_men_sphere_volume,_men_cuboid_surface_area]

_gra_found_funcs = [_gra_coordinate_quadrant,_gra_substitute_linear,_gra_gradient_two_points,_gra_y_intercept,_gra_equation_from_gradient_intercept,_gra_parallel_gradient,_gra_table_linear,_gra_distance_time_speed,_gra_midpoint,_gra_reciprocal_value,_gra_coordinate_quadrant,_gra_substitute_linear,_gra_y_intercept,_gra_table_linear,_gra_parallel_gradient]
_gra_inter_funcs = [_gra_gradient_two_points,_gra_equation_from_gradient_intercept,_gra_parallel_gradient,_gra_distance_time_speed,_gra_quadratic_substitute,_gra_root_from_factorised,_gra_midpoint,_gra_line_intersection_simple,_gra_reciprocal_value,_gra_cubic_substitute,_gra_table_linear,_gra_substitute_linear,_gra_gradient_two_points,_gra_quadratic_substitute,_gra_root_from_factorised]
_gra_diff_funcs = [_gra_line_intersection_simple,_gra_quadratic_substitute,_gra_root_from_factorised,_gra_cubic_substitute,_gra_reciprocal_value,_gra_region_inequality,_gra_midpoint,_gra_gradient_two_points,_gra_equation_from_gradient_intercept,_gra_distance_time_speed,_gra_line_intersection_simple,_gra_quadratic_substitute,_gra_root_from_factorised,_gra_cubic_substitute,_gra_region_inequality]

_b1_register('geometry_angles_foundational', {'v': _geo_found_funcs})
_b1_register('geometry_angles_intermediate', {'v': _geo_inter_funcs})
_b1_register('geometry_angles_difficult', {'v': _geo_diff_funcs})
_b1_register('mensuration_foundational', {'v': _men_found_funcs})
_b1_register('mensuration_intermediate', {'v': _men_inter_funcs})
_b1_register('mensuration_difficult', {'v': _men_diff_funcs})
_b1_register('graphs_foundational', {'v': _gra_found_funcs})
_b1_register('graphs_intermediate', {'v': _gra_inter_funcs})
_b1_register('graphs_difficult', {'v': _gra_diff_funcs})


def _b1_pool(topic, difficulty):
    if topic == 'geometry_angles':
        found = [globals()[f'_geometry_angles_foundational_v_{i:02d}'] for i in range(1,16)]
        inter = [globals()[f'_geometry_angles_intermediate_v_{i:02d}'] for i in range(1,16)]
        diff = [globals()[f'_geometry_angles_difficult_v_{i:02d}'] for i in range(1,16)]
    elif topic == 'mensuration':
        found = [globals()[f'_mensuration_foundational_v_{i:02d}'] for i in range(1,16)]
        inter = [globals()[f'_mensuration_intermediate_v_{i:02d}'] for i in range(1,16)]
        diff = [globals()[f'_mensuration_difficult_v_{i:02d}'] for i in range(1,16)]
    else:
        found = [globals()[f'_graphs_foundational_v_{i:02d}'] for i in range(1,16)]
        inter = [globals()[f'_graphs_intermediate_v_{i:02d}'] for i in range(1,16)]
        diff = [globals()[f'_graphs_difficult_v_{i:02d}'] for i in range(1,16)]
    if difficulty == 'foundational': return found
    if difficulty == 'intermediate': return inter
    if difficulty == 'difficult': return diff
    return random.sample(found,4) + random.sample(inter,4) + random.sample(diff,2)


def _b1_variants(topic, difficulty, mode):
    if mode == 'mcq':
        return [_b1_mcq_factory(topic)] * 10
    pool = _b1_pool(topic, difficulty)
    shuffled = random.sample(pool, len(pool))
    return (shuffled * (10 // len(shuffled) + 1))[:10]


def _b1_mcq_factory(topic):
    def mcq():
        pool = _b1_pool(topic, random.choice(['foundational','intermediate','difficult']))
        q, s, hint, marks = random.choice(pool)()
        correct = _b1_extract_answer(s)
        options, letter = _b1_options(correct, ['90°','180°','12','y = 2x + 1'])
        return q, f"Answer: {letter}\n\n{hint}", hint, 1, options, letter
    mcq.__name__ = f'{topic}_mcq'
    return mcq


def gcse_geometry_angles_variants(difficulty, mode):
    return _b1_variants('geometry_angles', difficulty, mode)


def gcse_mensuration_variants(difficulty, mode):
    return _b1_variants('mensuration', difficulty, mode)


def gcse_graphs_variants(difficulty, mode):
    return _b1_variants('graphs', difficulty, mode)


def gcse_geometry_angles(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, opts, correct = _b1_mcq_factory('geometry_angles')()
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'geometry_angles', options=opts, correct_answer=correct)
    variants = gcse_geometry_angles_variants(difficulty, mode)
    if variant_name is None:
        variant = random.choice(variants)
    else:
        full_pool = _b1_pool('geometry_angles', difficulty)
        variant = {v.__name__: v for v in full_pool}.get(variant_name, random.choice(variants))
    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'geometry_angles')


def gcse_mensuration(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, opts, correct = _b1_mcq_factory('mensuration')()
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'mensuration', options=opts, correct_answer=correct)
    variants = gcse_mensuration_variants(difficulty, mode)
    if variant_name is None:
        variant = random.choice(variants)
    else:
        full_pool = _b1_pool('mensuration', difficulty)
        variant = {v.__name__: v for v in full_pool}.get(variant_name, random.choice(variants))
    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'mensuration')


def gcse_graphs(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        q, s, hint, marks, opts, correct = _b1_mcq_factory('graphs')()
        return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'graphs', options=opts, correct_answer=correct)
    variants = gcse_graphs_variants(difficulty, mode)
    if variant_name is None:
        variant = random.choice(variants)
    else:
        full_pool = _b1_pool('graphs', difficulty)
        variant = {v.__name__: v for v in full_pool}.get(variant_name, random.choice(variants))
    q, s, hint, marks = variant()
    return make_problem(q, s, hint, difficulty, marks, 'gcse', 'maths', 'graphs')
