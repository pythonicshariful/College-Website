// Main JavaScript for ISCM Website

// Hero Slider
document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.hero-slide');
    let currentSlide = 0;
    
    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove('active');
            if (i === index) {
                slide.classList.add('active');
            }
        });
    }
    
    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }
    
    // Auto-advance slides every 5 seconds
    if (slides.length > 0) {
        setInterval(nextSlide, 5000);
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Animate statistics on scroll
    const statNumbers = document.querySelectorAll('.stat-number');
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const finalValue = target.textContent;
                
                // Only animate if it's a number
                if (finalValue.includes('%') || finalValue.includes('+')) {
                    const numericValue = parseInt(finalValue.replace(/[^0-9]/g, ''));
                    animateValue(target, 0, numericValue, 2000, finalValue);
                    observer.unobserve(target);
                }
            }
        });
    }, observerOptions);
    
    statNumbers.forEach(stat => {
        observer.observe(stat);
    });
    
    function animateValue(element, start, end, duration, originalText) {
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(progress * (end - start) + start);
            
            // Preserve the original format (%, +, etc.)
            if (originalText.includes('%')) {
                element.textContent = current + '%';
            } else if (originalText.includes('+')) {
                element.textContent = current + '+';
            } else {
                element.textContent = current;
            }
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = originalText;
            }
        }
        
        requestAnimationFrame(update);
    }
    
    // Mobile menu toggle (if needed)
    const navToggle = document.querySelector('.nav-toggle');
    const mainNav = document.querySelector('.main-nav ul');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            mainNav.classList.toggle('active');
        });
    }
    
    // Highlight active navigation item on scroll
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.main-nav a[href^="#"]');
    
    window.addEventListener('scroll', function() {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
    
    // Add fade-in animation to cards on scroll
    const cards = document.querySelectorAll('.news-card, .leadership-card, .notice-board');
    
    const cardObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                cardObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        cardObserver.observe(card);
    });
    
    // Notice board ticker animation (vertical scroll)
    const noticeBoard = document.querySelector('.notice-board');
    if (noticeBoard) {
        const noticeItems = noticeBoard.querySelectorAll('.notice-item');
        
        // Add hover pause functionality
        noticeItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'var(--light-color)';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.backgroundColor = 'transparent';
            });
        });
    }
    
    console.log('ISCM Website loaded successfully!');
});
