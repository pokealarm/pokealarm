#Creates a default alarms.json file from a locales file
FILE=$1
echo "OLD FILE:$FILE"
NEW_FILE='alarms'$(echo $FILE | grep -Po '(?<=pokemon).*')
echo "NEW FILE: $NEW_FILE"
echo "{" > $NEW_FILE
echo -e "\t\"alarms\":["  >> $NEW_FILE
echo -e "\t]," >>  $NEW_FILE
echo -e "\t\"pokemon\":{">> $NEW_FILE
for pkmn in $(grep -Po '(?<=:)\"[^"]*\"' $FILE); do
	echo -e "\t\t$pkmn:\"False\"," >> $NEW_FILE
done
cat $NEW_FILE | sed '$ s/,$//g' >> $NEW_FILE
echo -e "\t}" >> $NEW_FILE
echo "}" >> $NEW_FILE