from decimal import Decimal

def calculate_and_apply_bonus(order):
    total_order_amount = Decimal('0.00')
    total_bonus_amount = Decimal('0.00')
    user = order.user

    for order_item in order.order_items.all():
        if order_item.is_bonus:
            total_bonus_amount += order_item.calculate_total_amount()
        else:
            total_order_amount += order_item.calculate_total_amount()

    # Проверяем, что пользователь существует и его бонусы не равны None
    if user is None or user.bonus is None:
        user_bonus = Decimal('0.00')
    else:
        user_bonus = user.bonus

    print(total_bonus_amount, user_bonus)

    # Проверка, достаточно ли бонусов у пользователя
    if total_bonus_amount > user_bonus:
        raise ValueError("Not enough bonus points.")

    # Вычитаем бонусы из баланса пользователя
    if user:
        user.bonus -= total_bonus_amount
        user.save()

    # Обновляем общую сумму заказа
    order.total_amount = total_order_amount
    order.save()

    return total_order_amount
