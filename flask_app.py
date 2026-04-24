from flask import Flask, render_template, request
import random
import sympy as sp

app = Flask(__name__)


# -----------------------------------------------
# TOPIC GENERATORS
# -----------------------------------------------
def gcse_physics_forces():
    m = random.randint(2, 20)
    a = random.randint(1, 15)
    f = m * a
    question = rf"A block of mass \( {m} \, \text{{kg}} \) accelerates at \( {a} \, \text{{m/s}}^2 \). Calculate the resultant force."
    solution = rf"Using Newton's Second Law \( F = ma \):<br>\( F = {m} \times {a} = {f} \, \text{{N}} \)"
    return question, solution

def gcse_math_algebra():
    x = sp.Symbol('x')
    a, b, c = random.randint(1, 6), random.randint(1, 10), random.randint(1, 10)
    expr = a * x**2 + b * x + c
    roots = sp.solve(expr, x)
    question = rf"Solve: \( {sp.latex(expr)} = 0 \)"
    if roots:
        solution = rf"Factorising gives roots: \( x = {sp.latex(roots[0])} \) and \( x = {sp.latex(roots[1])} \)" if len(roots) == 2 else rf"Solution: \( x = {sp.latex(roots[0])} \)"
    else:
        solution = "No real roots."
    return question, solution

# -----------------------------------------------
# ROUTER — add new topics here as you expand
# -----------------------------------------------
TOPICS = {
    'gcse': {
        'physics': {
            'forces': gcse_physics_forces,
        },
        'maths': {
            'algebra': gcse_math_algebra,
        }
    }
}

# -----------------------------------------------
# ROUTES
# -----------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    question, solution, error = None, None, None
    # Store selections so the form remembers them after reload
    selected_level = 'gcse'
    selected_subject = 'physics'
    selected_topic = 'forces'

    if request.method == 'POST':
        selected_level   = request.form.get('level', 'gcse')
        selected_subject = request.form.get('subject', 'physics')
        selected_topic   = request.form.get('topic', 'forces')

        try:
            generator = TOPICS[selected_level][selected_subject][selected_topic]
            question, solution = generator()
        except KeyError:
            error = "Invalid combination selected. Please try again."

    return render_template('index.html',
                           question=question,
                           solution=solution,
                           error=error,
                           selected_level=selected_level,
                           selected_subject=selected_subject,
                           selected_topic=selected_topic)

@app.route('/topics')
def topics_index():
    return render_template('topics.html')


if __name__ == '__main__':
    app.run(debug=True)