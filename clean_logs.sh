for FILE in $(find . -name '*.stdout')
do
    rm "$FILE"
done

for FILE in $(find . -name '*.stderr')
do
    rm "$FILE"
done
