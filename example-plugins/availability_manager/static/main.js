// Availability Manager - Vanilla JavaScript

const daysOfWeek = [
  { id: 'MO', label: 'Monday' },
  { id: 'TU', label: 'Tuesday' },
  { id: 'WE', label: 'Wednesday' },
  { id: 'TH', label: 'Thursday' },
  { id: 'FR', label: 'Friday' },
  { id: 'SA', label: 'Saturday' },
  { id: 'SU', label: 'Sunday' }
];

// State
let state = {
  providers: window.providers || [],
  locations: window.locations || [],
  recurrenceTypes: window.recurrence || [],
  noteTypes: window.noteTypes || [],
  calendarTypes: window.calendarTypes || [],
  events: window.events || [],
  showForm: false,
  editingEvent: null,
  currentEvent: {
    id: null,
    title: '',
    provider: null,
    location: null,
    calendarType: null,
    allowedNoteTypes: [],
    startTime: new Date().toISOString().slice(0, 16),
    endTime: new Date().toISOString().slice(0, 16),
    daysOfWeek: [],
    recurrence: {
      type: '',
      interval: 0,
      endDate: ''
    }
  }
};

// Helper functions
function getLocationName(locationId) {
  const location = state.locations.find(l => l.id.toString() === locationId);
  return location ? location.name : '';
}

function getProviderById(id) {
  return state.providers.find(p => p.id === id);
}

// State management
function updateCurrentEvent(field, value) {
  state.currentEvent[field] = value;
}

function toggleProvider(providerId) {
  state.currentEvent.provider = providerId;
}

function toggleNoteType(noteTypeId) {
  const index = state.currentEvent.allowedNoteTypes.indexOf(noteTypeId);
  if (index > -1) {
    state.currentEvent.allowedNoteTypes.splice(index, 1);
  } else {
    state.currentEvent.allowedNoteTypes.push(noteTypeId);
  }
}

function toggleDay(dayId) {
  const index = state.currentEvent.daysOfWeek.indexOf(dayId);
  if (index > -1) {
    state.currentEvent.daysOfWeek.splice(index, 1);
  } else {
    state.currentEvent.daysOfWeek.push(dayId);
  }
  // Update button active state
  const button = document.getElementById(`day-button-${dayId}`);
  if (button) {
    button.classList.toggle('active');
  }
}

function updateRecurrence(field, value) {
  state.currentEvent.recurrence[field] = value;
}

function deleteEvent(eventId) {
  if (window.confirm('Are you sure you want to delete this availability event?')) {

    fetch('/plugin-io/api/availability_manager/events', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ eventId })
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to delete event');

        // TODO: Improve state management after deletion
        state.events = state.events.filter(event => event.id !== eventId);
    }).catch(error => {
      alert('Error deleting event: ' + error.message);
    });

    render();
  }
}

function updateEvent() {
    if (state.currentEvent.recurrence.type === '' && (state.currentEvent.daysOfWeek.length > 0 || state.currentEvent.recurrence.interval !== 0)) {
      alert('Please select a recurrence frequency when days of the week are selected or an interval is set');
      return;
    }

    const event = state.currentEvent;

    const eventData = {
        eventId: event.id,
        title: event.title,
        startTime: event.startTime,
        endTime: event.endTime,
        recurrenceFrequency: event.recurrence.type,
        recurrenceInterval: event.recurrence.interval,
        recurrenceDays: event.daysOfWeek,
        recurrenceEndsAt: event.recurrence.endDate,
        allowedNoteTypes: event.allowedNoteTypes
    }

    fetch('/plugin-io/api/availability_manager/events', {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData)
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to update event');
        // TODO : Improve this logic to update state properly

        // Find the event in state.events and update its values after successful update
        const idx = state.events.findIndex(e => e.id === eventData.eventId);
        if (idx !== -1) {
          state.events[idx] = {
              ...state.events[idx],
              ...eventData,
              ...{allowedNoteTypes: event.allowedNoteTypes},
              ...{daysOfWeek: event.daysOfWeek},
              ...{recurrence: event.recurrence}
          };
          render();
        }
    }).catch(error => {
        alert('Error updating event: ' + error.message);
    });

    resetForm();
}

