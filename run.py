from __future__ import absolute_import

# pylint: disable-all
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

import pandas as pd
from dateutil.parser import parse as parsedate

# If using Pylance/Pyright, add the following to the project's vscode settings.json
# * "python.analysis.extraPaths": ["./Compile_bank_statements"]
from config import CATEGORY_MANIFEST  # type:ignore
from config import BANK_MANIFEST, DATA_FOLDER, BankColumnMaifest


class Transaction:
    """A dataclass which contains the properites of a transaction"""

    def __init__(self) -> None:
        self.date: datetime
        self.amount: float
        self.description: str
        self.category: Optional[str]
        self.bank_name: str

    def __repr__(self) -> str:
        return f"{self.bank_name} - {self.amount}$ - {self.date} - {self.description} - {self.category}"


class CompileBanks:
    def __init__(self) -> None:
        self.input_path: Path = Path(os.path.dirname(os.path.realpath(__file__)) + "/" + DATA_FOLDER)
        if not self.input_path.exists():
            print("Creating directory: " + str(self.input_path))
            os.makedirs(self.input_path)
        # timestamp = f'{datetime.now().strftime("%Y-%m-%d-%H%M")}'
        self.expenses_output_path: str = os.path.join(self.input_path, "Compiled expenses.csv")
        self.income_output_path: str = os.path.join(self.input_path, "Compiled Income.csv")

        self.column_manifest: List[BankColumnMaifest] = BANK_MANIFEST

        # If a match is found, replace that category with the string
        self.category_manifest: List[Tuple[str, str]] = CATEGORY_MANIFEST

    def get_docs(self) -> List[str]:
        """Returns a list of paths of csv files in the current python file dir"""
        files = []
        for filename in os.listdir(self.input_path):
            if not filename.endswith((".csv", ".CSV")):
                continue
            if filename in self.expenses_output_path or filename in self.income_output_path:
                continue

            files.append(os.path.join(self.input_path, filename))

        if not files:
            print("No files detected. Plase the statements in the this folder:", self.input_path)
        return files

    def get_bank_manifest_from_path(self, file_path: str) -> Optional[BankColumnMaifest]:
        """Finds the cooresponding bank manifest for the csv file in process"""
        for bank in self.column_manifest:
            if bank.name in file_path.lower():
                return bank
        return None

    @staticmethod
    def assign_index_from_col_name(bank: BankColumnMaifest, cols: List[str]):
        """Replaces all strings with ints in the bank manifest. Allows for quick index access"""
        try:
            if isinstance(bank.date, str):
                bank.date = cols.index(bank.date)
            if isinstance(bank.description, str):
                bank.description = cols.index(bank.description)
            if isinstance(bank.category, str):
                bank.category = cols.index(bank.category)
            if isinstance(bank.transaction_type, str):
                bank.transaction_type = cols.index(bank.transaction_type)
            if isinstance(bank.amount, str):
                bank.amount = cols.index(bank.amount)
            # Assigns debit and credit columns to indexes
            if isinstance(bank.debit_credit, (tuple, List)):
                debit_credit_l = []
                if isinstance(bank.debit_credit[0], str):
                    debit_credit_l = [cols.index(str(bank.debit_credit[0])), bank.debit_credit[1]]
                if isinstance(bank.debit_credit[1], str):
                    if not debit_credit_l:
                        debit_credit_l = [bank.debit_credit[0], cols.index(str(bank.debit_credit[1]))]
                    else:
                        debit_credit_l = [debit_credit_l[0], cols.index(str(bank.debit_credit[1]))]
                if debit_credit_l:
                    bank.debit_credit = [debit_credit_l[0], debit_credit_l[1]]
        except ValueError as e:
            # TODO: Add color here
            if str(e) == "'' is not in list":
                print('You cannot have bank manifest items with empty strings "". Delete these items and try again.')
            print(f"Error with bank: {bank.name}. Ensure the columns in the csv match the bank manifest - {e.args[0]}")

    @staticmethod
    def get_date_from_row(bank: BankColumnMaifest, row) -> datetime:
        if isinstance(bank.date, int):
            date_time_obj = parsedate(str(row[bank.date]))
            return date_time_obj
        else:
            raise TypeError()

    @staticmethod
    def get_amount_from_row(bank: BankColumnMaifest, row) -> float:
        if bank.amount:
            if str(row[bank.amount]).startswith("--"):
                return float(row[bank.amount][2:])
            if str(row[bank.amount]).startswith("$"):
                return float(row[bank.amount][1:])
            return float(row[bank.amount])

        if bank.debit_credit:
            deb: float = row[bank.debit_credit[0]]
            cred: float = row[bank.debit_credit[1]]

            if deb and cred:
                raise ValueError("Cannot be credit and debit at the same time")
            if deb:
                return deb * -1
            elif cred:
                return abs(cred)
            else:
                return 0
        else:
            raise ValueError("Cannot find amount maifest for ", bank.name)

    @staticmethod
    def filter_transatction(bank: BankColumnMaifest, desc: str) -> bool:
        """Returns true if the purchase should be filtered"""
        for regex in bank.regex_filters:
            match = re.search(regex, str(desc), re.M)
            if match:
                return True

        return False

    def add_category(self, transaction: Transaction) -> None:
        for line, new_cat in self.category_manifest:
            match = re.search(line, transaction.description, re.I)
            if match:
                transaction.category = new_cat
                return

    @staticmethod
    def update_category_with_amount(bank: BankColumnMaifest, transaction: Transaction) -> None:
        for line, amt, new_cat in bank.amount_category_manifest:
            match = re.search(line, transaction.description, re.I)
            if match:
                if amt == 0 or amt == -1:  # If the amount is 0/-1 then just change the category
                    transaction.category = new_cat
                elif transaction.amount == amt:  # Allows filtering of transactions on the bank of the exact price
                    if new_cat is None or new_cat is False:
                        transaction.amount = 0.00
                        transaction.category = "Filtered"
                    else:
                        transaction.category = new_cat
                    return

    @staticmethod
    def add_comma_to_csv_header(doc_path: str) -> None:
        """This section of code adds a comma to the first row (headers) in the csv"""
        with open(doc_path, mode="r+") as f:
            lines = f.readlines()
            f.seek(0)
            line_1 = lines[0].rstrip() + ",\n"
            updated_lines = [line_1] + lines[1:]
            f.writelines(updated_lines)

    def process_docs(self) -> List[Transaction]:
        """Loops over all docs found and returns a list of transaction objects"""
        transaction_list: List[Transaction] = []

        for doc_path in self.get_docs():
            bank = self.get_bank_manifest_from_path(doc_path)
            if not bank:
                print("Could not match the bank manifest for:", doc_path)
                continue
            print(f"Getting transactions from {bank.name} located at: {doc_path}")

            if bank.add_comma_to_csv_header is True:
                self.add_comma_to_csv_header(doc_path)

            df_nan = pd.read_csv(doc_path)  # To be immediatly changed and forgotten
            df = df_nan.where(pd.notnull(df_nan), None)  # Replaces 'nan' value with None

            # Extracts bank headers into column indexes. Example: Posting date = 1 (second column header)
            self.assign_index_from_col_name(bank, list(df.columns))

            for row in df.itertuples(index=False):
                if row[0] is None:
                    break  # Stops when a there are no rows with data left

                transaction = Transaction()
                transaction.bank_name = bank.name
                
                try:
                    if not bank.description or bank.description == "":
                        transaction.description = ""
                        
                    else:
                        transaction.description = row[bank.description]  # TODO: This line crashes if the columns dont match
                except:
                    print(f"Error in bank: ${bank.name}. The configured columns do not match.. Error occured on row ${row}")
                
                if self.filter_transatction(bank, transaction.description):
                    continue  # Removes anything that should be filtered
                
                # Switch to title case AFTER filters have been applied
                transaction.description = transaction.description.title()
                
                transaction.date = self.get_date_from_row(bank, row)
                transaction.category = row[bank.category] if bank.category else None
                self.add_category(transaction)
                transaction.amount = self.get_amount_from_row(bank, row)
                
                if bank.amount_multiple and isinstance(bank.amount_multiple, (int, float)):
                    transaction.amount = abs(transaction.amount) * bank.amount_multiple
                
                self.update_category_with_amount(bank, transaction)
                transaction_list.append(transaction)

        return transaction_list

    def make_df(self):
        """Creates a dataframe and writes it to a csv"""
        transactions = self.process_docs()
        income_data = []
        expenes_data = []

        for transaction in transactions:
            data = {
                "Date": transaction.date,
                "Item": transaction.description,  # Title case is applied later
                "Cost": abs(transaction.amount),
                "Category": transaction.category,
                "Bank": transaction.bank_name,
            }
            if transaction.amount > 0:
                income_data.append(data)
            elif transaction.amount < 0:
                expenes_data.append(data)
            # This excludes items that are $0.00

        if income_data:
            income_df = pd.DataFrame(income_data)
            income_df.sort_values(by=["Date"], inplace=True, ascending=True)
            income_df.to_csv(self.income_output_path, index=False)
            print("Saved income to:", self.income_output_path)
        if expenes_data:
            expenses_df = pd.DataFrame(expenes_data)
            expenses_df.sort_values(by=["Date"], inplace=True, ascending=True)
            expenses_df.to_csv(self.expenses_output_path, index=False)
            print("Saved expenses to:", self.expenses_output_path)


def run():
    CompileBanks().make_df()


if __name__ == "__main__":
    run()
