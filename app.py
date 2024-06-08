from flask import Flask, request, jsonify, render_template
import ast
import json

app = Flask(__name__)


def parse_python_code(code):
    tree = ast.parse(code)
    return tree


def find_parents(tree):
    parents = {}
    functions = {}
    classes = {}

    class_name = ""

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            parents[node.name] = class_name if class_name else None
            functions[node.name] = ast.unparse(node)
        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            classes[class_name] = ast.unparse(node)
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    parents[subnode.name] = class_name
                    functions[subnode.name] = ast.unparse(subnode)
            class_name = ""  # Reset after processing the class

    return parents, functions, classes


def analyze_python_code(code):
    tree = parse_python_code(code)
    parents, functions, classes = find_parents(tree)

    output_data = {}
    for name, parent in parents.items():
        output_data[name] = {
            "Type": "Function" if parent else "Function",
            "Parent": parent,
            "Contents": functions[name]
        }

    for name in classes.keys():
        output_data[name] = {
            "Type": "Class",
            "Parent": None,
            "Contents": classes[name]
        }

    return json.dumps(output_data, indent=4)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    code = request.form['code']
    print("Code accepted:", code)  # Print the code accepted from the form
    try:
        result = analyze_python_code(code)
        return jsonify({"code_accepted": code, "result": json.loads(result), "error_log": None})
    except Exception as e:
        error_message = str(e)
        print("Error encountered:", error_message)  # Print the error message
        return jsonify({"code_accepted": code, "result": None, "error_log": error_message})


if __name__ == '__main__':
    app.run(debug=True)
