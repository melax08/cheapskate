ACCESS_DENIED_LOG = 'Unauthorized access attempt from user: {}'
START_BOT_LOG = 'Someone starts bot: {}'
WRONG_EXPENSE_LOG = 'User {} sends the wrong message with expense: {}'
NO_CATEGORIES_LOG = "User {} can't add expense, no categories!"
CHOOSE_CATEGORY_LOG = 'User {} have to choose the category for expense: {}'
SPEND_EXPENSE_TO_API_LOG = (
    'User {} add expense {} to category {} to the API, money left: {}'
)
DELETE_EXPENSE_FROM_API_LOG = (
    'User {} delete expense {} from category {} on the API. money left: {}'
)

ADDED_CATEGORY_LOG = 'User {} added new expense category: {}'
CATEGORY_ALREADY_EXISTS_LOG = (
    'User {} tried to add already exists category: {}'
)
CATEGORY_NAME_TOO_LONG_LOG = (
    'User {} tried to add category with too long name: {}'
)
EXCEPTION_LOG = 'Exception while handling an update:'
