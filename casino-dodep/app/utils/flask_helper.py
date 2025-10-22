from flask import render_template_string
def render_template(template_file_path: str, **kwargs):
    with open(f'templates/{template_file_path}', 'r') as template_file:
        template = template_file.read()
    
    for k,v in kwargs.items():
        template = template.replace(f'[[{k}]]',v if isinstance(v, str) else '')
    return render_template_string(template, **kwargs)
