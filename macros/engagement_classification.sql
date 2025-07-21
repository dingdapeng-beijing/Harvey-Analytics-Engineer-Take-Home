{% macro engagement_classification(query_count, active_days) %}
    case 
        when {{ query_count }} >= 50 and {{ active_days }} >= 15 then 'Power User'
        when {{ query_count }} >= 20 and {{ active_days }} >= 8 then 'Active User'
        when {{ query_count }} >= 5 and {{ active_days }} >= 3 then 'Regular User'
        when {{ query_count }} >= 1 then 'Occasional User'
        else 'Inactive'
    end
{% endmacro %} 