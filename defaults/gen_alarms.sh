#Creates a default alarms.json file from a locales file
FILE=$1
echo "OLD FILE:$FILE"
NEW_FILE='alarms'$(echo $FILE | grep -Po '(?<=pokemon).*')
echo "NEW FILE: $NEW_FILE"
echo "{" > $NEW_FILE #start of file
echo -e "\t\"alarms\":[\n\t],"  >> $NEW_FILE #alarms section
echo -e "\t\"gyms\":{\n\t\t\"To_Valor\":\"False\",\n\t\t\"To_Mystic\":\"False\",\n\t\t\"To_Instinct\":\"False\",\n\t\t\"From_Valor\":\"False\",\n\t\t\"From_Mystic\":\"False\",\n\t\t\"From_Instinct\":\"False\"\n\t},">> $NEW_FILE
echo -e "\t\"pokestops\":{\n\t\t\"Lured\":\"false\"\n\t},">> $NEW_FILE
echo -e "\t\"pokemon\":{">> $NEW_FILE
while IFS= read -r pkmn; do
	echo -e "\t\t$pkmn:\"False\"," >> $NEW_FILE
done < <(grep -Po '(?<=:)\"[^"]+\"' $FILE)
cat $NEW_FILE | sed '$ s/,$//g' > $NEW_FILE
echo -e "\t}" >> $NEW_FILE
echo "}" >> $NEW_FILE