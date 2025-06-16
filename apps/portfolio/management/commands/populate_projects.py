"""
Django management command to populate the database with realistic project data.

Usage:
    python manage.py populate_projects
    python manage.py populate_projects --clear  # Clear existing data first
    python manage.py populate_projects --projects 15  # Create 15 projects instead of default 10
"""

import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile
from django.conf import settings
import os

from apps.portfolio.models import Project, Technology, GalleryImage


class Command(BaseCommand):
    help = 'Populate the database with realistic portfolio project data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--projects',
            type=int,
            default=10,
            help='Number of projects to create (default: 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing project data before populating'
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Skip creating placeholder images'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting portfolio data population...\n')
        )
        
        try:
            with transaction.atomic():
                if options['clear']:
                    self._clear_existing_data()
                
                # Create technologies first
                technologies = self._create_technologies()
                
                # Create gallery images
                gallery_images = self._create_gallery_images(skip_images=options['skip_images'])
                
                # Create projects
                projects_count = options['projects']
                self._create_projects(projects_count, technologies, gallery_images, skip_images=options['skip_images'])
                
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ Successfully populated database with {projects_count} projects!')
                )
                
        except Exception as e:
            raise CommandError(f'❌ Error populating data: {str(e)}')
    
    def _clear_existing_data(self):
        """Clear existing project data"""
        self.stdout.write('🧹 Clearing existing data...')
        
        Project.objects.all().delete()
        GalleryImage.objects.all().delete()
        Technology.objects.all().delete()
        
        self.stdout.write(self.style.WARNING('   ✔ Cleared existing projects, technologies, and gallery images'))
    
    def _create_technologies(self):
        """Create technology entries if they don't exist"""
        self.stdout.write('🛠️  Creating technologies...')
        
        tech_data = [
            # Frontend
            {'name': 'React', 'category': 'frontend'},
            {'name': 'Vue.js', 'category': 'frontend'},
            {'name': 'Angular', 'category': 'frontend'},
            {'name': 'Next.js', 'category': 'frontend'},
            {'name': 'Nuxt.js', 'category': 'frontend'},
            {'name': 'TypeScript', 'category': 'frontend'},
            {'name': 'JavaScript', 'category': 'frontend'},
            {'name': 'HTML5', 'category': 'frontend'},
            {'name': 'CSS3', 'category': 'frontend'},
            {'name': 'Tailwind CSS', 'category': 'frontend'},
            {'name': 'Bootstrap', 'category': 'frontend'},
            {'name': 'Sass/SCSS', 'category': 'frontend'},
            
            # Backend
            {'name': 'Django', 'category': 'backend'},
            {'name': 'Django REST Framework', 'category': 'backend'},
            {'name': 'FastAPI', 'category': 'backend'},
            {'name': 'Flask', 'category': 'backend'},
            {'name': 'Node.js', 'category': 'backend'},
            {'name': 'Express.js', 'category': 'backend'},
            {'name': 'Python', 'category': 'backend'},
            {'name': 'Java', 'category': 'backend'},
            {'name': 'Spring Boot', 'category': 'backend'},
            {'name': 'PHP', 'category': 'backend'},
            {'name': 'Laravel', 'category': 'backend'},
            
            # Database
            {'name': 'PostgreSQL', 'category': 'database'},
            {'name': 'MySQL', 'category': 'database'},
            {'name': 'MongoDB', 'category': 'database'},
            {'name': 'Redis', 'category': 'database'},
            {'name': 'SQLite', 'category': 'database'},
            {'name': 'Firebase', 'category': 'database'},
            
            # DevOps
            {'name': 'Docker', 'category': 'devops'},
            {'name': 'Kubernetes', 'category': 'devops'},
            {'name': 'AWS', 'category': 'devops'},
            {'name': 'Google Cloud', 'category': 'devops'},
            {'name': 'Azure', 'category': 'devops'},
            {'name': 'Jenkins', 'category': 'devops'},
            {'name': 'GitHub Actions', 'category': 'devops'},
            {'name': 'Nginx', 'category': 'devops'},
            
            # Mobile
            {'name': 'React Native', 'category': 'mobile'},
            {'name': 'Flutter', 'category': 'mobile'},
            {'name': 'Swift', 'category': 'mobile'},
            {'name': 'Kotlin', 'category': 'mobile'},
            
            # Other
            {'name': 'TensorFlow', 'category': 'other'},
            {'name': 'PyTorch', 'category': 'other'},
            {'name': 'OpenAI API', 'category': 'other'},
            {'name': 'Stripe API', 'category': 'other'},
            {'name': 'PayPal API', 'category': 'other'},
            {'name': 'GraphQL', 'category': 'other'},
            {'name': 'WebSockets', 'category': 'other'},
            {'name': 'Celery', 'category': 'other'},
            {'name': 'WebRTC', 'category': 'other'},
        ]
        
        technologies = []
        for tech_info in tech_data:
            tech, created = Technology.objects.get_or_create(
                name=tech_info['name'],
                defaults={
                    'slug': slugify(tech_info['name']),
                    'category': tech_info['category']
                }
            )
            technologies.append(tech)
            if created:
                self.stdout.write(f'   ✔ Created technology: {tech.name}')
        
        self.stdout.write(self.style.SUCCESS(f'   ✅ Technologies ready: {len(technologies)} total'))
        return technologies
    
    def _create_gallery_images(self, skip_images=False):
        """Create gallery image entries"""
        self.stdout.write('🖼️  Creating gallery images...')
        
        gallery_images = []
        image_descriptions = [
            'Dashboard overview showing key metrics',
            'User interface with modern design',
            'Mobile responsive layout',
            'Admin panel with data visualization',
            'API documentation interface',
            'Login and authentication flow',
            'User profile management screen',
            'Settings and configuration page',
            'Real-time notifications system',
            'Data analytics and reports view',
            'Payment integration interface',
            'Chat and messaging features',
            'File upload and management',
            'Search and filter functionality',
            'Landing page design',
            'Product catalog view',
            'Shopping cart and checkout',
            'User onboarding flow',
            'Error handling and feedback',
            'Performance monitoring dashboard'
        ]
        
        for i, description in enumerate(image_descriptions, 1):
            gallery_image = GalleryImage.objects.create(
                alt_text=description
            )
            
            if not skip_images:
                # Create a placeholder image file
                placeholder_content = self._create_placeholder_image_content(f"Gallery Image {i}")
                gallery_image.image.save(
                    f'gallery_image_{i}.jpg',
                    ContentFile(placeholder_content),
                    save=True
                )
            
            gallery_images.append(gallery_image)
            self.stdout.write(f'   ✔ Created gallery image: {description}')
        
        self.stdout.write(self.style.SUCCESS(f'   ✅ Gallery images ready: {len(gallery_images)} total'))
        return gallery_images
    
    def _create_projects(self, count, technologies, gallery_images, skip_images=False):
        """Create realistic project entries"""
        self.stdout.write(f'📂 Creating {count} realistic projects...')
        
        project_templates = [
            {
                'title': 'AI-Powered Resume Analyzer',
                'description': 'An intelligent resume analysis platform that uses natural language processing to evaluate resumes against job descriptions and provide actionable feedback.',
                'detailed_content': '''This comprehensive resume analysis platform leverages advanced AI technologies to help job seekers optimize their resumes. The system uses natural language processing to analyze resume content, compare it against job descriptions, and provide detailed feedback on improvements.

Key features include:
- Resume parsing and content extraction
- AI-powered keyword optimization suggestions
- ATS (Applicant Tracking System) compatibility scoring
- Industry-specific recommendations
- Real-time collaboration features
- Export capabilities in multiple formats

The platform has helped over 10,000 job seekers improve their resume quality and land interviews at top companies.''',
                'project_type': 'web',
                'tech_stack': ['Python', 'Django', 'OpenAI API', 'React', 'PostgreSQL', 'Docker'],
                'months_ago_start': 8,
                'months_duration': 4,
                'has_live_url': True,
                'has_github': True,
                'is_featured': True,
            },
            {
                'title': 'E-Commerce Platform with Stripe Integration',
                'description': 'A full-featured e-commerce solution with modern payment processing, inventory management, and comprehensive admin dashboard.',
                'detailed_content': '''A complete e-commerce platform built with modern web technologies, featuring secure payment processing through Stripe, comprehensive inventory management, and a powerful admin dashboard.

The platform includes:
- Product catalog with advanced search and filtering
- Shopping cart and wishlist functionality
- Secure payment processing with Stripe
- Order management and tracking
- Inventory management system
- Customer management and analytics
- Multi-language and multi-currency support
- Mobile-responsive design
- SEO optimization
- Email marketing integration

Successfully processing over $100K in monthly transactions with 99.9% uptime.''',
                'project_type': 'web',
                'tech_stack': ['Django', 'Django REST Framework', 'React', 'Stripe API', 'PostgreSQL', 'Redis', 'AWS'],
                'months_ago_start': 12,
                'months_duration': 6,
                'has_live_url': True,
                'has_github': False,
                'is_featured': True,
            },
            {
                'title': 'Real-Time Chat Application',
                'description': 'A modern real-time messaging platform with video calls, file sharing, and team collaboration features built with WebRTC and WebSockets.',
                'detailed_content': '''A comprehensive real-time communication platform that enables seamless messaging, video conferencing, and team collaboration. Built with modern web technologies for optimal performance and user experience.

Features include:
- Real-time messaging with WebSocket connections
- Video and audio calling with WebRTC
- File sharing and media uploads
- Group chats and channels
- User presence indicators
- Message history and search
- Push notifications
- Screen sharing capabilities
- Mobile apps for iOS and Android
- End-to-end encryption for privacy

Serving over 50,000 active users with sub-100ms message delivery.''',
                'project_type': 'web',
                'tech_stack': ['Node.js', 'Express.js', 'React', 'WebSockets', 'WebRTC', 'MongoDB', 'React Native'],
                'months_ago_start': 10,
                'months_duration': 5,
                'has_live_url': True,
                'has_github': True,
                'is_featured': False,
            },
            {
                'title': 'Portfolio Builder Web App',
                'description': 'A drag-and-drop portfolio builder that allows creatives to showcase their work with customizable templates and integrated analytics.',
                'detailed_content': '''An intuitive portfolio builder designed for creatives, freelancers, and professionals to showcase their work effectively. The platform offers drag-and-drop functionality, customizable templates, and built-in analytics.

Key capabilities:
- Drag-and-drop interface builder
- 50+ professional templates
- Custom domain support
- SEO optimization tools
- Integrated analytics and visitor tracking
- Social media integration
- Contact form management
- Image optimization and CDN
- Mobile-responsive designs
- Portfolio export options
- Client collaboration features

Over 25,000 portfolios created with an average 40% increase in client inquiries.''',
                'project_type': 'web',
                'tech_stack': ['Vue.js', 'Nuxt.js', 'Django', 'PostgreSQL', 'AWS', 'Tailwind CSS'],
                'months_ago_start': 6,
                'months_duration': 3,
                'has_live_url': True,
                'has_github': True,
                'is_featured': False,
            },
            {
                'title': 'Task Management API',
                'description': 'A RESTful API for task and project management with team collaboration, time tracking, and comprehensive reporting features.',
                'detailed_content': '''A robust RESTful API designed for task and project management applications. Built with FastAPI for high performance and automatic API documentation, featuring comprehensive team collaboration tools.

API features:
- Complete CRUD operations for tasks and projects
- User authentication and authorization
- Team management and permissions
- Time tracking and reporting
- File attachments and comments
- Real-time notifications
- Advanced filtering and search
- Rate limiting and security measures
- Automatic API documentation with Swagger
- Webhook integrations
- Third-party app integrations

Processing over 1 million API requests monthly with 99.95% uptime.''',
                'project_type': 'api',
                'tech_stack': ['FastAPI', 'Python', 'PostgreSQL', 'Redis', 'Docker', 'AWS'],
                'months_ago_start': 4,
                'months_duration': 2,
                'has_live_url': False,
                'has_github': True,
                'is_featured': False,
            },
            {
                'title': 'Fitness Tracking Mobile App',
                'description': 'Cross-platform mobile application for fitness tracking with workout planning, nutrition logging, and social features.',
                'detailed_content': '''A comprehensive fitness tracking application available on both iOS and Android platforms. The app helps users monitor their fitness journey with workout planning, nutrition tracking, and social motivation features.

App features:
- Workout planning and tracking
- Exercise library with video demonstrations
- Nutrition logging and calorie counting
- Progress photos and measurements
- Social features and challenges
- Wearable device integration
- Personal trainer connections
- Custom workout creation
- Achievement badges and rewards
- Offline functionality
- Health app integrations

Downloaded by over 100,000 users with 4.8-star average rating.''',
                'project_type': 'mobile',
                'tech_stack': ['React Native', 'Node.js', 'MongoDB', 'Firebase', 'TypeScript'],
                'months_ago_start': 14,
                'months_duration': 8,
                'has_live_url': True,
                'has_github': False,
                'is_featured': True,
            },
            {
                'title': 'Data Analytics Dashboard',
                'description': 'Interactive business intelligence dashboard with real-time data visualization, custom reports, and automated insights.',
                'detailed_content': '''A powerful business intelligence dashboard that transforms raw data into actionable insights. Built with modern visualization libraries and real-time data processing capabilities.

Dashboard features:
- Real-time data visualization
- Interactive charts and graphs
- Custom report generation
- Automated data insights
- Multi-source data integration
- Role-based access control
- Export capabilities (PDF, Excel, CSV)
- Scheduled report delivery
- Mobile-responsive design
- Data filtering and drill-down
- Alert system for anomalies

Helping businesses make data-driven decisions with 40% faster reporting.''',
                'project_type': 'web',
                'tech_stack': ['React', 'TypeScript', 'Django', 'PostgreSQL', 'Redis', 'Docker'],
                'months_ago_start': 5,
                'months_duration': 3,
                'has_live_url': True,
                'has_github': True,
                'is_featured': False,
            },
            {
                'title': 'Cloud-Based Note Taking App',
                'description': 'Secure cloud-based note taking application with markdown support, real-time sync, and collaborative editing features.',
                'detailed_content': '''A feature-rich note-taking application that syncs across all devices with real-time collaboration capabilities. Built with security and user experience as top priorities.

Application features:
- Rich text and Markdown editing
- Real-time synchronization
- Collaborative editing
- Folder organization and tags
- Advanced search functionality
- Offline access capability
- Version history and recovery
- Export options (PDF, HTML, MD)
- End-to-end encryption
- Team workspaces
- Integration with popular tools

Trusted by over 75,000 users for secure note management.''',
                'project_type': 'web',
                'tech_stack': ['Vue.js', 'Node.js', 'Express.js', 'MongoDB', 'WebSockets', 'AWS'],
                'months_ago_start': 7,
                'months_duration': 4,
                'has_live_url': True,
                'has_github': True,
                'is_featured': False,
            },
            {
                'title': 'Inventory Management System',
                'description': 'Enterprise-grade inventory management system with barcode scanning, automated reordering, and multi-location support.',
                'detailed_content': '''A comprehensive inventory management system designed for businesses of all sizes. Features advanced tracking, automated processes, and detailed reporting for efficient inventory control.

System capabilities:
- Barcode and QR code scanning
- Automated reorder point alerts
- Multi-location inventory tracking
- Supplier management
- Purchase order generation
- Stock movement tracking
- Detailed reporting and analytics
- Integration with accounting systems
- Mobile app for warehouse staff
- Batch and serial number tracking
- Cycle counting features

Reducing inventory costs by 25% for over 500 businesses.''',
                'project_type': 'web',
                'tech_stack': ['Django', 'React', 'PostgreSQL', 'Celery', 'Docker', 'Bootstrap'],
                'months_ago_start': 9,
                'months_duration': 5,
                'has_live_url': False,
                'has_github': True,
                'is_featured': False,
            },
            {
                'title': 'Learning Management System',
                'description': 'Modern LMS platform with interactive courses, video streaming, progress tracking, and certification management.',
                'detailed_content': '''A comprehensive learning management system that facilitates online education with interactive courses, multimedia content, and detailed progress tracking.

Platform features:
- Course creation and management
- Video streaming and playback
- Interactive quizzes and assignments
- Student progress tracking
- Certification management
- Discussion forums
- Live webinar integration
- Mobile learning app
- Gamification elements
- Advanced analytics
- Integration with external tools
- Multi-language support

Facilitating education for over 200,000 students worldwide.''',
                'project_type': 'web',
                'tech_stack': ['Django', 'React', 'PostgreSQL', 'Redis', 'AWS', 'TensorFlow'],
                'months_ago_start': 15,
                'months_duration': 10,
                'has_live_url': True,
                'has_github': False,
                'is_featured': True,
            },
        ]
        
        created_projects = []
        
        for i in range(count):
            template = project_templates[i % len(project_templates)]
            
            # Generate unique title if we're creating more projects than templates
            title = template['title']
            if i >= len(project_templates):
                title = f"{title} v{(i // len(project_templates)) + 1}"
            
            # Calculate dates
            start_date = date.today() - timedelta(days=template['months_ago_start'] * 30)
            end_date = None
            if template.get('months_duration'):
                end_date = start_date + timedelta(days=template['months_duration'] * 30)
                # 30% chance the project is still ongoing
                if random.random() < 0.3:
                    end_date = None
            
            # Generate URLs
            live_url = ''
            github_url = ''
            if template.get('has_live_url') and random.random() < 0.8:
                domain_slug = slugify(title.split()[0])
                live_url = f'https://{domain_slug}.pulcova.dev'
            
            if template.get('has_github') and random.random() < 0.9:
                repo_slug = slugify(title)
                github_url = f'https://github.com/priyanshu-sharma/{repo_slug}'
            
            # Create the project
            project = Project(
                title=title,
                slug=slugify(title),
                description=template['description'],
                detailed_content=template['detailed_content'],
                project_type=template['project_type'],
                start_date=start_date,
                end_date=end_date,
                is_featured=template.get('is_featured', False),
                is_published=True,
                published_at=timezone.now(),
                order_priority=random.randint(1, 100),
                view_count=random.randint(50, 2500),
                live_url=live_url,
                github_url=github_url,
                meta_title=f'{title} | Portfolio',
                meta_description=template['description'][:150],
            )
            
            # Handle featured image
            if not skip_images:
                placeholder_content = self._create_placeholder_image_content(title)
                project.featured_image.save(
                    f'{slugify(title)}_featured.jpg',
                    ContentFile(placeholder_content),
                    save=False  # Don't save the model yet
                )
            
            try:
                project.save()
                
                # Add technologies to the project
                project_technologies = []
                for tech_name in template['tech_stack']:
                    try:
                        tech = Technology.objects.get(name=tech_name)
                        project_technologies.append(tech)
                    except Technology.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'   ⚠ Technology "{tech_name}" not found for project "{title}"')
                        )
                
                if project_technologies:
                    project.tech_stack.set(project_technologies)
                
                # Add random gallery images (1-4 images per project)
                if gallery_images:
                    num_gallery_images = random.randint(1, min(4, len(gallery_images)))
                    selected_gallery_images = random.sample(gallery_images, num_gallery_images)
                    project.gallery_images.set(selected_gallery_images)
                
                created_projects.append(project)
                self.stdout.write(f'   ✔ Created project: {title}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Failed to create project "{title}": {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'   ✅ Projects created: {len(created_projects)} total')
        )
        return created_projects
    
    def _create_placeholder_image_content(self, text):
        """Create placeholder image content (simple text-based placeholder)"""
        # This is a simple placeholder. In a real scenario, you might want to
        # generate actual image files or use a service like placeholder.com
        placeholder_text = f"Placeholder image for: {text}"
        return placeholder_text.encode('utf-8')
