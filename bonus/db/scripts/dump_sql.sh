#!/bin/bash
echo "Welcome to $0"

echo -n "Enter username: "
read username

echo "Enter password: "
read -s password

echo -n "Enter database host: "
read host

echo -n "Enter database port: "
read port

echo -n "Enter database(s) to export [syntax: db1 [db2 db3]]: "
read db

echo -n "Enter save file name: "
read savefile

if [ "$db" == "" ] || [ "$db" == "\n" ]; then
    echo "No database specified, dumping all databases present"
    db="--all-databases"
else
    db="--databases $db"
fi

echo "Dumping sql from database:"
mariadb-dump -u $username -p$password -h $host -P $port $db >$savefile.sql
if [ $? -ne 0 ]; then
    STATUS=$?
    echo "Error: Failed to dump data"
    exit $STATUS
fi
echo "Data dumped to: $savefile.sql"

echo "When displayed, press the Q key to exit."
echo "Display file content? [(Y)es/(n)o]"
read -n 1 choice

echo "Displaying file content:"
if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
    cat $savefile.sql | less
fi

echo "(c) Created by Henry Letellier"
