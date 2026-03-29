#!/usr/bin/env python3
"""
General ChatGPT Sentiment Analysis on YouTube
============================================

Analyzes public sentiment about ChatGPT usage across YouTube by:
1. Searching for various ChatGPT-related queries
2. Extracting comments from multiple videos
3. Performing comprehensive sentiment analysis
"""

from youtube_sentiment_analysis import YouTubeSentimentAnalyzer
import pandas as pd

class GeneralChatGPTAnalyzer(YouTubeSentimentAnalyzer):
    """Extended analyzer for general ChatGPT sentiment across YouTube."""
    
    def __init__(self, api_key=None):
        super().__init__(api_key)
        
        # Define comprehensive search queries for general ChatGPT sentiment
        self.chatgpt_queries = [
            "ChatGPT opinion",
            "ChatGPT review", 
            "ChatGPT experience",
            "ChatGPT pros and cons",
            "ChatGPT good or bad",
            "ChatGPT thoughts",
            "ChatGPT worth it",
            "ChatGPT useful",
            "ChatGPT problems",
            "ChatGPT benefits",
            "using ChatGPT",
            "ChatGPT vs human",
            "ChatGPT accuracy",
            "ChatGPT limitations",
            "ChatGPT future"
        ]
    
    def comprehensive_search(self, max_videos_per_query=10):
        """
        Search across multiple ChatGPT-related queries to get diverse opinions.
        
        Args:
            max_videos_per_query (int): Maximum videos per search query
            
        Returns:
            list: Combined list of videos from all searches
        """
        all_videos = []
        
        print("Searching across multiple ChatGPT-related queries...")
        for i, query in enumerate(self.chatgpt_queries, 1):
            print(f"  {i}/{len(self.chatgpt_queries)}: '{query}'")
            
            videos = self.search_videos(query, max_results=max_videos_per_query)
            
            # Add query context to video metadata
            for video in videos:
                video['search_query'] = query
                video['query_category'] = self._categorize_query(query)
            
            all_videos.extend(videos)
        
        # Remove duplicates based on video_id
        unique_videos = []
        seen_ids = set()
        
        for video in all_videos:
            if video['video_id'] not in seen_ids:
                unique_videos.append(video)
                seen_ids.add(video['video_id'])
        
        print(f"Found {len(unique_videos)} unique videos across all queries")
        return unique_videos
    
    def _categorize_query(self, query):
        """Categorize search queries by intent."""
        if any(word in query.lower() for word in ['opinion', 'review', 'thoughts']):
            return 'Opinion'
        elif any(word in query.lower() for word in ['pros', 'cons', 'good', 'bad']):
            return 'Evaluation'
        elif any(word in query.lower() for word in ['using', 'experience', 'useful']):
            return 'Usage'
        elif any(word in query.lower() for word in ['problems', 'limitations', 'accuracy']):
            return 'Concerns'
        elif any(word in query.lower() for word in ['benefits', 'worth', 'future']):
            return 'Benefits'
        else:
            return 'General'
    
    def analyze_by_query_category(self):
        """Analyze sentiment patterns by query category."""
        if self.comments_df is None:
            raise ValueError("No comments data available. Run comprehensive analysis first.")
        
        # Group by query category
        category_analysis = {}
        
        for category in self.comments_df['query_category'].unique():
            category_data = self.comments_df[self.comments_df['query_category'] == category]
            
            category_analysis[category] = {
                'total_comments': len(category_data),
                'sentiment_distribution': category_data['sentiment_label'].value_counts(normalize=True) * 100,
                'avg_compound_score': category_data['compound'].mean(),
                'avg_engagement': category_data['likes'].mean(),
                'confidence_breakdown': category_data['confidence_level'].value_counts(normalize=True) * 100
            }
        
        return category_analysis
    
    def run_comprehensive_analysis(self, videos_per_query=8, comments_per_video=75):
        """
        Run complete analysis of general ChatGPT sentiment on YouTube.
        
        Args:
            videos_per_query (int): Videos to analyze per search query
            comments_per_video (int): Comments to extract per video
        """
        print("=== COMPREHENSIVE CHATGPT SENTIMENT ANALYSIS ===")
        print(f"Analyzing sentiment across {len(self.chatgpt_queries)} different query types")
        
        # 1. Search for videos across multiple queries
        all_videos = self.comprehensive_search(videos_per_query)
        
        if not all_videos:
            print("❌ No videos found. Check your API key and try again.")
            return
        
        # 2. Extract video IDs and metadata
        video_ids = [video['video_id'] for video in all_videos]
        
        # Create video metadata DataFrame for later analysis
        self.video_metadata = pd.DataFrame(all_videos)
        
        # 3. Extract comments
        print(f"\n📝 Extracting comments from {len(video_ids)} videos...")
        comments_df = self.extract_comments(video_ids, comments_per_video)
        
        if comments_df.empty:
            print("❌ No comments extracted. Videos might have comments disabled.")
            return
        
        # 4. Merge comment data with video metadata
        comments_df = comments_df.merge(
            self.video_metadata[['video_id', 'search_query', 'query_category']], 
            on='video_id', 
            how='left'
        )
        self.comments_df = comments_df
        
        # 5. Perform sentiment analysis
        print("🧠 Performing sentiment analysis...")
        self.analyze_sentiment(comments_df)
        
        # 6. Category-specific analysis
        print("📊 Analyzing patterns by query category...")
        category_results = self.analyze_by_query_category()
        
        # 7. Generate enhanced visualizations
        print("📈 Creating comprehensive visualizations...")
        self.create_enhanced_visualizations(category_results)
        
        # 8. Generate business report
        print("📋 Generating enhanced business report...")
        self.generate_enhanced_report(category_results)
        
        print("\n✅ Analysis complete!")
        print("📁 Files generated:")
        print("   - general_chatgpt_sentiment_analysis.png")
        print("   - futureproof_general_chatgpt_report.txt")
        
        return self.comments_df
    
    def create_enhanced_visualizations(self, category_results):
        """Create enhanced visualizations including category analysis."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        from wordcloud import WordCloud
        
        # Create larger figure for comprehensive analysis
        fig = plt.figure(figsize=(24, 20))
        
        # 1. Overall Sentiment Distribution (Enhanced)
        plt.subplot(4, 4, 1)
        sentiment_counts = self.comments_df['sentiment_label'].value_counts()
        colors = ['#2ecc71', '#e74c3c', '#95a5a6']
        wedges, texts, autotexts = plt.pie(sentiment_counts.values, labels=sentiment_counts.index, 
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title('Overall ChatGPT Sentiment Distribution', fontsize=14, fontweight='bold')
        
        # 2. Sentiment by Query Category
        plt.subplot(4, 4, 2)
        category_sentiment = pd.crosstab(self.comments_df['query_category'], self.comments_df['sentiment_label'])
        category_sentiment.plot(kind='bar', stacked=True, ax=plt.gca(), color=colors)
        plt.title('Sentiment by Query Type', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 3. Query Category Performance
        plt.subplot(4, 4, 3)
        category_scores = []
        category_names = []
        for category, data in category_results.items():
            category_scores.append(data['avg_compound_score'])
            category_names.append(category)
        
        bars = plt.bar(category_names, category_scores, color='skyblue', alpha=0.7)
        plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        plt.title('Average Sentiment by Query Category', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.ylabel('Average Compound Score')
        
        # Color bars based on sentiment
        for i, score in enumerate(category_scores):
            if score > 0.1:
                bars[i].set_color('#2ecc71')
            elif score < -0.1:
                bars[i].set_color('#e74c3c')
            else:
                bars[i].set_color('#95a5a6')
        
        # 4. Compound Score Distribution with Categories
        plt.subplot(4, 4, 4)
        for category in self.comments_df['query_category'].unique():
            data = self.comments_df[self.comments_df['query_category'] == category]['compound']
            plt.hist(data, alpha=0.6, label=category, bins=20)
        plt.axvline(x=0, color='red', linestyle='--', alpha=0.7)
        plt.title('Sentiment Score Distribution by Category', fontsize=14, fontweight='bold')
        plt.xlabel('Compound Score')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 5. Engagement vs Sentiment
        plt.subplot(4, 4, 5)
        sentiment_colors = {'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'}
        for sentiment in ['Positive', 'Negative', 'Neutral']:
            data = self.comments_df[self.comments_df['sentiment_label'] == sentiment]
            plt.scatter(data['likes'], data['compound'], alpha=0.6, 
                       label=sentiment, color=sentiment_colors[sentiment])
        plt.xlabel('Number of Likes')
        plt.ylabel('Compound Sentiment Score')
        plt.title('Engagement vs Sentiment Correlation', fontsize=14, fontweight='bold')
        plt.legend()
        
        # 6. Time-based Analysis
        plt.subplot(4, 4, 6)
        self.comments_df['published_date'] = pd.to_datetime(self.comments_df['published_at']).dt.date
        daily_sentiment = self.comments_df.groupby(['published_date', 'sentiment_label']).size().unstack(fill_value=0)
        if not daily_sentiment.empty and len(daily_sentiment) > 1:
            daily_sentiment.plot(kind='area', stacked=True, ax=plt.gca(), alpha=0.7, color=colors)
            plt.title('Sentiment Trends Over Time', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
        else:
            plt.text(0.5, 0.5, 'Insufficient time range\nfor trend analysis', 
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title('Sentiment Trends Over Time', fontsize=14, fontweight='bold')
        
        # 7-10. Word clouds for different categories
        categories = list(category_results.keys())[:4]
        positions = [(4, 4, 7), (4, 4, 8), (4, 4, 9), (4, 4, 10)]
        
        for i, category in enumerate(categories):
            if i < len(positions):
                plt.subplot(*positions[i])
                category_text = ' '.join(self.comments_df[
                    self.comments_df['query_category'] == category]['cleaned_text'].fillna(''))
                
                if category_text.strip():
                    wordcloud = WordCloud(width=300, height=200, background_color='white',
                                        max_words=50).generate(category_text)
                    plt.imshow(wordcloud, interpolation='bilinear')
                    plt.axis('off')
                    plt.title(f'Top Words: {category}', fontsize=12, fontweight='bold')
                else:
                    plt.text(0.5, 0.5, 'No data', ha='center', va='center')
                    plt.title(f'Top Words: {category}', fontsize=12, fontweight='bold')
        
        # 11. Confidence Analysis
        plt.subplot(4, 4, 11)
        confidence_sentiment = pd.crosstab(self.comments_df['confidence_level'], 
                                         self.comments_df['sentiment_label'])
        confidence_sentiment.plot(kind='bar', ax=plt.gca(), color=colors)
        plt.title('Sentiment by Confidence Level', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        
        # 12. Sample Size by Category
        plt.subplot(4, 4, 12)
        category_counts = self.comments_df['query_category'].value_counts()
        plt.bar(category_counts.index, category_counts.values, color='lightcoral', alpha=0.7)
        plt.title('Sample Size by Query Category', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.ylabel('Number of Comments')
        
        # 13-16. Individual sentiment components by category
        components = ['pos', 'neu', 'neg']
        for i, component in enumerate(components):
            plt.subplot(4, 4, 13 + i)
            comp_by_category = self.comments_df.groupby('query_category')[component].mean()
            bars = plt.bar(comp_by_category.index, comp_by_category.values, 
                          color=['green' if component=='pos' else 'gray' if component=='neu' else 'red'][0],
                          alpha=0.7)
            plt.title(f'Average {component.upper()} Score by Category', fontsize=12, fontweight='bold')
            plt.xticks(rotation=45)
            plt.ylabel(f'Average {component.upper()} Score')
        
        plt.tight_layout()
        plt.savefig('/Users/georgeshaheen/general_chatgpt_sentiment_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_enhanced_report(self, category_results):
        """Generate enhanced business report with category analysis."""
        from datetime import datetime
        
        # Calculate enhanced metrics
        total_comments = len(self.comments_df)
        overall_sentiment = self.comments_df['sentiment_label'].value_counts(normalize=True) * 100
        avg_compound = self.comments_df['compound'].mean()
        
        # Category insights
        best_category = max(category_results.items(), key=lambda x: x[1]['avg_compound_score'])
        worst_category = min(category_results.items(), key=lambda x: x[1]['avg_compound_score'])
        
        # Engagement analysis
        high_engagement = self.comments_df[self.comments_df['likes'] > self.comments_df['likes'].quantile(0.75)]
        high_engagement_sentiment = high_engagement['sentiment_label'].value_counts(normalize=True) * 100
        
        report = f"""
