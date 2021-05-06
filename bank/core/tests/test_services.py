from datetime import datetime

import pytest
import pytz
from model_bakery import baker
from rest_framework.exceptions import ValidationError

from bank.core.models import Customer, Account, Transaction
from bank.core.services import CustomerService, AccountService, TransactionService


def test_create_customer():
    customer_service = CustomerService()
    params = {
        'name': 'Maria Aparecida',
        'document_id': '99999999999',
        'birth_date': '1995-08-06',
    }
    customer_service.create(**params)
    record = Customer.objects.all().first()

    assert record.name == params['name']
    assert record.document_id == params['document_id']
    assert record.birth_date.isoformat() == params['birth_date']


@pytest.fixture
def one_customer():
    return baker.make('Customer')


@pytest.fixture
def fix_create_customer(one_customer, mocker):
    return mocker.patch(
        'bank.core.services.CustomerService.create', return_value=one_customer
    )


def test_create_account(one_customer, fix_create_customer):
    account_service = AccountService()
    params = {
        'customer': {
            'name': 'Maria Aparecida',
            'document_id': '99999999999',
            'birth_date': '1995-08-06',
        },
        'type': Account.AccountType.CHECKOUT.value,
    }
    account_service.create(**params)

    fix_create_customer.assert_called_once_with(**params['customer'])
    record = Account.objects.all().first()
    assert record.type == params['type']
    assert record.customer.pk == one_customer.pk


@pytest.fixture
def one_account():
    return baker.make('Account', balance=100.0)


@pytest.fixture
def fix_create_transaction(mocker):
    mocker.patch('bank.core.services.TransactionService.create')


def test_make_deposit_invalid(one_account, fix_create_transaction):
    account_service = AccountService()
    params = {'amount': -0.01, 'account': one_account.pk}

    with pytest.raises(ValidationError):
        account_service.make_deposit(**params)


def test_make_deposit(one_account, fix_create_transaction):
    account_service = AccountService()
    params = {'amount': 01.01, 'account': one_account.pk}
    account_service.make_deposit(**params)

    record = Account.objects.all().first()
    assert record.balance == round(one_account.balance + params['amount'], 2)


def test_make_withdarw_invalid(one_account, fix_create_transaction):
    account_service = AccountService()
    params = {'amount': -0.01, 'account': one_account.pk}

    with pytest.raises(ValidationError):
        account_service.make_withdraw(**params)


def test_make_withdraw(one_account, fix_create_transaction):
    account_service = AccountService()
    params = {'amount': 01.01, 'account': one_account.pk}
    account_service.make_withdraw(**params)

    record = Account.objects.all().first()
    assert record.balance == round(one_account.balance - params['amount'], 2)


def test_create_transaction(one_account):
    transaction_service = TransactionService()
    params = {
        'account': one_account,
        'amount': 101.01,
        'operation': Transaction.TransactionType.WITHDRAW.value,
    }
    record = transaction_service.create(**params)
    assert record.account.pk == one_account.pk
    assert record.amount == params['amount']
    assert record.operation == params['operation']


def test_get_by_pk(one_account):
    account_service = AccountService()
    record = account_service.get_by_pk(account=one_account.pk)
    assert record == one_account


def test_deactivate(one_account):
    account_service = AccountService()
    account_service.deactivate(account=one_account.pk)
    one_account.refresh_from_db()
    assert not one_account.active


@pytest.fixture
def three_transactions():
    return [baker.make('Transaction') for _ in range(3)]


def test_filter_transactions(three_transactions):
    transaction_service = TransactionService()
    account = three_transactions[0].account.pk
    transactions = transaction_service.filter_by_account(account=account)
    assert len(transactions) == 1
    assert transactions.first() == Transaction.objects.get(account__pk=account)


@pytest.fixture
def four_transactions_by_period():
    timezone = pytz.timezone('UTC')
    dates = [
        timezone.localize(datetime(2021, 1, 3)),
        timezone.localize(datetime(2021, 2, 1)),
        timezone.localize(datetime(2021, 2, 28)),
        timezone.localize(datetime(2021, 3, 1)),
    ]
    transactions = [baker.make('Transaction') for _ in range(len(dates))]
    for transaction, date in zip(transactions, dates):
        transaction.created_at = date
        transaction.save()

    return transactions


def test_filter_transactions_by_period(four_transactions_by_period):
    transaction_service = TransactionService()
    transactions = transaction_service.filter_by_period(
        start_date='2021-02-01', end_date='2021-02-28'
    )
    assert len(transactions) == 2
