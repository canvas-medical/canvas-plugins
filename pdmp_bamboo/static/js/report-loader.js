/**
 * PDMP Report Loader
 * 
 * Handles PDMP report button interactions, iframe loading, and skeleton loader display.
 */

(function() {
    'use strict';
    
    /**
     * PDMPReportLoader Class
     * Manages report loading state and UI updates
     */
    class PDMPReportLoader {
        constructor(buttonId) {
            this.buttonId = buttonId;
            this.button = null;
            this.isLoading = false;
            this.iframeLoaded = false;
            this.init();
        }
        
        /**
         * Initialize the button and attach event listeners
         */
        init() {
            // Wait for button to be available in DOM
            const tryInit = () => {
                this.button = document.getElementById(this.buttonId);
                if (!this.button) {
                    setTimeout(tryInit, 100);
                    return;
                }
                
                this.attachEventListeners();
            };
            
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', tryInit);
            } else {
                setTimeout(tryInit, 50);
            }
        }
        
        /**
         * Attach click event listener to button
         */
        attachEventListeners() {
            if (!this.button) {
                return;
            }
            
            this.button.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const reportUrl = this.button.getAttribute('data-report-url');
                const patientId = this.button.getAttribute('data-patient-id');
                const practitionerId = this.button.getAttribute('data-practitioner-id');
                const organizationId = this.button.getAttribute('data-organization-id');
                const staffId = this.button.getAttribute('data-staff-id');
                
                this.openReport(reportUrl, patientId, practitionerId, organizationId, staffId);
            };
        }
        
        /**
         * Open PDMP report by loading iframe
         */
        openReport(reportUrl, patientId, practitionerId, organizationId, staffId) {
            if (!this.button) {
                console.error('PDMP: Button not found');
                return;
            }
            
            if (this.isLoading || this.iframeLoaded) {
                return;
            }
            
            this.isLoading = true;
            this.updateButtonState('loading');
            this.injectSkeletonKeyframes();
            this.showSkeletonLoader();
            this.loadIframe(reportUrl, patientId, practitionerId, organizationId, staffId);
        }
        
        /**
         * Update button visual state
         */
        updateButtonState(state) {
            if (!this.button) return;
            
            switch (state) {
                case 'loading':
                    this.button.disabled = true;
                    this.button.className = 'btn pdmp-btn pdmp-btn-loading pdmp-btn-full';
                    this.button.textContent = 'Loading Report...';
                    break;
                case 'loaded':
                    this.button.className = 'btn pdmp-btn pdmp-btn-success pdmp-btn-full';
                    this.button.textContent = 'Report Loaded';
                    this.button.disabled = true;
                    break;
                case 'error':
                    this.button.className = 'btn pdmp-btn pdmp-btn-error pdmp-btn-full';
                    this.button.textContent = 'Error - Retry';
                    this.button.disabled = false;
                    break;
            }
        }
        
        /**
         * Inject CSS keyframes for skeleton animations
         */
        injectSkeletonKeyframes() {
            if (document.querySelector('#skeleton-keyframes')) {
                return;
            }
            
            const style = document.createElement('style');
            style.id = 'skeleton-keyframes';
            style.textContent = `
                @keyframes skeleton-shimmer {
                    0% { background-position: -200% 0; }
                    100% { background-position: 200% 0; }
                }
                @keyframes skeleton-spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
        
        /**
         * Get modal container element
         */
        _getModalContainer() {
            return document.querySelector('[data-modal-content="pdmp-modal"]') ||
                   document.querySelector('[data-modal-content]') ||
                   document.querySelector('.modal-content');
        }
        
        /**
         * Get patient header element
         */
        _getPatientHeader() {
            const container = this._getModalContainer();
            if (!container) return null;
            return container.querySelector('[data-component="patient-header-component"]');
        }
        
        /**
         * Show skeleton loader in modal
         */
        showSkeletonLoader() {
            const modalContainer = this._getModalContainer();
            if (!modalContainer) {
                console.error('PDMP: Modal container not found');
                return;
            }
            
            const patientHeader = this._getPatientHeader();
            const patientHeaderHTML = patientHeader ? patientHeader.outerHTML : '';
            
            const skeletonHTML = `
                <style>
                    @keyframes pdmp-skeleton-shimmer {
                        0% { background-position: -200% 0; }
                        100% { background-position: 200% 0; }
                    }
                    @keyframes pdmp-skeleton-spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
                <div id="pdmp-skeleton-container" class="pdmp-skeleton-container-full">
                    <div class="pdmp-skeleton-box">
                        <div class="pdmp-skeleton-flex">
                            <div class="pdmp-skeleton-spinner"></div>
                            <div class="pdmp-flex-1">
                                <div class="pdmp-skeleton-text-header-lg">Loading PDMP Report...</div>
                                <div class="pdmp-skeleton-text-sub">Please wait while we fetch your prescription monitoring data</div>
                            </div>
                        </div>

                        <div class="pdmp-skeleton-grid-mt">
                            <div class="pdmp-skeleton-line pdmp-skeleton-line-lg"></div>
                            <div class="pdmp-skeleton-line pdmp-skeleton-line-md"></div>
                            <div class="pdmp-skeleton-line pdmp-skeleton-line-xs"></div>
                            <div class="pdmp-skeleton-line pdmp-skeleton-line-md"></div>
                            <div class="pdmp-skeleton-line pdmp-skeleton-line-50"></div>
                        </div>
                    </div>
                </div>
            `;
            
            modalContainer.innerHTML = patientHeaderHTML + skeletonHTML;
        }
        
        /**
         * Load report iframe
         */
        loadIframe(reportUrl, patientId, practitionerId, organizationId, staffId) {
            const reportId = reportUrl.split('/').pop();
            const iframeUrl = '/plugin-io/api/pdmp_bamboo/report-iframe?report_id=' + reportId +
                           '&patient_id=' + patientId +
                           '&practitioner_id=' + practitionerId +
                           '&organization_id=' + organizationId +
                           (staffId ? '&staff_id=' + staffId : '');
            
            const modalContainer = this._getModalContainer();
            if (!modalContainer) {
                console.error('PDMP: Modal container not found');
                this.isLoading = false;
                return;
            }
            
            const patientHeader = this._getPatientHeader();
            const patientHeaderHTML = patientHeader ? patientHeader.outerHTML : '';
            
            const iframeContainer = document.createElement('div');
            iframeContainer.id = 'pdmp-iframe-container';
            iframeContainer.className = 'pdmp-iframe-container-inline';
            
            const iframeElement = document.createElement('iframe');
            iframeElement.id = 'pdmp-report-iframe';
            iframeElement.src = iframeUrl;
            iframeElement.className = 'pdmp-iframe';
            iframeElement.frameBorder = '0';
            iframeElement.allowFullscreen = true;
            iframeElement.sandbox = 'allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox';
            
            iframeContainer.appendChild(iframeElement);
            
            iframeElement.onload = () => {
                if (this.iframeLoaded) {
                    return;
                }
                
                this.iframeLoaded = true;
                
                const skeletonContainer = document.getElementById('pdmp-skeleton-container');
                if (skeletonContainer) {
                    skeletonContainer.style.display = 'none';
                }
                
                iframeContainer.style.display = 'block';
                this.updateButtonState('loaded');
                this.isLoading = false;
            };
            
            iframeElement.onerror = () => {
                console.error('PDMP: Iframe failed to load');
                this.isLoading = false;
                this.iframeLoaded = false;
                this.showError('Failed to load the PDMP report iframe');
                this.updateButtonState('error');
            };
            
            modalContainer.appendChild(iframeContainer);
        }
        
        /**
         * Show error message in modal
         */
        showError(errorMessage) {
            this.isLoading = false;
            this.iframeLoaded = false;
            
            const modalContainer = this._getModalContainer();
            if (!modalContainer) {
                console.error('PDMP: Modal container not found');
                return;
            }
            
            const patientHeader = this._getPatientHeader();
            const patientHeaderHTML = patientHeader ? patientHeader.outerHTML : '';
            
            const errorHTML = `
                <div class="pdmp-padding-content-lg pdmp-modal-content-bg">
                    <div class="pdmp-error-box">
                        <h3 class="pdmp-error-title">
                            <span class="pdmp-icon-md">X</span>
                            Report Loading Error
                        </h3>
                        <p class="pdmp-error-text">Failed to load the full PDMP report:</p>
                        <div class="pdmp-error-code">
                            ` + errorMessage + `
                        </div>
                        <div class="pdmp-info-box">
                            <p class="pdmp-info-text">
                                <strong>What to do next:</strong><br>
                                Please try clicking the "View PDMP Report" button again, or contact support if the problem persists.
                            </p>
                        </div>
                    </div>
                </div>
            `;
            
            modalContainer.innerHTML = patientHeaderHTML + errorHTML;
        }
    }
    
    // Initialize loader when script loads
    window.PDMPReportLoader = new PDMPReportLoader('reportHeaderBtn');
})();

