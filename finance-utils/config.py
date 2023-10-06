# pylint: disable-all
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, List, Optional, Tuple, Union

from strenum import StrEnum

DATA_FOLDER = "data"
# This file is used to specify the bank configurations that are unique as well as globally override categories

# Getting Amazon Purchases
# https://www.amazon.com/gp/b2b/reports/

# Use the type annotation and comments from this class to better understand its purpose
class BankColumnMaifest:
    """Contains the manifest for retrieving data from a bank csv. Most properties accept a str|int. A string
    (case sensitive) is the col name, a int is the col index"""

    def __init__(
        self,
        bank_name: str,
        headers: bool,
        date: Union[str, int],
        description: Union[str, int],
        category: Optional[Union[str, int]],
        transaction_type: Optional[Union[str, int]],
        debit_credit: Optional[List[Union[int, str]]],
        amount: Optional[Union[str, int]],
        amount_multiple: Optional[int],
        regex_filters: List[str] = [],
        amount_category_manifest: List[Tuple[str, float, Optional[str]]] = [],
        add_comma_to_csv_header: bool = False,
        aggregator: bool = False,
        account_name: Optional[Union[str, int]] = None,
    ) -> None:

        # The name of the bank
        self.name: str = bank_name.lower()

        # Are there headers in this csv
        self.headers: bool = headers

        ### The header name (case sensitive) or index

        # The date the transaction was posted or incurred (your preference)
        self.date: Union[str, int] = date

        # The description of the charge, usually the vendor or seller
        self.description: Union[str, int] = description

        # The category of this transaction (Food, travel, etc)
        self.category: Optional[Union[str, int]] = category

        # Debit or credit? This isnt used yet
        self.transaction_type: Optional[Union[str, int]] = transaction_type

        # If debit and credit are seperate columns, use this. Otherwise NONE
        self.debit_credit: Optional[List[Union[int, str]]] = debit_credit

        # This is an optional feature to fix issues with some bank's csv. This will add a comma to the last header title
        # If for some reason, your bank CSV cannot be parsed (or is parsed wrong), try setting this to true.
        self.add_comma_to_csv_header: bool = add_comma_to_csv_header  # Defalt FALSE

        # If amount is on one column only, use this
        self.amount: Optional[Union[str, int]] = amount
        
        # A number which the amount will by multiplied by.
        # Use 1 to ensure the amount is always positve.
        # Use -1 to ensure the amount is always negative.
        self.amount_multiple: Optional[int] = amount_multiple

        assert (not debit_credit and amount) or (debit_credit and not amount)  # One of these values must not be None
        
        assert (debit_credit and not transaction_type) or (transaction_type and not debit_credit) or (not debit_credit and not transaction_type) # Cannot have both of these values

        # If the regex matches this string, it will be discarded
        self.regex_filters: List[str] = regex_filters

        # The regex must match the description and amount to match
        # This overwrites the category if the name AND the amount match only on this bank
        #* Set the category to false to filter this match out
        #* Set amount to -1 or 0 to apply no amount requirement
        self.amount_category_manifest: List[Tuple[str, float, Optional[str]]] = amount_category_manifest
        
        # Is this bank an aggregator service that provides transactions for multiple banks?
        self.aggregator: bool = aggregator

        # Used for aggregator accounts
        self.account_name: Optional[Union[str, int]] = account_name

    def __repr__(self):
        return str(
            {
                "bank_name": self.name,
                "headers": self.headers,
                "date": self.date,
                "description": self.description,
                "category": self.category,
                "transaction_type": self.transaction_type,
                "debit_credit": self.debit_credit,
                "amount": self.amount,
                "amount_multiple": self.amount_multiple,
                "regex_filters": self.regex_filters,
                "amount_category_manifest": self.amount_category_manifest,
                "aggregator": self.aggregator,
                "account_name": self.account_name,
            }
        )

def get_bank_manifest(j) -> List[BankColumnMaifest]:
    '''Translates the bank info json to an objects'''
    banks: List[BankColumnMaifest] = []
    for bank_item in j.get("banks"):
        bank = BankColumnMaifest(
            bank_name=bank_item.get("bank_name", None),
            headers=bank_item.get("headers", None),
            date=bank_item.get("date", None),
            description=bank_item.get("description", None),
            category=bank_item.get("category", None),
            transaction_type=bank_item.get("transaction_type", None),
            debit_credit=bank_item.get("debit_credit", None),
            amount=bank_item.get("amount", None),
            amount_multiple=bank_item.get("amount_multiple", None),
            regex_filters=bank_item.get("regex_filters", None),
            amount_category_manifest=bank_item.get("amount_category_manifest", []),
            add_comma_to_csv_header=bank_item.get("add_comma_to_csv_header", None),
            aggregator=bank_item.get("aggregator", None),
            account_name=bank_item.get("account_name", None),
        )
        banks.append(bank)
    return banks

# This is a list of banks that the script will know about. Add as many as you want here
# The bank_name MUST be contained in the csv file name
def get_manifests() -> List[Any]:
    '''Reads the config.json'''
    p = Path(__file__).parent.absolute() / "data" / "config.json"
    print(f"Opening config at: {p.absolute()}")
    with open(p) as f:
        x = json.load(f)
        bank_manifests = get_bank_manifest(x)
    
        category_manifest = x.get("category_manifest")
        
        return [bank_manifests, category_manifest]

manifests = get_manifests()
BANK_MANIFEST: List[BankColumnMaifest] = manifests[0]

# This overrides the category of an item if the name matches the regex. Thia applies to ALL banks
CATEGORY_MANIFEST: List[Tuple[str, str]] = manifests[1]

class TransactionType(StrEnum):
    DEBIT = "Debit"
    CREDIT = "Credit"
    NONE = "None"