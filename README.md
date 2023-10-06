# Compile Bank Statements

The purpose of this script is to compile csv bank statements into one unified CSV.

Banks will often use different formats, columns, and headers when their data is exported; sometimes even different accounts within the same bank will be unique. This makes accounting using spreadsheets a chore.

A master `expenses` CSV will be created with the following format:

| Date | Expense | Amount | Category | Bank |
| ---- | --------| ------ | -------- | ---- |
| 12/25/21 | Costco Gas (10.0 gal) | $50.00 | Gas | Chase |
| 12/23/21 | Oil Change | $50.00 | Car Maintenance | Chase |
| 12/21/21 | Car Wash | $20.00 | Car Maintenance | Chase |

These files are grouped either by `purchases` or `expenses`

## Running in docker

```bash
docker run -v DATA-DIR:/app/finance-utils/data ghcr.io/minituff/finance-utils:main
```

The mapped data directory needs to contain:

* `config.json`
* Bank statements ending in `.csv`

## Setup Instructions

1. Create a `config.json` file (use the *default* as an example)
    * This file needs to reside `Finance-utils\config.json`
    * Bank Format

    ```javascript
   {
            "bank_name": "AMZN", (str)
            // This is the name of the bank. This can be anything, but it must match the first part of the csv file in the data folder.
            
            "headers": true, (bool) Default=true
            // Does the csv file have headers? If true then "date" "description "category "transaction_type" and "amount can be Strings, otherwise they should correspond with the column starting from 0. If this is false, then you must use index number for columns.

            "date": "Transaction Date",  (int|str)
            // The column name or index (starting from 0) where the date is shown
            
            "description": "Description", (int|str)
            // The column name or index where the description (or title) is shown
            // Place an empty string "" if the bank does not provide a descption
            
            "category": "Category", (int|str)
            // The column name or index where the item category is shown (Food, travel, etc.)
            
            "transaction_type": "Type", *Optional* (int|str)
            // The column name or index where the transction type is shown (Debit, Credit)
            // Use this parameter to tell the script if this was an expense or incomne based off the value in this column
            // Cannot be combined with the `debit_credit` column
            
            "amount": "Amount", (int|str) 
            // The column name or index where the transaction amount is stored

            "amount_multiple": "Amount", (int) 
            // A number which the amount will by multiplied by.
            // Use 1 to ensure the amount is always positve.
            // Use -1 to ensure the amount is always negative.
            
            "debit_credit": ["Debit","Credit"], *Optional* (List[int|str])
            /// FORMAT: [debit_column_identifier (int|str) , credit_column_identifier (int|str)]
            // If the csv uses unique colmns for debit and credit instead of positve and negative number then specify them here (either string or index as usual) Two items max, and they must be in the order of debit, then credit.

            "add_comma_to_csv_header": false, *Optional* (bool) Default=false 
            // This is an optional feature to fix issues with some bank's csv. This will add a comma to the last header title. If for some reason, your bank CSV cannot be parsed (or is parsed wrong), try setting this to true.

            "regex_filters": ["AUTOMATIC PAYMENT - THANK"], *Optional* (List[str])
            // Use these to filter out transactions that match the regex (or string) that is inputted in this list. Add as many items as you want.


            "amount_category_manifest": [["FUNDS TRANSFER", -100, "Savings"]] *Optional* (List[str|int])
            /// FORMAT: ["regex_match" (str) , amount (int) , "category" (str) ]
            // Allows you to manually reprogram the category of any transaction in this bank based on a regex AND amount match. If the item matches the regex (item 1) and amount (item 2) the category will be changed to what you set in item 3. This will override the category of the bank if it's tehre
            
            // Set amount to -1 or 0 to apply no amount requirement. This would allow you to reprogram the category on any regex match, regardless of price.
            // Set the category to false to filter this match out--it would work exactly like "regex_filters"
        },
    ```

1. Update category manifest (optional)
    * This json property exists in the `config.json` file

    ```javascript
    "category_manifest": [["In N Out","Meals Out"],["AA Flight123","Travel"]], *Optional* (List[str|int])
    // This allows you to override the categories of items that match the regex. Will be applied globally and after the `amount_category_manifest` for the bank
    ```

1. Add bank statements
    * Export bank statements in a `.csv` format and place them into the `data` folder.
    * These files needs to reside `Finance-utils\data\`
        * If the folder does not exist, create it
1. Run the script
    * See [Runing in Docker](#running-in-docker)
    * Report issues or suggest new features

1. Use Output
    * Two files will be created:
        * `Complied expenses.csv` Contains all the purchase transactions
        * `Complied income.csv` Contains all the incoming money transactions (interest paymenyts, etc)

## Notes

Amazon Order history: https://www.amazon.com/b2b/reports

* The `default_config.json` is ignored and will not be used, feel free to copy it to your `config.json` as a starting point

* You can also update the `config.py` which allows for full customization

<br>
<br>
<br>
<br>

## Bulding the docker image (developers only)

```bash
docker image rm finance-utils:0.0.1 -f
docker build -t finance-utils:0.0.1 .
```
