/* ============================================
   CHATBOT PRÉINSCRIPTION - JAVASCRIPT
   Interactive Features & API Integration
   Author: Madick Ange César
   ============================================ */

// ============================================
// GLOBAL VARIABLES & CONFIGURATION
// ============================================
const CONFIG = {
    API_ENDPOINTS: {
        MESSAGE: '/api/message',
        PREINSCRIPTION: '/api/preinscription',
        PREINSCRIPTIONS: '/api/preinscriptions'
    },
    MAX_MESSAGE_LENGTH: 1000,
    MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
    TYPING_DELAY: 1000
};

let currentStep = 1;
let sessionId = generateSessionId();

// ============================================
// UTILITY FUNCTIONS
// ============================================
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas fa-${getToastIcon(type)}"></i>
        <span>${message}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function showLoading(show = true) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }
}

function formatDate(date) {
    return new Date(date).toLocaleString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getCurrentTime() {
    return new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function sendQuickAction(query) {
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        const actionMap = {
            'programmes': 'Quels sont les programmes disponibles ?',
            'documents': 'Quels documents sont nécessaires ?',
            'frais': 'Quels sont les frais de scolarité ?',
            'calendrier': 'Quel est le calendrier académique ?',
            'inscription': 'Comment puis-je m\'inscrire ?',
            'aide': 'J\'ai besoin d\'aide',
            'contact': 'Comment vous contacter ?',
            'admission': 'Quelles sont les conditions d\'admission ?'
        };
        
        messageInput.value = actionMap[query] || query;
        sendMessage();
    }
}

function sendSuggestion(text) {
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.value = text;
        sendMessage();
    }
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn && !sendBtn.disabled) {
            sendMessage();
        }
    }
}

function attachFile() {
    showToast('Fonctionnalité bientôt disponible', 'info');
}

function addEmoji() {
    showToast('Fonctionnalité bientôt disponible', 'info');
}

function startApplication() {
    window.location.href = '/preinscription';
}

// ============================================
// LANDING PAGE FUNCTIONS
// ============================================
function initializeLandingPage() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuToggle && navLinks) {
        mobileMenuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Smooth scroll for navigation links
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

    // Navbar scroll effect
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .step').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
}

// ============================================
// CHAT PAGE FUNCTIONS
// ============================================
function initializeChat() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const newChatBtn = document.querySelector('.new-chat-btn');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.chat-sidebar');

    // Auto-resize textarea
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            // Auto-resize
            autoResize(this);
        });

        // Send message on Enter (Shift+Enter for new line)
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const sendBtn = document.getElementById('sendBtn');
                if (sendBtn && !sendBtn.disabled) {
                    sendMessage();
                }
            }
        });
    }

    // Send button click
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            if (question && messageInput) {
                messageInput.value = question;
                sendMessage();
            }
        });
    });

    // New chat button
    if (newChatBtn) {
        newChatBtn.addEventListener('click', startNewChat);
    }

    // Sidebar toggle for mobile
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Load chat history
    loadChatHistory();
}

