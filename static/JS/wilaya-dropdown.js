// ==================== WILAYA DROPDOWN FUNCTIONALITY ====================

// List of all 48 Algerian Wilayas
const WILAYAS = [
    "Adrar",
    "Chlef",
    "Laghouat",
    "Oum El Bouaghi",
    "Batna",
    "Béjaïa",
    "Biskra",
    "Béchar",
    "Blida",
    "Bouira",
    "Tamanrasset",
    "Tébessa",
    "Tlemcen",
    "Tiaret",
    "Tizi Ouzou",
    "Alger",
    "Djelfa",
    "Jijel",
    "Sétif",
    "Saida",
    "Skikda",
    "Sidi Bel Abbès",
    "Annaba",
    "Guelma",
    "Constantine",
    "Médéa",
    "Mostaganem",
    "M'Sila",
    "Mascara",
    "Ouargla",
    "Oran",
    "El Bayadh",
    "Illizi",
    "Bordj Bou Arréridj",
    "Boumerdès",
    "El Tarf",
    "Tindouf",
    "Tissemsilt",
    "El Oued",
    "Khenchela",
    "Souk Ahras",
    "Tipaza",
    "Mila",
    "Aïn Defla",
    "Naâma",
    "Aïn Témouchent",
    "Ghardaïa",
    "Relizane"
];

class WilayaDropdown {
    constructor(inputElement) {
        this.input = inputElement;
        this.container = null;
        this.dropdownList = null;
        this.selectedValue = this.input.value || '';
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        // Create dropdown container structure
        this.createDropdownStructure();
        
        // Bind events
        this.bindEvents();
        
        // Set initial value if exists
        if (this.selectedValue) {
            this.input.value = this.selectedValue;
            this.input.classList.add('has-value');
        }
    }
    
    createDropdownStructure() {
        // Wrap the input
        this.container = document.createElement('div');
        this.container.className = 'wilaya-dropdown-container';
        
        const wrapper = document.createElement('div');
        wrapper.className = 'wilaya-input-wrapper';
        
        // Replace original input's parent
        this.input.parentNode.insertBefore(this.container, this.input);
        wrapper.appendChild(this.input);
        this.container.appendChild(wrapper);
        
        // Add dropdown icon
        const icon = document.createElement('span');
        icon.className = 'wilaya-dropdown-icon';
        icon.innerHTML = '▼';
        wrapper.appendChild(icon);
        
        // Create dropdown list
        this.dropdownList = document.createElement('div');
        this.dropdownList.className = 'wilaya-dropdown-list';
        
        // Add all wilayas
        WILAYAS.forEach(wilaya => {
            const item = document.createElement('div');
            item.className = 'wilaya-dropdown-item';
            item.textContent = wilaya;
            item.dataset.value = wilaya;
            
            // ONLY mark as selected if it matches the initial value
            if (wilaya === this.selectedValue && this.selectedValue !== '') {
                item.classList.add('selected');
            }
            
            this.dropdownList.appendChild(item);
        });
        
        // Add no results message
        const noResults = document.createElement('div');
        noResults.className = 'wilaya-no-results';
        noResults.textContent = 'No wilaya found';
        this.dropdownList.appendChild(noResults);
        
        this.container.appendChild(this.dropdownList);
        
        // Update input attributes
        this.input.setAttribute('autocomplete', 'off');
        this.input.setAttribute('placeholder', 'Type or click to select wilaya...');
        this.input.classList.add('wilaya-input');
    }
    
