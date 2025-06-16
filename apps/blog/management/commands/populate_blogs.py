from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime, timedelta
from apps.blog.models import Article, Category, Tag


class Command(BaseCommand):
    help = 'Populate the database with realistic blog entries for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing blog data before populating',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting blog population...'))
        
        if options['clear']:
            self.clear_existing_data()
        
        try:
            # Create or get superuser
            author = self.create_or_get_author()
            
            # Create categories
            categories = self.create_categories()
            
            # Create tags
            tags = self.create_tags()
            
            # Create articles
            self.create_articles(author, categories, tags)
            
            self.stdout.write(
                self.style.SUCCESS('Successfully populated blog with realistic content!')
            )
            
        except Exception as e:
            raise CommandError(f'Error during blog population: {str(e)}')

    def clear_existing_data(self):
        """Clear existing blog data"""
        self.stdout.write('Clearing existing blog data...')
        Article.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        self.stdout.write(self.style.WARNING('Existing blog data cleared.'))

    def create_or_get_author(self):
        """Create or get a blog author"""
        author, created = User.objects.get_or_create(
            username='blog_author',
            defaults={
                'email': 'author@pulcova.com',
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'is_staff': True,
                'is_active': True,
            }
        )
        if created:
            author.set_password('blogauthor123')
            author.save()
            self.stdout.write(f'Created blog author: {author.username}')
        else:
            self.stdout.write(f'Using existing author: {author.username}')
        return author

    def create_categories(self):
        """Create blog categories"""
        categories_data = [
            {
                'name': 'Technology',
                'slug': 'technology',
                'description': 'Latest trends and insights in technology and software development.'
            },
            {
                'name': 'Business Strategy',
                'slug': 'business-strategy',
                'description': 'Strategic insights for modern businesses and entrepreneurs.'
            },
            {
                'name': 'Digital Marketing',
                'slug': 'digital-marketing',
                'description': 'Marketing strategies and trends in the digital age.'
            },
            {
                'name': 'Web Development',
                'slug': 'web-development',
                'description': 'Best practices and tutorials for web developers.'
            },
            {
                'name': 'Industry Insights',
                'slug': 'industry-insights',
                'description': 'Analysis and insights from various industries.'
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        return categories

    def create_tags(self):
        """Create blog tags"""
        tags_data = [
            {'name': 'Python', 'slug': 'python'},
            {'name': 'Django', 'slug': 'django'},
            {'name': 'JavaScript', 'slug': 'javascript'},
            {'name': 'React', 'slug': 'react'},
            {'name': 'AI', 'slug': 'ai'},
            {'name': 'Machine Learning', 'slug': 'machine-learning'},
            {'name': 'SEO', 'slug': 'seo'},
            {'name': 'Content Marketing', 'slug': 'content-marketing'},
            {'name': 'E-commerce', 'slug': 'e-commerce'},
            {'name': 'Cloud Computing', 'slug': 'cloud-computing'},
            {'name': 'DevOps', 'slug': 'devops'},
            {'name': 'UI/UX', 'slug': 'ui-ux'},
        ]
        
        tags = {}
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
            tags[tag_data['slug']] = tag
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
        
        return tags

    def create_articles(self, author, categories, tags):
        """Create realistic blog articles"""
        articles_data = [
            {
                'title': 'The Future of Web Development: Trends to Watch in 2025',
                'excerpt': 'Explore the cutting-edge trends shaping web development this year, from AI integration to progressive web apps and the rise of serverless architecture.',
                'content': """
                <p>As we dive deeper into 2025, the web development landscape continues to evolve at an unprecedented pace. New technologies, frameworks, and methodologies are reshaping how we build and interact with web applications.</p>
                
                <h2>AI-Powered Development Tools</h2>
                <p>Artificial Intelligence is no longer just a buzzword in web development. AI-powered tools are now helping developers write code faster, debug more efficiently, and create more personalized user experiences. From code completion to automated testing, AI is becoming an integral part of the development workflow.</p>
                
                <h2>Progressive Web Apps (PWAs) Go Mainstream</h2>
                <p>Progressive Web Apps have matured significantly, offering native-like experiences across all devices. With improved offline capabilities, push notifications, and app-store distribution, PWAs are becoming the go-to solution for businesses looking to reach users across multiple platforms.</p>
                
                <h2>Serverless Architecture Revolution</h2>
                <p>Serverless computing is transforming how we think about backend development. By eliminating server management overhead, developers can focus on writing business logic while cloud providers handle scaling, security, and maintenance.</p>
                
                <h2>Enhanced Security Measures</h2>
                <p>With cyber threats becoming more sophisticated, web security has become paramount. Modern frameworks are implementing security-first approaches, with built-in protection against common vulnerabilities and automated security scanning.</p>
                
                <p>The future of web development is bright, with technologies that make development faster, more secure, and more accessible than ever before.</p>
                """,
                'category': 'web-development',
                'tags': ['javascript', 'react', 'ai', 'cloud-computing'],
                'reading_time': 8,
                'is_featured': True,
                'meta_title': 'Future of Web Development 2025 | Pulcova Insights',
                'meta_description': 'Discover the latest web development trends for 2025, including AI integration, PWAs, serverless architecture, and enhanced security measures.',
            },
            {
                'title': 'Building Scalable E-commerce Solutions with Django',
                'excerpt': 'Learn how to leverage Django\'s robust framework to build scalable, secure, and maintainable e-commerce platforms that can grow with your business.',
                'content': """
                <p>Django has established itself as one of the most reliable frameworks for building complex web applications, and e-commerce platforms are no exception. Its "batteries included" philosophy and robust ecosystem make it an excellent choice for businesses of all sizes.</p>
                
                <h2>Why Choose Django for E-commerce?</h2>
                <p>Django offers several advantages for e-commerce development:</p>
                <ul>
                    <li>Built-in admin interface for easy content management</li>
                    <li>Robust ORM for complex database relationships</li>
                    <li>Excellent security features out of the box</li>
                    <li>Scalable architecture that grows with your business</li>
                </ul>
                
                <h2>Essential Components of a Django E-commerce Platform</h2>
                <p>A successful e-commerce platform requires careful planning and implementation of core components:</p>
                
                <h3>Product Management</h3>
                <p>Design flexible product models that can handle variations, categories, and complex pricing structures. Django's model inheritance and relationships make this straightforward.</p>
                
                <h3>Order Processing</h3>
                <p>Implement a robust order management system that handles cart functionality, checkout processes, and order tracking. Django's transaction management ensures data consistency.</p>
                
                <h3>Payment Integration</h3>
                <p>Integrate with popular payment gateways like Stripe, PayPal, or Square. Django's middleware system makes it easy to handle payment processing securely.</p>
                
                <h2>Performance Optimization</h2>
                <p>As your e-commerce platform grows, performance becomes crucial. Implement caching strategies, database optimization, and CDN integration to ensure fast loading times.</p>
                
                <p>With proper planning and implementation, Django can power e-commerce platforms that serve millions of users while maintaining security and performance.</p>
                """,
                'category': 'web-development',
                'tags': ['python', 'django', 'e-commerce'],
                'reading_time': 12,
                'is_featured': False,
                'meta_title': 'Build Scalable E-commerce with Django | Development Guide',
                'meta_description': 'Complete guide to building scalable e-commerce solutions using Django framework. Learn best practices, architecture patterns, and optimization techniques.',
            },
            {
                'title': 'Digital Marketing ROI: Measuring What Matters in 2025',
                'excerpt': 'Discover the key metrics and measurement strategies that modern businesses use to track digital marketing performance and maximize their return on investment.',
                'content': """
                <p>In today's competitive digital landscape, measuring marketing ROI has become more complex but also more crucial than ever. With multiple touchpoints, attribution models, and customer journeys, businesses need sophisticated approaches to understand what's working.</p>
                
                <h2>Beyond Vanity Metrics</h2>
                <p>While likes, shares, and follower counts provide some insights, they don't necessarily translate to business value. Modern marketers focus on metrics that directly correlate with revenue and business growth.</p>
                
                <h2>Key Performance Indicators That Matter</h2>
                
                <h3>Customer Lifetime Value (CLV)</h3>
                <p>Understanding the total value a customer brings over their entire relationship with your brand helps prioritize acquisition and retention strategies.</p>
                
                <h3>Customer Acquisition Cost (CAC)</h3>
                <p>Track how much you spend to acquire each customer across different channels. This metric is essential for budget allocation and channel optimization.</p>
                
                <h3>Attribution Modeling</h3>
                <p>Move beyond last-click attribution to understand the full customer journey. Multi-touch attribution provides a more accurate picture of marketing impact.</p>
                
                <h2>Tools and Technologies</h2>
                <p>Modern analytics platforms like Google Analytics 4, Adobe Analytics, and specialized marketing attribution tools provide the data needed for comprehensive ROI analysis.</p>
                
                <h2>The Future of Marketing Measurement</h2>
                <p>As privacy regulations evolve and third-party cookies phase out, marketers are adapting with first-party data strategies and privacy-compliant measurement approaches.</p>
                
                <p>Success in digital marketing measurement requires a balance of technical sophistication and business understanding. Focus on metrics that drive real business outcomes.</p>
                """,
                'category': 'digital-marketing',
                'tags': ['seo', 'content-marketing'],
                'reading_time': 10,
                'is_featured': True,
                'meta_title': 'Digital Marketing ROI Measurement 2025 | Pulcova',
                'meta_description': 'Learn how to measure digital marketing ROI effectively in 2025. Discover key metrics, attribution models, and tools for maximizing marketing performance.',
            },
            {
                'title': 'AI and Machine Learning: Transforming Business Operations',
                'excerpt': 'Explore how artificial intelligence and machine learning technologies are revolutionizing business processes, from automation to predictive analytics.',
                'content': """
                <p>Artificial Intelligence and Machine Learning are no longer futuristic concepts—they're practical tools that businesses of all sizes are using to improve efficiency, reduce costs, and create competitive advantages.</p>
                
                <h2>Practical AI Applications in Business</h2>
                
                <h3>Process Automation</h3>
                <p>AI-powered automation is streamlining repetitive tasks across industries. From invoice processing to customer service chatbots, businesses are freeing up human resources for higher-value activities.</p>
                
                <h3>Predictive Analytics</h3>
                <p>Machine learning models are helping businesses predict customer behavior, market trends, and operational needs. This foresight enables proactive decision-making and risk mitigation.</p>
                
                <h3>Personalization at Scale</h3>
                <p>AI enables businesses to deliver personalized experiences to thousands or millions of customers simultaneously, improving engagement and conversion rates.</p>
                
                <h2>Implementation Strategies</h2>
                
                <h3>Start Small, Scale Smart</h3>
                <p>Begin with pilot projects that address specific business problems. Prove value before expanding AI initiatives across the organization.</p>
                
                <h3>Data Quality Foundation</h3>
                <p>Successful AI implementation requires high-quality, well-organized data. Invest in data infrastructure and governance before deploying AI solutions.</p>
                
                <h3>Team Development</h3>
                <p>Build internal AI capabilities through training and hiring. Combining domain expertise with technical skills creates the most effective AI teams.</p>
                
                <h2>Overcoming Common Challenges</h2>
                <p>Address concerns about job displacement through reskilling programs. Focus on augmenting human capabilities rather than replacing workers entirely.</p>
                
                <p>AI and machine learning represent transformative opportunities for businesses willing to invest in the right strategies, people, and technologies.</p>
                """,
                'category': 'technology',
                'tags': ['ai', 'machine-learning', 'devops'],
                'reading_time': 9,
                'is_featured': False,
                'meta_title': 'AI & Machine Learning Business Transformation | Pulcova',
                'meta_description': 'Discover how AI and machine learning are transforming business operations. Learn implementation strategies, practical applications, and success factors.',
            },
            {
                'title': 'User Experience Design: Principles for Digital Success',
                'excerpt': 'Master the fundamental principles of user experience design that drive engagement, conversion, and customer satisfaction in digital products.',
                'content': """
                <p>Great user experience design is the cornerstone of successful digital products. It's the difference between applications that users love and those they abandon. Understanding UX principles is essential for anyone involved in digital product development.</p>
                
                <h2>Core UX Design Principles</h2>
                
                <h3>User-Centered Design</h3>
                <p>Always start with user needs and behaviors. Conduct user research, create personas, and map user journeys to understand how people interact with your product.</p>
                
                <h3>Simplicity and Clarity</h3>
                <p>Reduce cognitive load by presenting information clearly and eliminating unnecessary elements. Every design decision should serve a purpose and support user goals.</p>
                
                <h3>Consistency</h3>
                <p>Maintain consistent patterns, terminology, and visual elements throughout your product. Consistency builds user confidence and reduces learning curves.</p>
                
                <h2>The Design Process</h2>
                
                <h3>Research and Discovery</h3>
                <p>Understand your users through interviews, surveys, and analytics. Identify pain points and opportunities for improvement.</p>
                
                <h3>Ideation and Prototyping</h3>
                <p>Generate multiple solutions and test them quickly through prototypes. Fail fast and iterate based on user feedback.</p>
                
                <h3>Testing and Validation</h3>
                <p>Conduct usability testing to validate design decisions. Use both quantitative metrics and qualitative feedback to guide improvements.</p>
                
                <h2>Modern UX Trends</h2>
                
                <h3>Accessibility-First Design</h3>
                <p>Design for all users, including those with disabilities. Accessibility improves usability for everyone and expands your potential audience.</p>
                
                <h3>Micro-Interactions</h3>
                <p>Small interactive elements that provide feedback and guide users through tasks. These details significantly impact the overall user experience.</p>
                
                <h2>Measuring UX Success</h2>
                <p>Track metrics like task completion rates, user satisfaction scores, and conversion rates to measure the impact of UX improvements.</p>
                
                <p>Excellent user experience design requires empathy, creativity, and analytical thinking. Focus on solving real user problems to create products that people love to use.</p>
                """,
                'category': 'business-strategy',
                'tags': ['ui-ux'],
                'reading_time': 7,
                'is_featured': False,
                'meta_title': 'UX Design Principles for Digital Success | Pulcova Guide',
                'meta_description': 'Learn essential UX design principles that drive digital product success. Discover user-centered design strategies, testing methods, and modern trends.',
            },
            {
                'title': 'Cloud Computing Strategy: Choosing the Right Path for Your Business',
                'excerpt': 'Navigate the complex landscape of cloud computing options and develop a strategy that aligns with your business goals, budget, and technical requirements.',
                'content': """
                <p>Cloud computing has evolved from a technology trend to a business imperative. Organizations across all industries are leveraging cloud services to improve agility, reduce costs, and enable innovation. However, success requires a well-planned strategy.</p>
                
                <h2>Cloud Deployment Models</h2>
                
                <h3>Public Cloud</h3>
                <p>Services provided by third-party providers like AWS, Microsoft Azure, and Google Cloud. Offers scalability and cost-effectiveness for most applications.</p>
                
                <h3>Private Cloud</h3>
                <p>Dedicated cloud infrastructure for a single organization. Provides greater control and security but requires more resources to manage.</p>
                
                <h3>Hybrid Cloud</h3>
                <p>Combines public and private cloud environments. Allows organizations to optimize workload placement based on requirements and regulations.</p>
                
                <h2>Cloud Service Models</h2>
                
                <h3>Infrastructure as a Service (IaaS)</h3>
                <p>Provides fundamental computing resources. Ideal for organizations that want control over their infrastructure without physical hardware.</p>
                
                <h3>Platform as a Service (PaaS)</h3>
                <p>Offers development platforms and tools. Accelerates application development by providing pre-configured environments.</p>
                
                <h3>Software as a Service (SaaS)</h3>
                <p>Ready-to-use applications delivered over the internet. Reduces IT overhead and ensures users always have the latest features.</p>
                
                <h2>Migration Strategies</h2>
                
                <h3>Lift and Shift</h3>
                <p>Move existing applications to the cloud with minimal changes. Quick to implement but may not optimize cloud benefits.</p>
                
                <h3>Re-platforming</h3>
                <p>Make targeted optimizations during migration. Balances speed with cloud-native advantages.</p>
                
                <h3>Re-architecting</h3>
                <p>Redesign applications for cloud-native architectures. Maximizes cloud benefits but requires more time and resources.</p>
                
                <h2>Security and Compliance</h2>
                <p>Implement robust security measures including encryption, access controls, and monitoring. Ensure compliance with industry regulations and data protection laws.</p>
                
                <p>A successful cloud strategy requires careful planning, stakeholder alignment, and continuous optimization. Start with clear business objectives and choose cloud services that support your goals.</p>
                """,
                'category': 'technology',
                'tags': ['cloud-computing', 'devops'],
                'reading_time': 11,
                'is_featured': False,
                'meta_title': 'Cloud Computing Strategy Guide | Business Cloud Adoption',
                'meta_description': 'Develop an effective cloud computing strategy for your business. Learn about deployment models, service types, migration strategies, and best practices.',
            }
        ]
        
        # Create articles with staggered publication dates
        base_date = timezone.now() - timedelta(days=60)
        
        for i, article_data in enumerate(articles_data):
            # Check if article already exists
            slug = slugify(article_data['title'])
            if Article.objects.filter(slug=slug).exists():
                self.stdout.write(f'Article already exists: {article_data["title"]}')
                continue
            
            # Calculate publication date (spread over last 60 days)
            pub_date = base_date + timedelta(days=i * 10)
            
            # Create the article
            article = Article.objects.create(
                title=article_data['title'],
                slug=slug,
                excerpt=article_data['excerpt'],
                content=article_data['content'],
                author=author,
                category=categories[article_data['category']],
                reading_time=article_data['reading_time'],
                is_featured=article_data['is_featured'],
                is_published=True,
                published_at=pub_date,
                meta_title=article_data['meta_title'],
                meta_description=article_data['meta_description'],
            )
            
            # Add tags
            for tag_slug in article_data['tags']:
                if tag_slug in tags:
                    article.tags.add(tags[tag_slug])
            
            article.save()
            self.stdout.write(f'Created article: {article.title}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(articles_data)} blog articles!')
        )
