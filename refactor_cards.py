import re

file_path = r'c:\Users\DanyG\Desktop\RAMedio-Diagnostico-de-pcs-1\web\index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_card = False
card_div_depth = 0

for line in lines:
    if '<div class="question-grid">' in line:
        new_lines.append(line.replace('<div class="question-grid">', '<div class="row g-4 mt-2">'))
        continue
        
    if '<div class="question-card">' in line:
        indent_match = re.match(r'^\s*', line)
        indent = indent_match.group(0) if indent_match else ''
        new_lines.append(f'{indent}<div class="col-lg-6 col-12">\n')
        new_lines.append(line.replace('<div class="question-card">', '<div class="question-card h-100">').replace(indent, indent + '    ', 1))
        in_card = True
        card_div_depth = 1
        continue
        
    if in_card:
        # Count divs to know when card ends
        card_div_depth += line.count('<div')
        card_div_depth -= line.count('</div')
        
        # Add 4 spaces to indent
        if line.strip():
            indent_match = re.match(r'^\s*', line)
            indent = indent_match.group(0) if indent_match else ''
            new_lines.append(line.replace(indent, indent + '    ', 1))
        else:
            new_lines.append(line)
            
        if card_div_depth == 0:
            in_card = False
            # add wrapper closer
            # wait, the line that just made depth 0 is already appended.
            # we just need to append the wrapper closer
            indent_match = re.match(r'^\s*', line)
            indent = indent_match.group(0) if indent_match else ''
            # strip the 4 spaces for the outer div
            if len(indent) >= 4:
                indent = indent[:-4]
            new_lines.append(f'{indent}</div>\n')
        continue

    new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("index.html refactoring complete.")
