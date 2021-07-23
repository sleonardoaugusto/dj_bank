from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from bank.core.models import Account, Customer, Transaction
from bank.core.services import AccountService, TransactionService


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'name',
            'document_id',
            'birth_date',
        )


class AccountCreate(GenericAPIView):
    class InputSerializer(serializers.ModelSerializer):
        customer = CustomerSerializer(required=True)

        class Meta:
            ref_name = 'AccountCreate'
            model = Account
            fields = ('type', 'customer')

    serializer_class = InputSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_service = AccountService()
        account_service.create(**serializer.validated_data)
        return Response(status=status.HTTP_201_CREATED)


class AccountDeposit(GenericAPIView):
    class InputSerializer(serializers.ModelSerializer):
        amount = serializers.FloatField(required=True)

        class Meta:
            ref_name = 'AccountDeposit'
            model = Account
            fields = ('amount',)

    serializer_class = InputSerializer

    def post(self, request, account):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_service = AccountService()
        account_service.make_deposit(account=account, **serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountWithdraw(GenericAPIView):
    class InputSerializer(serializers.ModelSerializer):
        amount = serializers.FloatField(required=True)

        class Meta:
            ref_name = 'AccountWithdraw'
            model = Account
            fields = ('amount',)

    serializer_class = InputSerializer

    def post(self, request, account):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_service = AccountService()
        account_service.make_withdraw(account=account, **serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountDetail(GenericAPIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            ref_name = 'AccountDetail'
            model = Account
            fields = (
                'customer',
                'balance',
                'daily_withdrawal_limit',
                'active',
                'type',
            )

    serializer_class = OutputSerializer

    def get(self, request, account):
        record = Account.objects.get(pk=account)
        serializer = self.serializer_class(record)
        return Response(serializer.data)


class AccountBlock(APIView):
    def put(self, request, account):
        account_service = AccountService()
        account_service.deactivate(account=account)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountTransactions(GenericAPIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            ref_name = 'AccountTransaction'
            model = Transaction
            fields = (
                'id',
                'account',
                'amount',
                'operation',
            )

    serializer_class = OutputSerializer
    queryset = Transaction.objects.all()

    def get(self, request, account):
        transaction_service = TransactionService()
        transactions = transaction_service.filter_by_account_or_period(
            request=request, account=account
        )
        data = self.serializer_class(transactions, many=True).data
        return Response(data, status=status.HTTP_200_OK)
