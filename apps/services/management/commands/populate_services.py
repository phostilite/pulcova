"""
Django management command to populate the database with realistic services data.

This command creates sample data for the Services app including:
- Service entries with realistic content
- ServiceInquiry entries with various statuses

Usage:
    python manage.py populate_services
    python manage.py populate_services --clear  # Clear existing data first
    python manage.py populate_services --services 15  # Create 15 services instead of default 10
    python manage.py populate_services --inquiries 25  # Create 25 inquiries instead of default 20
"""

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from apps.services.models import Service, ServiceInquiry


class Command(BaseCommand):
    help = 'Populate the database with realistic services data for development and testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--services',
            type=int,
            default=10,
            help='Number of services to create (default: 10)'
        )
        parser.add_argument(
            '--inquiries',
            type=int,
            default=20,
            help='Number of service inquiries to create (default: 20)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing services data before populating'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting services data population...\n')
        )
        
        try:
            with transaction.atomic():
                if options['clear']:
                    self.clear_existing_data()
                
                # Create services
                services = self.create_services(count=options['services'])
                
                # Create service inquiries
                inquiries = self.create_service_inquiries(
                    count=options['inquiries'],
                    services=services
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Successfully created:\n'
                        f'   • {len(services)} services\n'
                        f'   • {len(inquiries)} service inquiries\n'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during services population: {str(e)}')
            )
            raise CommandError(f'Error during services population: {str(e)}')
    
    def clear_existing_data(self):
        """Clear existing services data with proper error handling"""
        try:
            self.stdout.write('🧹 Clearing existing services data...')
            inquiry_count = ServiceInquiry.objects.count()
            service_count = Service.objects.count()
            
            ServiceInquiry.objects.all().delete()
            Service.objects.all().delete()
            
            self.stdout.write(
                self.style.WARNING(
                    f'   Cleared {service_count} services and {inquiry_count} inquiries.\n'
                )
            )
        except Exception as e:
            raise CommandError(f'Error clearing existing data: {str(e)}')
    
    def create_services(self, count):
        """Create realistic service entries"""
        self.stdout.write(f'💼 Creating {count} services...')
        
        services_data = [
    {
        'title': 'Professional Website Development',
        'description': 'Modern, responsive websites for businesses and professionals using latest web technologies.',
        'detailed_content': '''Get a professional website that represents your brand effectively and converts visitors into customers. I specialize in creating fast, SEO-friendly websites that work perfectly on all devices.

**What's Included:**
- Custom responsive design
- Mobile-first approach
- SEO optimization basics
- Contact forms and integrations
- Content management system
- Basic analytics setup
- SSL certificate setup
- 30 days post-launch support

**Technologies I Use:**
- Frontend: HTML5, CSS3, JavaScript, React/Vue.js
- Backend: Django/Node.js
- Database: PostgreSQL/MySQL
- Deployment: Cloud hosting setup

**Process:**
1. Requirement gathering and planning
2. Design mockups and approval
3. Development and testing
4. Deployment and handover
5. Post-launch support

**Ideal For:**
- Small businesses
- Professional portfolios
- Service providers
- Startups
- Personal brands''',
        'price_range': '$300 - $1,200',
        'delivery_time': '2-4 weeks',
        'order_priority': 100
    },
    {
        'title': 'E-commerce Website Development',
        'description': 'Complete online store solutions with payment integration and inventory management.',
        'detailed_content': '''Launch your online business with a fully functional e-commerce website. I create secure, user-friendly online stores that help you sell effectively.

**E-commerce Features:**
- Product catalog management
- Shopping cart and checkout
- Payment gateway integration (Razorpay, PayPal, Stripe)
- Order management system
- Customer accounts
- Email notifications
- Basic inventory tracking
- Mobile responsive design

**Additional Features:**
- Product search and filters
- Customer reviews
- Wishlist functionality
- Discount codes
- Basic shipping calculator
- GST/Tax calculations
- Invoice generation

**Platform Options:**
- Custom Django e-commerce
- WooCommerce setup and customization
- Basic Shopify store setup

**Post-Launch Support:**
- 30 days bug fixes
- Payment testing assistance
- Basic training on managing products
- Documentation provided''',
        'price_range': '$500 - $2,000',
        'delivery_time': '3-6 weeks',
        'order_priority': 95
    },
    {
        'title': 'REST API Development',
        'description': 'Secure and scalable API development for web and mobile applications.',
        'detailed_content': '''Build robust APIs to power your applications and integrate with third-party services. I develop well-documented, secure APIs following industry best practices.

**API Development Services:**
- RESTful API design and development
- Database design and optimization
- Authentication and authorization (JWT, OAuth)
- API documentation
- Basic rate limiting
- Error handling
- CORS configuration

**Technologies:**
- Django REST Framework
- FastAPI (Python)
- Node.js with Express
- PostgreSQL/MySQL databases
- Redis for caching
- Postman documentation

**Common Use Cases:**
- Mobile app backends
- Web application APIs
- Third-party integrations
- Data synchronization
- Microservices communication

**Deliverables:**
- Fully functional API
- API documentation
- Postman collection
- Basic deployment guide
- 30 days support''',
        'price_range': '$400 - $1,500',
        'delivery_time': '2-5 weeks',
        'order_priority': 90
    },
    {
        'title': 'Bug Fixing & Code Optimization',
        'description': 'Quick resolution of bugs and performance optimization for existing applications.',
        'detailed_content': '''Struggling with bugs or slow performance? I help fix issues and optimize your existing applications for better performance and user experience.

**Services Offered:**
- Bug diagnosis and fixing
- Performance optimization
- Code refactoring
- Database query optimization
- Frontend performance improvements
- Memory leak fixes
- Security vulnerability patches

**Technologies I Work With:**
- Python (Django, Flask, FastAPI)
- JavaScript (React, Vue, Node.js)
- PHP (Laravel, WordPress)
- Databases (PostgreSQL, MySQL, MongoDB)
- Frontend frameworks
- API debugging

**Process:**
1. Initial code review
2. Issue identification
3. Solution implementation
4. Testing and verification
5. Documentation of changes

**Turnaround Time:**
- Critical bugs: 24-48 hours
- Performance issues: 3-5 days
- Code refactoring: 1-2 weeks''',
        'price_range': '$50 - $500',
        'delivery_time': '1-7 days',
        'order_priority': 85
    },
    {
        'title': 'WordPress Website & Customization',
        'description': 'Professional WordPress development, theme customization, and plugin configuration.',
        'detailed_content': '''Get a professional WordPress website tailored to your needs. I provide custom WordPress solutions that are easy to manage and scale.

**WordPress Services:**
- Custom theme development
- Theme customization
- Plugin installation and configuration
- Speed optimization
- Security hardening
- Backup setup
- SEO plugin configuration

**Features Included:**
- Responsive design
- Contact forms
- Social media integration
- Basic SEO setup
- Google Analytics
- Sitemap generation
- Basic security measures

**Additional Services:**
- WooCommerce setup
- Membership sites
- Learning management systems
- Multi-language setup
- Custom post types
- Migration services

**Maintenance Options:**
- Monthly updates: $50/month
- Security monitoring
- Regular backups
- Performance checks''',
        'price_range': '$200 - $800',
        'delivery_time': '1-3 weeks',
        'order_priority': 80
    },
    {
        'title': 'Landing Page Development',
        'description': 'High-converting landing pages for products, services, or marketing campaigns.',
        'detailed_content': '''Create compelling landing pages that convert visitors into customers. I design and develop landing pages optimized for conversions and performance.

**Landing Page Features:**
- Mobile-responsive design
- Fast loading speed
- Clear call-to-actions
- Contact form integration
- A/B testing ready
- Analytics integration
- SEO optimization

**What's Included:**
- Custom design based on your brand
- Copywriting assistance
- Form integration (email/CRM)
- Basic animations
- Social proof elements
- Performance optimization
- Cross-browser testing

**Technology Stack:**
- HTML5, CSS3, JavaScript
- React/Vue.js for interactive elements
- TailwindCSS for styling
- Form handling backend
- Hosting setup assistance

**Perfect For:**
- Product launches
- Service promotions
- Event registrations
- Lead generation
- App downloads''',
        'price_range': '$150 - $500',
        'delivery_time': '3-7 days',
        'order_priority': 75
    },
    {
        'title': 'Database Design & Setup',
        'description': 'Professional database architecture design and implementation for scalable applications.',
        'detailed_content': '''Design efficient database structures that scale with your business. I create well-organized databases with proper relationships and optimizations.

**Database Services:**
- Database schema design
- Table relationships setup
- Index optimization
- Migration scripts
- Backup strategies
- Basic performance tuning

**Supported Databases:**
- PostgreSQL
- MySQL
- MongoDB
- SQLite
- Redis (caching)

**Deliverables:**
- Entity relationship diagrams
- Optimized database schema
- Migration scripts
- Basic queries documentation
- Backup procedures
- Performance recommendations

**Additional Services:**
- Data migration from old systems
- Database performance audit
- Query optimization
- Backup automation setup
- Basic monitoring setup''',
        'price_range': '$200 - $800',
        'delivery_time': '1-2 weeks',
        'order_priority': 70
    },
    {
        'title': 'Full Stack Web Application',
        'description': 'Complete web application development from frontend to backend with database.',
        'detailed_content': '''Build your complete web application idea from scratch. I develop full-featured web applications using modern technologies and best practices.

**Full Stack Development:**
- Custom frontend development
- Backend API development
- Database design and setup
- User authentication system
- Admin panel
- Email integration
- Basic deployment

**Technology Stack:**
- Frontend: React/Vue.js
- Backend: Django/Node.js
- Database: PostgreSQL/MySQL
- Authentication: JWT/Session
- Deployment: VPS/Cloud

**Common Applications:**
- Management systems
- Booking platforms
- Social platforms
- SaaS MVPs
- Internal tools
- Dashboard applications

**Project Includes:**
- Requirement analysis
- UI/UX design consultation
- Development and testing
- Deployment assistance
- Documentation
- 45 days support''',
        'price_range': '$800 - $3,000',
        'delivery_time': '4-8 weeks',
        'order_priority': 65
    },
    {
        'title': 'Mobile App Backend Development',
        'description': 'Scalable backend APIs and services for mobile applications.',
        'detailed_content': '''Power your mobile app with a robust backend. I develop secure, scalable backend services that handle your app's data and business logic efficiently.

**Backend Services:**
- RESTful API development
- User authentication (JWT/OAuth)
- Push notification setup
- File upload handling
- Real-time features (basic)
- Database design
- Third-party integrations

**Features:**
- User management
- Data synchronization
- Offline capability support
- Basic analytics
- Social login integration
- Payment gateway integration
- Email/SMS notifications

**Technologies:**
- Django REST Framework
- Node.js/Express
- PostgreSQL/MongoDB
- Redis for caching
- Firebase integration
- AWS S3 for storage

**Deliverables:**
- Complete API backend
- API documentation
- Deployment guide
- Postman collection
- Basic admin panel''',
        'price_range': '$600 - $2,000',
        'delivery_time': '3-6 weeks',
        'order_priority': 60
    },
    {
        'title': 'Website Maintenance & Support',
        'description': 'Monthly website maintenance, updates, and technical support services.',
        'detailed_content': '''Keep your website running smoothly with regular maintenance and support. I provide reliable maintenance services to ensure your site stays secure and up-to-date.

**Monthly Maintenance Includes:**
- Regular security updates
- Plugin/package updates
- Weekly backups
- Uptime monitoring
- Performance checks
- Bug fixes (up to 4 hours)
- Content updates

**Additional Services:**
- Emergency support
- Security incident response
- Performance optimization
- Feature additions
- Server management
- SSL certificate renewal
- Domain management

**Support Channels:**
- Email support
- WhatsApp for urgent issues
- Monthly status reports
- Backup restoration
- Update documentation

**Plans Available:**
- Basic: $60/month (5 hours support)
- Standard: $120/month (10 hours support)
- Premium: $200/month (20 hours support)''',
        'price_range': '$60 - $200/month',
        'delivery_time': 'Ongoing',
        'order_priority': 55
    },
    {
        'title': 'Technical Consultation',
        'description': 'Expert advice on technology stack, architecture, and development strategies.',
        'detailed_content': '''Get expert guidance for your technical decisions. I provide consultation on technology choices, architecture design, and development best practices.

**Consultation Services:**
- Technology stack selection
- Architecture review
- Code review and audit
- Performance analysis
- Security assessment
- Scalability planning
- Development roadmap

**Areas of Expertise:**
- Web application architecture
- API design patterns
- Database optimization
- Cloud deployment strategies
- Security best practices
- Performance optimization
- Cost optimization

**Consultation Formats:**
- One-time consultation calls
- Written recommendations
- Code review sessions
- Architecture diagrams
- Implementation guides
- Follow-up support

**Ideal For:**
- Startups planning MVPs
- Businesses scaling applications
- Teams facing technical challenges
- Technology migration projects''',
        'price_range': '$50 - $150/hour',
        'delivery_time': 'As needed',
        'order_priority': 50
    },
    {
        'title': 'MVP Development',
        'description': 'Rapid development of Minimum Viable Products for startups and entrepreneurs.',
        'detailed_content': '''Launch your startup idea quickly with a well-built MVP. I help entrepreneurs validate their ideas with functional prototypes that can scale.

**MVP Development Process:**
- Idea refinement and scope definition
- Core feature identification
- Rapid prototyping
- Iterative development
- User feedback integration
- Launch preparation

**What's Included:**
- Basic UI/UX design
- Core feature development
- User authentication
- Basic admin panel
- Payment integration (if needed)
- Deployment setup
- 30 days post-launch support

**Technology Choices:**
- Fast development frameworks
- Proven technology stacks
- Scalable architecture
- Cloud-ready deployment
- Mobile-responsive design

**Timeline & Approach:**
- Week 1-2: Planning and design
- Week 3-6: Core development
- Week 7-8: Testing and launch
- Post-launch: Iterations based on feedback''',
        'price_range': '$1,000 - $4,000',
        'delivery_time': '4-8 weeks',
        'order_priority': 45
    },
    {
        'title': 'SEO & Performance Optimization',
        'description': 'Improve your website\'s search rankings and loading speed.',
        'detailed_content': '''Boost your website's visibility and performance. I optimize websites for better search engine rankings and faster loading times.

**SEO Services:**
- Technical SEO audit
- On-page optimization
- Meta tags optimization
- Schema markup implementation
- Sitemap generation
- Robots.txt optimization
- Basic keyword research

**Performance Optimization:**
- Page speed optimization
- Image optimization
- Code minification
- Caching implementation
- CDN setup assistance
- Database query optimization
- Lazy loading implementation

**Deliverables:**
- SEO audit report
- Performance analysis
- Implementation of fixes
- Before/after metrics
- Optimization guide
- Monitoring setup

**Results You Can Expect:**
- Improved page load times
- Better search rankings
- Enhanced user experience
- Reduced bounce rates
- Mobile performance boost''',
        'price_range': '$200 - $600',
        'delivery_time': '1-2 weeks',
        'order_priority': 40
    },
    {
        'title': 'Payment Gateway Integration',
        'description': 'Secure payment processing integration for websites and applications.',
        'detailed_content': '''Accept payments seamlessly on your platform. I integrate popular payment gateways with proper security measures and testing.

**Payment Gateways:**
- Razorpay (recommended for India)
- PayPal
- Stripe
- Paytm
- UPI integration
- International payments setup

**Integration Features:**
- Secure payment processing
- Multiple payment methods
- Recurring payments
- Refund handling
- Payment webhooks
- Transaction logging
- Invoice generation

**Security Measures:**
- PCI compliance basics
- SSL implementation
- Secure API handling
- Data encryption
- Fraud prevention basics

**Testing & Support:**
- Sandbox testing
- Live payment testing
- Error handling
- Documentation
- 30 days support''',
        'price_range': '$150 - $500',
        'delivery_time': '3-7 days',
        'order_priority': 35
    },
    {
        'title': 'Custom Automation Scripts',
        'description': 'Python scripts and tools to automate repetitive tasks and workflows.',
        'detailed_content': '''Automate your repetitive tasks and save time. I develop custom Python scripts and automation tools tailored to your specific needs.

**Automation Services:**
- Web scraping scripts
- Data processing automation
- Email automation
- File management scripts
- API integration scripts
- Report generation
- Task scheduling

**Common Use Cases:**
- Data extraction from websites
- Bulk file processing
- Automated reporting
- Social media posting
- Database backups
- System monitoring
- Workflow automation

**Technologies:**
- Python (BeautifulSoup, Selenium)
- Task schedulers (Cron, Celery)
- API integrations
- Database connections
- Cloud functions
- Email services

**Deliverables:**
- Working scripts
- Documentation
- Setup instructions
- Basic UI (if needed)
- Source code
- 30 days support''',
        'price_range': '$100 - $800',
        'delivery_time': '3-10 days',
        'order_priority': 30
    }
]
        
        created_services = []
        
        for i, service_data in enumerate(services_data[:count]):
            try:
                # Generate a unique slug
                base_slug = slugify(service_data['title'])
                slug = base_slug
                counter = 1
                while Service.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                # Create service with realistic data
                service = Service.objects.create(
                    title=service_data['title'],
                    slug=slug,
                    description=service_data['description'],
                    detailed_content=service_data['detailed_content'],
                    price_range=service_data.get('price_range', ''),
                    delivery_time=service_data.get('delivery_time', ''),
                    order_priority=service_data.get('order_priority', 50 - i),
                    is_active=True,
                    is_published=random.choice([True, True, True, False]),  # 75% published
                    published_at=timezone.now() - timedelta(
                        days=random.randint(1, 30)
                    ) if random.choice([True, False]) else None
                )
                
                created_services.append(service)
                self.stdout.write(f'   ✓ Created service: {service.title}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'   ⚠ Failed to create service {i+1}: {str(e)}')
                )
                continue
        
        return created_services
    
    def create_service_inquiries(self, count, services):
        """Create realistic service inquiry entries"""
        if not services:
            self.stdout.write(
                self.style.WARNING('No services available for creating inquiries.')
            )
            return []
        
        self.stdout.write(f'📧 Creating {count} service inquiries...')
        
        # Realistic inquiry data templates
        inquiry_templates = [
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.j@techcorp.com',
                'company': 'TechCorp Solutions',
                'budget_range': '$10,000 - $25,000',
                'project_description': 'We need a custom web application for our customer management system. The app should include user authentication, dashboard, reporting features, and API integration with our existing CRM.',
                'timeline': '3-4 months',
                'status': 'new'
            },
            {
                'name': 'Michael Chen',
                'email': 'mchen@startupventure.io',
                'company': 'StartupVenture',
                'budget_range': '$15,000 - $40,000',
                'project_description': 'Looking for mobile app development for both iOS and Android. The app should have user profiles, social features, payment integration, and real-time notifications.',
                'timeline': '4-6 months',
                'status': 'contacted'
            },
            {
                'name': 'Emily Rodriguez',
                'email': 'emily@localrestaurant.com',
                'company': 'Local Restaurant Group',
                'budget_range': '$5,000 - $15,000',
                'project_description': 'Need an e-commerce website for online food ordering with delivery tracking, payment processing, and inventory management.',
                'timeline': '2-3 months',
                'status': 'converted'
            },
            {
                'name': 'David Wilson',
                'email': 'd.wilson@consultingfirm.com',
                'company': 'Wilson Consulting',
                'budget_range': '$8,000 - $20,000',
                'project_description': 'Require a complete digital marketing strategy including SEO, PPC campaigns, social media management, and content marketing for our B2B services.',
                'timeline': 'Ongoing monthly service',
                'status': 'new'
            },
            {
                'name': 'Lisa Thompson',
                'email': 'lisa.t@healthcareplus.org',
                'company': 'HealthCare Plus',
                'budget_range': '$20,000 - $50,000',
                'project_description': 'Looking for HIPAA-compliant web application development for patient management with secure messaging, appointment scheduling, and billing integration.',
                'timeline': '6-8 months',
                'status': 'contacted'
            },
            {
                'name': 'Robert Martinez',
                'email': 'rmartinez@manufacturer.com',
                'company': 'Martinez Manufacturing',
                'budget_range': '$12,000 - $30,000',
                'project_description': 'Need inventory management system with barcode scanning, real-time tracking, automated reordering, and integration with accounting software.',
                'timeline': '4-5 months',
                'status': 'new'
            },
            {
                'name': 'Amanda Foster',
                'email': 'afoster@realestate.net',
                'company': 'Foster Real Estate',
                'budget_range': '$6,000 - $18,000',
                'project_description': 'Require a real estate website with property listings, virtual tours, lead capture forms, and CRM integration for managing clients.',
                'timeline': '2-4 months',
                'status': 'converted'
            },
            {
                'name': 'James Kim',
                'email': 'jkim@ecommercebrand.com',
                'company': 'E-commerce Brand Co.',
                'budget_range': '$25,000 - $60,000',
                'project_description': 'Looking for complete e-commerce platform development with multi-vendor support, advanced analytics, subscription management, and mobile app.',
                'timeline': '6-9 months',
                'status': 'contacted'
            },
            {
                'name': 'Jennifer Adams',
                'email': 'j.adams@nonprofit.org',
                'company': 'Community Nonprofit',
                'budget_range': '$3,000 - $8,000',
                'project_description': 'Need a website for our nonprofit with donation processing, volunteer management, event calendar, and newsletter signup.',
                'timeline': '1-2 months',
                'status': 'closed'
            },
            {
                'name': 'Christopher Lee',
                'email': 'clee@financialservices.com',
                'company': 'Premier Financial Services',
                'budget_range': '$18,000 - $45,000',
                'project_description': 'Require secure financial platform development with client portal, document management, reporting dashboard, and compliance features.',
                'timeline': '5-7 months',
                'status': 'new'
            },
            {
                'name': 'Michelle Brown',
                'email': 'mbrown@educationtech.edu',
                'company': 'EduTech Solutions',
                'budget_range': '$15,000 - $35,000',
                'project_description': 'Looking for learning management system development with course creation tools, student progress tracking, and video conferencing integration.',
                'timeline': '4-6 months',
                'status': 'contacted'
            },
            {
                'name': 'Daniel Garcia',
                'email': 'dgarcia@logistics.com',
                'company': 'Garcia Logistics',
                'budget_range': '$10,000 - $25,000',
                'project_description': 'Need fleet management system with GPS tracking, route optimization, driver management, and fuel monitoring capabilities.',
                'timeline': '3-5 months',
                'status': 'converted'
            },
            {
                'name': 'Rachel Green',
                'email': 'rgreen@fashionbrand.com',
                'company': 'Green Fashion Brand',
                'budget_range': '$8,000 - $22,000',
                'project_description': 'Require fashion e-commerce website with size guides, color variations, customer reviews, wishlist, and social media integration.',
                'timeline': '3-4 months',
                'status': 'new'
            },
            {
                'name': 'Kevin White',
                'email': 'kwhite@sportinggoods.com',
                'company': 'Athletic Gear Pro',
                'budget_range': '$12,000 - $28,000',
                'project_description': 'Looking for sports equipment e-commerce platform with product configurator, team ordering system, and bulk pricing features.',
                'timeline': '4-5 months',
                'status': 'contacted'
            },
            {
                'name': 'Stephanie Clark',
                'email': 's.clark@beautystore.com',
                'company': 'Beauty Store Chain',
                'budget_range': '$20,000 - $50,000',
                'project_description': 'Need multi-store e-commerce platform with loyalty program, beauty quiz features, virtual try-on, and subscription services.',
                'timeline': '5-8 months',
                'status': 'new'
            }
        ]
        
        created_inquiries = []
        
        for i in range(count):
            try:
                # Select random template and service
                template = random.choice(inquiry_templates)
                service = random.choice(services)
                
                # Add some variation to the template data
                variation_suffix = f" {random.randint(1, 999)}" if random.choice([True, False]) else ""
                
                inquiry = ServiceInquiry.objects.create(
                    service=service,
                    name=template['name'] + variation_suffix,
                    email=template['email'].replace('@', f'+{random.randint(1, 999)}@') if random.choice([True, False]) else template['email'],
                    company=template['company'] + variation_suffix,
                    budget_range=template['budget_range'],
                    project_description=template['project_description'],
                    timeline=template['timeline'],
                    status=random.choice(['new', 'contacted', 'converted', 'closed']),
                    created_at=timezone.now() - timedelta(
                        days=random.randint(1, 60),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                )
                
                created_inquiries.append(inquiry)
                if i < 5:  # Show first 5 for brevity
                    self.stdout.write(
                        f'   ✓ Created inquiry: {inquiry.name} for {inquiry.service.title}'
                    )
                elif i == 5:
                    self.stdout.write(f'   ✓ ... and {count - 5} more inquiries')
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'   ⚠ Failed to create inquiry {i+1}: {str(e)}')
                )
                continue
        
        return created_inquiries
