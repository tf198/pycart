{% macro glyphicon(name) -%}
	<i class="glyphicon glyphicon-{{ name }}"></i>
{%- endmacro %}

{% macro commit_link(repo, commit) -%}
	<a href="{{ commit_url(repo, commit) }}">{{ commit[:10] }}</a>
{%- endmacro %}

{% macro tree_url(repo, sha, path) %}/repo/{{ repo }}/tree/{{ sha }}/{{ path }}{% endmacro %}
{% macro commit_url(repo, commit) %}/repo/{{ repo }}/commit/{{ commit }}{% endmacro %}
{% macro history_url(repo, sha, path) %}/repo/{{ repo }}/history/{{ sha }}/{{ path }}{% endmacro %}