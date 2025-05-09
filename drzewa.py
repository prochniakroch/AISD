#!/usr/bin/env python3
import sys
import argparse
import time

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1


def insert_bst(root, value):
    if root is None:
        return Node(value)
    if value < root.value:
        root.left = insert_bst(root.left, value)
    else:
        root.right = insert_bst(root.right, value)
    return root


def insert_avl(root, value):
    if root is None:
        return Node(value)
    if value < root.value:
        root.left = insert_avl(root.left, value)
    else:
        root.right = insert_avl(root.right, value)

    root.height = 1 + max(get_height(root.left), get_height(root.right))
    balance = get_balance(root)

    if balance > 1 and value < root.left.value:
        return right_rotate(root)
    if balance < -1 and value > root.right.value:
        return left_rotate(root)
    if balance > 1 and value > root.left.value:
        root.left = left_rotate(root.left)
        return right_rotate(root)
    if balance < -1 and value < root.right.value:
        root.right = right_rotate(root.right)
        return left_rotate(root)

    return root


def left_rotate(z):
    y = z.right
    T2 = y.left
    y.left = z
    z.right = T2
    z.height = 1 + max(get_height(z.left), get_height(z.right))
    y.height = 1 + max(get_height(y.left), get_height(y.right))
    return y


def right_rotate(y):
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    y.height = 1 + max(get_height(y.left), get_height(y.right))
    x.height = 1 + max(get_height(x.left), get_height(x.right))
    return x


def get_height(root):
    if root is None:
        return 0
    return root.height


def get_balance(root):
    if root is None:
        return 0
    return get_height(root.left) - get_height(root.right)


def print_inorder(root):
    return print_tree(root, 'inorder')


def print_preorder(root):
    return print_tree(root, 'preorder')


def print_postorder(root):
    return print_tree(root, 'postorder')


def print_tree(root, order):
    result = []
    if root:
        if order == 'preorder':
            result.append(root.value)
        result.extend(print_tree(root.left, order))
        if order == 'inorder':
            result.append(root.value)
        result.extend(print_tree(root.right, order))
        if order == 'postorder':
            result.append(root.value)
    return result


def find_min(root):
    while root and root.left:
        root = root.left
    return root


def find_max(root):
    while root and root.right:
        root = root.right
    return root


def remove(root, value):
    if root is None:
        return root

    if value < root.value:
        root.left = remove(root.left, value)
    elif value > root.value:
        root.right = remove(root.right, value)
    else:
        if root.left is None:
            return root.right
        elif root.right is None:
            return root.left
        else:
            min_larger_node = find_min(root.right)
            root.value = min_larger_node.value
            root.right = remove(root.right, min_larger_node.value)
    return root


def delete_tree(root):
    if root:
        root.left = delete_tree(root.left)
        root.right = delete_tree(root.right)
        root = None
    return root


