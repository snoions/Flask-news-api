from flask import (
    Blueprint,
    request,
    jsonify
)
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from mgflask.db import db_session
from mgflask.models import Article
from sqlalchemy import and_, or_
from sqlalchemy.sql import func
import os

bp = Blueprint('news', __name__, url_prefix='/news')

# Query parameters should be sent in json format in request body. Accepted parameters are values are defined below.
# Each query parameter can contain a single or a list of accepted values.

# these columns are defined in model.py to match news.api parameters: https://newsapi.org/docs/endpoints/top-headlines
# exact_columns need to match exactly
EXACT_COLUMNS = ['id', 'author', 'source', 'url', 'urlToImage']
# fuzzy_columns uses the LIKE operator to partically match
FUZZY_COLUMNS = ['title', 'content', 'description']
# for range columns the first two values will be interpreted as the lower and upper bouond and the rest discarded (if only one value then it will an exact match)
RANGE_COLUMNS = ['leftBias', 'right-Bias']
# same as range columns except when given only one time string the range will be one day from that time
DATE_COLUMNS = ['publishedAt']
# query on comments and article_ratings not yet implemented

# upper limit on the number of to return
LIMIT_ARTICLE_PARAM = 'limit_articles'

# if this param is givemn, the results will be partitioned into subarrays according to its value
# must be a column name
PARTITION_BY_PARAM = 'partition_by'

# search among all articles


@bp.route('/', methods=['GET'])
def get_articles():
    params = request.args
    print("params:", params)
    filters = []
    statusCode = 200

    if not params:
        articles = db_session.query(Article)
        return jsonify({"articles": [article.serialize_response for article in articles], "statusCode": statusCode})

    for col in Article.__table__.columns:
        param = params.getlist(col.key)
        if len(param)==1:
            param = param[0]
        if col.key in EXACT_COLUMNS and param:
            if isinstance(param, list):
                filters.append(col.in_(param))
            else:
                filters.append(col == param)
        elif col.key in FUZZY_COLUMNS and param:
            if isinstance(param, list):
                fuzzy_filters = [col.ilike("%"+each+"%") for each in param]
                filters.append(or_(*fuzzy_filters))
            else:
                filters.append(col.ilike("%"+param+"%"))
        elif col.key in RANGE_COLUMNS and param:
            if isinstance(param, list):
                filters.append(col.between(param[0], param[1]))
            else:
                filters.append(col == param)
        elif col.key in DATE_COLUMNS and param:
            if isinstance(param, list):
                filters.append(col.between(param[0], param[1])) 
            else:
                if (os.environ.get('FLASK_ENV') is None):
                    filters.append(col.between(
                        param, func.date(param, '+1 day')))
                else:
                    filters.append(col.between(
                        param, func.ADDDATE(param, 1)))


    articles = db_session.query(Article).filter(and_(*filters))

    partition_by = params.get(PARTITION_BY_PARAM)
    if partition_by:
        articles = articles.order_by(params.get(PARTITION_BY_PARAM))
    if params.get(LIMIT_ARTICLE_PARAM):
        articles = articles.limit(params.get(LIMIT_ARTICLE_PARAM))
    if partition_by:
        formatted = partition_ordered(articles, partition_by)
    else:
        formatted = [article.serialize_response for article in articles]

    return jsonify({"articles": formatted, "statusCode": statusCode})


def partition_ordered(articles, partition_by):
    if not articles.all():
        return {}
    partition_key = getattr(articles[0], partition_by)
    partitions = {}
    subpartition = []
    for article in articles:
        current_key = getattr(article, partition_by)
        if partition_key == current_key:
            subpartition.append(article.serialize_response)
        else:
            partitions[partition_key] = subpartition
            subpartition = [article.serialize_response]
            partition_key = current_key

    partitions[partition_key] = subpartition
    return partitions


''' not completed
@bp.route('/by_sources', methods=['GET'])
def get_articles_by_sources():
    from  mgflask.news_retrieval import TARGET_SOURCES
    params = request.json
    filters = []
    statusCode = 200
    for source in target sources:
        articles = db_session.query(Article).filter
    articles = db_session.query(Article).filter(and_(*filters))

    return jsonify({"articles": formatted, "statusCode": statusCode})
'''

