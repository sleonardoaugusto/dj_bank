from rest_framework.exceptions import ValidationError

from bank.core.models import Account, Customer, Transaction


class CustomerService:
    def create(self, *, name: str, document_id: str, birth_date: str) -> Customer:
        customer = Customer(name=name, document_id=document_id, birth_date=birth_date)
        customer.full_clean()
        customer.save()
        return customer


class TransactionService:
    def create(
        self, *, amount: float, account: Account, operation: Account.AccountType.choices
    ) -> Transaction:
        transaction = Transaction(account=account, amount=amount, operation=operation)
        transaction.full_clean()
        transaction.save()
        return transaction

    def filter_by_account(self, *, account: int):
        return Transaction.objects.filter(account__pk=account)

    def filter_by_period(self, *, start_date, end_date):
        return Transaction.objects.filter(
            created_at__gte=start_date, created_at__lte=end_date
        )


class AccountService:
    def greater_than_zero(self, number):
        if number < 0:
            message = 'amount value should be greater than zero'
            raise ValidationError(message, code='less_than_zero')

    def create(self, *, type: int, customer: dict) -> Account:
        customer_service = CustomerService()
        customer = customer_service.create(**customer)

        account = Account(type=type, customer=customer)
        account.full_clean()
        account.save()

        return account

    def make_deposit(self, *, account: int, amount: float):
        self.greater_than_zero(amount)

        record = self.get_by_pk(account=account)
        record.balance = round(record.balance + amount, 2)
        record.save()

        transaction_service = TransactionService()
        transaction_service.create(
            amount=amount,
            account=record,
            operation=Transaction.TransactionType.DEPOSIT,
        )

    def make_withdraw(self, *, account: int, amount: float):
        self.greater_than_zero(amount)

        record = self.get_by_pk(account=account)
        record.balance = round(record.balance - amount, 2)
        record.save()

        transaction_service = TransactionService()
        transaction_service.create(
            amount=amount,
            account=record,
            operation=Transaction.TransactionType.WITHDRAW,
        )

    def get_by_pk(self, *, account: int):
        return Account.objects.get(pk=account)

    def deactivate(self, *, account: int):
        record = self.get_by_pk(account=account)
        record.active = False
        record.save()