function saveEvent() {
    if (state.currentEvent.provider === null || state.currentEvent.title === '') {
        alert('Please fill in all required fields, select at least one provider');
        return;
    }

    if (state.currentEvent.recurrence.type === '' && (state.currentEvent.daysOfWeek.length > 0 || state.currentEvent.recurrence.interval !== 0)) {
        alert('Please select a recurrence frequency when days of the week are selected or an interval is set');
        return;
    }

    const event = state.currentEvent;

    const calendarData = {
        provider: state.currentEvent.provider,
        providerName: getProviderById(state.currentEvent.provider).full_name,
        location: state.currentEvent.location || '',
        locationName: getLocationName(state.currentEvent.location),
        type: state.currentEvent.calendarType
    }

    fetch('/plugin-io/api/availability_manager/calendar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(calendarData)
    })
        .then(response => {
            if (!response.ok) throw new Error('Failed to create calendar');
            return response.json();
        })
        .then(data => {
            const {calendarId} = data;

            if (calendarId) {
                const eventData = {
                    calendar: calendarId,
                    title: event.title,
                    startTime: event.startTime,
                    endTime: event.endTime,
                    recurrenceFrequency: event.recurrence.type,
                    recurrenceInterval: event.recurrence.interval,
                    recurrenceDays: event.daysOfWeek,
                    recurrenceEndsAt: event.recurrence.endDate,
                    allowedNoteTypes: event.allowedNoteTypes
                }

                fetch('/plugin-io/api/availability_manager/events', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(eventData)
                })
                    .then(response => {
                        if (!response.ok) throw new Error('Failed to create event');
                    }).catch(error => {
                    alert('Error saving event: ' + error.message);
                });

                resetForm();
            }
        })
        .catch(error => {
            alert('Error saving event: ' + error.message);
        });

    resetForm();
}

function resetForm() {
  state.currentEvent = {
    id: null,
    title: '',
    providers: [],
    location: null,
    calendarType: null,
    allowedNoteTypes: [],
    startTime: new Date().toISOString().slice(0, 16),
    endTime: new Date().toISOString().slice(0, 16),
    daysOfWeek: [],
    recurrence: {
      type: '',
      interval: 0,
      endDate: ''
    }
  };
  state.showForm = false;
  state.editingEvent = null;
  render();
}

function editEvent(event) {
  state.currentEvent = JSON.parse(JSON.stringify(event));
  state.editingEvent = event
  state.showForm = true;
  render();
}

function showForm() {
  state.showForm = true;
  render();
}

// Render functions
function render() {
  const app = document.getElementById('app');

  app.innerHTML = `
    <div class="app-container">
      <div class="max-width-container">
        ${renderHeader()}
        ${state.showForm ? renderFormModal() : ''}
        ${renderEventsList()}
      </div>
    </div>
  `;
}

function renderHeader() {
  return `
    <div class="header">
      <div class="header-content">
        <div>
          <h1 class="header-title">
            📅 Provider Availability Management
          </h1>
          <p class="header-subtitle">Manage clinic schedules and availability events</p>
        </div>
        <button
          onclick="showFormHandler()"
          class="btn btn-primary"
        >
          + New Event
        </button>
      </div>
    </div>
  `;
}