COMPREHENSIVE YOUTUBE CHATGPT SENTIMENT ANALYSIS
==============================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Company: FutureProof - Cybersecurity Solutions
Analysis Scope: General ChatGPT Usage Sentiment

EXECUTIVE SUMMARY
================
This comprehensive analysis examines public sentiment toward ChatGPT usage across 
YouTube through {len(self.chatgpt_queries)} different query categories, providing 
FutureProof with data-driven insights for AI adoption strategy.

DATASET OVERVIEW
===============
• Total Comments Analyzed: {total_comments:,}
• Unique Videos: {self.comments_df['video_id'].nunique():,}
• Query Categories: {len(category_results)}
• Date Range: {self.comments_df['published_at'].min()[:10]} to {self.comments_df['published_at'].max()[:10]}

OVERALL SENTIMENT METRICS
=========================
• Overall Sentiment Score: {avg_compound:.3f} (Scale: -1 to +1)
• Sentiment Distribution:
  - Positive: {overall_sentiment.get('Positive', 0):.1f}%
  - Neutral: {overall_sentiment.get('Neutral', 0):.1f}%  
  - Negative: {overall_sentiment.get('Negative', 0):.1f}%

CATEGORY-SPECIFIC ANALYSIS
=========================

Most Positive Category: {best_category[0]}
• Average Score: {best_category[1]['avg_compound_score']:.3f}
• Sample Size: {best_category[1]['total_comments']} comments
• Positive Rate: {best_category[1]['sentiment_distribution'].get('Positive', 0):.1f}%

