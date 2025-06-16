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
                'title': 'Custom Web Development',
                'description': 'Professional custom web development services tailored to your business needs.',
                'detailed_content': '''We specialize in creating custom web applications that drive business growth and enhance user experience. Our team of experienced developers uses cutting-edge technologies to build scalable, secure, and high-performance web solutions.

**What We Offer:**
- Custom web application development
- Responsive design implementation
- Database design and optimization
- API development and integration
- Performance optimization
- Security implementation
- Ongoing maintenance and support

**Technologies We Use:**
- Frontend: React, Vue.js, Angular, HTML5, CSS3, JavaScript
- Backend: Django, Node.js, Laravel, Express.js
- Databases: PostgreSQL, MySQL, MongoDB
- Cloud: AWS, Google Cloud, Azure

**Our Process:**
1. **Discovery & Planning**: Understanding your requirements and business goals
2. **Design & Prototyping**: Creating wireframes and interactive prototypes
3. **Development**: Building your application with best practices
4. **Testing**: Comprehensive testing across devices and browsers
5. **Deployment**: Launching your application with proper configuration
6. **Support**: Ongoing maintenance and feature updates

**Why Choose Us:**
- 5+ years of experience in web development
- Agile development methodology
- Regular communication and updates
- Post-launch support and maintenance
- Competitive pricing with transparent billing''',
                'price_range': '$5,000 - $50,000',
                'delivery_time': '4-16 weeks',
                'order_priority': 100
            },
            {
                'title': 'E-commerce Development',
                'description': 'Complete e-commerce solutions to help you sell online effectively.',
                'detailed_content': '''Transform your business with our comprehensive e-commerce development services. We create powerful online stores that convert visitors into customers and drive sales growth.

**E-commerce Solutions:**
- Custom e-commerce platforms
- Shopify and WooCommerce development
- Payment gateway integration
- Inventory management systems
- Order processing automation
- Mobile-responsive design
- SEO optimization

**Key Features:**
- Secure payment processing
- User-friendly admin panels
- Advanced product catalogs
- Shopping cart optimization
- Customer account management
- Analytics and reporting
- Multi-language support
- Social media integration

**Platforms We Work With:**
- Shopify & Shopify Plus
- WooCommerce
- Magento
- Custom solutions with Django/React

**Our E-commerce Expertise:**
- B2B and B2C platforms
- Marketplace development
- Subscription-based models
- Digital product delivery
- International shipping integration
- Tax calculation systems

**Success Metrics:**
- Average 35% increase in conversion rates
- 50% reduction in cart abandonment
- 99.9% uptime guarantee
- Mobile-first approach for better user experience''',
                'price_range': '$8,000 - $80,000',
                'delivery_time': '6-20 weeks',
                'order_priority': 95
            },
            {
                'title': 'Mobile App Development',
                'description': 'Native and cross-platform mobile applications for iOS and Android.',
                'detailed_content': '''Create engaging mobile experiences with our professional mobile app development services. We build native and cross-platform applications that deliver exceptional user experiences.

**Mobile Development Services:**
- iOS app development (Swift/SwiftUI)
- Android app development (Kotlin/Java)
- Cross-platform development (React Native, Flutter)
- Progressive Web Apps (PWA)
- App Store optimization
- Mobile app maintenance

**App Categories We Specialize In:**
- Business and productivity apps
- E-commerce and marketplace apps
- Social networking applications
- Healthcare and fitness apps
- Educational and learning apps
- Entertainment and gaming apps
- Financial and fintech apps

**Development Process:**
1. **Strategy & Planning**: Market research and feature planning
2. **UI/UX Design**: User-centered design and prototyping
3. **Development**: Agile development with regular updates
4. **Testing**: Comprehensive testing on multiple devices
5. **App Store Submission**: Handling submission process
6. **Post-Launch Support**: Updates, maintenance, and new features

**Key Features:**
- Native performance optimization
- Offline functionality
- Push notifications
- In-app purchases
- Social media integration
- Analytics and user tracking
- Security and data protection

**Why Our Mobile Apps Stand Out:**
- Average 4.5+ App Store ratings
- 99.9% crash-free rate
- Optimized for battery life
- Seamless user experience
- Regular updates and improvements''',
                'price_range': '$15,000 - $100,000',
                'delivery_time': '8-24 weeks',
                'order_priority': 90
            },
            {
                'title': 'Digital Marketing Strategy',
                'description': 'Comprehensive digital marketing strategies to grow your online presence.',
                'detailed_content': '''Accelerate your business growth with our data-driven digital marketing strategies. We help businesses increase their online visibility, attract qualified leads, and convert them into loyal customers.

**Digital Marketing Services:**
- SEO (Search Engine Optimization)
- PPC (Pay-Per-Click) advertising
- Social media marketing
- Content marketing
- Email marketing campaigns
- Conversion rate optimization
- Marketing automation

**SEO Services:**
- Keyword research and analysis
- On-page optimization
- Technical SEO audits
- Link building strategies
- Local SEO optimization
- SEO content creation
- Performance tracking and reporting

**PPC Advertising:**
- Google Ads campaigns
- Facebook and Instagram ads
- LinkedIn advertising
- YouTube advertising
- Remarketing campaigns
- Landing page optimization
- A/B testing and optimization

**Social Media Marketing:**
- Social media strategy development
- Content creation and curation
- Community management
- Influencer partnerships
- Social media advertising
- Analytics and reporting

**Content Marketing:**
- Content strategy development
- Blog writing and optimization
- Video content creation
- Infographic design
- Email newsletter creation
- Webinar planning and execution

**Results You Can Expect:**
- 150% increase in organic traffic
- 300% improvement in lead generation
- 25% reduction in customer acquisition cost
- 200% increase in social media engagement''',
                'price_range': '$2,000 - $15,000/month',
                'delivery_time': '2-4 weeks setup',
                'order_priority': 85
            },
            {
                'title': 'UI/UX Design Services',
                'description': 'User-centered design solutions that enhance user experience and drive conversions.',
                'detailed_content': '''Create exceptional user experiences with our professional UI/UX design services. We design interfaces that are not only beautiful but also functional and user-friendly.

**UI/UX Design Services:**
- User research and analysis
- Information architecture
- Wireframing and prototyping
- Visual design and branding
- Usability testing
- Design system creation
- Mobile-first design approach

**Design Process:**
1. **Research**: Understanding users, competitors, and market
2. **Strategy**: Defining goals and user journeys
3. **Wireframing**: Creating structural blueprints
4. **Prototyping**: Building interactive prototypes
5. **Visual Design**: Applying colors, typography, and imagery
6. **Testing**: Validating designs with real users
7. **Implementation**: Working with developers for pixel-perfect execution

**Specializations:**
- Web application interfaces
- Mobile app design
- E-commerce user experience
- SaaS product design
- Dashboard and admin interfaces
- Landing page optimization
- Accessibility compliance

**Design Tools & Technologies:**
- Figma, Sketch, Adobe XD
- InVision, Principle, Framer
- Adobe Creative Suite
- Zeplin for developer handoff
- UsabilityHub for testing
- Hotjar for user behavior analysis

**What Makes Our Designs Effective:**
- User-centered design approach
- Data-driven design decisions
- Accessibility standards compliance
- Mobile-first responsive design
- Conversion rate optimization
- Brand consistency across platforms

**Deliverables:**
- User research reports
- Wireframes and user flows
- High-fidelity mockups
- Interactive prototypes
- Design specifications
- Style guides and design systems''',
                'price_range': '$3,000 - $25,000',
                'delivery_time': '3-8 weeks',
                'order_priority': 80
            },
            {
                'title': 'Cloud Infrastructure Setup',
                'description': 'Secure and scalable cloud infrastructure solutions for modern businesses.',
                'detailed_content': '''Build a robust foundation for your applications with our cloud infrastructure services. We help businesses migrate to the cloud and optimize their infrastructure for performance, security, and cost-effectiveness.

**Cloud Services:**
- Cloud migration planning and execution
- Infrastructure as Code (IaC)
- Auto-scaling configuration
- Load balancing setup
- Database optimization
- Security implementation
- Monitoring and alerting

**Cloud Platforms:**
- Amazon Web Services (AWS)
- Google Cloud Platform (GCP)
- Microsoft Azure
- DigitalOcean
- Heroku for rapid deployment

**Infrastructure Components:**
- Virtual private clouds (VPC)
- Container orchestration (Kubernetes, Docker)
- Content delivery networks (CDN)
- Database clusters and replication
- Backup and disaster recovery
- SSL certificates and security
- CI/CD pipeline setup

**DevOps Services:**
- Continuous Integration/Continuous Deployment
- Infrastructure monitoring
- Automated testing pipelines
- Configuration management
- Log aggregation and analysis
- Performance optimization
- Cost optimization strategies

**Security Features:**
- Identity and Access Management (IAM)
- Network security groups
- Data encryption at rest and in transit
- Regular security audits
- Compliance frameworks (SOC 2, HIPAA, GDPR)
- Intrusion detection systems
- Automated backup solutions

**Benefits of Our Cloud Solutions:**
- 99.9% uptime guarantee
- 40% reduction in infrastructure costs
- Improved scalability and flexibility
- Enhanced security and compliance
- 24/7 monitoring and support
- Disaster recovery capabilities

**Migration Process:**
1. **Assessment**: Current infrastructure analysis
2. **Planning**: Migration strategy and timeline
3. **Setup**: Cloud environment configuration
4. **Migration**: Gradual data and application transfer
5. **Testing**: Performance and functionality validation
6. **Go-Live**: Final cutover and monitoring
7. **Optimization**: Ongoing performance tuning''',
                'price_range': '$5,000 - $40,000',
                'delivery_time': '4-12 weeks',
                'order_priority': 75
            },
            {
                'title': 'API Development & Integration',
                'description': 'Custom API development and third-party integrations to connect your systems.',
                'detailed_content': '''Connect your applications and systems seamlessly with our API development and integration services. We create robust, scalable APIs and integrate third-party services to enhance your business capabilities.

**API Development Services:**
- RESTful API development
- GraphQL API implementation
- Microservices architecture
- API documentation and testing
- Authentication and authorization
- Rate limiting and throttling
- API versioning strategies

**Integration Services:**
- Payment gateway integration (Stripe, PayPal, Square)
- CRM integration (Salesforce, HubSpot, Pipedrive)
- E-commerce platform integration
- Social media API integration
- Email service integration
- Analytics and tracking integration
- Inventory management system integration

**API Technologies:**
- Django REST Framework
- Node.js with Express
- FastAPI (Python)
- Spring Boot (Java)
- ASP.NET Core (C#)
- Ruby on Rails API

**API Features:**
- Comprehensive error handling
- Request/response validation
- Automatic API documentation
- Performance monitoring
- Security best practices
- Caching mechanisms
- Webhook support

**Integration Capabilities:**
- Real-time data synchronization
- Batch data processing
- Event-driven architecture
- Message queue implementation
- Database integration
- File storage integration
- Notification systems

**Quality Assurance:**
- Automated testing suites
- Performance testing
- Security vulnerability testing
- Load testing and optimization
- API monitoring and alerting
- Documentation maintenance

**Business Benefits:**
- Improved operational efficiency
- Real-time data access
- Reduced manual processes
- Enhanced customer experience
- Scalable system architecture
- Future-proof integrations''',
                'price_range': '$3,000 - $30,000',
                'delivery_time': '3-10 weeks',
                'order_priority': 70
            },
            {
                'title': 'Database Design & Optimization',
                'description': 'Professional database design, optimization, and management services.',
                'detailed_content': '''Optimize your data management with our comprehensive database services. We design efficient database schemas, optimize performance, and ensure data integrity and security.

**Database Services:**
- Database design and modeling
- Performance optimization
- Query optimization
- Index strategy implementation
- Database migration services
- Backup and recovery planning
- Security implementation

**Database Technologies:**
- PostgreSQL
- MySQL
- MongoDB
- Redis
- Elasticsearch
- SQLite
- Microsoft SQL Server

**Design & Modeling:**
- Entity relationship diagrams
- Normalization and denormalization
- Data warehouse design
- Schema optimization
- Constraint implementation
- Trigger and procedure development

**Performance Optimization:**
- Query performance analysis
- Index optimization
- Database tuning
- Connection pooling
- Caching strategies
- Partitioning implementation
- Replication setup

**Data Migration:**
- Legacy system migration
- Platform migration
- Data cleaning and validation
- ETL process development
- Minimal downtime strategies
- Data integrity verification

**Security Features:**
- Access control implementation
- Data encryption
- Audit logging
- Compliance management
- Backup encryption
- User privilege management

**Monitoring & Maintenance:**
- Performance monitoring
- Automated backup solutions
- Health check implementation
- Capacity planning
- Disaster recovery testing
- Regular maintenance schedules

**Results & Benefits:**
- 60% improvement in query performance
- 99.9% data availability
- Enhanced data security
- Reduced storage costs
- Improved application responsiveness
- Scalable data architecture''',
                'price_range': '$2,500 - $20,000',
                'delivery_time': '2-8 weeks',
                'order_priority': 65
            },
            {
                'title': 'SEO Audit & Optimization',
                'description': 'Comprehensive SEO audits and optimization to improve search engine rankings.',
                'detailed_content': '''Boost your search engine visibility with our comprehensive SEO audit and optimization services. We identify issues, implement improvements, and help you achieve higher rankings.

**SEO Audit Services:**
- Technical SEO analysis
- On-page SEO evaluation
- Content audit and analysis
- Backlink profile assessment
- Competitor analysis
- Local SEO audit
- Mobile optimization review

**Technical SEO:**
- Site speed optimization
- Core Web Vitals improvement
- URL structure optimization
- XML sitemap creation
- Robots.txt optimization
- Schema markup implementation
- Canonical tag implementation

**On-Page Optimization:**
- Keyword research and mapping
- Title tag optimization
- Meta description improvement
- Header tag structure
- Internal linking strategy
- Image optimization
- Content optimization

**Content Strategy:**
- Content gap analysis
- Keyword-focused content creation
- Content optimization
- Blog strategy development
- FAQ page optimization
- Landing page optimization

**Local SEO:**
- Google My Business optimization
- Local citation building
- Review management
- Local keyword optimization
- NAP consistency check
- Local schema markup

**Link Building:**
- Link audit and cleanup
- White-hat link building strategies
- Guest posting opportunities
- Resource page outreach
- Broken link building
- Internal link optimization

**Reporting & Analytics:**
- Monthly SEO reports
- Keyword ranking tracking
- Traffic analysis
- Conversion tracking
- ROI measurement
- Competitor monitoring

**Expected Results:**
- 150% increase in organic traffic
- 200% improvement in keyword rankings
- 50% increase in conversion rates
- Better user experience metrics
- Enhanced local visibility
- Long-term sustainable growth''',
                'price_range': '$1,500 - $10,000',
                'delivery_time': '2-6 weeks',
                'order_priority': 60
            },
            {
                'title': 'WordPress Development',
                'description': 'Custom WordPress development, themes, and plugin development services.',
                'detailed_content': '''Create powerful WordPress websites with our expert development services. We build custom themes, develop plugins, and optimize WordPress sites for performance and security.

**WordPress Services:**
- Custom theme development
- Plugin development
- WordPress customization
- WooCommerce development
- Site migration and maintenance
- Performance optimization
- Security hardening

**Custom Theme Development:**
- Responsive design implementation
- Custom post types and fields
- Advanced Custom Fields integration
- Gutenberg block development
- Theme customization
- Cross-browser compatibility
- SEO-friendly structure

**Plugin Development:**
- Custom functionality development
- Third-party API integration
- Payment gateway plugins
- Membership and subscription plugins
- SEO and marketing plugins
- E-commerce extensions

**WooCommerce Development:**
- Custom e-commerce solutions
- Payment gateway integration
- Shipping method customization
- Product configurators
- Inventory management
- Multi-vendor marketplace setup

**Performance Optimization:**
- Page speed optimization
- Database optimization
- Caching implementation
- Image optimization
- CDN integration
- Code minification

**Security Services:**
- Security audits
- Malware removal
- SSL certificate installation
- Firewall configuration
- Regular security updates
- Backup solutions

**Maintenance Services:**
- Regular updates
- Security monitoring
- Performance monitoring
- Content updates
- Bug fixes
- Feature enhancements

**WordPress Expertise:**
- 8+ years WordPress experience
- Certified WordPress developers
- Latest WordPress standards
- Best practice implementation
- Custom development approach
- Ongoing support and maintenance

**Deliverables:**
- Fully functional WordPress site
- Custom theme files
- Plugin documentation
- Training materials
- Maintenance guidelines
- Performance reports''',
                'price_range': '$2,000 - $15,000',
                'delivery_time': '3-8 weeks',
                'order_priority': 55
            },
            {
                'title': 'Cybersecurity Consulting',
                'description': 'Comprehensive cybersecurity assessments and implementation services.',
                'detailed_content': '''Protect your business with our comprehensive cybersecurity consulting services. We assess vulnerabilities, implement security measures, and help you maintain a strong security posture.

**Security Services:**
- Security assessments and audits
- Penetration testing
- Vulnerability management
- Security policy development
- Incident response planning
- Compliance consulting
- Employee security training

**Security Assessments:**
- Network security analysis
- Application security testing
- Infrastructure vulnerability scanning
- Social engineering testing
- Physical security assessment
- Data protection audit

**Implementation Services:**
- Firewall configuration
- Intrusion detection systems
- Multi-factor authentication
- Endpoint protection
- Data encryption
- Backup and recovery systems

**Compliance Frameworks:**
- GDPR compliance
- HIPAA compliance
- SOC 2 certification
- ISO 27001 implementation
- PCI DSS compliance
- NIST framework adoption

**Incident Response:**
- Incident response planning
- Breach detection and analysis
- Forensic investigation
- Recovery procedures
- Post-incident analysis
- Process improvement

**Employee Training:**
- Security awareness training
- Phishing simulation
- Best practices workshops
- Policy training
- Role-specific training
- Regular updates and refreshers

**Ongoing Services:**
- Continuous monitoring
- Threat intelligence
- Regular security updates
- Quarterly assessments
- Policy reviews
- Emergency response support

**Security Technologies:**
- Next-generation firewalls
- SIEM solutions
- Endpoint detection and response
- Email security solutions
- Web application firewalls
- Identity management systems

**Benefits:**
- Reduced security risks
- Regulatory compliance
- Business continuity protection
- Customer trust enhancement
- Cost-effective security measures
- 24/7 security monitoring''',
                'price_range': '$3,000 - $25,000',
                'delivery_time': '2-8 weeks',
                'order_priority': 50
            },
            {
                'title': 'Business Process Automation',
                'description': 'Automate repetitive tasks and streamline business processes for efficiency.',
                'detailed_content': '''Increase productivity and reduce costs with our business process automation services. We identify automation opportunities and implement solutions that streamline your operations.

**Automation Services:**
- Process analysis and mapping
- Workflow automation
- Document management automation
- Customer service automation
- Marketing automation
- Financial process automation
- HR process automation

**Automation Technologies:**
- Robotic Process Automation (RPA)
- Workflow management systems
- API integrations
- Custom automation tools
- AI and machine learning
- Business intelligence tools

**Process Areas:**
- Data entry automation
- Invoice processing
- Customer onboarding
- Report generation
- Email marketing campaigns
- Lead qualification
- Inventory management

**Implementation Process:**
1. **Assessment**: Current process analysis
2. **Opportunity Identification**: Automation potential evaluation
3. **Solution Design**: Custom automation strategy
4. **Development**: Tool configuration and custom development
5. **Testing**: Process validation and optimization
6. **Deployment**: Live implementation with monitoring
7. **Training**: User training and documentation

**Automation Tools:**
- Zapier and Microsoft Power Automate
- UiPath and Automation Anywhere
- Custom Python and JavaScript solutions
- Salesforce Process Builder
- HubSpot Workflows
- Slack and Microsoft Teams integrations

**Business Benefits:**
- 70% reduction in manual tasks
- 90% improvement in process accuracy
- 50% reduction in processing time
- Cost savings through efficiency
- Improved employee satisfaction
- Better customer experience

**ROI & Metrics:**
- Average 300% ROI within first year
- Measurable productivity improvements
- Error reduction tracking
- Time savings quantification
- Cost reduction analysis
- Process efficiency metrics

**Ongoing Support:**
- Process monitoring and optimization
- Regular automation updates
- Performance reporting
- User support and training
- Scaling automation solutions
- Integration with new systems''',
                'price_range': '$4,000 - $35,000',
                'delivery_time': '4-12 weeks',
                'order_priority': 45
            },
            {
                'title': 'Data Analytics & Reporting',
                'description': 'Transform your data into actionable insights with advanced analytics solutions.',
                'detailed_content': '''Unlock the power of your data with our comprehensive analytics and reporting services. We help businesses make data-driven decisions through advanced analytics and visualization.

**Analytics Services:**
- Data collection and integration
- Business intelligence dashboards
- Custom reporting solutions
- Predictive analytics
- Data visualization
- Performance monitoring
- KPI tracking and optimization

**Data Integration:**
- Multiple data source connection
- Real-time data synchronization
- Data cleaning and transformation
- ETL pipeline development
- Data warehouse setup
- Cloud data migration

**Dashboard Development:**
- Interactive business dashboards
- Real-time reporting systems
- Mobile-responsive analytics
- Custom KPI visualization
- Automated report generation
- Alert and notification systems

**Analytics Technologies:**
- Google Analytics and Google Data Studio
- Power BI and Tableau
- Python and R for data science
- SQL databases and data warehouses
- Machine learning platforms
- Custom analytics applications

**Reporting Solutions:**
- Executive summary reports
- Departmental performance reports
- Customer behavior analysis
- Sales and marketing analytics
- Financial reporting automation
- Operational efficiency reports

**Data Visualization:**
- Interactive charts and graphs
- Geographic data mapping
- Trend analysis visualizations
- Comparative performance charts
- Real-time monitoring displays
- Mobile-optimized dashboards

**Advanced Analytics:**
- Predictive modeling
- Customer segmentation
- Churn analysis
- Forecasting and planning
- A/B testing analysis
- Statistical analysis

**Industry Applications:**
- E-commerce analytics
- Marketing campaign analysis
- Financial performance tracking
- Operations optimization
- Customer journey analysis
- Supply chain analytics

**Deliverables:**
- Custom analytics dashboards
- Automated reporting systems
- Data integration pipelines
- Training and documentation
- Ongoing support and maintenance
- Regular insights and recommendations

**Business Impact:**
- 40% improvement in decision-making speed
- 25% increase in operational efficiency
- Better understanding of customer behavior
- Reduced costs through optimization
- Increased revenue through insights
- Competitive advantage through data''',
                'price_range': '$3,500 - $30,000',
                'delivery_time': '4-10 weeks',
                'order_priority': 40
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
