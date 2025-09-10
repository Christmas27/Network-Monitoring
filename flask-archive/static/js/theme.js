// Create: static/js/theme.js

class ThemeManager {
    constructor() {
        this.currentTheme = 'light'; // Default to light
        this.init();
    }

    init() {
        this.loadSavedTheme();
        this.setupEventListeners();
    }

    loadSavedTheme() {
        // Default to light mode, load saved preference
        const savedTheme = localStorage.getItem('dashboard-theme') || 'light';
        this.currentTheme = savedTheme;
        this.applyTheme(savedTheme);
        this.updateThemeIcon(savedTheme);
    }

    setupEventListeners() {
        // Find theme toggle button
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Also support onclick function for backward compatibility
        window.toggleTheme = () => this.toggleTheme();
    }

    toggleTheme() {
        // Toggle between light and dark
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.currentTheme = newTheme;
        
        this.applyTheme(newTheme);
        this.updateThemeIcon(newTheme);
        this.saveTheme(newTheme);
        this.showThemeNotification(newTheme);
        
        console.log(`🎨 Theme switched to: ${newTheme}`);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update body classes for Bootstrap compatibility
        if (theme === 'dark') {
            document.body.classList.add('bg-dark');
            document.body.classList.remove('bg-light');
        } else {
            document.body.classList.add('bg-light');
            document.body.classList.remove('bg-dark');
        }
    }

    updateThemeIcon(theme) {
        const themeIcon = document.querySelector('.theme-toggle i');
        if (themeIcon) {
            // Add rotation animation
            themeIcon.style.transform = 'rotate(360deg)';
            
            setTimeout(() => {
                // Light mode shows moon (to switch to dark)
                // Dark mode shows sun (to switch to light)
                themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
                themeIcon.style.transform = 'rotate(0deg)';
            }, 150);
        }
    }

    saveTheme(theme) {
        localStorage.setItem('dashboard-theme', theme);
    }

    showThemeNotification(theme) {
        // Remove existing notification
        const existing = document.querySelector('.theme-notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.className = 'alert alert-info position-fixed theme-notification';
        notification.style.cssText = `
            top: 80px; 
            right: 20px; 
            z-index: 1055; 
            min-width: 250px;
            animation: slideInRight 0.3s ease;
            border-radius: 0.5rem;
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${theme === 'dark' ? 'moon' : 'sun'} me-2"></i>
                <span>Switched to ${theme === 'dark' ? 'Dark' : 'Light'} Mode</span>
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 3000);
    }

    // Public method to get current theme
    getCurrentTheme() {
        return this.currentTheme;
    }

    // Public method to set theme
    setTheme(theme) {
        if (theme === 'light' || theme === 'dark') {
            this.currentTheme = theme;
            this.applyTheme(theme);
            this.updateThemeIcon(theme);
            this.saveTheme(theme);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.themeManager = new ThemeManager();
    console.log('🎨 Theme Manager initialized - Default: Light Mode');
});

// CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .theme-toggle i {
        transition: transform 0.3s ease;
    }
    
    .theme-notification {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
`;
document.head.appendChild(style);