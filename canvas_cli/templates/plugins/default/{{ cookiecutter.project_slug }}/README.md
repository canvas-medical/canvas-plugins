{% for _ in cookiecutter.project_name %}={% endfor %}
{{ cookiecutter.project_name }}
{% for _ in cookiecutter.project_name %}={% endfor %}

{{ cookiecutter.project_short_description }}


## Structure

```
{{ cookiecutter.project_slug }}/
├── {{ cookiecutter.project_package_name }}/
│   ├── __init__.py
│   └── plugin.py # Add your plugin code here.
├── pyproject.toml
├── poetry.lock
└── README.md
```
