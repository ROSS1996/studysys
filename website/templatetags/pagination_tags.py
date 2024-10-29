# templatetags/pagination_tags.py
from django import template

register = template.Library()

@register.simple_tag
def calculate_page_range(current_page, total_pages, window=5):
    """Calculate the range of page numbers to display in pagination."""
    half_window = window // 2
    start_page = max(current_page - half_window, 1)
    end_page = min(current_page + half_window, total_pages)
    
    # Adjust the range if we're at the edges
    if end_page - start_page + 1 < window:
        if start_page == 1:
            end_page = min(window, total_pages)
        elif end_page == total_pages:
            start_page = max(total_pages - window + 1, 1)
    
    return range(start_page, end_page + 1)

@register.inclusion_tag('components/pagination.html')
def render_pagination(page_obj):
    """Render the pagination component."""
    return {
        'page_obj': page_obj,
        'page_range': calculate_page_range(
            page_obj.number,
            page_obj.paginator.num_pages
        )
    }