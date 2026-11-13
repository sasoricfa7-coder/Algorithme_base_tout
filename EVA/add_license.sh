#!/usr/bin/env zsh
# add_license.sh - Ajoute l'en-tête AGPL v3+ aux fichiers .py du projet EVA
# Usage: ./add_license.sh

set -e

HEADER='# EVA - Langage Algorithmique Pédagogique
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
# along with this program. If not, see <https://www.gnu.org/licenses/>.'

MARKER="GNU Affero General Public License"

count=0
skipped=0

# Trouve tous les .py sauf dans les dossiers techniques
while IFS= read -r file; do
    # Idempotence : si le marqueur est déjà dans les 15 premières lignes, on saute
    if head -n 15 "$file" 2>/dev/null | grep -q "$MARKER"; then
        skipped=$((skipped + 1))
        continue
    fi

    tmp=$(mktemp)
    first_line=$(head -n 1 "$file")

    # Si le fichier commence par un shebang ou un encoding line, on le préserve
    if [[ "$first_line" =~ '^#!' ]] || [[ "$first_line" =~ '^# -\*-' ]]; then
        echo "$first_line" > "$tmp"
        echo "" >> "$tmp"
        printf '%s\n' "$HEADER" >> "$tmp"
        echo "" >> "$tmp"
        tail -n +2 "$file" >> "$tmp"
    else
        printf '%s\n' "$HEADER" >> "$tmp"
        echo "" >> "$tmp"
        cat "$file" >> "$tmp"
    fi

    mv "$tmp" "$file"
    count=$((count + 1))
    echo "✅ $file"
done < <(find . -type f -name "*.py" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.venv/*" \
    -not -path "*/venv/*" \
    -not -path "*/.git/*" \
    -not -path "*/build/*" \
    -not -path "*/dist/*")

echo ""
echo "────────────────────────────────────"
echo "Fichiers modifiés     : $count"
echo "Fichiers déjà à jour  : $skipped"
echo "────────────────────────────────────"
