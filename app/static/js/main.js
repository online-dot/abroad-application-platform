document.addEventListener('DOMContentLoaded', function() {
    // Language Selector
    const languageSelector = document.getElementById('languageSelector');
    if (languageSelector) {
        languageSelector.addEventListener('change', function() {
            const lang = this.value;
            
            const translations = {
                en: {
                    welcome: "Your Canadian Immigration Journey Starts Here",
                    chooseUs: "Why Choose <span class='text-primary'>Canadian Visa Expert</span>",
                    testimonials: "What Our Customers Say",
                    ctaTitle: "Ready to Begin Your Canadian Journey?",
                    ctaSubtitle: "Take the first step towards your new life in Canada today.",
                    startBtn: "Start Free Evaluation",
                    contactBtn: "Speak to an Expert"
                },
                sw: {
                    welcome: "Safari Yako Ya Uhamiaji Canada Huanza Hapa",
                    chooseUs: "Kwa Nini Uchague <span class='text-primary'>Canadian Visa Expert</span>",
                    testimonials: "Wateja Wetu Wanasema Nini",
                    ctaTitle: "Tayari Kuanza Safari Yako Ya Canada?",
                    ctaSubtitle: "Chukua hatua ya kwanza kuelekea maisha yako mapya Canada leo.",
                    startBtn: "Anza Tathmini Bila Malipo",
                    contactBtn: "Ongea na Mtaalamu"
                },
                fr: {
                    welcome: "Votre parcours d'immigration canadienne commence ici",
                    chooseUs: "Pourquoi choisir <span class='text-primary'>Canadian Visa Expert</span>",
                    testimonials: "Ce que disent nos clients",
                    ctaTitle: "Prêt à commencer votre aventure canadienne?",
                    ctaSubtitle: "Faites le premier pas vers votre nouvelle vie au Canada aujourd'hui.",
                    startBtn: "Commencez l'évaluation gratuite",
                    contactBtn: "Parler à un expert"
                },
                ar: {
                    welcome: "رحلتك الكندية تبدأ من هنا",
                    chooseUs: "لماذا تختار <span class='text-primary'>خبير التأشيرات الكندية</span>",
                    testimonials: "ما يقوله عملاؤنا",
                    ctaTitle: "هل أنت مستعد لبدء رحلتك الكندية؟",
                    ctaSubtitle: "اتخذ الخطوة الأولى نحو حياتك الجديدة في كندا اليوم.",
                    startBtn: "ابدأ التقييم المجاني",
                    contactBtn: "تحدث إلى خبير"
                }
            };
            
            // Update all translatable elements
            if (document.querySelector(".hero-section h1")) {
                document.querySelector(".hero-section h1").textContent = translations[lang].welcome;
            }
            
            if (document.querySelector(".why-us .section-title")) {
                document.querySelector(".why-us .section-title").innerHTML = translations[lang].chooseUs;
            }
            
            if (document.querySelector(".testimonials .section-title")) {
                document.querySelector(".testimonials .section-title").textContent = translations[lang].testimonials;
            }
            
            if (document.querySelector(".cta h2")) {
                document.querySelector(".cta h2").textContent = translations[lang].ctaTitle;
            }
            
            if (document.querySelector(".cta .lead")) {
                document.querySelector(".cta .lead").textContent = translations[lang].ctaSubtitle;
            }
            
            const startBtns = document.querySelectorAll('a[href="#apply"]');
            startBtns.forEach(btn => {
                if (btn.textContent.includes("Start") || btn.textContent.includes("Anza") || 
                    btn.textContent.includes("Commencez") || btn.textContent.includes("ابدأ")) {
                    btn.textContent = translations[lang].startBtn;
                }
            });
            
            const contactBtns = document.querySelectorAll('a[href="#contact"]');
            contactBtns.forEach(btn => {
                if (btn.textContent.includes("Speak") || btn.textContent.includes("Ongea") || 
                    btn.textContent.includes("Parler") || btn.textContent.includes("تحدث")) {
                    btn.textContent = translations[lang].contactBtn;
                }
            });
        });
    }
    
    // Testimonial Slider
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    let currentIndex = 0;
    let intervalId;
    
    function showTestimonial(index) {
        // Hide all testimonials
        testimonialCards.forEach(card => card.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        // Show the selected testimonial
        testimonialCards[index].classList.add('active');
        dots[index].classList.add('active');
        currentIndex = index;
        
        // Reset the auto-rotation timer
        resetInterval();
    }
    
    function nextTestimonial() {
        let newIndex = currentIndex + 1;
        if (newIndex >= testimonialCards.length) newIndex = 0;
        showTestimonial(newIndex);
    }
    
    function prevTestimonial() {
        let newIndex = currentIndex - 1;
        if (newIndex < 0) newIndex = testimonialCards.length - 1;
        showTestimonial(newIndex);
    }
    
    function startInterval() {
        intervalId = setInterval(nextTestimonial, 5000); // Rotate every 5 seconds
    }
    
    function resetInterval() {
        clearInterval(intervalId);
        startInterval();
    }
    
    // Initialize the slider
    if (testimonialCards.length > 0) {
        showTestimonial(0);
        startInterval();
        
        // Add click event to dots
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => showTestimonial(index));
        });
        
        // Add click event to navigation buttons
        if (nextBtn) nextBtn.addEventListener('click', nextTestimonial);
        if (prevBtn) prevBtn.addEventListener('click', prevTestimonial);
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70, // Adjust for fixed header
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarNav = document.querySelector('#navbarNav');
    
    if (navbarToggler && navbarNav) {
        navbarToggler.addEventListener('click', function() {
            navbarNav.classList.toggle('show');
        });
    }
    
    // Close mobile menu when clicking on a link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (navbarNav.classList.contains('show')) {
                navbarNav.classList.remove('show');
            }
        });
    });
});