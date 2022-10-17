#!/bin/bash
# arg 1: history file
# arg 2: transactions file from coinbase custody
# arg 3: COINBASE coin name
if [ $# -eq 0 ]; then
    echo "args: 1: history csv file, 2: transactions file from coinbase custody (NO SPACES IN FILENAME), 3: coinbase coin name (note CELO is CGLD)"
    exit 1
fi

cat <<EOF | sqlite3
.mode csv
.import "$1" history
.import "$2" transactions
create view transactions_view as select date("final status time") as date, "transaction value" as value, "transaction currency" as currency from transactions where "activity title" like "%Reward%" and "asset" like "$3";
create view history_view as select date(date) as date, cast(price as 'decimal') as price from history;
select sum(price * value) from transactions_view, history_view where transactions_view.date = history_view.date;

EOF
