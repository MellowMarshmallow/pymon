#!/usr/bin/env bash


# remove existing data
rm -rf ./download && echo "delete ./download ... done" || echo "./download does not exist"


# create directories
mkdir -p ./download/ExcelBinOutput ./download/TextMap && echo "create directories ... done"


# download
svn checkout https://github.com/Dimbreath/GenshinData/trunk/ExcelBinOutput ./download/ExcelBinOutput > /dev/null && echo "download data ... done"
curl -L -o ./download/TextMap/TextMapEN.json https://raw.githubusercontent.com/Dimbreath/GenshinData/master/TextMap/TextMapEN.json && echo "download text map ... done"
