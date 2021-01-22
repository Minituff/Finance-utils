# Compile Bank Statements

The purpose of this script is to compile csv bank statements into one unified CSV.
Banks will often use different formats,columns, and headers when their data is exported; sometimes even different accounts within the same bank will be unique. 

## Setup Instructions

1. Create a `config.json` file
    * This file needs to reside `Finance-utils\Compile_bank_statements\config.json`
    * Bank Format

    ```javascript
   {
            "bank_name": "AMZN", (str)
            // This is the name of the bank. This can be anything, but it must match the first part of the csv file in the data folder.
            
            "headers": true, (bool) Default=true
            // Does the csv file have headers? If true then "date" "description "category "transaction_type" and "amount can be Strings, otherwise they should correspond with the column starting from 0. If this is false, then you must use index number for columns.

            "date": "Transaction Date",  (int|str)
            // The column name or index where the date is shown
            
            "description": "Description", (int|str)
            // The column name or index where the description (or title) is shown
            
            "category": "Category", (int|str)
            // The column name or index where the item category is shown (Food, travel, etc.)
            
            "transaction_type": "Type", *Optional* (int|str)
            // The column name or index where the transction is shown
            
            "amount": "Amount", (int|str) 
            // The column name or index where the transaction amount is stored
            
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
    * These files needs to reside `Finance-utils\Compile_bank_statements\data\`
        * If the folder does not exist, create it
1. Run the script
    * `Finance-utils> python compile_bank_satements.py`
    * Report issues or suggest new features

1. Use Output
    * Two files will be created:
        * `Complied expenses.csv` Contains all the purchase transactions
        * `Complied income.csv` Contains all the incoming money transactions (interest paymenyts, etc)

## Notes

The `default_config.json` is ignored and will not be used, feel free to copy it to your `config.json` as a starting point
