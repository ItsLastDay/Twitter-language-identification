TARGET_FOLDER="../parsed_text_features"
if [ ! -d $TARGET_FOLDER ]; then
    mkdir $TARGET_FOLDER
fi
rm $TARGET_FOLDER/*
python text_with_features_getters.py 3 ../twits/ground_truth $TARGET_FOLDER/dutch_gt dutch 
python text_with_features_getters.py 3 ../twits/ground_truth $TARGET_FOLDER/english_gt english
python text_with_features_getters.py 3 ../twits/ground_truth $TARGET_FOLDER/french_gt french
python text_with_features_getters.py 3 ../twits/ground_truth $TARGET_FOLDER/german_gt german 
python text_with_features_getters.py 3 ../twits/ground_truth $TARGET_FOLDER/spanish_gt spanish 

python text_with_features_getters.py 3 ../twits/tatarcha $TARGET_FOLDER/tatarcha
python text_with_features_getters.py 3 ../twits/chuvash $TARGET_FOLDER/chuvash
python text_with_features_getters.py 3 ../twits/turkish $TARGET_FOLDER/turkish

python text_with_features_getters.py 2 ../twits/russian/positive.csv $TARGET_FOLDER/russian_huge1
python text_with_features_getters.py 2 ../twits/russian/negative.csv $TARGET_FOLDER/russian_huge2

python text_with_features_getters.py 1 ../twits/liga/de_DE $TARGET_FOLDER/german_liga
python text_with_features_getters.py 1 ../twits/liga/en_UK $TARGET_FOLDER/english_liga
python text_with_features_getters.py 1 ../twits/liga/es_ES $TARGET_FOLDER/spanish_liga
python text_with_features_getters.py 1 ../twits/liga/fr_FR $TARGET_FOLDER/french_liga
python text_with_features_getters.py 1 ../twits/liga/it_IT $TARGET_FOLDER/italian_liga
python text_with_features_getters.py 1 ../twits/liga/nl_NL $TARGET_FOLDER/dutch_liga


for language in 'russian' 'marathi' 'nepali' 'urdu' 'ukrainian' 'bulgarian' 'farsi' 'hindi' 'arabic'
do
    python text_with_features_getters.py 0 "../twits/bergsma/${language}.dev" "$TARGET_FOLDER/${language}1_bergsma"
    python text_with_features_getters.py 0 "../twits/bergsma/${language}.test" "$TARGET_FOLDER/${language}2_bergsma"
    python text_with_features_getters.py 0 "../twits/bergsma/${language}.train" "$TARGET_FOLDER/${language}3_bergsma"
done

python merge_files.py $TARGET_FOLDER 4
python make_txt.py $TARGET_FOLDER
python gen_stat.py $TARGET_FOLDER
