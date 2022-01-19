from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from mgflask.db import Base


class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True)
    publishedAt = Column(DateTime)
    author = Column(Text)
    source = Column(String(24), nullable=False)
    title = Column(Text, nullable=False)
    right_bias = Column(Integer, default=0)
    left_bias = Column(Integer, default=0)
    content = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    url = Column(Text)
    urlToImage = Column(Text)
    comments = relationship('Comment', back_populates="article")
    article_ratings = relationship('ArticleRating', back_populates="article")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'publishedAt': self.publishedAt,
            'author': self.author,
            'source': self.source,
            'title': self.title,
            'right_bias': self.right_bias,
            'left_bias': self.left_bias,
            'content': self.content,
            'description': self.description,
            'url': self.url,
            'urlToImage': self.urlToImage,
            'comments': str(self.comments),
            'article_ratings': str(self.article_ratings),
        }

    @property
    def serialize_response(self):
        """Return object data in easily serializeable format as response to the client"""
        return {
            'id': self.id,
            'publishedAt': self.publishedAt.strftime('%Y-%m-%d %H:%M:%S') if self.publishedAt else None,
            'author': self.author,
            'source': self.source,
            'title': self.title,
            'right_bias': self.right_bias,
            'left_bias': self.left_bias,
            'content': self.content,
            'description': self.description,
            'url': self.url,
            'urlToImage': self.urlToImage,
            'comments': [comment.serialize_response for comment in self.comments],
            'article_ratings': [rating.serialize_response for rating in self.article_ratings],
        }

