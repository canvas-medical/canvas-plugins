
    let allProviders = [];
    let allOrders = [];
    let loggedInStaffId = null;
    let providerIdToNameMap = new Map();
    let currentPage = 1;
    let paginationData = null;
    let searchTimeout = null;
    let savedFilters = [];
    let activeFilterId = null;
    const PATIENT_CHART_APPLICATION = btoa("{{patientChartApplication}}")

    // Load saved filters from backend on startup
    async function loadSavedFilters() {
      try {
        const response = await fetch('/plugin-io/api/order_tracking/filters');
        if (!response.ok) {
          throw new Error('Failed to load saved filters');
        }
        const data = await response.json();
        savedFilters = data.filters || [];
        renderSavedFilters();
      } catch (error) {
        console.error('Error loading saved filters:', error);
        savedFilters = [];
        renderSavedFilters();
      }
    }

    // Save filter to backend
    async function saveFilterToBackend(filterData) {
      try {
        const response = await fetch('/plugin-io/api/order_tracking/filter', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(filterData)
        });

        if (!response.ok) {
          throw new Error('Failed to save filter');
        }

        const data = await response.json();
        return data.filter;
      } catch (error) {
        console.error('Error saving filter:', error);
        throw error;
      }
    }

    // Delete filter from backend
    async function deleteFilterFromBackend(filterId) {
      try {
        const response = await fetch(`/plugin-io/api/order_tracking/filter/${filterId}`, {
          method: 'DELETE'
        });

        if (!response.ok) {
          throw new Error('Failed to delete filter');
        }

        return true;
      } catch (error) {
        console.error('Error deleting filter:', error);
        throw error;
      }
    }

    // Get current filter state
    function getCurrentFilterState() {
      const providerDropdown = document.getElementById('provider-dropdown');
      const typeDropdown = document.getElementById('type-dropdown');
      const patientNameInput = document.getElementById('patient-name-filter');
      const dobInput = document.getElementById('patient-dob-filter');
      const sentToInput = document.getElementById('sent-to-filter');
      const dateFromInput = document.getElementById('date-from-filter');
      const dateToInput = document.getElementById('date-to-filter');

      return {
        providers: providerDropdown.getAttribute('data-values').split(',').filter(v => v),
        types: typeDropdown.getAttribute('data-values').split(',').filter(v => v),
        patientName: patientNameInput.value.trim(),
        patientDob: dobInput.value,
        sentTo: sentToInput.value.trim(),
        dateFrom: dateFromInput.value,
        dateTo: dateToInput.value
      };
    }

    // Apply filter state
    function applyFilterState(filterState) {
      // Clear current active state
      activeFilterId = null;

      // Apply provider filters
      const providerDropdown = document.getElementById('provider-dropdown');
      const providerCheckboxes = providerDropdown.querySelectorAll('input[type="checkbox"]');
      const providerAllCheckbox = providerDropdown.querySelector('#provider-all');

      // Reset all provider checkboxes
      providerCheckboxes.forEach(cb => cb.checked = false);

      if (!filterState.providers || filterState.providers.length === 0) {
        providerAllCheckbox.checked = true;
      } else {
        filterState.providers.forEach(provider => {
          const checkbox = Array.from(providerCheckboxes).find(cb => {
            const option = cb.closest('.dropdown-option');
            return option && option.getAttribute('data-value') === provider;
          });
          if (checkbox) checkbox.checked = true;
        });
      }
      updateSelectedDisplay(providerDropdown);

      // Apply type filters
      const typeDropdown = document.getElementById('type-dropdown');
      const typeCheckboxes = typeDropdown.querySelectorAll('input[type="checkbox"]');
      const typeAllCheckbox = typeDropdown.querySelector('#type-all');

      // Reset all type checkboxes
      typeCheckboxes.forEach(cb => cb.checked = false);

      if (!filterState.types || filterState.types.length === 0) {
        typeAllCheckbox.checked = true;
      } else {
        filterState.types.forEach(type => {
          const checkbox = Array.from(typeCheckboxes).find(cb => {
            const option = cb.closest('.dropdown-option');
            return option && option.getAttribute('data-value') === type;
          });
          if (checkbox) checkbox.checked = true;
        });
      }
      updateSelectedDisplay(typeDropdown);

      // Apply text inputs
      document.getElementById('patient-name-filter').value = filterState.patientName || '';
      document.getElementById('patient-dob-filter').value = filterState.patientDob || '';
      document.getElementById('sent-to-filter').value = filterState.sentTo || '';
      document.getElementById('date-from-filter').value = filterState.dateFrom || '';
      document.getElementById('date-to-filter').value = filterState.dateTo || '';

      // Trigger filter change
      handleFilterChange();
    }

    // Check if current state has any active filters
    function hasActiveFilters() {
      const state = getCurrentFilterState();
      return state.providers.length > 0 ||
             state.types.length > 0 ||
             state.patientName ||
             state.patientDob ||
             state.sentTo ||
             state.dateFrom ||
             state.dateTo;
    }

    // Render saved filters
    function renderSavedFilters() {
      const container = document.getElementById('saved-filters-container');
      const saveBtn = document.getElementById('save-current-btn');

      // Update save button state
      saveBtn.disabled = !hasActiveFilters();

      if (savedFilters.length === 0) {
        container.innerHTML = '<span class="no-saved-filters">No saved filters yet</span>';
        return;
      }

      container.innerHTML = savedFilters.map(filter => `
        <div class="saved-filter-pill ${filter.id === activeFilterId ? 'active' : ''}" data-filter-id="${filter.id}">
          <span class="filter-name" title="${filter.name}">${filter.name}</span>
          <span class="remove-filter" data-filter-id="${filter.id}" title="Remove filter">&times;</span>
        </div>
      `).join('');

      // Add event listeners
      container.querySelectorAll('.saved-filter-pill').forEach(pill => {
        const filterId = pill.getAttribute('data-filter-id');

        pill.addEventListener('click', (e) => {
          console.log("###########  clicking the pillll")
          if (e.target.classList.contains('remove-filter')) {
            return; // Let the remove handler handle this
          }
          console.log("############ loading save filter")
          loadSavedFilter(filterId);
        });
      });

      container.querySelectorAll('.remove-filter').forEach(removeBtn => {
        removeBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          const filterId = removeBtn.getAttribute('data-filter-id');
          removeSavedFilter(filterId);
        });
      });
    }

    // Initialize saved filters functionality
    function initializeSavedFilters() {
      const saveBtn = document.getElementById('save-current-btn');
      const modal = document.getElementById('save-filter-modal');
      const nameInput = document.getElementById('filter-name-input');
      const cancelBtn = document.getElementById('cancel-save-btn');
      const confirmBtn = document.getElementById('confirm-save-btn');

      // Save current button
      saveBtn.addEventListener('click', () => {
        if (!hasActiveFilters()) return;

        modal.style.display = 'flex';
        nameInput.value = '';
        nameInput.focus();
      });

      // Cancel save
      cancelBtn.addEventListener('click', () => {
        modal.style.display = 'none';
      });

      // Confirm save
      confirmBtn.addEventListener('click', async () => {
        const name = nameInput.value.trim();
        if (!name) {
          nameInput.focus();
          return;
        }

        // Disable button to prevent double-clicks
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Saving...';

        try {
          await saveCurrentFilter(name);
          modal.style.display = 'none';
        } catch (error) {
          alert('Error saving filter. Please try again.');
        } finally {
          confirmBtn.disabled = false;
          confirmBtn.textContent = 'Save';
        }
      });

      // Enter key in name input
      nameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          confirmBtn.click();
        }
      });

      // Close modal on backdrop click
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.style.display = 'none';
        }
      });

      // Load saved filters on startup
      loadSavedFilters();
    }

    // Save current filter state
    async function saveCurrentFilter(name) {
      const filterState = getCurrentFilterState();
      const filterData = {
        id: `${new Date().getTime()}`,
        name: name,
        filters: filterState
      };

      try {
        const savedFilter = await saveFilterToBackend(filterData);

        // Add to local array
        savedFilters.push(savedFilter);
        renderSavedFilters();
      } catch (error) {
        throw error; // Re-throw to handle in the calling function
      }
    }

    // Load a saved filter
    function loadSavedFilter(filterId) {
      const filter = savedFilters.find(f => f.id === filterId);
      if (!filter) return;

      activeFilterId = filterId;
      applyFilterState(filter.filters);
      renderSavedFilters(); // Re-render to show active state
    }

    // Remove a saved filter
    async function removeSavedFilter(filterId) {
      if (!confirm('Are you sure you want to delete this saved filter?')) {
        return;
      }

      try {
        await deleteFilterFromBackend(filterId);

        // Remove from local array
        savedFilters = savedFilters.filter(f => f.id !== filterId);
        if (activeFilterId === filterId) {
          activeFilterId = null;
        }
        renderSavedFilters();
      } catch (error) {
        alert('Error deleting filter. Please try again.');
      }
    }

    // Filter toggle functionality
    function initializeFilterToggle() {
      const filterToggle = document.getElementById('filter-toggle');
      const filtersContainer = document.getElementById('filters-container');

      if (!filterToggle || !filtersContainer) {
        console.error('Filter toggle elements not found');
        return;
      }

      filterToggle.addEventListener('click', function(e) {
        // Prevent event bubbling
        e.stopPropagation();

        const isExpanded = filtersContainer.classList.contains('expanded');

        if (isExpanded) {
          filtersContainer.classList.remove('expanded');
          filterToggle.classList.remove('expanded');
        } else {
          filtersContainer.classList.add('expanded');
          filterToggle.classList.add('expanded');
        }
      });
    }

    // Function to count and update active filters
    function updateFilterBadge() {
      let activeFilterCount = 0;

      // Check dropdown filters
      const providerDropdown = document.getElementById('provider-dropdown');
      const typeDropdown = document.getElementById('type-dropdown');

      const selectedProviders = providerDropdown.getAttribute('data-values').split(',').filter(v => v);
      const selectedTypes = typeDropdown.getAttribute('data-values').split(',').filter(v => v);

      if (selectedProviders.length > 0) activeFilterCount++;
      if (selectedTypes.length > 0) activeFilterCount++;

      // Check text inputs
      const patientNameInput = document.getElementById('patient-name-filter');
      const sentToInput = document.getElementById('sent-to-filter');
      const dobInput = document.getElementById('patient-dob-filter');
      const dateFromInput = document.getElementById('date-from-filter');
      const dateToInput = document.getElementById('date-to-filter');

      if (patientNameInput.value.trim()) activeFilterCount++;
      if (sentToInput.value.trim()) activeFilterCount++;
      if (dobInput.value) activeFilterCount++;
      if (dateFromInput.value || dateToInput.value) activeFilterCount++;

      // Update badge
      const filterBadge = document.getElementById('filter-badge');

      if (activeFilterCount > 0) {
        filterBadge.textContent = activeFilterCount;
        filterBadge.classList.remove('hidden');
      } else {
        filterBadge.classList.add('hidden');
      }

      // Update save button state
      const saveBtn = document.getElementById('save-current-btn');
      if (saveBtn) {
        saveBtn.disabled = !hasActiveFilters();
      }
    }

    // Custom dropdown functionality
    function initializeDropdowns() {
      const dropdowns = document.querySelectorAll('.filter-dropdown');

      dropdowns.forEach(dropdown => {
        const selectedValue = dropdown.querySelector('.selected-value');
        const options = dropdown.querySelector('.dropdown-options');

        // Toggle dropdown
        selectedValue.addEventListener('click', (e) => {
          e.stopPropagation();

          // Close other dropdowns
          dropdowns.forEach(otherDropdown => {
            if (otherDropdown !== dropdown) {
              otherDropdown.classList.remove('open');
              otherDropdown.querySelector('.dropdown-options').classList.remove('show');
            }
          });

          // Toggle current dropdown
          dropdown.classList.toggle('open');
          options.classList.toggle('show');
        });

        // Handle checkbox changes
        function setupOptionListeners() {
          const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
          const allCheckbox = dropdown.querySelector('input[type="checkbox"][id$="-all"]');

          checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
              e.stopPropagation();

              if (checkbox === allCheckbox) {
                // If "All" is checked, uncheck all others
                if (checkbox.checked) {
                  checkboxes.forEach(cb => {
                    if (cb !== allCheckbox) cb.checked = false;
                  });
                }
              } else {
                // If any specific option is checked, uncheck "All"
                if (checkbox.checked && allCheckbox) {
                  allCheckbox.checked = false;
                }

                // If no specific options are checked, check "All"
                const specificCheckboxes = Array.from(checkboxes).filter(cb => cb !== allCheckbox);
                const anyChecked = specificCheckboxes.some(cb => cb.checked);
                if (!anyChecked && allCheckbox) {
                  allCheckbox.checked = true;
                }
              }

              updateSelectedDisplay(dropdown);
              handleFilterChange();
            });
          });
        }

        setupOptionListeners();
        dropdown.setupOptionListeners = setupOptionListeners;
      });

      // Close dropdowns when clicking outside
      document.addEventListener('click', () => {
        dropdowns.forEach(dropdown => {
          dropdown.classList.remove('open');
          dropdown.querySelector('.dropdown-options').classList.remove('show');
        });
      });
    }

    function updateSelectedDisplay(dropdown) {
      const selectedValue = dropdown.querySelector('.selected-value');
      const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');
      const allCheckbox = dropdown.querySelector('input[type="checkbox"][id$="-all"]');

      // Get selected values (excluding "All")
      const selectedValues = [];
      const selectedLabels = [];

      checkboxes.forEach(checkbox => {
        if (checkbox.checked && checkbox !== allCheckbox) {
          const label = dropdown.querySelector(`label[for="${checkbox.id}"]`);
          if (label) {
            selectedValues.push(checkbox.closest('.dropdown-option').getAttribute('data-value'));
            selectedLabels.push(label.textContent);
          }
        }
      });

      // Update data-values attribute
      dropdown.setAttribute('data-values', selectedValues.join(','));

      // Update display
      selectedValue.innerHTML = '';

      if (selectedLabels.length === 0 || (allCheckbox && allCheckbox.checked)) {
        // Show placeholder
        const placeholder = dropdown.id === 'provider-dropdown' ? 'All Providers' : 'All Types';
        selectedValue.innerHTML = `<span class="placeholder-text">${placeholder}</span>`;
      } else {
        // Show selected tags
        selectedLabels.forEach((label, index) => {
          const tag = document.createElement('span');
          tag.className = 'selected-tag';
          tag.innerHTML = `
            ${label}
            <span class="remove-tag" data-value="${selectedValues[index]}">&times;</span>
          `;
          selectedValue.appendChild(tag);
        });

        // Add event listeners to remove tags
        selectedValue.querySelectorAll('.remove-tag').forEach(removeBtn => {
          removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const valueToRemove = removeBtn.getAttribute('data-value');
            const checkbox = dropdown.querySelector(`input[type="checkbox"][data-value="${valueToRemove}"]`) ||
                           dropdown.querySelector(`.dropdown-option[data-value="${valueToRemove}"] input[type="checkbox"]`);
            if (checkbox) {
              checkbox.checked = false;
              updateSelectedDisplay(dropdown);
              handleFilterChange();
            }
          });
        });
      }
    }

    function initializePatientNameFilter() {
      const patientNameInput = document.getElementById('patient-name-filter');

      patientNameInput.addEventListener('input', (e) => {
        // Clear existing timeout
        if (searchTimeout) {
          clearTimeout(searchTimeout);
        }

        // Set new timeout to debounce the search
        searchTimeout = setTimeout(() => {
          handleFilterChange();
        }, 300); // Wait 300ms after user stops typing
      });

      // Also trigger search on Enter key
      patientNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          if (searchTimeout) {
            clearTimeout(searchTimeout);
          }
          handleFilterChange();
        }
      });
    }

    function initializeDobFilter() {
      const dobInput = document.getElementById('patient-dob-filter');

      dobInput.addEventListener('change', (e) => {
        handleFilterChange();
      });
    }

    function initializeSentToFilter() {
      const sentToInput = document.getElementById('sent-to-filter');

      sentToInput.addEventListener('input', (e) => {
        // Clear existing timeout
        if (searchTimeout) {
          clearTimeout(searchTimeout);
        }

        // Set new timeout to debounce the search
        searchTimeout = setTimeout(() => {
          handleFilterChange();
        }, 300); // Wait 300ms after user stops typing
      });

      // Also trigger search on Enter key
      sentToInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          if (searchTimeout) {
            clearTimeout(searchTimeout);
          }
          handleFilterChange();
        }
      });
    }

    function initializeDateRangeFilter() {
      const dateFromInput = document.getElementById('date-from-filter');
      const dateToInput = document.getElementById('date-to-filter');

      dateFromInput.addEventListener('change', (e) => {
        handleFilterChange();
      });

      dateToInput.addEventListener('change', (e) => {
        handleFilterChange();
      });
    }

    function handleFilterChange() {
      const providerDropdown = document.getElementById('provider-dropdown');
      const typeDropdown = document.getElementById('type-dropdown');
      const patientNameInput = document.getElementById('patient-name-filter');
      const dobInput = document.getElementById('patient-dob-filter');
      const sentToInput = document.getElementById('sent-to-filter');
      const dateFromInput = document.getElementById('date-from-filter');
      const dateToInput = document.getElementById('date-to-filter');

      const selectedProviders = providerDropdown.getAttribute('data-values').split(',').filter(v => v);
      const selectedTypes = typeDropdown.getAttribute('data-values').split(',').filter(v => v);
      const patientName = patientNameInput.value.trim();
      const patientDob = dobInput.value;
      const sentTo = sentToInput.value.trim();
      const dateFrom = dateFromInput.value;
      const dateTo = dateToInput.value;

      // Clear active filter when manually changing filters
      if (activeFilterId) {
        activeFilterId = null;
        renderSavedFilters();
      }

      // Update filter badge
      updateFilterBadge();

      // Get provider IDs from names
      let providerIds = [];
      if (selectedProviders.length > 0) {
        providerIds = selectedProviders.map(providerName => {
          return Array.from(providerIdToNameMap.entries())
            .find(([id, name]) => name === providerName)?.[0];
        }).filter(id => id);
      }

      // Reset to page 1 when filters change
      currentPage = 1;
      fetchOrders(providerIds, selectedTypes, patientName, patientDob, sentTo, dateFrom, dateTo, currentPage);
    }

    async function fetchProviders() {
      try {
        const response = await fetch('/plugin-io/api/order_tracking/providers');
        const data = await response.json();

        loggedInStaffId = data.logged_in_staff_id;

        const providers = data.providers || [];

        // Create maps for providers
        const providerMap = new Map();

        providers.forEach(provider => {
          if (provider.preferred_name && provider.id) {
            providerMap.set(provider.id, provider.preferred_name);
            providerIdToNameMap.set(provider.id, provider.preferred_name);
          }
        });

        allProviders = Array.from(providerMap.values());
        populateProvidersDropdown();
      } catch (error) {
        console.error('Error fetching providers:', error);
      }
    }

    function populateProvidersDropdown() {
      const providerOptions = document.getElementById('provider-options');
      const providerDropdown = document.getElementById('provider-dropdown');

      // Get the logged-in staff member's name if they exist in providers
      const loggedInStaffName = loggedInStaffId ? providerIdToNameMap.get(loggedInStaffId) : null;

      let optionsHTML = `
        <div class="dropdown-option" data-value="">
          <input type="checkbox" id="provider-all" checked>
          <label for="provider-all">All Providers</label>
        </div>
      `;

      allProviders.forEach((provider, index) => {
        const isSelected = loggedInStaffName && provider === loggedInStaffName;
        optionsHTML += `
          <div class="dropdown-option" data-value="${provider}">
            <input type="checkbox" id="provider-${index}" ${isSelected ? 'checked' : ''}>
            <label for="provider-${index}">${provider}</label>
          </div>
        `;
      });

      providerOptions.innerHTML = optionsHTML;

      // Update selected display and trigger filter if logged-in staff should be auto-selected
      if (loggedInStaffName && allProviders.includes(loggedInStaffName)) {
        const allCheckbox = providerDropdown.querySelector('#provider-all');
        if (allCheckbox) allCheckbox.checked = false;

        updateSelectedDisplay(providerDropdown);

        // Fetch orders with their filter applied
        const providerIds = [loggedInStaffId];
        if (providerIds[0]) {
          fetchOrders(providerIds);
        }
      } else {
        updateSelectedDisplay(providerDropdown);
      }

      // Re-setup event listeners for new options
      providerDropdown.setupOptionListeners();

      // Update filter badge after populating
      updateFilterBadge();
    }

    async function fetchOrders(providerIds = [], orderTypes = [], patientName = null, patientDob = null, sentTo = null, dateFrom = null, dateTo = null, page = 1) {
      try {
        currentPage = page;

        // Build query parameters
        const params = new URLSearchParams();

        // Handle multiple provider IDs as comma-separated string
        if (providerIds && providerIds.length > 0) {
          const validProviderIds = providerIds.filter(id => id);
          if (validProviderIds.length > 0) {
            params.append('provider_ids', validProviderIds.join(','));
          }
        }

        // Handle multiple order types as comma-separated string
        if (orderTypes && orderTypes.length > 0) {
          const validOrderTypes = orderTypes.filter(type => type && type !== 'All Types');
          if (validOrderTypes.length > 0) {
            params.append('types', validOrderTypes.join(','));
          }
        }

        if (patientName && patientName.length > 0) {
          params.append('patient_name', patientName);
        }
        if (patientDob && patientDob.length > 0) {
          params.append('patient_dob', patientDob);
        }
        if (sentTo && sentTo.length > 0) {
          params.append('sent_to', sentTo);
        }
        if (dateFrom && dateFrom.length > 0) {
          params.append('date_from', dateFrom);
        }
        if (dateTo && dateTo.length > 0) {
          params.append('date_to', dateTo);
        }
        params.append('page', page);
        params.append('page_size', 20);

        const url = `/plugin-io/api/order_tracking/orders?${params.toString()}`;
        const response = await fetch(url);
        const data = await response.json();

        paginationData = data.pagination;

        // Combine imaging and lab orders
        const imagingOrders = (data.imaging_orders || []).map(order => ({
          ...order,
          type: 'Imaging',
          orderName: order.order || 'Imaging Order',
          patientName: order.patient_name,
          patientId: order.patient_id,
          id: order.id,
          orderingProvider: order.ordering_provider?.preferred_name || 'Unknown Provider',
          orderingProviderId: order.ordering_provider?.id,
          sentTo: order.sent_to || 'Not specified',
          orderedDate: formatDate(order.created_date),
          priority: order.priority || 'Routine',
        }));

        const labOrders = (data.lab_orders || []).map(order => ({
          ...order,
          type: 'Lab',
          orderName: order.order || 'Lab Order',
          patientName: order.patient_name,
          patientId: order.patient_id,
          orderingProvider: order.ordering_provider?.preferred_name || 'Unknown Provider',
          orderingProviderId: order.ordering_provider?.id,
          sentTo: order.sent_to || 'Not specified',
          orderedDate: formatDate(order.created_date),
        }));

        const referralOrders = (data.referrals || []).map(order => ({
          ...order,
          type: 'Referral',
          orderName: order.order || 'Referral',
          patientName: order.patient_name,
          patientId: order.patient_id,
          id: order.id,
          orderingProvider: order.ordering_provider?.preferred_name || 'Unknown Provider',
          orderingProviderId: order.ordering_provider?.id,
          sentTo: order.sent_to || 'Not specified',
          orderedDate: formatDate(order.created_date),
          priority: order.priority || 'Routine',
        }));

        allOrders = [...imagingOrders, ...labOrders, ...referralOrders];
        populateOrdersTable();
        updatePaginationControls();
      } catch (error) {
        console.error('Error fetching orders:', error);
        document.getElementById('orders-accordion').innerHTML = '<div class="section-header">Error loading orders</div>';
      }
    }

    function formatDate(dateString) {
      if (!dateString) return '';
      try {
        return new Date(dateString).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        });
      } catch {
        return dateString;
      }
    }

    function populateOrdersTable() {
      const accordion = document.getElementById('orders-accordion');
      const infoBar = document.getElementById('info-bar');

      if (allOrders.length === 0) {
        accordion.innerHTML = '<div class="section-header">No orders found</div>';
        infoBar.textContent = 'No orders available';
        return;
      }

      const urgentOrders = allOrders.filter(order => order.priority?.toLowerCase() === 'urgent');
      const routineOrders = allOrders.filter(order => order.priority?.toLowerCase() !== 'urgent');

      let html = '';

      // Add table header
      html += `
        <div class="accordion-header-row">
          <div>Patient</div>
          <div>DOB</div>
          <div>Order</div>
          <div>Type</div>
          <div>Provider</div>
          <div>Sent To</div>
          <div>Status</div>
          <div>Date</div>
          <div></div>
        </div>
      `;

      if (urgentOrders.length > 0) {
        html += `<div class="section-header section-header-urgent">⚠ Urgent Orders (${urgentOrders.length})</div>`;
        urgentOrders.forEach(order => {
          html += createOrderAccordionItem(order, true);
        });
      }

      if (routineOrders.length > 0) {
        html += `<div class="section-header text-gray-700">⏱ Routine Orders (${routineOrders.length})</div>`;
        routineOrders.forEach(order => {
          html += createOrderAccordionItem(order, false);
        });
      }

      if (html === '') {
        html = '<div class="section-header">No orders found</div>';
      }

      accordion.innerHTML = html;
      setupAccordionListeners();

      if (paginationData) {
        const start = (paginationData.current_page - 1) * paginationData.page_size + 1;
        const end = Math.min(start + allOrders.length - 1, paginationData.total_count);
        infoBar.textContent = `Showing ${start}-${end} of ${paginationData.total_count} orders (${urgentOrders.length} urgent, ${routineOrders.length} routine)`;
      } else {
        infoBar.textContent = `Showing ${allOrders.length} orders (${urgentOrders.length} urgent, ${routineOrders.length} routine)`;
      }
    }

    function updatePaginationControls() {
      if (!paginationData) {
        document.getElementById('pagination-container').style.display = 'none';
        return;
      }

      document.getElementById('pagination-container').style.display = 'flex';

      // Update pagination info
      document.getElementById('pagination-info').textContent = `Page ${paginationData.current_page} of ${paginationData.total_pages}`;

      // Update prev/next buttons
      document.getElementById('prev-page').disabled = !paginationData.has_previous;
      document.getElementById('next-page').disabled = !paginationData.has_next;

      // Update page numbers
      const pageNumbers = document.getElementById('page-numbers');
      pageNumbers.innerHTML = '';

      const startPage = Math.max(1, paginationData.current_page - 2);
      const endPage = Math.min(paginationData.total_pages, paginationData.current_page + 2);

      for (let i = startPage; i <= endPage; i++) {
        const button = document.createElement('button');
        button.textContent = i;
        button.onclick = () => goToPage(i);
        if (i === paginationData.current_page) {
          button.style.backgroundColor = 'var(--primary)';
          button.style.color = 'white';
        }
        pageNumbers.appendChild(button);
      }
    }

    function goToPage(page) {
      const providerDropdown = document.getElementById('provider-dropdown');
      const typeDropdown = document.getElementById('type-dropdown');
      const patientNameInput = document.getElementById('patient-name-filter');
      const dobInput = document.getElementById('patient-dob-filter');
      const sentToInput = document.getElementById('sent-to-filter');
      const dateFromInput = document.getElementById('date-from-filter');
      const dateToInput = document.getElementById('date-to-filter');

      const selectedProviders = providerDropdown.getAttribute('data-values').split(',').filter(v => v);
      const selectedTypes = typeDropdown.getAttribute('data-values').split(',').filter(v => v);
      const patientName = patientNameInput.value.trim();
      const patientDob = dobInput.value;
      const sentTo = sentToInput.value.trim();
      const dateFrom = dateFromInput.value;
      const dateTo = dateToInput.value;

      // Get provider IDs from names
      let providerIds = [];
      if (selectedProviders.length > 0) {
        providerIds = selectedProviders.map(providerName => {
          return Array.from(providerIdToNameMap.entries())
            .find(([id, name]) => name === providerName)?.[0];
        }).filter(id => id);
      }

      fetchOrders(providerIds, selectedTypes, patientName, patientDob, sentTo, dateFrom, dateTo, page);
    }

    function createOrderAccordionItem(order, isUrgent) {
      const itemClass = isUrgent ? 'bg-red-50' : '';
      const badgeClass = getBadgeClass(order.type);
      const statusBadgeClass = getStatusBadgeClass(order.status);
      const actions = order.actions ? `<button>${order.actions}</button>` : '';
      const orderId = `${order.id}`;
      const headerId = `header-${orderId}`;

      // Check if this is a Lab order
      const isLabOrder = order.type && order.type.toLowerCase() === 'lab';
      const headerClass = isLabOrder ? 'disabled' : '';
      const iconClass = isLabOrder ? 'hidden' : '';

      return `
        <div class="accordion-item ${itemClass}">
          <div class="accordion-header ${headerClass}" id="${headerId}" data-target="${orderId}" data-patient-id="${order.patientId}" data-order-type="${order.type}" data-order-id="${order.id}">
            <div class="column-value"><a href='/patient/${order.patientId}/#application=${PATIENT_CHART_APPLICATION}' target="_top" style="color: var(--primary); cursor: pointer; text-decoration: none;">${order.patientName || ''}</a></div>
            <div class="column-value">${order.dob || ''}</div>
            <div class="column-value">${order.orderName || ''}</div>
            <div class="column-value"><span class="badge ${badgeClass}">${order.type || ''}</span></div>
            <div class="column-value">${order.orderingProvider || ''}</div>
            <div class="column-value">${order.sentTo || ''}</div>
            <div class="column-value"><span class="badge ${statusBadgeClass}">${order.status || 'Open'}</span></div>
            <div class="column-value">${order.orderedDate || ''}</div>
            <div class="expand-icon ${iconClass}">▶</div>
          </div>
          <div class="accordion-content" id="${orderId}">
            <div style="margin-bottom: 1rem;">
              <h4 style="margin: 0 0 0.5rem 0; font-weight: 600;">Task Comments</h4>
              <div id="comments-${orderId}" style="margin-bottom: 1rem; padding: 0.5rem; background-color: #f9fafb; border-radius: 0.375rem; min-height: 60px;">
                Loading comments...
              </div>
              <div style="display: flex; gap: 0.5rem;">
                <input type="text" id="comment-input-${orderId}" placeholder="Add a comment..." style="flex: 1; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem;">
                <button id="add-btn-${orderId}" onclick="addComment('${order.patientId}', '${order.type}', '${order.id}')" style="padding: 0.5rem 1rem; background-color: var(--primary); color: white; border: none; border-radius: 0.375rem; cursor: pointer;">Add</button>

              </div>
            </div>
            ${actions ? `<div>${actions}</div>` : ''}
          </div>
        </div>
      `;
    }

    function getBadgeClass(type) {
      switch(type?.toLowerCase()) {
        case 'lab': return 'badge-outline';
        case 'imaging': return 'badge-outline';
        case 'referral': return 'badge-outline';
        default: return 'badge-outline';
      }
    }

    function getStatusBadgeClass(status) {
      switch(status?.toLowerCase()) {
        case 'open': return 'badge-outline';
        case 'sent': return 'badge-default';
        case 'delegated': return 'badge-secondary';
        default: return 'badge-outline';
      }
    }

    function setupAccordionListeners() {
      // Get all accordion headers and add individual listeners
      const accordionHeaders = document.querySelectorAll('.accordion-header');

      accordionHeaders.forEach(header => {
        const headerId = header.id;
        if (!headerId) return; // Skip if no ID

        // Skip if this is a disabled header (Lab orders)
        if (header.classList.contains('disabled')) {
          return;
        }

        // Create a unique click handler for this specific header
        const clickHandler = function(event) {
          // Allow links to work normally
          if (event.target.tagName === 'A') {
            return; // Don't prevent default for links
          }

          event.preventDefault();
          event.stopPropagation();

          const targetId = this.getAttribute('data-target');
          const content = document.getElementById(targetId);
          const icon = this.querySelector('.expand-icon');

          if (!content || !icon) return;

          // Close all other accordion items first (single open behavior)
          const allHeaders = document.querySelectorAll('.accordion-header');
          allHeaders.forEach(otherHeader => {
            if (otherHeader.id !== headerId) {
              const otherTargetId = otherHeader.getAttribute('data-target');
              const otherContent = document.getElementById(otherTargetId);
              const otherIcon = otherHeader.querySelector('.expand-icon');

              if (otherContent && otherContent.classList.contains('show')) {
                otherContent.classList.remove('show');
                otherHeader.classList.remove('expanded');
                if (otherIcon) otherIcon.classList.remove('rotated');
              }
            }
          });

          // Toggle current accordion item
          const isCurrentlyOpen = content.classList.contains('show');

          if (isCurrentlyOpen) {
            content.classList.remove('show');
            this.classList.remove('expanded');
            icon.classList.remove('rotated');
          } else {
            content.classList.add('show');
            this.classList.add('expanded');
            icon.classList.add('rotated');

            // Get order data from the data attributes
            const patientId = this.getAttribute('data-patient-id');
            const orderType = this.getAttribute('data-order-type');
            const orderId = this.getAttribute('data-order-id');
            loadComments({ patientId, type: orderType, id: orderId });
          }
        };

        // Remove any existing listeners on this header
        header.removeEventListener('click', header._accordionClickHandler);

        // Store the handler reference and add the listener
        header._accordionClickHandler = clickHandler;
        header.addEventListener('click', clickHandler);
      });
    }

    async function loadComments(order) {
      const commentsDiv = document.getElementById(`comments-${order.id}`);
      try {
        let url = `/plugin-io/api/order_tracking/task-comments?order_type=${order.type}`;

        // Add specific ID parameters based on order type
        if (order.type.toLowerCase() === 'referral') {
          url += `&referral_id=${order.id}`;
        } else if (order.type.toLowerCase() === 'imaging') {
          url += `&imaging_id=${order.id}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        // Store task_id for adding comments
        let taskId = null;
        if (data.comments && data.comments.length > 0) {
          taskId = data.comments[0].task_id; // All comments belong to the same task
          commentsDiv.innerHTML = data.comments.map(comment =>
            `<div style="margin-bottom: 0.75rem; padding: 0.75rem; background-color: white; border-radius: 0.5rem; border: 1px solid #e5e7eb; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; padding-bottom: 0.25rem; border-bottom: 1px solid #f3f4f6;">
                <div style="font-weight: 500; color: #374151; font-size: 0.875rem;">${comment.author}</div>
                <div style="font-size: 0.75rem; color: #6b7280;">${comment.date}</div>
              </div>
              <div style="color: #1f2937; line-height: 1.5; white-space: pre-wrap;">${comment.text}</div>
            </div>`
          ).join('');
        } else {
          commentsDiv.innerHTML = '<div style="color: #6b7280; font-style: italic; text-align: center; padding: 2rem;">No comments yet</div>';
        }

        // Store the task_id in a data attribute for the add comment button
        const addButton = document.getElementById(`add-btn-${order.id}`);
        if (addButton && taskId) {
          addButton.setAttribute('data-task-id', taskId);
        }
      } catch (error) {
        console.error('Error loading comments:', error);
        commentsDiv.innerHTML = '<div style="color: #dc2626;">Error loading comments</div>';
      }
    }

    async function addComment(patientId, orderType, orderId) {
      const input = document.getElementById(`comment-input-${orderId}`);
      const comment = input.value.trim();

      if (!comment) return;

      // Get the task_id from the button's data attribute
      const addButton = document.getElementById(`add-btn-${orderId}`);
      const taskId = addButton ? addButton.getAttribute('data-task-id') : null;

      try {
        const response = await fetch('/plugin-io/api/order_tracking/task-comments', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            patient_id: patientId,
            task_id: taskId,
            comment: comment,
            order_type: orderType,
            order_id: orderId
          })
        });

        if (response.ok) {
          input.value = '';
          loadComments({patientId, type: orderType, id: orderId});
        } else {
          console.error('Failed to add comment');
        }
      } catch (error) {
        console.error('Error adding comment:', error);
      }
    }

    document.addEventListener('DOMContentLoaded', async function() {
      // Initialize saved filters
      initializeSavedFilters();

      // Initialize other components
      initializeDropdowns();
      initializePatientNameFilter();
      initializeDobFilter();
      initializeSentToFilter();
      initializeDateRangeFilter();

      // Load data
      await Promise.all([fetchProviders(), fetchOrders()]);
    });

    // Add event listeners for pagination buttons
    document.getElementById('prev-page').addEventListener('click', function() {
      if (paginationData && paginationData.has_previous) {
        goToPage(paginationData.current_page - 1);
      }
    });

    document.getElementById('next-page').addEventListener('click', function() {
      if (paginationData && paginationData.has_next) {
        goToPage(paginationData.current_page + 1);
      }
    });
