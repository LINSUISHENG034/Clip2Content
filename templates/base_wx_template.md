{% block content %}
## {{ summary.title }}

{{ summary.content|indent(4) }}

{% include "qrcode_component.md" %}
{% endblock %}