{% macro firm_size_categorization(firm_size) %}
    case 
        when {{ firm_size }} < 100 then 'Small'
        when {{ firm_size }} between 100 and 500 then 'Medium'
        else 'Large'
    end
{% endmacro %} 