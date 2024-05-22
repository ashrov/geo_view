export NERUS_URL=${NERUS_URL:-'https://storage.yandexcloud.net/natasha-nerus/data/nerus_lenta.conllu.gz'}
export NOMINATIM_URL=${NOMINATIM_URL:-'http://nominatim:8080/search'}
export NERUS_FILE=news/nerus.conllu.gz
export NERUS_PROCESSED=news/nerus-processed.flag

if [ -f "$NERUS_FILE" ]
then
  echo "Skipping downloading nerus dataset"
else
  echo "Downloading nerus dataset from $NERUS_URL" && \
  wget "$NERUS_URL" -O "$NERUS_FILE"
fi

if [ -f "$NERUS_PROCESSED" ]
then
  echo "Skipping nerus processing"
else
  echo "Processing nerus" && \
  django-admin process_locations --nerus-file "$NERUS_FILE" --nominatim-url "$NOMINATIM_URL" && \
  touch "$NERUS_PROCESSED" && \
  echo "Processing finished"
fi
