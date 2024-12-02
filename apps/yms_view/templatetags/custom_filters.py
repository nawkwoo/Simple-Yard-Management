# apps/yms_view/templatetags/custom_filters.py

from django import template

register = template.Library()


@register.filter(name='to_range')
def to_range(start, end):
    """
    숫자 범위를 생성하는 필터.
    사용법: {% for i in 1|to_range:40 %}
    
    Args:
        start (int): 시작 숫자.
        end (int): 끝 숫자.
    
    Returns:
        range: start부터 end까지의 range 객체.
    """
    try:
        start = int(start)
        end = int(end)
        if start > end:
            return range(0)
        return range(start, end + 1)
    except (ValueError, TypeError):
        return range(0)


@register.filter(name='get_item')
def get_item(lst, index):
    """
    리스트에서 특정 인덱스의 아이템을 반환하는 필터.
    사용법: {{ list|get_item:index }}
    
    Args:
        lst (list): 대상 리스트.
        index (int): 인덱스 (1부터 시작).
    
    Returns:
        item or None: 해당 인덱스의 아이템 또는 None.
    """
    try:
        index = int(index)
        if index < 1:
            return None
        return lst[index - 1]
    except (ValueError, TypeError, IndexError):
        return None
