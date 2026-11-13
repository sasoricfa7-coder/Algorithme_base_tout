# EVA - Langage Algorithmique Pédagogique
# Copyright (C) 2026 SASORI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import field, is_dataclass, fields

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