Most Critical Category: {worst_category[0]}  
• Average Score: {worst_category[1]['avg_compound_score']:.3f}
• Sample Size: {worst_category[1]['total_comments']} comments
• Negative Rate: {worst_category[1]['sentiment_distribution'].get('Negative', 0):.1f}%

Detailed Category Breakdown:
"""
        
        for category, data in sorted(category_results.items(), 
                                   key=lambda x: x[1]['avg_compound_score'], reverse=True):
            report += f"""
{category.upper()} QUERIES
• Sentiment Score: {data['avg_compound_score']:.3f}
• Comments: {data['total_comments']}
• Positive: {data['sentiment_distribution'].get('Positive', 0):.1f}%
• Neutral: {data['sentiment_distribution'].get('Neutral', 0):.1f}%  
• Negative: {data['sentiment_distribution'].get('Negative', 0):.1f}%
• Avg Engagement: {data['avg_engagement']:.1f} likes
"""
        
        # High engagement analysis
        report += f"""

ENGAGEMENT ANALYSIS
==================
High-Engagement Comments (Top 25%):
• Positive: {high_engagement_sentiment.get('Positive', 0):.1f}%
• Neutral: {high_engagement_sentiment.get('Neutral', 0):.1f}%
• Negative: {high_engagement_sentiment.get('Negative', 0):.1f}%

