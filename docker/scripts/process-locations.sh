export ARTICLES_FLAG=news/articles-processed.flag

if [ -f "$ARTICLES_FLAG" ]
then
  echo "Skipping articles processing"
else
  echo "Processing articles" && \
  django-admin process_locations && \
  touch "$ARTICLES_FLAG" && \
  echo "Processing finished"
fi
