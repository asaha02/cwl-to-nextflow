/*
 * Generated Nextflow workflow from CWL
 * Workflow: {{ workflow_info.name }}
 * Version: {{ workflow_info.version }}
 * Description: {{ workflow_info.description }}
 */

// Workflow parameters
{% for input in inputs %}
params.{{ input.name }} = {{ input.default if input.default else 'null' }}  // {{ input.description }}
{% endfor %}

// Input channels
{% for input in inputs %}
{{ input.name }}_channel = Channel.value(params.{{ input.name }})
{% endfor %}

// Process definitions
{% for process in processes %}
process {{ process.name }} {
    {% if process.container %}
    container '{{ process.container }}'
    {% endif %}
    
    {% if process.resources %}
    // Resource requirements
    {% if process.resources.cpus %}
    cpus {{ process.resources.cpus }}
    {% endif %}
    {% if process.resources.memory %}
    memory '{{ process.resources.memory }}'
    {% endif %}
    {% if process.resources.time %}
    time '{{ process.resources.time }}'
    {% endif %}
    {% endif %}
    
    // Inputs
    {% for input in process.inputs %}
    input:
    {% if input.source %}
    val {{ input.name }} from {{ input.source }}
    {% else %}
    val {{ input.name }}
    {% endif %}
    {% endfor %}
    
    // Outputs
    {% for output in process.outputs %}
    output:
    {% if output.type == 'file' %}
    file "{{ output.name }}" into {{ output.name }}_channel
    {% else %}
    val {{ output.name }} into {{ output.name }}_channel
    {% endif %}
    {% endfor %}
    
    script:
    """
    {{ process.script }}
    """
}
{% endfor %}

// Workflow definition
workflow {
    {% for step in workflow %}
    // {{ step.name }}
    {% if step.dependencies %}
    {% for dep in step.dependencies %}
    {{ step.name }}({{ dep }}_channel)
    {% endfor %}
    {% else %}
    {{ step.name }}()
    {% endif %}
    {% endfor %}
    
    // Outputs
    {% for output in outputs %}
    {{ output.name }}_channel.view()
    {% endfor %}
}