// ============================================
// CHAT MESSAGE FUNCTIONS (GLOBAL)
// ============================================
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessageToChat(message, 'user');

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Remove welcome message if present
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    // Show typing indicator
    showTypingIndicator(true);

    // Send to API
    fetch(CONFIG.API_ENDPOINTS.MESSAGE, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            session_id: sessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        showTypingIndicator(false);
        if (data.response) {
            addMessageToChat(data.response, 'bot');
            saveChatToHistory(message);
        } else {
            throw new Error('Invalid response');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showTypingIndicator(false);
        addMessageToChat('Désolé, une erreur s\'est produite. Veuillez réessayer.', 'bot');
        showToast('Erreur de connexion au serveur', 'error');
    });
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    
    if (sender === 'bot') {
        avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';
    } else {
        avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = message;

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = formatDate(new Date());

    contentDiv.appendChild(bubbleDiv);
    contentDiv.appendChild(timeDiv);

    if (sender === 'bot') {
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
    } else {
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(avatarDiv);
    }

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator(show) {
    const typingIndicator = document.querySelector('.typing-indicator');
    const onlineStatus = document.querySelector('.online-status');

    if (typingIndicator && onlineStatus) {
        if (show) {
            typingIndicator.style.display = 'inline-flex';
            onlineStatus.style.display = 'none';
        } else {
            typingIndicator.style.display = 'none';
            onlineStatus.style.display = 'inline';
        }
    }
}

function startNewChat() {
    sessionId = generateSessionId();
    const chatMessages = document.getElementById('chatMessages');
    
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <h3>Nouvelle conversation ! 👋</h3>
                <p>Comment puis-je vous aider aujourd'hui ?</p>
                <div class="quick-actions">
                    <button class="quick-action-btn" data-question="Quels sont les programmes disponibles ?">
                        <i class="fas fa-book"></i>
                        <span>Programmes disponibles</span>
                    </button>
                    <button class="quick-action-btn" data-question="Quels documents sont nécessaires ?">
                        <i class="fas fa-file-alt"></i>
                        <span>Documents requis</span>
                    </button>
                    <button class="quick-action-btn" data-question="Quels sont les frais de scolarité ?">
                        <i class="fas fa-money-bill-wave"></i>
                        <span>Frais de scolarité</span>
                    </button>
                    <button class="quick-action-btn" data-question="Comment puis-je m'inscrire ?">
                        <i class="fas fa-user-plus"></i>
                        <span>Procédure d'inscription</span>
                    </button>
                </div>
            </div>
        `;
        
        // Re-attach event listeners to new quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const question = this.getAttribute('data-question');
                const messageInput = document.getElementById('messageInput');
                if (question && messageInput) {
                    messageInput.value = question;
                    sendMessage();
                }
            });
        });
    }

    showToast('Nouvelle conversation démarrée', 'success');
}

function loadChatHistory() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
    
    if (history.length === 0) {
        historyList.innerHTML = '<p style="color: var(--text-tertiary); font-size: 0.875rem; padding: 1rem 0;">Aucun historique</p>';
        return;
    }

    historyList.innerHTML = history.slice(0, 10).map(item => `
        <div class="history-item" data-session="${item.session}">
            ${item.message}
        </div>
    `).join('');

    // Add click handlers
    historyList.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', function() {
            const message = this.textContent.trim();
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                messageInput.value = message;
                messageInput.focus();
            }
        });
    });
}

function saveChatToHistory(message) {
    const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
    history.unshift({
        session: sessionId,
        message: message.substring(0, 50) + (message.length > 50 ? '...' : ''),
        timestamp: Date.now()
    });

    // Keep only last 50 items
    localStorage.setItem('chatHistory', JSON.stringify(history.slice(0, 50)));
    loadChatHistory();
}

// ============================================
// FORM PAGE FUNCTIONS
// ============================================
function initializeForm() {
    const form = document.getElementById('preinscriptionForm');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    // Navigation buttons
    if (nextBtn) {
        nextBtn.addEventListener('click', () => navigateStep('next'));
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => navigateStep('prev'));
    }

    // Form submission
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    // File upload handling
    initializeFileUploads();

    // Real-time validation
    initializeValidation();

    // Character counter for motivation
    const motivationInput = document.getElementById('motivation');
    const motivationCounter = document.getElementById('motivationCounter');
    
    if (motivationInput && motivationCounter) {
        motivationInput.addEventListener('input', function() {
            const count = this.value.length;
            motivationCounter.textContent = Math.min(count, 500);
            
            if (count > 500) {
                this.value = this.value.substring(0, 500);
            }
        });
    }

    // Initialize first step
    showStep(1);
}

function navigateStep(direction) {
    const totalSteps = 4;

    // Validate current step before proceeding
    if (direction === 'next') {
        if (!validateStep(currentStep)) {
            showToast('Veuillez remplir tous les champs obligatoires', 'warning');
            return;
        }
        currentStep = Math.min(currentStep + 1, totalSteps);
    } else {
        currentStep = Math.max(currentStep - 1, 1);
    }

    showStep(currentStep);
    updateProgressBar();
}

function showStep(step) {
    // Hide all steps
    document.querySelectorAll('.form-step').forEach(s => {
        s.classList.remove('active');
    });

    // Show current step
    const currentStepEl = document.querySelector(`.form-step[data-step="${step}"]`);
    if (currentStepEl) {
        currentStepEl.classList.add('active');
    }

    // Update buttons
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    if (prevBtn) prevBtn.style.display = step === 1 ? 'none' : 'inline-flex';
    if (nextBtn) nextBtn.style.display = step === 4 ? 'none' : 'inline-flex';
    if (submitBtn) submitBtn.style.display = step === 4 ? 'inline-flex' : 'none';

    // Generate summary on last step
    if (step === 4) {
        generateSummary();
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateProgressBar() {
    const progress = (currentStep / 4) * 100;
    const progressFill = document.getElementById('progressFill');
    
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }

    // Update progress steps
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        if (index + 1 < currentStep) {
            step.classList.add('completed');
            step.classList.remove('active');
        } else if (index + 1 === currentStep) {
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            step.classList.remove('active', 'completed');
        }
    });
}

function validateStep(step) {
    const stepEl = document.querySelector(`.form-step[data-step="${step}"]`);
    if (!stepEl) return true;

    const requiredInputs = stepEl.querySelectorAll('[required]');
    let isValid = true;

    requiredInputs.forEach(input => {
        if (input.type === 'radio') {
            const name = input.name;
            const group = stepEl.querySelectorAll(`[name="${name}"]`);
            const checked = Array.from(group).some(radio => radio.checked);
            
            if (!checked) {
                isValid = false;
                showFieldError(group[0], 'Ce champ est obligatoire');
            } else {
                clearFieldError(group[0]);
            }
        } else if (input.type === 'checkbox') {
            if (!input.checked) {
                isValid = false;
                showFieldError(input, 'Vous devez accepter les conditions');
            } else {
                clearFieldError(input);
            }
        } else if (!input.value.trim()) {
            isValid = false;
            showFieldError(input, 'Ce champ est obligatoire');
        } else {
            clearFieldError(input);
        }
    });

    return isValid;
}

function showFieldError(input, message) {
    const formGroup = input.closest('.form-group') || input.closest('.program-cards');
    if (!formGroup) return;

    const errorEl = formGroup.querySelector('.error-message');
    if (errorEl) {
        errorEl.textContent = message;
    }

    if (input.classList) {
        input.classList.add('error');
    }
}

function clearFieldError(input) {
    const formGroup = input.closest('.form-group') || input.closest('.program-cards');
    if (!formGroup) return;

    const errorEl = formGroup.querySelector('.error-message');
    if (errorEl) {
        errorEl.textContent = '';
    }

    if (input.classList) {
        input.classList.remove('error');
    }
}

function initializeValidation() {
    // Email validation
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                showFieldError(this, 'Adresse email invalide');
            } else {
                clearFieldError(this);
            }
        });
    }

    // Phone validation
    const phoneInput = document.getElementById('telephone');
    if (phoneInput) {
        phoneInput.addEventListener('blur', function() {
            const phoneRegex = /^[\d\s+()-]{8,}$/;
            if (this.value && !phoneRegex.test(this.value)) {
                showFieldError(this, 'Numéro de téléphone invalide');
            } else {
                clearFieldError(this);
            }
        });
    }

    // Clear errors on input
    document.querySelectorAll('input, textarea, select').forEach(input => {
        input.addEventListener('input', function() {
            if (this.value) {
                clearFieldError(this);
            }
        });
    });
}

function initializeFileUploads() {
    document.querySelectorAll('.file-upload-wrapper').forEach(wrapper => {
        const input = wrapper.querySelector('input[type="file"]');
        const area = wrapper.querySelector('.file-upload-area');

        if (!input || !area) return;

        // Click to upload
        area.addEventListener('click', () => input.click());

        // File selected
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (!file) return;

            // Check file size
            if (file.size > CONFIG.MAX_FILE_SIZE) {
                showToast('Le fichier est trop volumineux (max 5 Mo)', 'error');
                this.value = '';
                return;
            }

            // Show file name
            const fileName = area.querySelector('.file-name');
            if (fileName) {
                fileName.textContent = file.name;
            }

            area.classList.add('has-file');
            showToast(`Fichier "${file.name}" ajouté`, 'success');
        });

        // Drag and drop
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('drag-over');
        });

        area.addEventListener('dragleave', () => {
            area.classList.remove('drag-over');
        });

        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('drag-over');

            const file = e.dataTransfer.files[0];
            if (file) {
                input.files = e.dataTransfer.files;
                input.dispatchEvent(new Event('change'));
            }
        });
    });
}

function generateSummary() {
    const summaryContent = document.getElementById('summaryContent');
    if (!summaryContent) return;

    const formData = {
        'Nom': document.getElementById('nom')?.value,
        'Prénom': document.getElementById('prenom')?.value,
        'Email': document.getElementById('email')?.value,
        'Téléphone': document.getElementById('telephone')?.value,
        'Date de naissance': document.getElementById('dateNaissance')?.value,
        'Lieu de naissance': document.getElementById('lieuNaissance')?.value,
        'Adresse': document.getElementById('adresse')?.value,
        'Programme': document.querySelector('input[name="programme"]:checked')?.value,
        'Niveau': document.getElementById('niveau')?.value
    };

    summaryContent.innerHTML = Object.entries(formData)
        .filter(([key, value]) => value)
        .map(([key, value]) => `
            <div class="summary-item">
                <span class="summary-label">${key}:</span>
                <span class="summary-value">${value}</span>
            </div>
        `).join('');
}

function handleFormSubmit(e) {
    e.preventDefault();

    if (!validateStep(4)) {
        showToast('Veuillez accepter les conditions générales', 'error');
        return;
    }

    showLoading(true);

    const formData = new FormData(e.target);

    fetch(CONFIG.API_ENDPOINTS.PREINSCRIPTION, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            showSuccessModal();
            e.target.reset();
            currentStep = 1;
            showStep(1);
            updateProgressBar();
        } else {
            throw new Error(data.message || 'Erreur lors de la soumission');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showLoading(false);
        showToast('Erreur lors de la soumission du formulaire', 'error');
    });
}

function showSuccessModal() {
    const modal = document.getElementById('successModal');
    if (modal) {
        modal.style.display = 'flex';
        
        // Close on backdrop click
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
}

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // Detect current page and initialize accordingly
    if (document.body.classList.contains('landing-page')) {
        initializeLandingPage();
    } else if (document.body.classList.contains('chat-page')) {
        initializeChat();
    } else if (document.body.classList.contains('form-page')) {
        initializeForm();
    }
});

// ============================================
// AUTHENTICATION UTILITIES
// ============================================
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Erreur vérification auth:', error);
        return { authenticated: false };
    }
}

async function logoutUser() {
    if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                showToast('Déconnexion réussie', 'success');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1000);
            } else {
                showToast('Erreur lors de la déconnexion', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            showToast('Erreur de connexion', 'error');
        }
    }
}

async function getUserProfile() {
    try {
        const response = await fetch('/api/auth/profile');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Erreur récupération profil:', error);
        return { success: false };
    }
}

// Protect pages that require authentication
async function requireAuth(redirectUrl = '/login') {
    const authData = await checkAuth();
    if (!authData.authenticated) {
        window.location.href = redirectUrl;
        return false;
    }
    return true;
}

// Redirect if already authenticated
async function redirectIfAuth(redirectUrl = '/chat') {
    const authData = await checkAuth();
    if (authData.authenticated) {
        window.location.href = redirectUrl;
        return true;
    }
    return false;
}

// Export functions for use in inline scripts
window.initializeChat = initializeChat;
window.initializeForm = initializeForm;
window.checkAuth = checkAuth;
window.logoutUser = logoutUser;
window.getUserProfile = getUserProfile;
window.requireAuth = requireAuth;
window.redirectIfAuth = redirectIfAuth;
window.sendMessage = sendMessage;
window.sendQuickAction = sendQuickAction;
window.sendSuggestion = sendSuggestion;
window.handleKeyDown = handleKeyDown;
window.autoResize = autoResize;
window.attachFile = attachFile;
window.addEmoji = addEmoji;
window.startApplication = startApplication;