def mortgage_interest_payments(loan_amount, monthly_payment, loan_term_years, annual_interest_rate):
    # Переводим процентную ставку и срок кредитования в месяцы
    monthly_interest_rate = annual_interest_rate / 12 / 100
    loan_term_months = loan_term_years * 12

    # Инициализация переменных
    total_interest = 0
    balance = loan_amount
    count = 0

    for month in range(loan_term_months):
        count += 1
        # Рассчитываем процентную часть платежа
        interest_payment = balance * monthly_interest_rate
        # Вычитаем из общего баланса основную часть платежа
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        # Суммируем процентный платеж к общему количеству процентов
        total_interest += interest_payment

        print(f"{count}\t{balance}\t{interest_payment}\t{principal_payment}")

        # Прерываем цикл, если баланс равен или меньше нуля
        if balance <= 0:
            break

    return total_interest, count

# Ввод данных
# loan_amount = float(input("Введите сумму кредита: "))
# monthly_payment = float(input("Введите ежемесячный платеж: "))
# loan_term_years = int(input("Введите срок кредитования в годах: "))
# annual_interest_rate = float(input("Введите годовую процентную ставку: "))

loan_amount = 1000000.0
monthly_payment = 20000.0
loan_term_years = 30
annual_interest_rate = 22


# Вызов функции и вывод результата
total_interest, count = mortgage_interest_payments(loan_amount, monthly_payment, loan_term_years, annual_interest_rate)
print(f"Общая сумма процентов, уплаченных за срок кредита: {total_interest:.2f} рублей")
print(f"{count / 12} лет")
