export NEWS_URL=${NEWS_URL:-'https://github.com/yutkin/Lenta.Ru-News-Dataset/releases/download/v1.1/lenta-ru-news.csv.bz2'}
export NEWS_FILE_BZ2=news/news.csv.bz2
export NEWS_FILE_GZ=news/news.csv.gz

if [ -f "$NEWS_FILE_GZ" ]
then
  echo "Skipping downloading dataset"
else
  echo "Downloading news dataset from $NEWS_URL" && \
  wget "$NEWS_URL" -O "$NEWS_FILE_BZ2" && \
  echo "Changing format to gzip" && \
  bzcat "$NEWS_FILE_BZ2" | gzip -c > "$NEWS_FILE_GZ" && \
  rm "$NEWS_FILE_BZ2"
fi

echo "Importing to database" && \
django-admin import_news --news-file "$NEWS_FILE_GZ" && \
rm  "$NEWS_FILE_GZ"

echo "Importing finished"
