"""
Django management command to populate the database with realistic solutions data.

Usage:
    python manage.py populate_solutions
    python manage.py populate_solutions --clear  # Clear existing data first
    python manage.py populate_solutions --solutions 20  # Create 20 solutions instead of default 15
"""

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from apps.solutions.models import Solution, CodeSnippet
from apps.portfolio.models import Technology
from apps.blog.models import Tag


class Command(BaseCommand):
    help = 'Populate the database with realistic solutions data for development and testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--solutions',
            type=int,
            default=15,
            help='Number of solutions to create (default: 15)'
        )
        parser.add_argument(
            '--code-snippets',
            type=int,
            default=10,
            help='Number of code snippets to create (default: 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing solutions data before populating'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting solutions data population...\n')
        )
        
        try:
            with transaction.atomic():
                if options['clear']:
                    self.clear_existing_data()
                
                # Ensure we have technologies and tags
                technologies = self.get_or_create_technologies()
                tags = self.get_or_create_tags()
                
                # Create solutions
                solutions = self.create_solutions(
                    count=options['solutions'],
                    technologies=technologies
                )
                
                # Create code snippets
                self.create_code_snippets(
                    count=options['code_snippets'],
                    tags=tags
                )
                
                # Create relationships between solutions
                self.create_solution_relationships(solutions)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Successfully created:\n'
                        f'   • {len(solutions)} solutions\n'
                        f'   • {options["code_snippets"]} code snippets\n'
                        f'   • Solution relationships\n'
                    )
                )
                
        except Exception as e:
            raise CommandError(f'❌ Error during solutions population: {str(e)}')
    
    def clear_existing_data(self):
        """Clear existing solutions data"""
        self.stdout.write('🧹 Clearing existing solutions data...')
        Solution.objects.all().delete()
        CodeSnippet.objects.all().delete()
        self.stdout.write(self.style.WARNING('   Existing solutions data cleared.\n'))
    
    def get_or_create_technologies(self):
        """Get existing technologies or create basic ones if none exist"""
        technologies = list(Technology.objects.all())
        
        if not technologies:
            self.stdout.write('📱 Creating basic technologies...')
            tech_data = [
                {'name': 'JavaScript', 'slug': 'javascript', 'category': 'frontend'},
                {'name': 'Python', 'slug': 'python', 'category': 'backend'},
                {'name': 'React', 'slug': 'react', 'category': 'frontend'},
                {'name': 'Django', 'slug': 'django', 'category': 'backend'},
                {'name': 'Node.js', 'slug': 'nodejs', 'category': 'backend'},
                {'name': 'Vue.js', 'slug': 'vuejs', 'category': 'frontend'},
                {'name': 'PHP', 'slug': 'php', 'category': 'backend'},
                {'name': 'MySQL', 'slug': 'mysql', 'category': 'database'},
                {'name': 'PostgreSQL', 'slug': 'postgresql', 'category': 'database'},
                {'name': 'Docker', 'slug': 'docker', 'category': 'devops'},
            ]
            
            for tech in tech_data:
                technology, created = Technology.objects.get_or_create(
                    slug=tech['slug'],
                    defaults=tech
                )
                technologies.append(technology)
                if created:
                    self.stdout.write(f'   Created technology: {technology.name}')
        
        return technologies
    
    def get_or_create_tags(self):
        """Get existing tags or create basic ones if none exist"""
        tags = list(Tag.objects.all())
        
        if not tags:
            self.stdout.write('🏷️  Creating basic tags...')
            tag_names = [
                'debugging', 'performance', 'security', 'optimization', 'api',
                'database', 'frontend', 'backend', 'responsive', 'mobile',
                'testing', 'deployment', 'authentication', 'validation', 'forms'
            ]
            
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    slug=slugify(tag_name),
                    defaults={'name': tag_name}
                )
                tags.append(tag)
                if created:
                    self.stdout.write(f'   Created tag: {tag.name}')
        
        return tags
    
    def create_solutions(self, count, technologies):
        """Create realistic solution entries"""
        self.stdout.write(f'💡 Creating {count} solutions...')
        
        solutions_data = [
            {
                'title': 'Fix "Cannot read property of undefined" JavaScript Error',
                'difficulty': 'beginner',
                'tech_name': 'JavaScript',
                'problem': 'Getting "Cannot read property \'x\' of undefined" error when trying to access object properties in JavaScript.',
                'root_cause': 'This error occurs when you try to access a property of a variable that is undefined or null. Common scenarios include accessing nested object properties without proper checks, or trying to use variables before they are properly initialized.',
                'solution': '''The best way to handle this is to use optional chaining or proper null checks:

**Method 1: Optional Chaining (ES2020)**
```javascript
// Instead of this (which can cause errors):
const userName = user.profile.name;

// Use optional chaining:
const userName = user?.profile?.name;
```

**Method 2: Traditional Null Checks**
```javascript
// Check if object exists before accessing properties
if (user && user.profile && user.profile.name) {
    const userName = user.profile.name;
}
```

**Method 3: Default Values**
```javascript
// Provide default values
const userName = (user && user.profile && user.profile.name) || 'Anonymous';
// Or with optional chaining:
const userName = user?.profile?.name || 'Anonymous';
```

**Method 4: Using try-catch for complex scenarios**
```javascript
try {
    const userName = user.profile.name;
    // Process userName
} catch (error) {
    console.error('Error accessing user name:', error);
    // Handle the error appropriately
}
```'''
            },
            {
                'title': 'Resolve Django CORS Issues in Development',
                'difficulty': 'intermediate',
                'tech_name': 'Django',
                'problem': 'Frontend application cannot make API requests to Django backend due to CORS (Cross-Origin Resource Sharing) errors in development environment.',
                'root_cause': 'CORS errors occur when a web application running on one domain tries to access resources from another domain. In development, this commonly happens when your frontend (e.g., React on localhost:3000) tries to access your Django API (e.g., localhost:8000).',
                'solution': '''To fix CORS issues in Django, install and configure django-cors-headers:

**Step 1: Install django-cors-headers**
```bash
pip install django-cors-headers
```

**Step 2: Add to INSTALLED_APPS in settings.py**
```python
INSTALLED_APPS = [
    # ... other apps
    'corsheaders',
    # ... rest of your apps
]
```

**Step 3: Add middleware (must be at the top)**
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]
```

**Step 4: Configure CORS settings**
```python
# For development only - allow all origins
CORS_ALLOW_ALL_ORIGINS = True

# For production - specify allowed origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://yourdomain.com",
]

# Allow credentials if needed
CORS_ALLOW_CREDENTIALS = True

# Specify allowed headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```'''
            },
            {
                'title': 'Fix React Component Not Re-rendering on State Change',
                'difficulty': 'intermediate',
                'tech_name': 'React',
                'problem': 'React component is not re-rendering when state changes, causing the UI to not update even though the state value has changed.',
                'root_cause': 'This usually happens when you mutate state directly instead of creating new objects/arrays, or when state updates are not properly handled in functional components.',
                'solution': '''Here are the most common causes and solutions:

**Problem 1: Direct State Mutation**
```javascript
// ❌ Wrong - mutating state directly
const [items, setItems] = useState([]);
const addItem = (newItem) => {
    items.push(newItem); // Direct mutation
    setItems(items); // React won't detect the change
};

// ✅ Correct - create new array
const addItem = (newItem) => {
    setItems([...items, newItem]); // New array reference
};
```

**Problem 2: Mutating Object State**
```javascript
// ❌ Wrong
const [user, setUser] = useState({ name: '', email: '' });
const updateName = (newName) => {
    user.name = newName; // Direct mutation
    setUser(user); // React won't detect the change
};

// ✅ Correct
const updateName = (newName) => {
    setUser({ ...user, name: newName }); // New object reference
};
```

**Problem 3: useEffect Dependencies**
```javascript
// ❌ Wrong - missing dependencies
useEffect(() => {
    fetchData(userId);
}, []); // Missing userId dependency

// ✅ Correct
useEffect(() => {
    fetchData(userId);
}, [userId]); // Include all dependencies
```

**Problem 4: State Updates in Loops**
```javascript
// ❌ Wrong - state updates not batched properly
items.forEach(item => {
    setCount(count + item.value); // Using stale state
});

// ✅ Correct - use functional updates
items.forEach(item => {
    setCount(prevCount => prevCount + item.value);
});
```'''
            },
            {
                'title': 'Optimize Slow Database Queries in Production',
                'difficulty': 'advanced',
                'tech_name': 'PostgreSQL',
                'problem': 'Database queries are running slowly in production, causing timeouts and poor user experience. The application was fast in development but degrades with real data volume.',
                'root_cause': 'Slow queries in production typically result from missing indexes, inefficient query patterns, lack of query optimization, or N+1 query problems that aren\'t apparent with small development datasets.',
                'solution': '''Here\'s a systematic approach to optimize database performance:

**Step 1: Identify Slow Queries**
```sql
-- Enable query logging in PostgreSQL
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries > 1 second
SELECT pg_reload_conf();

-- Or use pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slowest queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    stddev_time
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

**Step 2: Analyze Query Plans**
```sql
-- Use EXPLAIN ANALYZE for detailed execution plan
EXPLAIN ANALYZE 
SELECT * FROM users u 
JOIN orders o ON u.id = o.user_id 
WHERE u.created_at > '2024-01-01';
```

**Step 3: Add Strategic Indexes**
```sql
-- Index on foreign keys
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Composite indexes for common queries
CREATE INDEX idx_users_created_status ON users(created_at, status);

-- Partial indexes for filtered queries
CREATE INDEX idx_active_users ON users(id) WHERE status = 'active';
```

**Step 4: Optimize Django ORM Queries**
```python
# ❌ N+1 Query Problem
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # Hits database for each user

# ✅ Use select_related for foreign keys
users = User.objects.select_related('profile').all()

# ✅ Use prefetch_related for many-to-many
users = User.objects.prefetch_related('orders').all()

# ✅ Only fetch needed fields
users = User.objects.only('id', 'name', 'email').all()
```

**Step 5: Query Optimization Techniques**
```sql
-- Use LIMIT for pagination
SELECT * FROM users ORDER BY created_at DESC LIMIT 20 OFFSET 0;

-- Use EXISTS instead of IN for large datasets
SELECT * FROM users u 
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- Avoid SELECT * - specify only needed columns
SELECT id, name, email FROM users WHERE active = true;
```'''
            },
            {
                'title': 'Handle File Upload Size Limits in Web Applications',
                'difficulty': 'intermediate',
                'tech_name': 'PHP',
                'problem': 'Users cannot upload large files through web forms, getting errors like "File too large" or uploads failing silently.',
                'root_cause': 'File upload limits are controlled by multiple layers: web server configuration, PHP settings, and application-level restrictions. Each layer can impose its own limits.',
                'solution': '''Configure file upload limits at multiple levels:

**Step 1: PHP Configuration (php.ini)**
```ini
; Maximum allowed size for uploaded files
upload_max_filesize = 50M

; Maximum size of POST data
post_max_size = 50M

; Maximum execution time for scripts
max_execution_time = 300

; Maximum input time
max_input_time = 300

; Memory limit
memory_limit = 256M
```

**Step 2: Web Server Configuration**

**For Apache (.htaccess)**
```apache
# Increase upload limits
php_value upload_max_filesize 50M
php_value post_max_size 50M
php_value max_execution_time 300
php_value max_input_time 300
```

**For Nginx**
```nginx
server {
    # Maximum allowed size of client request body
    client_max_body_size 50M;
    
    # Timeout for reading client request body
    client_body_timeout 300s;
}
```

**Step 3: Application-Level Handling**
```php
<?php
// Check upload errors
if ($_FILES['upload']['error'] !== UPLOAD_ERR_OK) {
    switch ($_FILES['upload']['error']) {
        case UPLOAD_ERR_INI_SIZE:
            $error = 'File exceeds upload_max_filesize directive';
            break;
        case UPLOAD_ERR_FORM_SIZE:
            $error = 'File exceeds MAX_FILE_SIZE directive';
            break;
        case UPLOAD_ERR_PARTIAL:
            $error = 'File was only partially uploaded';
            break;
        case UPLOAD_ERR_NO_FILE:
            $error = 'No file was uploaded';
            break;
        default:
            $error = 'Unknown upload error';
            break;
    }
    throw new Exception($error);
}

// Validate file size
$maxSize = 50 * 1024 * 1024; // 50MB in bytes
if ($_FILES['upload']['size'] > $maxSize) {
    throw new Exception('File size exceeds limit');
}

// Validate file type
$allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
if (!in_array($_FILES['upload']['type'], $allowedTypes)) {
    throw new Exception('File type not allowed');
}
?>
```

**Step 4: Frontend Progress Indication**
```javascript
// Show upload progress
function uploadFile(file) {
    const formData = new FormData();
    formData.append('upload', file);
    
    fetch('/upload.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Upload successful:', data);
    })
    .catch(error => {
        console.error('Upload failed:', error);
    });
}
```'''
            },
            {
                'title': 'Fix Memory Leaks in Node.js Applications',
                'difficulty': 'advanced',
                'tech_name': 'Node.js',
                'problem': 'Node.js application memory usage keeps growing over time, eventually causing the application to crash or become unresponsive.',
                'root_cause': 'Memory leaks in Node.js typically occur due to unclosed event listeners, retaining references to large objects, circular references, or improper cleanup of timers and streams.',
                'solution': '''Identify and fix common Node.js memory leak patterns:

**Step 1: Monitor Memory Usage**
```javascript
// Add memory monitoring
function logMemoryUsage() {
    const used = process.memoryUsage();
    console.log('Memory Usage:');
    for (let key in used) {
        console.log(`${key}: ${Math.round(used[key] / 1024 / 1024 * 100) / 100} MB`);
    }
}

// Log every 30 seconds
setInterval(logMemoryUsage, 30000);
```

**Step 2: Fix Event Listener Leaks**
```javascript
// ❌ Problem - event listeners not removed
function createUser(userId) {
    const user = new EventEmitter();
    
    // This listener is never removed
    user.on('update', handleUpdate);
    
    return user;
}

// ✅ Solution - properly remove listeners
function createUser(userId) {
    const user = new EventEmitter();
    
    function handleUpdate(data) {
        // Handle update
    }
    
    user.on('update', handleUpdate);
    
    // Cleanup function
    user.cleanup = () => {
        user.removeListener('update', handleUpdate);
        user.removeAllListeners();
    };
    
    return user;
}
```

**Step 3: Fix Timer and Interval Leaks**
```javascript
// ❌ Problem - timers not cleared
function startPolling() {
    setInterval(() => {
        fetchData();
    }, 5000);
}

// ✅ Solution - clear timers properly
function startPolling() {
    const intervalId = setInterval(() => {
        fetchData();
    }, 5000);
    
    // Return cleanup function
    return () => clearInterval(intervalId);
}

// Usage
const stopPolling = startPolling();
// Later, when no longer needed:
stopPolling();
```

**Step 4: Handle Stream Cleanup**
```javascript
// ❌ Problem - streams not properly closed
function processFile(filename) {
    const readStream = fs.createReadStream(filename);
    const writeStream = fs.createWriteStream('output.txt');
    
    readStream.pipe(writeStream);
    // Streams might not be properly closed
}

// ✅ Solution - ensure proper cleanup
function processFile(filename) {
    return new Promise((resolve, reject) => {
        const readStream = fs.createReadStream(filename);
        const writeStream = fs.createWriteStream('output.txt');
        
        readStream.on('error', (err) => {
            cleanup();
            reject(err);
        });
        
        writeStream.on('error', (err) => {
            cleanup();
            reject(err);
        });
        
        writeStream.on('finish', () => {
            cleanup();
            resolve();
        });
        
        function cleanup() {
            readStream.destroy();
            writeStream.destroy();
        }
        
        readStream.pipe(writeStream);
    });
}
```

**Step 5: Use Memory Profiling Tools**
```bash
# Install clinic.js for memory profiling
npm install -g clinic

# Profile your application
clinic doctor -- node app.js

# Or use built-in Node.js inspector
node --inspect app.js
# Then open Chrome DevTools for memory profiling
```'''
            },
            {
                'title': 'Implement Responsive Images for Better Performance',
                'difficulty': 'intermediate',
                'tech_name': 'HTML',
                'problem': 'Website loads slowly on mobile devices because large desktop images are being served to all devices, wasting bandwidth and degrading user experience.',
                'root_cause': 'Serving the same large images to all devices regardless of screen size, resolution, or bandwidth capabilities leads to unnecessary data usage and slower loading times.',
                'solution': '''Implement responsive images using modern HTML techniques:

**Step 1: Use srcset for Different Resolutions**
```html
<!-- Basic responsive image -->
<img 
    src="image-800w.jpg" 
    srcset="image-400w.jpg 400w,
            image-800w.jpg 800w,
            image-1200w.jpg 1200w"
    sizes="(max-width: 600px) 400px,
           (max-width: 900px) 800px,
           1200px"
    alt="Responsive image example"
    loading="lazy"
/>
```

**Step 2: Use Picture Element for Art Direction**
```html
<!-- Different crops for different screen sizes -->
<picture>
    <!-- Mobile: square crop -->
    <source 
        media="(max-width: 600px)" 
        srcset="hero-mobile-400w.jpg 400w,
                hero-mobile-800w.jpg 800w"
        sizes="100vw"
    />
    
    <!-- Tablet: 16:9 crop -->
    <source 
        media="(max-width: 1200px)" 
        srcset="hero-tablet-800w.jpg 800w,
                hero-tablet-1600w.jpg 1600w"
        sizes="100vw"
    />
    
    <!-- Desktop: wide crop -->
    <source 
        srcset="hero-desktop-1200w.jpg 1200w,
                hero-desktop-2400w.jpg 2400w"
        sizes="100vw"
    />
    
    <!-- Fallback -->
    <img 
        src="hero-desktop-1200w.jpg" 
        alt="Hero image"
        loading="lazy"
    />
</picture>
```

**Step 3: Modern Format Support**
```html
<!-- Progressive enhancement with modern formats -->
<picture>
    <!-- AVIF for supported browsers -->
    <source 
        type="image/avif"
        srcset="image-400w.avif 400w,
                image-800w.avif 800w,
                image-1200w.avif 1200w"
        sizes="(max-width: 600px) 400px,
               (max-width: 900px) 800px,
               1200px"
    />
    
    <!-- WebP for supported browsers -->
    <source 
        type="image/webp"
        srcset="image-400w.webp 400w,
                image-800w.webp 800w,
                image-1200w.webp 1200w"
        sizes="(max-width: 600px) 400px,
               (max-width: 900px) 800px,
               1200px"
    />
    
    <!-- JPEG fallback -->
    <img 
        src="image-800w.jpg"
        srcset="image-400w.jpg 400w,
                image-800w.jpg 800w,
                image-1200w.jpg 1200w"
        sizes="(max-width: 600px) 400px,
               (max-width: 900px) 800px,
               1200px"
        alt="Optimized responsive image"
        loading="lazy"
    />
</picture>
```

**Step 4: CSS for Responsive Images**
```css
/* Ensure images don't overflow containers */
img {
    max-width: 100%;
    height: auto;
}

/* Object-fit for maintaining aspect ratios */
.hero-image {
    width: 100%;
    height: 400px;
    object-fit: cover;
    object-position: center;
}

/* Responsive containers */
.image-container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
}

@media (max-width: 768px) {
    .hero-image {
        height: 250px;
    }
}
```'''
            },
            {
                'title': 'Debug and Fix CSS Grid Layout Issues',
                'difficulty': 'intermediate',
                'tech_name': 'CSS',
                'problem': 'CSS Grid layout is not working as expected - items are not positioning correctly, grid areas are overlapping, or the layout breaks on different screen sizes.',
                'root_cause': 'Common CSS Grid issues include incorrect grid template definitions, misnamed grid areas, improper use of grid-auto-flow, or lack of responsive considerations.',
                'solution': '''Systematically debug and fix CSS Grid issues:

**Step 1: Basic Grid Setup Debugging**
```css
/* ❌ Common mistakes */
.grid-container {
    display: grid;
    /* Missing grid-template-columns */
    grid-template-rows: repeat(3, 1fr);
    gap: 20px;
}

/* ✅ Correct setup */
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    grid-template-rows: auto;
    gap: 20px;
    padding: 20px;
}
```

**Step 2: Grid Area Debugging**
```css
/* ❌ Problematic grid areas */
.layout {
    display: grid;
    grid-template-areas: 
        "header header header"
        "sidebar main main"
        "footer footer footer";
    /* Missing grid-template-columns definition */
}

/* ✅ Properly defined grid areas */
.layout {
    display: grid;
    grid-template-columns: 250px 1fr 1fr;
    grid-template-rows: auto 1fr auto;
    grid-template-areas: 
        "header header header"
        "sidebar main main"
        "footer footer footer";
    min-height: 100vh;
    gap: 20px;
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; }
.footer { grid-area: footer; }
```

**Step 3: Responsive Grid Solutions**
```css
/* Mobile-first responsive grid */
.grid-container {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1rem;
}

/* Tablet */
@media (min-width: 768px) {
    .grid-container {
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        padding: 1.5rem;
    }
}

/* Desktop */
@media (min-width: 1024px) {
    .grid-container {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
}

/* Responsive grid areas */
@media (max-width: 767px) {
    .layout {
        grid-template-areas: 
            "header"
            "main"
            "sidebar"
            "footer";
        grid-template-columns: 1fr;
    }
}
```

**Step 4: Advanced Grid Debugging**
```css
/* Debug mode - visualize grid lines */
.grid-debug {
    background-image: 
        linear-gradient(rgba(255,0,0,0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,0,0,0.1) 1px, transparent 1px);
    background-size: 20px 20px;
}

/* Grid item debugging */
.grid-item {
    border: 2px solid red; /* Temporary for debugging */
    background: rgba(0,255,0,0.1); /* See item boundaries */
}

/* Use Firefox Grid Inspector or Chrome DevTools */
/* Add these temporarily for debugging */
.grid-container * {
    outline: 1px solid rgba(255,0,0,0.3);
}
```

**Step 5: Common Grid Fixes**
```css
/* Fix overlapping items */
.grid-item {
    /* Ensure items don't grow beyond their area */
    max-width: 100%;
    overflow: hidden;
    
    /* If using explicit positioning */
    grid-column: span 1; /* Don't span multiple columns unintentionally */
    grid-row: span 1;
}

/* Fix content overflow */
.grid-item-content {
    word-wrap: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
}

/* Handle images in grid */
.grid-item img {
    width: 100%;
    height: auto;
    object-fit: cover;
}

/* Prevent grid blowout */
.grid-container {
    overflow: hidden; /* Prevent horizontal scroll */
}
```'''
            },
            {
                'title': 'Resolve Docker Container Networking Issues',
                'difficulty': 'advanced',
                'tech_name': 'Docker',
                'problem': 'Docker containers cannot communicate with each other or external services, resulting in connection timeouts and application failures.',
                'root_cause': 'Container networking issues typically stem from incorrect network configuration, port mapping problems, firewall restrictions, or DNS resolution failures within the Docker environment.',
                'solution': '''Diagnose and fix Docker networking step by step:

**Step 1: Understand Docker Networks**
```bash
# List all Docker networks
docker network ls

# Inspect default bridge network
docker network inspect bridge

# Create custom bridge network
docker network create --driver bridge mynetwork

# Connect container to custom network
docker network connect mynetwork mycontainer
```

**Step 2: Fix Container-to-Container Communication**
```yaml
# docker-compose.yml - Proper network setup
version: '3.8'
services:
  web:
    build: .
    ports:
      - "3000:3000"
    networks:
      - app-network
    environment:
      - API_URL=http://api:8000  # Use service name as hostname
    depends_on:
      - api
      - database

  api:
    build: ./api
    ports:
      - "8000:8000"
    networks:
      - app-network
    environment:
      - DATABASE_URL=postgresql://user:pass@database:5432/mydb
    depends_on:
      - database

  database:
    image: postgres:13
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    networks:
      - app-network
    volumes:
      - postgres_data:/var/lib/postgresql/data

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

**Step 3: Debug Network Connectivity**
```bash
# Test container connectivity
docker exec -it container_name ping api
docker exec -it container_name nslookup api
docker exec -it container_name curl http://api:8000/health

# Check if ports are listening
docker exec -it container_name netstat -tlnp
docker exec -it container_name ss -tlnp

# Test external connectivity
docker exec -it container_name ping google.com
docker exec -it container_name curl https://api.github.com
```

**Step 4: Fix Port Mapping Issues**
```bash
# ❌ Wrong - conflicting port mappings
docker run -p 3000:3000 app1
docker run -p 3000:3000 app2  # Will fail

# ✅ Correct - use different host ports
docker run -p 3000:3000 app1
docker run -p 3001:3000 app2

# Check what ports are in use
docker ps --format "table {{.Names}}\\t{{.Ports}}"
netstat -tlnp | grep :3000
```

**Step 5: Application Configuration for Docker**
```javascript
// Node.js app configuration
const express = require('express');
const app = express();

// ❌ Wrong - hardcoded localhost
const API_URL = 'http://localhost:8000';

// ✅ Correct - use environment variables and service names
const API_URL = process.env.API_URL || 'http://api:8000';

// Bind to all interfaces, not just localhost
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
});
```

**Step 6: Dockerfile Best Practices**
```dockerfile
FROM node:16-alpine

# Create app directory
WORKDIR /usr/src/app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Copy app source
COPY --chown=nextjs:nodejs . .

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:3000/health || exit 1

# Start application
CMD ["npm", "start"]
```'''
            },
            {
                'title': 'Optimize MySQL Query Performance with Proper Indexing',
                'difficulty': 'advanced',
                'tech_name': 'MySQL',
                'problem': 'MySQL queries are executing slowly, causing application timeouts and poor user experience, especially on large datasets.',
                'root_cause': 'Poor query performance usually results from missing indexes, suboptimal query structure, full table scans, or inefficient use of MySQL features like joins and subqueries.',
                'solution': '''Systematically optimize MySQL query performance:

**Step 1: Identify Slow Queries**
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1; -- Log queries taking > 1 second
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- Or use Performance Schema
SELECT 
    DIGEST_TEXT,
    COUNT_STAR,
    AVG_TIMER_WAIT/1000000000 as avg_time_seconds,
    SUM_ROWS_EXAMINED/COUNT_STAR as avg_rows_examined
FROM performance_schema.events_statements_summary_by_digest 
ORDER BY AVG_TIMER_WAIT DESC 
LIMIT 10;
```

**Step 2: Analyze Query Execution Plans**
```sql
-- Use EXPLAIN to analyze query execution
EXPLAIN SELECT u.name, p.title 
FROM users u 
JOIN posts p ON u.id = p.user_id 
WHERE u.created_at > '2024-01-01' 
AND p.status = 'published'
ORDER BY p.created_at DESC;

-- Use EXPLAIN ANALYZE for detailed timing (MySQL 8.0+)
EXPLAIN ANALYZE SELECT u.name, p.title 
FROM users u 
JOIN posts p ON u.id = p.user_id 
WHERE u.created_at > '2024-01-01';
```

**Step 3: Create Strategic Indexes**
```sql
-- Index for foreign key joins
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- Composite index for WHERE clauses
CREATE INDEX idx_users_created_status ON users(created_at, status);

-- Index for ORDER BY clauses
CREATE INDEX idx_posts_created_desc ON posts(created_at DESC);

-- Covering index (includes all needed columns)
CREATE INDEX idx_posts_covering ON posts(user_id, status, created_at, title);

-- Partial index for common filtered queries
CREATE INDEX idx_published_posts ON posts(created_at) WHERE status = 'published';
```

**Step 4: Optimize Query Structure**
```sql
-- ❌ Avoid SELECT *
SELECT * FROM users WHERE email = 'user@example.com';

-- ✅ Select only needed columns
SELECT id, name, email FROM users WHERE email = 'user@example.com';

-- ❌ Avoid functions in WHERE clauses
SELECT * FROM posts WHERE YEAR(created_at) = 2024;

-- ✅ Use range conditions instead
SELECT * FROM posts 
WHERE created_at >= '2024-01-01' 
AND created_at < '2025-01-01';

-- ❌ Avoid OR conditions that prevent index usage
SELECT * FROM users WHERE name = 'John' OR email = 'john@example.com';

-- ✅ Use UNION for better index usage
SELECT * FROM users WHERE name = 'John'
UNION
SELECT * FROM users WHERE email = 'john@example.com';
```

**Step 5: Optimize JOINs**
```sql
-- ❌ Inefficient subquery
SELECT * FROM users 
WHERE id IN (
    SELECT user_id FROM posts WHERE status = 'published'
);

-- ✅ Use JOIN instead
SELECT DISTINCT u.* FROM users u
JOIN posts p ON u.id = p.user_id
WHERE p.status = 'published';

-- ✅ Use EXISTS for better performance in some cases
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM posts p 
    WHERE p.user_id = u.id AND p.status = 'published'
);
```

**Step 6: Monitor and Maintain Performance**
```sql
-- Check index usage
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    SEQ_IN_INDEX,
    COLUMN_NAME,
    CARDINALITY
FROM INFORMATION_SCHEMA.STATISTICS 
WHERE TABLE_SCHEMA = 'your_database'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- Find unused indexes
SELECT 
    s.TABLE_SCHEMA,
    s.TABLE_NAME,
    s.INDEX_NAME
FROM INFORMATION_SCHEMA.STATISTICS s
LEFT JOIN INFORMATION_SCHEMA.INDEX_STATISTICS i 
    ON s.TABLE_SCHEMA = i.TABLE_SCHEMA 
    AND s.TABLE_NAME = i.TABLE_NAME 
    AND s.INDEX_NAME = i.INDEX_NAME
WHERE i.INDEX_NAME IS NULL 
AND s.INDEX_NAME != 'PRIMARY';

-- Regular maintenance
ANALYZE TABLE users, posts;
OPTIMIZE TABLE users, posts;
```'''
            }
        ]
        
        solutions = []
        for i, data in enumerate(solutions_data):
            try:
                # Find the technology
                technology = next(
                    (tech for tech in technologies if tech.name == data['tech_name']),
                    random.choice(technologies)
                )
                
                # Create solution
                solution = Solution.objects.create(
                    title=data['title'],
                    slug=slugify(data['title']),
                    problem_description=data['problem'],
                    root_cause=data['root_cause'],
                    solution_content=data['solution'],
                    technology=technology,
                    difficulty_level=data['difficulty'],
                    helpful_count=random.randint(5, 150),
                    view_count=random.randint(50, 2000),
                    is_published=True,
                    published_at=timezone.now() - timedelta(days=random.randint(1, 180)),
                    meta_title=f"{data['title']} | Solutions",
                    meta_description=data['problem'][:150] + "..."
                )
                
                solutions.append(solution)
                self.stdout.write(f'   ✅ Created: {solution.title}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Failed to create solution {i+1}: {str(e)}')
                )
        
        return solutions
    
    def create_code_snippets(self, count, tags):
        """Create code snippets"""
        self.stdout.write(f'📝 Creating {count} code snippets...')
        
        snippets_data = [
            {
                'title': 'React useEffect Cleanup Pattern',
                'language': 'javascript',
                'description': 'Proper cleanup pattern for useEffect to prevent memory leaks',
                'code': '''useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();
    
    const fetchData = async () => {
        try {
            const response = await fetch('/api/data', {
                signal: controller.signal
            });
            const data = await response.json();
            
            if (isMounted) {
                setData(data);
            }
        } catch (error) {
            if (error.name !== 'AbortError' && isMounted) {
                setError(error.message);
            }
        }
    };
    
    fetchData();
    
    return () => {
        isMounted = false;
        controller.abort();
    };
}, []);''',
                'tag_names': ['react', 'cleanup', 'useeffect']
            },
            {
                'title': 'Django Model Validation',
                'language': 'python',
                'description': 'Custom model validation in Django with clean methods',
                'code': '''from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Event(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_attendees = models.PositiveIntegerField()
    
    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError('End date must be after start date.')
            
            if self.start_date < timezone.now():
                raise ValidationError('Start date cannot be in the past.')
        
        if self.max_attendees and self.max_attendees < 1:
            raise ValidationError('Maximum attendees must be at least 1.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)''',
                'tag_names': ['django', 'validation', 'models']
            },
            {
                'title': 'CSS Grid Responsive Layout',
                'language': 'css',
                'description': 'Responsive CSS Grid layout with fallbacks',
                'code': '''.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

/* Fallback for older browsers */
.grid-container {
    display: flex;
    flex-wrap: wrap;
    margin: -1rem;
}

.grid-container > * {
    flex: 1 1 300px;
    margin: 1rem;
}

/* Modern grid support */
@supports (display: grid) {
    .grid-container {
        display: grid;
        margin: 0;
    }
    
    .grid-container > * {
        margin: 0;
    }
}

@media (max-width: 768px) {
    .grid-container {
        grid-template-columns: 1fr;
        gap: 1rem;
        padding: 1rem;
    }
}''',
                'tag_names': ['css', 'grid', 'responsive']
            },
            {
                'title': 'Node.js Error Handling Middleware',
                'language': 'javascript',
                'description': 'Express.js error handling middleware with logging',
                'code': '''const errorHandler = (err, req, res, next) => {
    let error = { ...err };
    error.message = err.message;
    
    // Log error
    console.error(err);
    
    // Mongoose bad ObjectId
    if (err.name === 'CastError') {
        const message = 'Resource not found';
        error = { message, statusCode: 404 };
    }
    
    // Mongoose duplicate key
    if (err.code === 11000) {
        const message = 'Duplicate field value entered';
        error = { message, statusCode: 400 };
    }
    
    // Mongoose validation error
    if (err.name === 'ValidationError') {
        const message = Object.values(err.errors).map(val => val.message);
        error = { message, statusCode: 400 };
    }
    
    res.status(error.statusCode || 500).json({
        success: false,
        error: error.message || 'Server Error'
    });
};

module.exports = errorHandler;''',
                'tag_names': ['nodejs', 'express', 'error-handling']
            },
            {
                'title': 'SQL Query Optimization',
                'language': 'sql',
                'description': 'Optimized SQL query with proper indexing strategy',
                'code': '''-- Create indexes for optimization
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
CREATE INDEX idx_orders_created_desc ON orders(created_at DESC);
CREATE INDEX idx_users_active ON users(id) WHERE active = true;

-- Optimized query
SELECT 
    u.name,
    u.email,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id 
    AND o.status = 'completed'
    AND o.created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
WHERE u.active = true
GROUP BY u.id, u.name, u.email
HAVING order_count > 0
ORDER BY total_spent DESC
LIMIT 100;

-- Query analysis
EXPLAIN ANALYZE SELECT /* your query here */;''',
                'tag_names': ['sql', 'optimization', 'indexing']
            }
        ]
        
        created_count = 0
        for snippet_data in snippets_data[:count]:
            try:
                snippet = CodeSnippet.objects.create(
                    title=snippet_data['title'],
                    description=snippet_data['description'],
                    code=snippet_data['code'],
                    language=snippet_data['language']
                )
                
                # Add tags
                snippet_tags = []
                for tag_name in snippet_data.get('tag_names', []):
                    tag = next((tag for tag in tags if tag.name == tag_name), None)
                    if tag:
                        snippet_tags.append(tag)
                
                if snippet_tags:
                    snippet.tags.set(snippet_tags)
                
                created_count += 1
                self.stdout.write(f'   ✅ Created snippet: {snippet.title}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Failed to create snippet: {str(e)}')
                )
        
        self.stdout.write(f'   📝 Created {created_count} code snippets')
    
    def create_solution_relationships(self, solutions):
        """Create relationships between solutions"""
        self.stdout.write('🔗 Creating solution relationships...')
        
        relationship_count = 0
        for solution in solutions:
            # Find related solutions (same technology, different solution)
            related_solutions = [
                s for s in solutions 
                if s.technology == solution.technology and s != solution
            ]
            
            if related_solutions:
                # Add 1-3 related solutions
                num_related = min(random.randint(1, 3), len(related_solutions))
                selected_related = random.sample(related_solutions, num_related)
                solution.related_solutions.set(selected_related)
                relationship_count += num_related
        
        self.stdout.write(f'   🔗 Created {relationship_count} solution relationships')
