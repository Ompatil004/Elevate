import os
import re

IGNORE_DIRS = {'.git', '.github', '.venv', 'node_modules', '__pycache__', 'build', 'dist', '.claude'}
ALLOWED_EXTS = {'.js', '.jsx', '.py', '.json', '.md', '.html', '.css'}

def process_file(path):
    ext = os.path.splitext(path)[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return []
    
    out_lines = []
    
    if ext in ['.py']:
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('def ') or stripped.startswith('async def ') or stripped.startswith('class '):
                out_lines.append(line.rstrip())
                out_lines.append('    # [Logic Hidden]')
            elif stripped.startswith('#') or stripped.startswith('\"\"\"') or stripped.startswith('\'\'\''):
                if len(out_lines) == 0 or out_lines[-1].strip() != '# [Logic Hidden]':
                    out_lines.append(line.rstrip())
    
    elif ext in ['.js', '.jsx']:
        for line in lines:
            stripped = line.strip()
            if 'function' in stripped or '=>' in stripped or stripped.startswith('class ') or 'router.' in stripped or 'app.' in stripped:
                out_lines.append(line.rstrip())
                out_lines.append('  // [Logic Hidden]')
            elif stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                if len(out_lines) == 0 or out_lines[-1].strip() != '// [Logic Hidden]':
                    out_lines.append(line.rstrip())
    else:
        # Just return the first few lines for other files or nothing
        pass
        
    return out_lines

def main():
    root_dir = '.'
    output_file = 'docs/codebase_map.md'
    
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write('# Codebase Structural Map\n\n')
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            
            for file in sorted(filenames):
                if any(file.endswith(ext) for ext in ALLOWED_EXTS):
                    full_path = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(full_path, root_dir).replace(r'\\', '/')
                    
                    if rel_path == 'docs/codebase_map.md':
                        continue
                        
                    lines = process_file(full_path)
                    if lines:
                        out.write(f'## {rel_path}\n')
                        ext = os.path.splitext(file)[1]
                        lang = 'javascript' if ext in ['.js', '.jsx'] else 'python' if ext == '.py' else ''
                        out.write(f'`{lang}\n')
                        for line in lines:
                            out.write(f'{line}\n')
                        out.write('`\n\n')

if __name__ == '__main__':
    main()
