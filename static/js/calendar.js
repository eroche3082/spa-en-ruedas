/**
 * Spa en Ruedas - Calendar JavaScript
 * Handles the calendar functionality for events and locations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize FullCalendar
    const calendarElement = document.getElementById('calendar');
    
    if (calendarElement) {
        // Process events data received from the backend
        const events = processEventsData();
        
        // Create calendar
        const calendar = new FullCalendar.Calendar(calendarElement, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,listWeek'
            },
            events: events,
            eventClick: handleEventClick,
            locale: 'es',
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                list: 'Lista'
            },
            firstDay: 1, // Monday as first day of the week
            dayMaxEvents: true, // Allow "more" link when too many events
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                meridiem: 'short'
            },
            themeSystem: 'bootstrap5'
        });
        
        // Render the calendar
        calendar.render();
        
        // Handle window resize to make calendar responsive
        window.addEventListener('resize', function() {
            calendar.updateSize();
        });
    }
    
    // Event modal functionality
    const eventModal = document.getElementById('eventModal');
    
    if (eventModal) {
        eventModal.addEventListener('hidden.bs.modal', function() {
            // Reset modal content when it's closed
            document.getElementById('eventTitle').textContent = '';
            document.getElementById('eventDate').textContent = '';
            document.getElementById('eventLocation').textContent = '';
            document.getElementById('eventDescription').textContent = '';
            document.getElementById('eventBookingLink').href = '#';
        });
    }
    
    // Process event data from the backend
    function processEventsData() {
        // Get the data from the global variables defined in the template
        // eventsData and locationsData should be defined in the template
        const processedEvents = [];
        
        if (typeof eventsData !== 'undefined' && Array.isArray(eventsData)) {
            eventsData.forEach(event => {
                // Find location details for this event
                let locationName = 'Ubicación no especificada';
                
                if (typeof locationsData !== 'undefined' && Array.isArray(locationsData)) {
                    const location = locationsData.find(loc => loc.id === event.location_id);
                    if (location) {
                        locationName = location.name;
                    }
                }
                
                // Create FullCalendar event object
                processedEvents.push({
                    id: event.id,
                    title: event.title,
                    start: event.date, // Assumes event.date is in YYYY-MM-DD format
                    allDay: true,
                    description: event.description,
                    location: locationName,
                    location_id: event.location_id,
                    backgroundColor: '#8e44ad', // Primary color
                    borderColor: '#8e44ad',
                    url: '#', // Will be handled by eventClick instead
                    extendedProps: {
                        location_id: event.location_id
                    }
                });
            });
        }
        
        return processedEvents;
    }
    
    // Handle event click to show details in modal
    function handleEventClick(info) {
        // Prevent the default action (which would navigate to the URL)
        info.jsEvent.preventDefault();
        
        // Get event details
        const event = info.event;
        const title = event.title;
        const date = event.start ? formatDate(event.start) : 'Fecha no especificada';
        const description = event.extendedProps.description || 'Sin descripción';
        const location = event.extendedProps.location || 'Ubicación no especificada';
        
        // Set modal content
        document.getElementById('eventTitle').textContent = title;
        document.getElementById('eventDate').textContent = `Fecha: ${date}`;
        document.getElementById('eventLocation').textContent = `Ubicación: ${location}`;
        document.getElementById('eventDescription').textContent = description;
        
        // Set booking link
        const bookingLink = document.getElementById('eventBookingLink');
        bookingLink.href = `/booking?event=${event.id}`;
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('eventModal'));
        modal.show();
    }
    
    // Helper function to format date
    function formatDate(date) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('es-PR', options);
    }
    
    // Location filtering (if locations filter exists)
    const locationFilter = document.getElementById('locationFilter');
    
    if (locationFilter) {
        locationFilter.addEventListener('change', function() {
            const selectedLocationId = this.value;
            
            // Filter events by location
            if (selectedLocationId) {
                calendar.getEvents().forEach(event => {
                    if (event.extendedProps.location_id === selectedLocationId) {
                        event.setProp('display', 'auto');
                    } else {
                        event.setProp('display', 'none');
                    }
                });
            } else {
                // Show all events if "All Locations" is selected
                calendar.getEvents().forEach(event => {
                    event.setProp('display', 'auto');
                });
            }
        });
    }
    
    // Month navigation shortcuts (if they exist)
    const monthButtons = document.querySelectorAll('.month-button');
    
    if (monthButtons.length > 0) {
        monthButtons.forEach(button => {
            button.addEventListener('click', function() {
                const monthIndex = parseInt(this.dataset.month, 10);
                const year = parseInt(this.dataset.year, 10) || new Date().getFullYear();
                
                // Navigate to the specified month
                calendar.gotoDate(new Date(year, monthIndex, 1));
            });
        });
    }
});
