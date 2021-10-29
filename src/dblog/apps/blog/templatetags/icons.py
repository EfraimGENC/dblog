from django import template

register = template.Library()

@register.simple_tag
def get_ordering_icon_class(choice):
    icons = {
        'latest': 'fas fa-sort-numeric-up',
        'earliest': 'fas fa-sort-numeric-down-alt',
        'a_to_z': 'fas fa-sort-alpha-down',
        'z_to_a': 'fas fa-sort-alpha-up-alt',
        'showcase': 'simple-icon-lock-open',
        'in_stock': 'fas fa-clipboard-check',
    }
    return icons.get(choice, 'fas fa-circle')