This indicates that {'positive' if high_engagement_sentiment.get('Positive', 0) > high_engagement_sentiment.get('Negative', 0) else 'negative'} comments receive more engagement.

KEY INSIGHTS & IMPLICATIONS
==========================

1. PUBLIC PERCEPTION ANALYSIS
{'   ✅ GENERALLY FAVORABLE' if avg_compound > 0.2 else '   ⚠️  MIXED RECEPTION' if avg_compound > -0.1 else '   ❌ PREDOMINANTLY NEGATIVE'}: 
   Overall sentiment score of {avg_compound:.3f} suggests public opinion 
   {'strongly supports' if avg_compound > 0.2 else 'is divided on' if avg_compound > -0.1 else 'has concerns about'} ChatGPT usage.

2. CATEGORY INSIGHTS
   • STRONGEST SUPPORT: {best_category[0]} queries show most positive sentiment
   • HIGHEST CONCERN: {worst_category[0]} queries reveal key challenges
   • This pattern suggests users are most {'optimistic about benefits' if 'benefit' in best_category[0].lower() else 'positive about practical usage' if 'usage' in best_category[0].lower() else 'supportive of general applications'}

3. ENGAGEMENT PATTERNS
   {'Positive sentiment drives higher engagement, suggesting supporters are more active' if high_engagement_sentiment.get('Positive', 0) > high_engagement_sentiment.get('Negative', 0) else 'Critical voices receive more engagement, indicating active discussion around concerns'}

STRATEGIC RECOMMENDATIONS FOR FUTUREPROOF
=========================================

OVERALL STRATEGY: {"🟢 PROCEED WITH CONFIDENCE" if avg_compound > 0.2 else "🟡 PROCEED WITH MEASURED APPROACH" if avg_compound > -0.1 else "🔴 PROCEED WITH EXTREME CAUTION"}

Specific Action Items:

