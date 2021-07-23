from django.urls import path, include

from bank.api.core.views import (
    AccountCreate,
    AccountDeposit,
    AccountDetail,
    AccountWithdraw,
    AccountBlock,
    AccountTransactions,
)

account_patterns = [
    path('', AccountCreate.as_view(), name='account-create'),
    path('<int:account>/', AccountDetail.as_view(), name='account-detail'),
    path('<int:account>/deposit/', AccountDeposit.as_view(), name='account-deposit'),
    path('<int:account>/withdraw/', AccountWithdraw.as_view(), name='account-withdraw'),
    path('<int:account>/block/', AccountBlock.as_view(), name='account-block'),
    path(
        '<int:account>/transactions/',
        AccountTransactions.as_view(),
        name='account-transactions',
    ),
]

urlpatterns = [
    path('accounts/', include(account_patterns)),
]
