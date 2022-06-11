FROM python:3.9

RUN mkdir -p /usr/src/rss-app/
WORKDIR /usr/src/rss-app/

COPY . /usr/src/rss-app/
COPY requirements.txt .

# next command clone github repo (secret token is required) and run docker container from github project
# RUN git clone -b master https://:{SECRET_TOKEN}@{PATH_TO_THE_GITHUB_PROJECT_WITHOUT_HTTPS} /usr/src/rss-app/

RUN pip install -e /usr/src/rss-app/

CMD ["rss-reader", "https://news.yahoo.com/rss/", "--date", "20211020", "--verbose", "--to-html", ".", "--colorize", "--json"]