def rebalance_tree(root, insert_values):
    root = None
    for value in insert_values:
        root = insert_avl(root, value)
    return root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", choices=["AVL", "BST"], required=True)
    parser.add_argument("--file", type=str, help="Ścieżka do pliku z danymi wejściowymi")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, 'r') as f:
                input_line = f.readline().strip()
        except FileNotFoundError:
            print(f"Plik {args.file} nie został znaleziony.")
            sys.exit(1)
    else:
        input_line = input("values> ").strip()

    try:
        values = list(map(int, input_line.split()))
    except ValueError:
        print("Błąd: dane wejściowe muszą być liczbami całkowitymi oddzielonymi spacją.")
        sys.exit(1)

    if not values:
        print("Brak danych wejściowych.")
        sys.exit(1)

    insert_values = values
    num_nodes = len(insert_values)

    print(f"nodes> {num_nodes}")
    print(f"insert> {' '.join(map(str, insert_values))}")

    if args.tree == "AVL":
        print("Sorted:", ', '.join(map(str, sorted(insert_values))))
        n = len(insert_values)
        if n % 2 == 0:
            median = (sorted(insert_values)[n//2 - 1] + sorted(insert_values)[n//2]) / 2
        else:
            median = sorted(insert_values)[n//2]
        print("Median:", median)
    else:
        print(f"Inserting: {', '.join(map(str, insert_values))}")

    # Tworzenie drzewa z pomiarem czasu
    root = None
    start_time = time.perf_counter()
    if args.tree == "AVL":
        for value in insert_values:
            root = insert_avl(root, value)
    else:
        for value in insert_values:
            root = insert_bst(root, value)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Tree construction time: {elapsed_time:.6f} seconds")

    print("Type 'Help' for list of commands.")

    while True:
        try:
            action = input("action> ").strip().lower()
        except EOFError:
            print("Program exited with status: 0")
            break

        if action == "help":
            print("Help - Show this message")
            print("Print - Print the tree using In-order, Pre-order, Post-order")
            print("findminmax - Print min and max value")
            print("Remove - Remove elements of the tree")
            print("Delete - Delete whole tree")
            print("Export - Export the tree to TikZpicture")
            print("Rebalance - Rebalance the tree")
            print("Exit - Exits the program (same as ctrl+D)")
        elif action == "print":
            start = time.perf_counter()
            inorder = print_inorder(root)
            elapsed = time.perf_counter() - start
            print("In-order:", ', '.join(map(str, inorder)))
            print(f"In-order traversal time: {elapsed:.6f} seconds")

            print("Pre-order:", ', '.join(map(str, print_preorder(root))))
            print("Post-order:", ', '.join(map(str, print_postorder(root))))
        elif action == "findminmax":
            if root:
                start = time.perf_counter()
                min_node = find_min(root)
                max_node = find_max(root)
                elapsed = time.perf_counter() - start
                print(f"Min: {min_node.value}")
                print(f"Max: {max_node.value}")
                print(f"FindMinMax time: {elapsed:.6f} seconds")
            else:
                print("Tree is empty.")
        elif action == "remove":
            to_remove = input("remove> ").strip().split()
            for val in map(int, to_remove):
                root = remove(root, val)
        elif action == "delete":
            root = delete_tree(root)
        elif action == "delete all":
            root = delete_tree(root)
            print("Tree successfully removed")
        elif action == "rebalance":
            start = time.perf_counter()
            root = rebalance_tree(root, insert_values)
            elapsed = time.perf_counter() - start
            print(f"Tree rebalanced in {elapsed:.6f} seconds")
        elif action == "export":
            tikz_code = export_to_tikzpicture(root)
            print("TikZ output:\n")
            print(tikz_code)
        elif action == "exit":
            print("Program exited with status: 0")
            break
        else:
            print("Unknown command.")



def export_to_tikzpicture(root):
    def tikz_node(node):
        if node is None:
            return "child {node {$\\varnothing$}}"
        s = f"child {{node {{{node.value}}}"
        if node.left or node.right:
            s += "\n" + (tikz_node(node.left) if node.left else "child {node {$\\varnothing$}}") + "\n"
            s += (tikz_node(node.right) if node.right else "child {node {$\\varnothing$}}") + "\n"
        s += "}"
        return s

    if root is None:
        return (
            "\\begin{TikzTreeStyle}\n"
            "\\node {$\\varnothing$};\n"
            "\\end{TikzTreeStyle}"
        )

    tikz_code = "\\begin{TikzTreeStyle}\n"
    tikz_code += f"  \\node {{{root.value}}}\n"
    if root.left or root.right:
        tikz_code += tikz_node(root.left) + "\n"
        tikz_code += tikz_node(root.right) + ";\n"
    else:
        tikz_code += ";\n"
    tikz_code += "  \\path[draw=none] (0,-2) -- (0,14mm);\n"
    tikz_code += "\\end{TikzTreeStyle}"
    return tikz_code


if __name__ == "__main__":
    main()
