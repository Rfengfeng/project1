from decimal import Decimal
from typing import Callable


def aggregate_revenue(
        revenue_data: list,
        aggregation_index: int = 0,
        label_formatter: Callable[[str | int], str] = None):
  '''
  Aggregate revenue data by the given index
  '''

  # Initialize grand totals
  grand_totals = {
      'workshop': Decimal(0.00),
      'lesson': Decimal(0.00),
      'subscription': Decimal(0.00),
      'total': Decimal(0.00)
  }

  # Initialize results
  results = {}
  for row in revenue_data:
    # Get the label
    label = row[aggregation_index]
    label = label_formatter(label) if label_formatter else label

    # Group the data by the label
    data = {}
    if label not in results:
      # Initialize the data if it does not exist
      data = results[label] = {
          'total': Decimal(0.00),
          'lesson': Decimal(0.00),
          'workshop': Decimal(0.00),
          'subscription': Decimal(0.00)
      }
      results[label] = data
    else:
      data = results[label]
    if row.item_type == 'workshop':
      data['workshop'] += row.total_revenue or Decimal(0.00)
    elif row.item_type == 'lesson':
      data['lesson'] += row.total_revenue or Decimal(0.00)
    elif row.item_type == 'subscription':
      data['subscription'] += row.total_revenue or Decimal(0.00)
    data['total'] = data['lesson'] + data['workshop'] + data['subscription']

  # Calculate the grand totals
  for data in results.values():
    grand_totals['workshop'] += data['workshop']
    grand_totals['lesson'] += data['lesson']
    grand_totals['subscription'] += data['subscription']
    grand_totals['total'] += data['total']

  return (grand_totals, results)
