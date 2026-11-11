def afficher_ast(node, indent="", last=True):
    """Affiche un AST fait de dataclasses sous forme d'arbre ASCII."""
    prefix = "└── " if last else "├── "
    child_indent = indent + ("    " if last else "│   ")

    if is_dataclass(node):
        print(f"{indent}{prefix}\033[1;34m{node.__class__.__name__}\033[0m")
        field_list = fields(node)
        for i, field in enumerate(field_list):
            val = getattr(node, field.name)
            is_last_field = (i == len(field_list) - 1)
            field_prefix = "└── " if is_last_field else "├── "
            sub_child_indent = child_indent + ("    " if is_last_field else "│   ")
            
            print(f"{child_indent}{field_prefix}\033[33m{field.name}\033[0m:")
            
            if isinstance(val, list):
                if not val:
                    print(f"{sub_child_indent}└── []")
                else:
                    for j, item in enumerate(val):
                        afficher_ast(item, sub_child_indent, j == len(val) - 1)
            elif is_dataclass(val):
                afficher_ast(val, sub_child_indent, True)
            else:
                print(f"{sub_child_indent}└── \033[32m{repr(val)}\033[0m")

    elif isinstance(node, list):
        for i, item in enumerate(node):
            afficher_ast(item, indent, i == len(node) - 1)
    else:
        print(f"{indent}{prefix}\033[32m{repr(node)}\033[0m")
