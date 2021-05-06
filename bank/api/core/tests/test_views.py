import json
from datetime import date

import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from bank.core.models import Account


@pytest.fixture
def fix_create_account(mocker):
    mocker.patch('bank.core.services.AccountService.create', return_value=None)


def test_create_account(api_client: APIClient, fix_create_account):
    request_payload = {
        'customer': {
            'name': 'Maria Aparecida',
            'document_id': '99999999999',
            'birth_date': '1995-08-06',
        },
        'type': Account.AccountType.SALARY.value,
    }
    resp = api_client.post(
        reverse('api:account-create'),
        json.dumps(request_payload),
        content_type='application/json',
    )
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.fixture
def one_account():
    return baker.make('Account', balance=100.0)


@pytest.fixture
def fix_make_deposit(mocker):
    mocker.patch('bank.core.services.AccountService.make_deposit', return_value=None)


def test_make_deposit(api_client: APIClient, one_account, fix_make_deposit):
    request_payload = {'amount': 1.0}
    resp = api_client.post(
        reverse('api:account-deposit', args=[one_account.pk]),
        json.dumps(request_payload),
        content_type='application/json',
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.fixture
def fix_make_withdraw(mocker):
    mocker.patch('bank.core.services.AccountService.make_withdraw', return_value=None)


def test_make_withdraw(api_client: APIClient, one_account, fix_make_withdraw):
    request_payload = {'amount': 1.0}
    resp = api_client.post(
        reverse('api:account-withdraw', args=[one_account.pk]),
        json.dumps(request_payload),
        content_type='application/json',
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_account_detail(api_client: APIClient, one_account):
    resp = api_client.get(reverse('api:account-detail', args=[one_account.pk]))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {
        'customer': one_account.customer.pk,
        'balance': one_account.balance,
        'daily_withdrawal_limit': one_account.daily_withdrawal_limit,
        'active': one_account.active,
        'type': one_account.type,
    }


@pytest.fixture
def fix_account_block(mocker):
    mocker.patch('bank.core.services.AccountService.deactivate', return_value=None)


def test_account_block(api_client: APIClient, one_account, fix_account_block):
    resp = api_client.put(reverse('api:account-block', args=[one_account.pk]))
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.fixture
def one_transaction():
    return baker.make('Transaction')


@pytest.fixture
def fix_filter_by_account(mocker, one_transaction):
    mocker.patch(
        'bank.core.services.TransactionService.filter_by_account',
        return_value=[one_transaction],
    )
    mocker.patch(
        'bank.core.services.TransactionService.filter_by_period',
        return_value=None,
    )


def test_account_transactions(
    api_client: APIClient, one_transaction, fix_filter_by_account
):
    resp = api_client.get(
        reverse('api:account-transactions', args=[one_transaction.account.pk])
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == [
        {
            'id': one_transaction.pk,
            'account': one_transaction.account.pk,
            'amount': one_transaction.amount,
            'operation': one_transaction.operation,
        }
    ]


@pytest.fixture
def fix_filter_by_period(mocker, one_transaction):
    mocker.patch(
        'bank.core.services.TransactionService.filter_by_period',
        return_value=[one_transaction],
    )
    mocker.patch(
        'bank.core.services.TransactionService.filter_by_account', return_value=None
    )


def test_transactions_by_period(
    api_client: APIClient, one_transaction, fix_filter_by_period
):
    query_params = (
        f'start_date={date.today().isoformat()}&end_date={date.today().isoformat()}'
    )
    resp = api_client.get(
        f"{reverse('api:account-transactions', args=[one_transaction.account.pk])}?{query_params}"
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == [
        {
            'id': one_transaction.pk,
            'account': one_transaction.account.pk,
            'amount': one_transaction.amount,
            'operation': one_transaction.operation,
        }
    ]
