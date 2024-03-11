from collections import defaultdict
import math
'''
## Settle money, 类似splitwise, 类似465

https://leetcode.com/problems/optimal-account-balancing/description/

    1. input 是transaction list, [[payer: 'A',amount: 4000,payees: ['A', 'B', 'C', 'D'.]],   [payer: 'B',amount: 2000,payees: ['A', 'B']]]

    2. return  C转A 2000， D转A…..，B转A….这样


O(n!)
'''
class Solution:
    def minTransfers(self, input_transactions):
        balance = defaultdict(int)
        transactions = []
        for trans in input_transactions:
            amount = trans['amount']
            payer = trans['payer']
            payees = trans['payees']
            # Split the transaction amount among the payees (excluding the payer)
            per_person = round(amount / len(payees))
            for payee in payees:
                transactions.append((payer, payee, per_person))
        for from_, to, amt in transactions:
            balance[to] += amt
            balance[from_] -= amt
            
        # Filter out zero balances and create a list of non-zero balances
        debts = list(filter(lambda x: x != 0, balance.values()))
        people = list(filter(lambda x: balance[x] != 0, balance.keys()))
        # Helper function to find the min transactions to settle starting from 'index'
        def backtrack(index):
            # Skip already settled accounts
            while index < len(debts) and debts[index] == 0:
                index += 1
            if index == len(debts):
                return [], 0

            min_txns = math.inf
            min_trans_list = []
            for j in range(index + 1, len(debts)):
                # Pruning. debts[j] must be non zero and of different sign
                if debts[j] * debts[index] < 0:
                    # Temporarily settle the debt
                    debts[j] += debts[index]
                    next_trans_list, num_txns = backtrack(index + 1)
                    # If better solution found, update the result
                    if num_txns + 1 < min_txns:
                        min_txns = num_txns + 1
                        amt = abs(debts[index])
                        # Determine the payer and payee based on the sign of debts[index]
                        transaction = f"{people[index] if debts[index] > 0 else people[j]} pays {people[j] if debts[index] > 0 else people[index]} ${amt}"
                        # Include current transaction in the list
                        min_trans_list = next_trans_list + [transaction]
                    # Backtrack the temporary change
                    debts[j] -= debts[index]
            return min_trans_list, min_txns

        transactions, min_txns = backtrack(0)
        return transactions, min_txns

# Example usage:
input_transactions = [
    {'payer': 'xia', 'amount': 15, 'payees': ['xia', 'hao']},
    {'payer': 'hao', 'amount': 62, 'payees': ['xia', 'hao']}
]

solution = Solution()
final_transactions = solution.minTransfers(input_transactions)
print(final_transactions)