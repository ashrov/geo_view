export ARTICLES_FLAG=news/articles-processed.flag

if [ -f "$ARTICLES_FLAG" ]
then
  echo "Skipping nerus processing"
else
  echo "Processing nerus" && \
  django-admin process_locations && \
  touch "$ARTICLES_FLAG" && \
  echo "Processing finished"
fi
