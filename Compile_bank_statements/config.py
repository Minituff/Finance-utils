# pylint: disable-all
from typing import List, Optional, Tuple, Union

# This file is used to specify the bank configurations that are unique as well as globally override categories

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
        debit_credit: Optional[Tuple[Union[int, str], Union[int, str]]],
        amount: Optional[Union[str, int]],
        regex_filters: List[str] = [],
        amount_category_manifest: List[Tuple[str, float, Optional[str]]] = [],
    ) -> None:

        # The name of the bank
        self.name: str = bank_name.lower()

        # Are there headers in this csv
        self.headers: bool = headers

        # The header name (case sensitive) or index
        self.date: Union[str, int] = date
        self.description: Union[str, int] = description
        self.category: Optional[Union[str, int]] = category
        self.transaction_type: Optional[Union[str, int]] = transaction_type

        # If debit and credit are seperate columns, use this
        self.debit_credit: Optional[Tuple[Union[int, str], Union[int, str]]] = debit_credit

        # If amount is on one column only, use this
        self.amount: Optional[Union[str, int]] = amount

        assert (not debit_credit and amount) or (debit_credit and not amount)  # One of these values must not be None

        # If the regex matches this string, it will be discarded
        self.regex_filters: List[str] = regex_filters

        # The regex must match the description and amount to match
        # This overwrites the category if the name AND the amount match only on this bank
        # Set the category to NONE to filter this match out
        self.amount_category_manifest: List[Tuple[str, float, Optional[str]]] = amount_category_manifest


# This is a list of banks that the script will know about. Add as many as you want here
# The bank_name MUST be contained in the csv file name
BANK_MANIFEST: List[BankColumnMaifest] = [
    BankColumnMaifest(
        bank_name="Chase",
        headers=True,
        date="Transaction Date",
        description="Description",
        category="Category",
        transaction_type="Type",
        debit_credit=None,
        amount="Amount",
        regex_filters=[r"AUTOMATIC PAYMENT - THANK"],
    ),
    BankColumnMaifest(
        bank_name="CITI",
        headers=True,
        date="Date",
        description="Description",
        category=None,
        transaction_type=None,
        debit_credit=("Debit", "Credit"),
        amount=None,
        regex_filters=[r"AUTOPAY.*AUTO-PMT"],
    ),
    BankColumnMaifest(
        bank_name="USAA",
        headers=False,
        date=2,
        description=4,
        category=5,
        transaction_type=None,
        debit_credit=None,
        amount=6,
        regex_filters=[
            r"USAA CREDIT CARD PAYMENT",
            r"DISCOVER\s*E-PAYMENT",
            r"CITI AUTOPAY",
            r"CHASE CREDIT CRD AUTOPAY",
            r"CHASE CREDIT CRD AUTOPAY",
            # r"INTEREST PAID",
            # r"USAA FUNDS TRANSFER",
            r"CAPITAL ONE\s*CRCARDPMT",
        ],
        amount_category_manifest=[
            (r"USAA FUNDS TRANSFER", -750.0, "Savings"),
            (r"USAA FUNDS TRANSFER", -4150.0, "Savings"),
            (r"USAA FUNDS TRANSFER", -100, None),
        ],
    ),
]

# This overrides the category of an item if the name matches the regex. Thia applies to ALL banks
CATEGORY_MANIFEST: List[Tuple[str, str]] = [
    (r"In N Out", "Meals Out"),
    (r"Chipotle", "Meals Out"),
    (r"5Guys", "Meals Out"),
    (r"Pei Wei", "Meals Out"),
    (r"Chick-Fil-A", "Meals Out"),
    (r"Jamba Juice", "Meals Out"),
    (r"Mexican Food", "Meals Out"),
    (r"Ihop ", "Meals Out"),
    (r"Mr\. Spicy", "Meals Out"),
    (r"Baked Bear", "Meals Out"),
    (r"Freddy's", "Meals Out"),
    (r"Mongolian Grill", "Meals Out"),
    (r"Panera Bread", "Meals Out"),
    (r"Food at", "Meals Out"),
    (r"Crack Shack", "Meals Out"),
    (r"Ralphs", "Groceries"),
    (r"SD Gas Elec", "Power Bill"),
    (r"ATT\s*Payment", "Internet"),
    (r"Gas", "Gas"),
    (r"Shell Oil", "Gas"),
    (r"Frys Fuel", "Gas"),
    (r"Chevron", "Gas"),
    (r"Arco ", "Gas"),
    (r"Qt ", "Gas"),
    (r"Vanguard.*Investment", "Investments"),
    (r"Coinbase", "Investments"),
]
