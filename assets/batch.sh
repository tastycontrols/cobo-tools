#!/usr/bin/env bash
# batch.sh: suggested method for generating a COBO build
# SLD 2021
#

# !!!!!!!!!!!! CHANGE THIS !!!!!!!!!!!!
collection=cobo-sld
# !!!!!!!!!!!! ----------- !!!!!!!!!!!!

# Make name- and date-stamped main directory and clone in recipes
# Start by generating name for destination directory
#tohash=$collection\_$(date +"%Y-%m-%d")
tohash=$collection

# If directory already exists (hopefully doesn't), remove it
rm -rf ./$tohash

# Create directory and clone in recipes
mkdir ./$tohash
mkdir ./$tohash/SOURCES
cp ./sources/*.* ./$tohash/SOURCES

# In the main directory, build a global JSON file
python3 cobo.py build sources=./$tohash/SOURCES output=./$tohash/cobo.json &>/dev/null

# In the main directory, create a list of all tags from global JSON file
python3 cobo.py get-tags input=./$tohash/cobo.json output=./$tohash/tags.txt &>/dev/null

# Pass through tags in tag file
# For each tag: subset the global JSON into a subset JSON, in the main directory
# Then compile each subset JSON to MD, in the main directory
subsets=$(cat ./$tohash/tags.txt)
for indiv_subset in $subsets
do
  python3 cobo.py subset tag=$indiv_subset input=./$tohash/cobo.json output=./$tohash/$indiv_subset.json.subset &>/dev/null
  python3 cobo.py compile-md input=./$tohash/$indiv_subset.json.subset output=./$tohash/01_$indiv_subset.md &>/dev/null
done

# In the main directory, compile global JSON to MD
python3 cobo.py compile-md input=./$tohash/cobo.json output=./$tohash/00_global.md &>/dev/null

# Create a subdirectory for all JSON files, and migrate
mkdir ./$tohash/JSON
mv ./$tohash/*.json ./$tohash/JSON/
mv ./$tohash/*.json.subset ./$tohash/JSON/

################
# DEPRECATED: convert MD files to HTML and migrate
#
#
# Pass through MD files in the main directory and create HTML files
#mdfiles=$(ls ./$tohash/*.md)
#for this_mdfile in $mdfiles
#do
#  pandoc -o ${this_mdfile/md/html} $this_mdfile
#done
#
# Create a subdirectory for all HTML files, and migrate
#mkdir ./$tohash/HTML
#mv ./$tohash/*.html ./$tohash/HTML/
#
#
################

# Create a subdirectory for all MD files, and migrate
mkdir ./$tohash/MARKDOWN
mv ./$tohash/*.md ./$tohash/MARKDOWN/

# Clean up tags
#rm ./$tohash/tags.txt

# Start making README.md
# Quietly remove existing copy, if exist
rm ./$tohash/README.md &>/dev/null

# Next, create new README.md, and add prelude
echo "
# Cookbook \`\`\`$collection\`\`\`
">> ./$tohash/README.md

# Add Markdown ToC links
echo "#### All Recipes">> ./$tohash/README.md
echo [All Recipes]\(./$tohash/MARKDOWN/00_global.md\)>> ./$tohash/README.md
echo "#### Recipes By Tag">> ./$tohash/README.md
tags=$(cat ./$tohash/tags.txt)
for this_tag in $tags
do
  echo [$this_tag]\(./$tohash/MARKDOWN/01_$this_tag.md\) \\>> ./$tohash/README.md
done
head -n -1 ./$tohash/README.md > ./$tohash/README.md.tmp
mv ./$tohash/README.md.tmp ./$tohash/README.md
echo [$this_tag]\(./$tohash/MARKDOWN/01_$this_tag.md\)>> ./$tohash/README.md






# !!!!!!!!!!! BLOCK COMMENT !!!!!!!!!!!
#:<<'EOF'
#EOF
