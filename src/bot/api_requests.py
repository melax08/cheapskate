class ApiRequest:
    """
    - Open session;
    - Request exceptions;
    - get_categories method;
    - send_expense method;
    - delete_expense method;
    - month_statistic;
    - etc;
    """
    ...


async def get_categories():
    ...


async def send_expense_to_api(money: str, category_id: str) -> tuple[int, int]:
    print(f'ЗАГЛУШКА. Отправлено {money} денег по категории {category_id}')
    return 100500 - int(money), 5


async def delete_expense_request(expense_id: str):
    print(f'ЗАГЛУШКА. Удален, а может и не удален расход с id {expense_id} на сумму ...')