function renderFormModal() {
  return `
    <div class="modal-overlay">
      <div class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2 class="modal-title">
              ${state.editingEvent ? 'Edit' : 'Create'} Availability Event
            </h2>
            <button onclick="resetFormHandler()" class="btn-close">
              ✕
            </button>
          </div>

          <div class="modal-body">
            ${renderEventNameInput()}
            ${renderProvidersSelect()}
            ${renderNoteTypesSelect()}
            ${renderCalendarTypesSelect()}
            ${renderLocationSelect()}
            ${renderWorkingHours()}
            ${renderDaysOfWeek()}
            ${renderRecurrencePattern()}
          </div>

          <div class="modal-footer">
            <button
              onclick="resetFormHandler()"
              class="btn btn-secondary"
            >
              Cancel
            </button>
            ${state.currentEvent.id ? `
                <button
                  onclick="updateEventHandler()"
                  class="btn btn-primary"
                >
                  💾 Update Event
                </button>
            ` : `
                <button
                  onclick="saveEventHandler()"
                  class="btn btn-primary"
                >
                  💾 Save Event
                </button>
            `}
            
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderEventNameInput() {
  return `
    <div class="form-group">
      <label class="form-label">
        Event Name *
      </label>
      <input
        type="text"
        id="template-name"
        value="${state.currentEvent.title}"
        onchange="updateEventNameHandler(this.value)"
        class="form-input"
        placeholder="e.g., Regular Weekday Schedule"
      />
    </div>
  `;
}

function renderProvidersSelect() {
  return `
    <div class="form-group">
      <label class="form-label">
        Assign Provider *
      </label>
      <div class="grid providers-container">
        <select
          id="provider-select"
          onchange="toggleProviderHandler(this.value)"
          class="form-select"
          ${state.currentEvent.id ? 'disabled' : ''}
        >
          <option value="">Select a provider</option>
          ${state.providers.map(provider => `
            <option value="${provider.id}" ${state.currentEvent.provider === provider.id ? 'selected' : ''}>
              ${provider.name}
            </option>
          `).join('')}
        </select>
      </div>
    </div>
  `;
}

function renderNoteTypesSelect() {
  return `
    <div class="form-group">
      <label class="form-label">
        Allowed Note Types
      </label>
      <div class="grid providers-container">
        ${state.noteTypes.map(noteType => `
          <label class="provider-item">
            <input
              type="checkbox"
              ${state.currentEvent.allowedNoteTypes.includes(noteType.id) ? 'checked' : ''}
              onchange="toggleNoteTypeHandler('${noteType.id}')"
              class="provider-checkbox"
            />
            <div class="provider-info">
              <p class="provider-name">${noteType.name}</p>
            </div>
          </label>
        `).join('')}
      </div>
    </div>
  `;
}

function renderLocationSelect() {
  return `
    <div class="form-group">
      <label class="form-label">
        Location
      </label>
      <select
        id="location-select"
        onchange="updateLocationHandler(this.value)"
        class="form-select"
        ${state.currentEvent.id ? 'disabled' : ''}
      >
        <option value="">Select a location</option>
        ${state.locations.map(location => `
          <option value="${location.id}" ${state.currentEvent.location === location.id ? 'selected' : ''}>
            ${location.name}
          </option>
        `).join('')}
      </select>
    </div>
  `;
}

function renderCalendarTypesSelect() {
  return `
    <div class="form-group">
      <label class="form-label">
        Calendar Type
      </label>
      <select
        id="calendar-type-select"
        onchange="updateCalendarTypeHandler(this.value)"
        class="form-select"
        ${state.currentEvent.id ? 'disabled' : ''}
      >
        <option value="">Select a calendar type</option>
        ${state.calendarTypes.map(type => `
          <option value="${type.value}" ${state.currentEvent.calendarType === type.value ? 'selected' : ''}>
            ${type.label}
          </option>
        `).join('')}
      </select>
    </div>
  `;
}

function renderWorkingHours() {
  return `
    <div class="grid grid-cols-2">
      <div class="form-group">
        <label class="form-label">
          Start Time *
        </label>
        <input
          type="datetime-local"
          id="start-time"
          value="${state.currentEvent.startTime}"
          onchange="updateStartTimeHandler(this.value)"
          class="form-input"
        />
      </div>
      <div class="form-group">
        <label class="form-label">
          End Time *
        </label>
        <input
          type="datetime-local"
          id="end-time"
          value="${state.currentEvent.endTime}"
          onchange="updateEndTimeHandler(this.value)"
          class="form-input"
        />
      </div>
    </div>
  `;
}

function renderDaysOfWeek() {
  return `
    <div class="form-group">
      <label class="form-label">
        Days of Week
      </label>
      <div class="grid grid-cols-7">
        ${daysOfWeek.map(day => `
          <button
            id="day-button-${day.id}"
            type="button"
            onclick="toggleDayHandler('${day.id}')"
            class="day-button ${state.currentEvent.daysOfWeek.includes(day.id) ? 'active' : ''}"
          >
            ${day.label}
          </button>
        `).join('')}
      </div>
    </div>
  `;
}

function renderRecurrencePattern() {
  return `
    <div class="form-group">
      <label class="form-label">
        Recurrence Pattern
      </label>
      <div class="grid grid-cols-1-md-3">
        <div>
          <select
            id="recurrence-type"
            onchange="updateRecurrenceTypeHandler(this.value)"
            class="form-select"
          >
            <option value="" ${state.currentEvent.recurrence.type === null || state.currentEvent.recurrence.type === '' ? 'selected' : ''}>
              Select Frequency
            </option>
            ${state.recurrenceTypes.map(type => `
              <option value="${type.value}" ${state.currentEvent.recurrence.type === type.value ? 'selected' : ''}>
                ${type.label}
              </option>
            `).join('')}
          </select>
        </div>
        <div>
          <input
            type="number"
            min="1"
            max="12"
            id="recurrence-interval"
            value="${state.currentEvent.recurrence.interval}"
            onchange="updateRecurrenceIntervalHandler(this.value)"
            class="form-input"
            placeholder="Interval"
          />
        </div>
        <div>
          <input
            type="datetime-local"
            id="recurrence-end-date"
            value="${state.currentEvent.recurrence.endDate}"
            onchange="updateRecurrenceEndDateHandler(this.value)"
            class="form-input"
            placeholder="End date (optional)"
          />
        </div>
      </div>
    </div>
  `;
}

function renderEventsList() {
  return `
    <div class="events-container">
      <div class="events-header">
        <h2 class="events-title">
          Availability Events (${state.events.length})
        </h2>
      </div>

      <div class="events-list">
        ${state.events.map(event => renderEventCard(event)).join('')}
      </div>
    </div>
  `;
}

function renderEventCard(event) {
  return `
    <div class="template-card">
      <div class="template-content">
        <div class="template-info">
          <div class="template-header">
            <h3 class="template-name">${event.title}</h3>
            ${event.recurrence.type && `
              <span class="badge badge-blue">
                ${state.recurrenceTypes.find(t => t.value === event.recurrence.type || '')?.label}
              </span>
            `}
          </div>

          <div class="template-details">
            <div class="detail-item">
              ${event.location !== '' ? `📍 <span>${getLocationName(event.location)}</span>` : ''}
            </div>

            <div class="detail-item">
              🕐 
              <div class="detail-item-times">
                <span>${new Date(event.startTime).toLocaleString('en-US')}</span>
                <span>${new Date(event.endTime).toLocaleString('en-US')}</span>
              </div>
            </div>

            <div class="detail-item">
              ${event.recurrence.endDate && `📅 <span>${new Date(event.recurrence.endDate).toLocaleString('en-US')}</span>`}
            </div>
          </div>

          <div class="template-providers">
            <span class="template-providers-label">Provider: </span>
            <span class="template-providers-list">
              ${event.provider && getProviderById(event.provider).full_name}
            </span>
          </div>
        </div>

        <div class="template-actions">
          <button
            onclick="editEventHandler('${event.id}')"
            class="btn-icon"
            title="Edit Event"
          >
            ✏️
          </button>
          <button
            onclick="deleteEventHandler('${event.id}')"
            class="btn-icon delete"
            title="Delete Event"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  `;
}

// Event handlers (global functions for onclick attributes)
function showFormHandler() {
  showForm();
}

function resetFormHandler() {
  resetForm();
}

function saveEventHandler() {
  saveEvent();
}

function updateEventHandler() {
  updateEvent();
}

function updateEventNameHandler(value) {
  updateCurrentEvent('title', value);
}

function toggleProviderHandler(id) {
  toggleProvider(id);
}

function toggleNoteTypeHandler(id) {
  toggleNoteType(id);
}

function updateLocationHandler(value) {
  updateCurrentEvent('location', value);
}

function updateCalendarTypeHandler(value) {
  updateCurrentEvent('calendarType', value);
}

function updateStartTimeHandler(value) {
  updateCurrentEvent('startTime', value);
}

function updateEndTimeHandler(value) {
  updateCurrentEvent('endTime', value);
}

function toggleDayHandler(dayId) {
  toggleDay(dayId);
}

function updateRecurrenceTypeHandler(value) {
  updateRecurrence('type', value);
}

function updateRecurrenceIntervalHandler(value) {
  updateRecurrence('interval', parseInt(value));
}

function updateRecurrenceEndDateHandler(value) {
  updateRecurrence('endDate', value);
}

function editEventHandler(id) {
  const event = state.events.find(t => t.id === id);
  if (event) {
    editEvent(event);
  }
}

function deleteEventHandler(id) {
  deleteEvent(id);
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
  render();
});