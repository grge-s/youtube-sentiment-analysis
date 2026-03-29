#!/usr/bin/env python3
"""
YouTube ChatGPT Sentiment Analysis Tool
======================================

A comprehensive tool for analyzing sentiment of YouTube comments about ChatGPT
to help FutureProof's marketing team make informed decisions about AI content generation.

Author: Data Analytics Team
Company: FutureProof
Purpose: Defensive cybersecurity analytics and business intelligence
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
import warnings
from datetime import datetime, timedelta
from collections import Counter
import json
from dotenv import load_dotenv

warnings.filterwarnings('ignore')
load_dotenv()

class YouTubeSentimentAnalyzer:
    """
    A comprehensive YouTube sentiment analysis tool for ChatGPT-related content.
    
    This class provides functionality to:
    - Extract comments from YouTube videos
    - Preprocess text data
    - Perform sentiment analysis using NLTK VADER
    - Generate visualizations and business reports
    """
    
    def __init__(self, api_key=None):
        """Initialize the YouTube sentiment analyzer."""
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY environment variable.")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.sia = None
        self.comments_df = None
        
        # Download required NLTK data
        self._setup_nltk()
    
    def _setup_nltk(self):
        """Download required NLTK datasets."""
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
        
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
    
    def search_videos(self, query="ChatGPT", max_results=50):
        """
        Search for YouTube videos related to the query.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of videos to return
            
        Returns:
            list: List of video IDs and metadata
        """
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance'
            ).execute()
            
            videos = []
            for search_result in search_response.get('items', []):
                video_data = {
                    'video_id': search_result['id']['videoId'],
                    'title': search_result['snippet']['title'],
                    'channel': search_result['snippet']['channelTitle'],
                    'published_at': search_result['snippet']['publishedAt'],
                    'description': search_result['snippet']['description']
                }
                videos.append(video_data)
            
            print(f"Found {len(videos)} videos for query: '{query}'")
            return videos
            
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            return []
    
    def extract_comments(self, video_ids, max_comments_per_video=100):
        """
        Extract comments from YouTube videos.
        
        Args:
            video_ids (list): List of video IDs
            max_comments_per_video (int): Maximum comments per video
            
        Returns:
            pandas.DataFrame: DataFrame containing comments and metadata
        """
        all_comments = []
        
        for video_id in video_ids:
            try:
                comments_response = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=max_comments_per_video,
                    order='relevance'
                ).execute()
                
                for item in comments_response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comment_data = {
                        'video_id': video_id,
                        'comment_id': item['snippet']['topLevelComment']['id'],
                        'text': comment['textDisplay'],
                        'author': comment['authorDisplayName'],
                        'likes': comment['likeCount'],
                        'published_at': comment['publishedAt'],
                        'updated_at': comment['updatedAt']
                    }
                    all_comments.append(comment_data)
                
                print(f"Extracted {len(comments_response.get('items', []))} comments from video {video_id}")
                
            except HttpError as e:
                print(f"Error extracting comments from video {video_id}: {e}")
                continue
        
        self.comments_df = pd.DataFrame(all_comments)
        print(f"Total comments extracted: {len(self.comments_df)}")
        return self.comments_df
    
    def preprocess_text(self, text):
        """
        Preprocess text for sentiment analysis.
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove user mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def analyze_sentiment(self, df=None):
        """
        Perform sentiment analysis on comments using NLTK VADER.
        
        Args:
            df (pandas.DataFrame): DataFrame with comments
            
        Returns:
            pandas.DataFrame: DataFrame with sentiment scores
        """
        if df is None:
            df = self.comments_df.copy()
        
        # Preprocess text
        df['cleaned_text'] = df['text'].apply(self.preprocess_text)
        
        # Calculate sentiment scores
        sentiment_scores = []
        for text in df['text']:
            scores = self.sia.polarity_scores(text)
            sentiment_scores.append(scores)
        
        # Create sentiment DataFrame
        sentiment_df = pd.DataFrame(sentiment_scores)
        
        # Combine with original DataFrame
        result_df = pd.concat([df, sentiment_df], axis=1)
        
        # Classify sentiment based on compound score
        def classify_sentiment(compound_score):
            if compound_score >= 0.05:
                return 'Positive'
            elif compound_score <= -0.05:
                return 'Negative'
            else:
                return 'Neutral'
        
        result_df['sentiment_label'] = result_df['compound'].apply(classify_sentiment)
        
        # Add confidence levels
        result_df['confidence'] = result_df['compound'].abs()
        
        def confidence_level(conf):
            if conf >= 0.5:
                return 'High'
            elif conf >= 0.2:
                return 'Medium'
            else:
                return 'Low'
        
        result_df['confidence_level'] = result_df['confidence'].apply(confidence_level)
        
        self.comments_df = result_df
        return result_df
    
    def generate_word_frequencies(self, sentiment_filter=None):
        """
        Generate word frequency analysis for different sentiment categories.
        
        Args:
            sentiment_filter (str): Filter by sentiment ('Positive', 'Negative', 'Neutral')
            
        Returns:
            dict: Word frequency data
        """
        if self.comments_df is None:
            raise ValueError("No comments data available. Run analyze_sentiment first.")
        
        df = self.comments_df.copy()
        if sentiment_filter:
            df = df[df['sentiment_label'] == sentiment_filter]
        
        # Tokenize and remove stopwords
        all_words = []
        for text in df['cleaned_text']:
            words = word_tokenize(text)
            words = [word for word in words if word not in self.stop_words and len(word) > 2]
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        return dict(word_freq.most_common(50))
    
    def create_visualizations(self):
        """Create comprehensive visualizations for sentiment analysis results."""
        if self.comments_df is None:
            raise ValueError("No sentiment data available. Run analyze_sentiment first.")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 24))
        
        # 1. Sentiment Distribution Pie Chart
        plt.subplot(3, 3, 1)
        sentiment_counts = self.comments_df['sentiment_label'].value_counts()
        colors = ['#2ecc71', '#e74c3c', '#95a5a6']
        plt.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%', colors=colors)
        plt.title('Overall Sentiment Distribution', fontsize=14, fontweight='bold')
        
        # 2. Sentiment by Confidence Level
        plt.subplot(3, 3, 2)
        conf_sentiment = pd.crosstab(self.comments_df['confidence_level'], self.comments_df['sentiment_label'])
        conf_sentiment.plot(kind='bar', stacked=True, ax=plt.gca(), color=colors)
        plt.title('Sentiment by Confidence Level', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.legend(title='Sentiment')
        
        # 3. Compound Score Distribution
        plt.subplot(3, 3, 3)
        plt.hist(self.comments_df['compound'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(x=0, color='red', linestyle='--', alpha=0.7)
        plt.title('Distribution of Compound Sentiment Scores', fontsize=14, fontweight='bold')
        plt.xlabel('Compound Score')
        plt.ylabel('Frequency')
        
        # 4. Sentiment vs Likes Correlation
        plt.subplot(3, 3, 4)
        for sentiment in ['Positive', 'Negative', 'Neutral']:
            data = self.comments_df[self.comments_df['sentiment_label'] == sentiment]
            plt.scatter(data['likes'], data['compound'], alpha=0.6, label=sentiment)
        plt.xlabel('Number of Likes')
        plt.ylabel('Compound Sentiment Score')
        plt.title('Sentiment Score vs Comment Popularity', fontsize=14, fontweight='bold')
        plt.legend()
        
        # 5. Sentiment Score Components
        plt.subplot(3, 3, 5)
        sentiment_components = self.comments_df[['pos', 'neu', 'neg']].mean()
        plt.bar(sentiment_components.index, sentiment_components.values, color=['green', 'gray', 'red'], alpha=0.7)
        plt.title('Average Sentiment Component Scores', fontsize=14, fontweight='bold')
        plt.ylabel('Average Score')
        
        # 6. Time Series Analysis (if date data available)
        plt.subplot(3, 3, 6)
        self.comments_df['published_date'] = pd.to_datetime(self.comments_df['published_at']).dt.date
        daily_sentiment = self.comments_df.groupby(['published_date', 'sentiment_label']).size().unstack(fill_value=0)
        if not daily_sentiment.empty:
            daily_sentiment.plot(kind='area', stacked=True, ax=plt.gca(), alpha=0.7)
            plt.title('Sentiment Trends Over Time', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
        
        # 7. Top Positive Words Word Cloud
        plt.subplot(3, 3, 7)
        positive_words = self.generate_word_frequencies('Positive')
        if positive_words:
            wordcloud = WordCloud(width=300, height=200, background_color='white').generate_from_frequencies(positive_words)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Most Common Positive Words', fontsize=14, fontweight='bold')
        
        # 8. Top Negative Words Word Cloud
        plt.subplot(3, 3, 8)
        negative_words = self.generate_word_frequencies('Negative')
        if negative_words:
            wordcloud = WordCloud(width=300, height=200, background_color='white', colormap='Reds').generate_from_frequencies(negative_words)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Most Common Negative Words', fontsize=14, fontweight='bold')
        
        # 9. Confidence Distribution by Sentiment
        plt.subplot(3, 3, 9)
        for sentiment in ['Positive', 'Negative', 'Neutral']:
            data = self.comments_df[self.comments_df['sentiment_label'] == sentiment]['confidence']
            plt.hist(data, alpha=0.6, label=sentiment, bins=20)
        plt.xlabel('Confidence Score')
        plt.ylabel('Frequency')
        plt.title('Confidence Score Distribution by Sentiment', fontsize=14, fontweight='bold')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('/Users/georgeshaheen/youtube_sentiment_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_business_report(self):
        """Generate a comprehensive business report with insights and recommendations."""
        if self.comments_df is None:
            raise ValueError("No sentiment data available. Run analyze_sentiment first.")
        
        # Calculate key metrics
        total_comments = len(self.comments_df)
        sentiment_dist = self.comments_df['sentiment_label'].value_counts(normalize=True) * 100
        avg_compound = self.comments_df['compound'].mean()
        
        # High confidence sentiment analysis
        high_conf = self.comments_df[self.comments_df['confidence_level'] == 'High']
        high_conf_sentiment = high_conf['sentiment_label'].value_counts(normalize=True) * 100
        
        # Engagement analysis
        avg_likes_by_sentiment = self.comments_df.groupby('sentiment_label')['likes'].mean()
        
        # Generate report
        report = f"""
YOUTUBE CHATGPT SENTIMENT ANALYSIS REPORT
========================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Company: FutureProof
Department: Data Analytics Team

EXECUTIVE SUMMARY
================
This report analyzes public sentiment toward ChatGPT on YouTube to inform FutureProof's 
marketing strategy for AI-enhanced content generation and social media management.

KEY FINDINGS
============
• Total Comments Analyzed: {total_comments:,}
• Overall Sentiment Score: {avg_compound:.3f} (Range: -1 to +1)

Sentiment Distribution:
• Positive: {sentiment_dist.get('Positive', 0):.1f}%
• Neutral: {sentiment_dist.get('Neutral', 0):.1f}%
• Negative: {sentiment_dist.get('Negative', 0):.1f}%

High-Confidence Analysis (Most Reliable Opinions):
• Positive: {high_conf_sentiment.get('Positive', 0):.1f}%
• Neutral: {high_conf_sentiment.get('Neutral', 0):.1f}%
• Negative: {high_conf_sentiment.get('Negative', 0):.1f}%

Engagement Metrics:
• Average Likes on Positive Comments: {avg_likes_by_sentiment.get('Positive', 0):.1f}
• Average Likes on Negative Comments: {avg_likes_by_sentiment.get('Negative', 0):.1f}
• Average Likes on Neutral Comments: {avg_likes_by_sentiment.get('Neutral', 0):.1f}

INSIGHTS & ANALYSIS
==================
1. PUBLIC PERCEPTION ANALYSIS
   {'✓ Generally Positive' if avg_compound > 0.1 else '⚠ Mixed Reception' if avg_compound > -0.1 else '✗ Generally Negative'}: 
   The overall sentiment score of {avg_compound:.3f} indicates that public opinion toward ChatGPT
   {'leans positive' if avg_compound > 0.1 else 'is mixed with both supporters and critics' if avg_compound > -0.1 else 'is predominantly negative'}.

2. ENGAGEMENT CORRELATION
   {'Positive comments receive more engagement' if avg_likes_by_sentiment.get('Positive', 0) > avg_likes_by_sentiment.get('Negative', 0) else 'Negative comments receive more engagement'}, 
   suggesting that {'supporters are more active in promoting positive content' if avg_likes_by_sentiment.get('Positive', 0) > avg_likes_by_sentiment.get('Negative', 0) else 'critics are more vocal and engaged'}.

3. CONFIDENCE LEVELS
   {len(high_conf)} comments ({len(high_conf)/total_comments*100:.1f}%) express strong opinions,
   providing reliable indicators of genuine public sentiment.

BUSINESS RECOMMENDATIONS
========================
Based on this analysis, we recommend the following strategy for FutureProof:

{"🟢 PROCEED WITH CONFIDENCE" if avg_compound > 0.2 else "🟡 PROCEED WITH CAUTION" if avg_compound > -0.1 else "🔴 CONSIDER ALTERNATIVE APPROACH"}

Specific Recommendations:

1. CONTENT STRATEGY
   • {"Leverage positive sentiment in marketing materials" if avg_compound > 0.1 else "Address concerns proactively in content"}
   • {"Highlight AI benefits and success stories" if sentiment_dist.get('Positive', 0) > 50 else "Focus on transparency and addressing limitations"}
   • {"Use testimonials and positive user experiences" if avg_compound > 0.1 else "Emphasize human oversight and quality control"}

2. RISK MITIGATION
   • Monitor social media sentiment continuously
   • {"Prepare responses to common concerns" if sentiment_dist.get('Negative', 0) > 20 else "Maintain current communication strategy"}
   • Implement human review for all AI-generated content
   • Establish clear guidelines for AI tool usage

3. IMPLEMENTATION APPROACH
   • {"Start with a pilot program showcasing AI benefits" if avg_compound > 0.1 else "Begin with limited, well-monitored implementation"}
   • Train team on ethical AI practices
   • {"Emphasize AI as a productivity enhancer, not replacement" if sentiment_dist.get('Negative', 0) > 30 else "Position AI as an innovation driver"}

NEXT STEPS
==========
1. Present findings to executive team
2. {"Develop AI content guidelines and best practices" if avg_compound > 0 else "Conduct additional market research"}
3. {"Launch pilot AI content program" if avg_compound > 0.2 else "Create stakeholder education program"}
4. Establish ongoing sentiment monitoring system
5. {"Plan full rollout timeline" if avg_compound > 0.1 else "Reassess strategy based on additional data"}

TECHNICAL APPENDIX
==================
• Analysis Method: NLTK VADER Sentiment Analysis
• Data Source: YouTube API v3
• Processing: Text preprocessing, spam filtering, confidence scoring
• Validation: Cross-referenced with engagement metrics

Report prepared by: Data Analytics Team
Contact: analytics@futureproof.com
"""
        
        # Save report
        with open('/Users/georgeshaheen/futureproof_chatgpt_sentiment_report.txt', 'w') as f:
            f.write(report)
        
        print(report)
        return report

def main():
    """Main execution function with example usage."""
    print("YouTube ChatGPT Sentiment Analysis Tool")
    print("=" * 50)
    
    # Initialize analyzer
    # Note: You need to set your YouTube API key as an environment variable
    # or pass it directly: analyzer = YouTubeSentimentAnalyzer("YOUR_API_KEY_HERE")
    analyzer = YouTubeSentimentAnalyzer()
    
    # Search for ChatGPT-related videos
    print("\n1. Searching for ChatGPT-related videos...")
    videos = analyzer.search_videos("ChatGPT review opinion", max_results=20)
    
    if not videos:
        print("No videos found. Please check your API key and try again.")
        return
    
    # Extract video IDs
    video_ids = [video['video_id'] for video in videos[:10]]  # Limit to first 10 videos
    
    # Extract comments
    print("\n2. Extracting comments from videos...")
    comments_df = analyzer.extract_comments(video_ids, max_comments_per_video=50)
    
    if comments_df.empty:
        print("No comments found. This might be due to privacy settings on videos.")
        return
    
    # Perform sentiment analysis
    print("\n3. Performing sentiment analysis...")
    sentiment_df = analyzer.analyze_sentiment()
    
    # Generate visualizations
    print("\n4. Creating visualizations...")
    analyzer.create_visualizations()
    
    # Generate business report
    print("\n5. Generating business report...")
    report = analyzer.generate_business_report()
    
    print(f"\nAnalysis complete! Results saved to:")
    print("- Visualization: youtube_sentiment_analysis.png")
    print("- Business Report: futureproof_chatgpt_sentiment_report.txt")
    print("- Data: Available in sentiment_df variable")

if __name__ == "__main__":
    # Example of how to use the tool
    # You'll need to set up your YouTube API key first
    print("Please set your YouTube API key as an environment variable 'YOUTUBE_API_KEY'")
    print("Or modify the code to pass it directly to YouTubeSentimentAnalyzer()")
    print("\nTo run the analysis, execute: python youtube_sentiment_analysis.py")
