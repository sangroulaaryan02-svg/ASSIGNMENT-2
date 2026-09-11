import os


def format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    if isinstance(value, int):
        return str(value)

    rounded = round(float(value), 4)

    if rounded.is_integer():
        return str(int(rounded))

    return f"{rounded:.4f}".rstrip('0').rstrip('.')


def tokenize(expression):
    tokens = []
    i = 0

    while i < len(expression):
        ch = expression[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            start = i

            while i < len(expression) and expression[i].isdigit():
                i += 1

            if i < len(expression) and expression[i] == '.':
                i += 1

                decimal_start = i
                while i < len(expression) and expression[i].isdigit():
                    i += 1

                if decimal_start == i:
                    raise ValueError("Invalid number")

            value = expression[start:i]
            tokens.append(("NUM", value))
            continue

        if ch in "+-*/%^":
            tokens.append(("OP", ch))
            i += 1
            continue

        if ch == '(':
            tokens.append(("LPAREN", ch))
            i += 1
            continue

        if ch == ')':
            tokens.append(("RPAREN", ch))
            i += 1
            continue

        raise ValueError("Invalid character")

    tokens.append(("END", ""))
    return tokens


def tokens_to_string(tokens):
    parts = []

    for token_type, value in tokens:
        if token_type == "END":
            parts.append("[END]")
        else:
            parts.append(f"[{token_type}:{value}]")

    return " ".join(parts)


def current_token(state):
    return state["tokens"][state["pos"]]


def advance(state):
    token = current_token(state)
    state["pos"] += 1
    return token


def make_number_node(text):
    value = float(text)
    return {
        "kind": "number",
        "value": value,
        "tree": format_number(value)
    }


def make_unary_node(operand):
    return {
        "kind": "unary",
        "op": "neg",
        "operand": operand,
        "tree": f"(neg {operand['tree']})"
    }


def make_binary_node(op, left, right):
    return {
        "kind": "binary",
        "op": op,
        "left": left,
        "right": right,
        "tree": f"({op} {left['tree']} {right['tree']})"
    }


def parse_expression(state):
    return parse_add_sub(state)


def parse_add_sub(state):
    node = parse_mul_div_mod(state)

    while current_token(state) in (("OP", "+"), ("OP", "-")):
        op = advance(state)[1]
        right = parse_mul_div_mod(state)
        node = make_binary_node(op, node, right)

    return node


def begins_implicit_factor(token):
    # Parenthesised expressions can be adjacent to a completed factor:
    # 2(3+4), (2+3)(4+5), etc.
    #
    # A plain adjacent number such as "2 3" is explicitly NOT implicit
    # multiplication according to the assignment specification.
    return token[0] == "LPAREN"


def parse_mul_div_mod(state):
    node = parse_unary(state)

    while True:
        token = current_token(state)

        if token in (("OP", "*"), ("OP", "/"), ("OP", "%")):
            op = advance(state)[1]
            right = parse_unary(state)
            node = make_binary_node(op, node, right)

        elif begins_implicit_factor(token):
            right = parse_unary(state)
            node = make_binary_node("*", node, right)

        else:
            break

    return node


def parse_unary(state):
    token = current_token(state)

    if token == ("OP", "-"):
        advance(state)
        operand = parse_unary(state)
        return make_unary_node(operand)

    if token == ("OP", "+"):
        raise ValueError("Unary plus is not supported")

    return parse_power(state)


def parse_power(state):
    left = parse_primary(state)

    if current_token(state) == ("OP", "^"):
        advance(state)
        right = parse_unary(state)
        return make_binary_node("^", left, right)

    return left


def parse_primary(state):
    token_type, value = current_token(state)

    if token_type == "NUM":
        advance(state)
        return make_number_node(value)

    if token_type == "LPAREN":
        advance(state)
        node = parse_expression(state)

        if current_token(state)[0] != "RPAREN":
            raise ValueError("Missing closing parenthesis")

        advance(state)
        return node

    raise ValueError("Expected number or parenthesis")


def evaluate_tree(node):
    if node["kind"] == "number":
        return node["value"]

    if node["kind"] == "unary":
        return -evaluate_tree(node["operand"])

    left = evaluate_tree(node["left"])
    right = evaluate_tree(node["right"])
    op = node["op"]

    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        return left / right
    if op == "%":
        return left % right
    if op == "^":
        return left ** right

    raise ValueError("Unknown operator")


def process_expression(expression):
    try:
        tokens = tokenize(expression)
    except Exception:
        return {
            "input": expression,
            "tree": "ERROR",
            "tokens": "ERROR",
            "result": "ERROR"
        }

    token_string = tokens_to_string(tokens)

    try:
        state = {"tokens": tokens, "pos": 0}
        tree = parse_expression(state)

        if current_token(state)[0] != "END":
            raise ValueError("Unexpected token")

        tree_string = tree["tree"]

        try:
            value = evaluate_tree(tree)
            result = float(value)
        except Exception:
            result = "ERROR"

        return {
            "input": expression,
            "tree": tree_string,
            "tokens": token_string,
            "result": result
        }

    except Exception:
        return {
            "input": expression,
            "tree": "ERROR",
            "tokens": "ERROR",
            "result": "ERROR"
        }


def write_output(results, output_path):
    blocks = []

    for item in results:
        if item["result"] == "ERROR":
            result_text = "ERROR"
        else:
            result_text = format_number(item["result"])

        block = (
            f"Input: {item['input']}\n"
            f"Tree: {item['tree']}\n"
            f"Tokens: {item['tokens']}\n"
            f"Result: {result_text}"
        )
        blocks.append(block)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n\n".join(blocks))


def evaluate_file(input_path: str) -> list[dict]:
    with open(input_path, "r", encoding="utf-8") as file:
        lines = file.read().splitlines()

    results = [process_expression(line) for line in lines]

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(input_path)),
        "output.txt"
    )

    write_output(results, output_path)
    return results


if __name__ == "__main__":
    evaluate_file("input.txt")