    bindEvents() {
        // Click on input to toggle dropdown
        this.input.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        // Focus on input to open dropdown
        this.input.addEventListener('focus', () => {
            this.open();
        });
        
        // Type to filter
        this.input.addEventListener('input', (e) => {
            this.filterWilayas(e.target.value);
            if (!this.isOpen) {
                this.open();
            }
        });
        
        // Click on dropdown item
        this.dropdownList.addEventListener('click', (e) => {
            if (e.target.classList.contains('wilaya-dropdown-item')) {
                this.selectWilaya(e.target.dataset.value);
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.close();
            }
        });
        
        // Keyboard navigation
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
            } else if (e.key === 'Enter') {
                e.preventDefault();
                const visibleItems = this.getVisibleItems();
                if (visibleItems.length === 1) {
                    this.selectWilaya(visibleItems[0].dataset.value);
                }
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateDropdown('down');
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateDropdown('up');
            }
        });
    }
    
    open() {
        this.isOpen = true;
        this.container.classList.add('active');
        this.filterWilayas(this.input.value);
    }
    
    close() {
        this.isOpen = false;
        this.container.classList.remove('active');
        
        // If no valid selection, restore previous value
        if (!WILAYAS.includes(this.input.value)) {
            this.input.value = this.selectedValue;
        }
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    filterWilayas(searchTerm) {
        const items = this.dropdownList.querySelectorAll('.wilaya-dropdown-item');
        const noResults = this.dropdownList.querySelector('.wilaya-no-results');
        let visibleCount = 0;
        
        const normalizedSearch = this.normalizeText(searchTerm);
        
        items.forEach(item => {
            const wilaya = item.dataset.value;
            const normalizedWilaya = this.normalizeText(wilaya);
            
            if (normalizedWilaya.includes(normalizedSearch)) {
                item.classList.remove('hidden');
                visibleCount++;
            } else {
                item.classList.add('hidden');
            }
        });
        
        // Show/hide no results message
        if (visibleCount === 0) {
            noResults.classList.add('show');
        } else {
            noResults.classList.remove('show');
        }
    }
    
    selectWilaya(wilaya) {
        // Update selected value
        this.selectedValue = wilaya;
        this.input.value = wilaya;
        this.input.classList.add('has-value');
        
        // IMPORTANT: Remove selected class from ALL items first
        const allItems = this.dropdownList.querySelectorAll('.wilaya-dropdown-item');
        allItems.forEach(item => {
            item.classList.remove('selected');
            item.classList.remove('hover');
        });
        
        // Then add selected class ONLY to the chosen item
        allItems.forEach(item => {
            if (item.dataset.value === wilaya) {
                item.classList.add('selected');
            }
        });
        
        // Trigger change event for form validation
        const event = new Event('change', { bubbles: true });
        this.input.dispatchEvent(event);
        
        // Close dropdown
        this.close();
        
        // Optional: Trigger custom event for shipping cost calculation
        const customEvent = new CustomEvent('wilayaSelected', {
            detail: { wilaya: wilaya },
            bubbles: true
        });
        this.input.dispatchEvent(customEvent);
    }
    
    navigateDropdown(direction) {
        const visibleItems = this.getVisibleItems();
        if (visibleItems.length === 0) return;
        
        const currentIndex = visibleItems.findIndex(item => 
            item.classList.contains('hover') || item.classList.contains('selected')
        );
        
        let nextIndex;
        if (direction === 'down') {
            nextIndex = currentIndex < visibleItems.length - 1 ? currentIndex + 1 : 0;
        } else {
            nextIndex = currentIndex > 0 ? currentIndex - 1 : visibleItems.length - 1;
        }
        
        // Remove hover class from all
        visibleItems.forEach(item => item.classList.remove('hover'));
        
        // Add hover to next
        visibleItems[nextIndex].classList.add('hover');
        visibleItems[nextIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
    
    getVisibleItems() {
        return Array.from(this.dropdownList.querySelectorAll('.wilaya-dropdown-item:not(.hidden)'));
    }
    
    normalizeText(text) {
        // Remove accents and convert to lowercase for better matching
        return text
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');
    }
    
    // Public method to get selected value
    getValue() {
        return this.selectedValue;
    }
    
    // Public method to set value programmatically
    setValue(wilaya) {
        if (WILAYAS.includes(wilaya)) {
            this.selectWilaya(wilaya);
        }
    }
    
    // Public method to reset
    reset() {
        this.selectedValue = '';
        this.input.value = '';
        this.input.classList.remove('has-value');
        
        const items = this.dropdownList.querySelectorAll('.wilaya-dropdown-item');
        items.forEach(item => item.classList.remove('selected'));
    }
}

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Find all wilaya inputs and initialize
    const wilayaInputs = document.querySelectorAll('input[name="wilaya"], #wilaya, .wilaya-select');
    
    wilayaInputs.forEach(input => {
        // Skip if it's already a select element
        if (input.tagName === 'SELECT') {
            return;
        }
        
        // Initialize dropdown
        new WilayaDropdown(input);
    });
});

// Export for manual initialization if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WilayaDropdown;
}