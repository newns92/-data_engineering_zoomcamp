{%- macro generate_schema_name(custom_schema_name, node) -%}

{{ log( node ~ '\n custom schema name: ' ~ custom_schema_name, info=True) }}

  {% if target.name == 'default' %}
    {{target.schema}}{{ '_' ~ custom_schema_name if custom_schema_name else '' }}

  {% elif target.name == 'prod' %}
    {{ 'prod_' }}

  {% endif %}

{%- endmacro -%}