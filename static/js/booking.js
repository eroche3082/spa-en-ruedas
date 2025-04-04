/**
 * Spa en Ruedas - Booking Form JavaScript
 * Handles the booking form functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date picker with Flatpickr
    const datePicker = flatpickr("#date", {
        minDate: "today",
        dateFormat: "Y-m-d",
        disable: [
            function(date) {
                // Disable Sundays (0 is Sunday)
                return date.getDay() === 0;
            }
        ],
        locale: {
            firstDayOfWeek: 1 // Start the week on Monday
        },
        onChange: function(selectedDates, dateStr, instance) {
            // When a date is selected, enable the time select and fetch available slots
            const timeSelect = document.getElementById('time');
            const locationSelect = document.getElementById('location');
            
            if (dateStr && locationSelect.value) {
                fetchAvailableTimeSlots(dateStr, locationSelect.value);
                timeSelect.disabled = false;
            } else {
                timeSelect.disabled = true;
                timeSelect.innerHTML = '<option value="">Primero selecciona fecha y ubicación</option>';
            }
        }
    });
    
    // Listen for location change to update available times
    const locationSelect = document.getElementById('location');
    
    if (locationSelect) {
        locationSelect.addEventListener('change', function() {
            const dateInput = document.getElementById('date');
            const timeSelect = document.getElementById('time');
            
            if (this.value && dateInput.value) {
                fetchAvailableTimeSlots(dateInput.value, this.value);
                timeSelect.disabled = false;
            } else {
                timeSelect.disabled = true;
                timeSelect.innerHTML = '<option value="">Primero selecciona fecha y ubicación</option>';
            }
        });
    }
    
    // Service selection change handler
    const serviceSelect = document.getElementById('service');
    const selectedServiceInfo = document.getElementById('selectedServiceInfo');
    
    if (serviceSelect && selectedServiceInfo) {
        serviceSelect.addEventListener('change', function() {
            if (this.value) {
                // Fetch service details
                fetch(`/get_service_details?service_id=${this.value}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.service) {
                            // Display service details
                            document.getElementById('serviceTitle').textContent = data.service.name;
                            document.getElementById('serviceDescription').textContent = data.service.description;
                            document.getElementById('serviceDuration').textContent = data.service.duration;
                            document.getElementById('servicePrice').textContent = data.service.price;
                            
                            // Show the service info card
                            selectedServiceInfo.classList.remove('d-none');
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching service details:', error);
                        // Fallback: display basic info from the option
                        const selectedOption = this.options[this.selectedIndex];
                        const price = selectedOption.dataset.price;
                        
                        document.getElementById('serviceTitle').textContent = selectedOption.text.split(' - ')[0];
                        document.getElementById('serviceDescription').textContent = "Detalles no disponibles";
                        document.getElementById('serviceDuration').textContent = "60";
                        document.getElementById('servicePrice').textContent = price;
                        
                        // Show the service info card
                        selectedServiceInfo.classList.remove('d-none');
                    });
            } else {
                // Hide the service info card if no service is selected
                selectedServiceInfo.classList.add('d-none');
            }
        });
        
        // Check URL parameters for pre-selected service
        const urlParams = new URLSearchParams(window.location.search);
        const serviceId = urlParams.get('service');
        
        if (serviceId) {
            serviceSelect.value = serviceId;
            // Trigger the change event to load service details
            serviceSelect.dispatchEvent(new Event('change'));
        }
    }
    
    // Form validation
    const bookingForm = document.getElementById('bookingForm');
    
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(event) {
            if (!this.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            this.classList.add('was-validated');
        });
    }
    
    // Initialize terms modal
    const termsModal = document.getElementById('termsModal');
    
    if (termsModal) {
        const termsCheck = document.getElementById('termsCheck');
        const acceptTermsBtn = termsModal.querySelector('.btn-primary');
        
        // When the user clicks "Entendido" in the modal, check the terms checkbox
        acceptTermsBtn.addEventListener('click', function() {
            termsCheck.checked = true;
        });
    }
    
    // Function to fetch available time slots
    function fetchAvailableTimeSlots(date, locationId) {
        const timeSelect = document.getElementById('time');
        
        // Show loading state
        timeSelect.innerHTML = '<option value="">Cargando horarios disponibles...</option>';
        
        // Fetch available slots from the server
        fetch(`/get_available_slots?date=${date}&location_id=${locationId}`)
            .then(response => response.json())
            .then(data => {
                if (data.slots && data.slots.length > 0) {
                    // Generate options for each available slot
                    let options = '<option value="">Selecciona una hora</option>';
                    
                    data.slots.forEach(slot => {
                        // Format the time for display (e.g., "09:00" to "9:00 AM")
                        const timeObj = new Date(`2000-01-01T${slot}:00`);
                        const formattedTime = timeObj.toLocaleTimeString('es-PR', { 
                            hour: '2-digit', 
                            minute: '2-digit', 
                            hour12: true 
                        });
                        
                        options += `<option value="${slot}">${formattedTime}</option>`;
                    });
                    
                    timeSelect.innerHTML = options;
                } else {
                    // No slots available
                    timeSelect.innerHTML = '<option value="">No hay horarios disponibles</option>';
                }
            })
            .catch(error => {
                console.error('Error fetching available slots:', error);
                timeSelect.innerHTML = '<option value="">Error al cargar horarios</option>';
            });
    }
});
