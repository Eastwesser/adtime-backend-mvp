from prometheus_client import Counter

ORDER_TRANSITIONS = Counter(
    'order_status_transitions_total',
    'Count of order status transitions',
    ['from', 'to', 'result']
)