1. CONTENT STRATEGY
{'   • Emphasize benefits and success stories in marketing materials' if avg_compound > 0.1 else '   • Address concerns proactively and transparently'}
{'   • Leverage positive user experiences from ' + best_category[0].lower() + ' context' if best_category[1]['avg_compound_score'] > 0.2 else '   • Focus on addressing ' + worst_category[0].lower() + ' concerns'}
   • Create content that acknowledges both benefits and limitations

2. RISK MITIGATION  
{'   • Monitor for sentiment shifts, especially in ' + worst_category[0].lower() + ' discussions' if worst_category[1]['avg_compound_score'] < -0.1 else '   • Maintain current positive momentum while monitoring edge cases'}
   • Prepare response strategies for common concerns
   • Implement robust quality control and human oversight

3. IMPLEMENTATION ROADMAP
   Phase 1: {'Pilot program highlighting AI productivity benefits' if avg_compound > 0.1 else 'Limited deployment with extensive monitoring'}
   Phase 2: {'Expand based on positive feedback and metrics' if avg_compound > 0.1 else 'Address identified concerns before expansion'}
   Phase 3: {'Full deployment with ongoing sentiment monitoring' if avg_compound > 0.2 else 'Gradual rollout based on improved public perception'}

CYBERSECURITY IMPLICATIONS
==========================
• Monitor for AI-related security discussions
• Address data privacy concerns proactively  
• Position FutureProof as leader in responsible AI implementation
• Emphasize human oversight in all AI-assisted security operations

NEXT STEPS
==========
1. Present findings to executive leadership
2. {'Develop AI integration guidelines emphasizing positive use cases' if avg_compound > 0.1 else 'Create comprehensive change management and education program'}
3. Establish continuous sentiment monitoring system
4. {'Launch pilot program in Q1 2024' if avg_compound > 0.2 else 'Conduct stakeholder education sessions before implementation'}
5. Prepare crisis communication protocols

TECHNICAL METHODOLOGY
====================
• Data Source: YouTube Data API v3
• Analysis Framework: NLTK VADER Sentiment Analysis
• Query Scope: {len(self.chatgpt_queries)} comprehensive search categories
• Validation: Cross-referenced with engagement metrics and confidence scores
• Quality Control: Text preprocessing, spam filtering, duplicate removal

CONFIDENCE METRICS
==================
• High Confidence Opinions: {len(self.comments_df[self.comments_df['confidence_level'] == 'High'])} ({len(self.comments_df[self.comments_df['confidence_level'] == 'High'])/total_comments*100:.1f}%)
• Medium Confidence: {len(self.comments_df[self.comments_df['confidence_level'] == 'Medium'])} ({len(self.comments_df[self.comments_df['confidence_level'] == 'Medium'])/total_comments*100:.1f}%)
• Low Confidence: {len(self.comments_df[self.comments_df['confidence_level'] == 'Low'])} ({len(self.comments_df[self.comments_df['confidence_level'] == 'Low'])/total_comments*100:.1f}%)

Report Prepared By: Data Analytics Team
Contact: analytics@futureproof.com
Classification: Internal Business Intelligence
"""
        
        # Save enhanced report
        with open('/Users/georgeshaheen/futureproof_general_chatgpt_report.txt', 'w') as f:
            f.write(report)
        
        print(report)
        return report

def main():
    """Run comprehensive ChatGPT sentiment analysis."""
    print("🚀 COMPREHENSIVE CHATGPT SENTIMENT ANALYSIS")
    print("=" * 60)
    
    try:
        # Initialize enhanced analyzer
        analyzer = GeneralChatGPTAnalyzer()
        
        # Run comprehensive analysis
        results = analyzer.run_comprehensive_analysis(
            videos_per_query=6,    # Analyze 6 videos per query type
            comments_per_video=50  # Extract 50 comments per video
        )
        
        if results is not None:
            print("\n🎯 ANALYSIS SUMMARY:")
            print(f"✅ {len(results)} comments analyzed")
            print(f"✅ {results['video_id'].nunique()} unique videos")
            print(f"✅ {len(results['query_category'].unique())} query categories")
            
            sentiment_summary = results['sentiment_label'].value_counts(normalize=True) * 100
            print(f"✅ Overall: {sentiment_summary.get('Positive', 0):.1f}% Positive, "
                  f"{sentiment_summary.get('Neutral', 0):.1f}% Neutral, "
                  f"{sentiment_summary.get('Negative', 0):.1f}% Negative")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have set your YouTube API key in the .env file")

if __name__ == "__main__":
    main()