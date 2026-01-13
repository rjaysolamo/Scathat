// Documentation Website JavaScript
class ScathatDocs {
    constructor() {
        this.init();
    }

    init() {
        this.setupTheme();
        this.setupSearch();
        this.setupSmoothScroll();
        this.setupMobileMenu();
        this.setupActiveNav();
        this.setupCopyButtons();
    }

    // Theme Toggle Functionality
    setupTheme() {
        const themeToggle = document.getElementById('themeToggle');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Set initial theme based on system preference or saved preference
        const savedTheme = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // Add animation class
                themeToggle.classList.add('rotating');
                setTimeout(() => themeToggle.classList.remove('rotating'), 600);
            });
        }
    }

    // Search Functionality
    setupSearch() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            this.filterContent(searchTerm);
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch(searchInput.value);
            }
        });
    }

    filterContent(searchTerm) {
        const cards = document.querySelectorAll('.doc-card');
        const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
        
        cards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const content = card.querySelector('p').textContent.toLowerCase();
            
            if (title.includes(searchTerm) || content.includes(searchTerm)) {
                card.style.display = 'block';
                card.classList.add('fade-in');
            } else {
                card.style.display = 'none';
            }
        });

        // Also filter sidebar links
        sidebarLinks.forEach(link => {
            const text = link.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                link.style.display = 'block';
            } else {
                link.style.display = 'none';
            }
        });
    }

    performSearch(term) {
        if (!term.trim()) return;
        
        // Highlight search results (simplified version)
        const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, li');
        elements.forEach(el => {
            const text = el.textContent;
            if (text.toLowerCase().includes(term.toLowerCase())) {
                el.style.backgroundColor = 'var(--accent)';
                el.style.color = 'white';
                el.style.padding = '0.25rem';
                el.style.borderRadius = '4px';
                
                // Scroll to first result
                if (!this.firstResult) {
                    this.firstResult = el;
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }

    // Smooth scrolling for anchor links
    setupSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Mobile menu toggle (for future use)
    setupMobileMenu() {
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.querySelector('.sidebar');
        
        if (menuToggle && sidebar) {
            menuToggle.addEventListener('click', () => {
                sidebar.classList.toggle('mobile-open');
            });
        }
    }

    // Set active navigation based on current page
    setupActiveNav() {
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        const navLinks = document.querySelectorAll('.sidebar-nav a');
        
        navLinks.forEach(link => {
            const linkPage = link.getAttribute('href');
            if (linkPage === currentPage) {
                link.classList.add('active');
            }
        });
    }

    // Copy code blocks functionality
    setupCopyButtons() {
        document.querySelectorAll('.code-block').forEach(block => {
            const copyButton = document.createElement('button');
            copyButton.textContent = 'Copy';
            copyButton.className = 'copy-btn';
            copyButton.style.cssText = `
                position: absolute;
                top: 0.5rem;
                right: 0.5rem;
                background: var(--primary);
                color: white;
                border: none;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
                cursor: pointer;
            `;
            
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(block.textContent)
                    .then(() => {
                        copyButton.textContent = 'Copied!';
                        setTimeout(() => {
                            copyButton.textContent = 'Copy';
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Failed to copy: ', err);
                    });
            });
            
            block.style.position = 'relative';
            block.appendChild(copyButton);
        });
    }

    // Utility method to debounce function calls
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ScathatDocs();
});

// Add some interactive animations
document.addEventListener('DOMContentLoaded', () => {
    // Animate cards on page load
    const cards = document.querySelectorAll('.doc-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'translateY(-2px)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translateY(0)';
        });
    });
});