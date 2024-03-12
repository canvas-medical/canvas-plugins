{% for _ in cookiecutter.project_name %}={% endfor %}
{{ cookiecutter.project_name }}
{% for _ in cookiecutter.project_name %}={% endfor %}

{{ cookiecutter.project_short_description }}

## Structure

```
{{ cookiecutter.project_slug }}/
├── commands/
├── content/
├── effects/
├── protocols/
├── views/
├── CANVAS_MANIFEST.json
└── README.md
```
