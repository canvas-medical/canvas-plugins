/* global Fullscript */
// OAuth Configuration
const OAUTH_CONFIG = {
  clientId: 'DlLXo2nPWVM2OqXBICWIUbpvZEU0dnoX-caHtuZzp8A', // Replace with your actual client ID
  redirectUri: window.location.origin + '/application/auth/patient/ZnVsbHNjcmlwdC5hcHBsaWNhdGlvbnMubXlfYXBwbGljYXRpb246TXlBcHBsaWNhdGlvbg', // Redirect back to main app
  authUrl: 'https://us-snd.fullscript.io/oauth/authorize'
}

const fullscriptClient = Fullscript({
  publicKey: 'DlLXo2nPWVM2OqXBICWIUbpvZEU0dnoX-caHtuZzp8A',
  env: 'us-snd'
})

function showError (message) {
  document.getElementById('app').innerHTML =
    '<div style="padding: 20px; font-family: sans-serif; background-color: #e8fae7; text-align: center; line-height: 24px; border: 1px solid #0e5414; border-radius: 4px; color: #469641;">' + message + '</div>'
}

function startOAuthFlow () {
  const authUrl = new URL(OAUTH_CONFIG.authUrl)
  authUrl.searchParams.append('client_id', OAUTH_CONFIG.clientId)
  authUrl.searchParams.append('redirect_uri', OAUTH_CONFIG.redirectUri)
  authUrl.searchParams.append('response_type', 'code')
  authUrl.searchParams.append('state', window.patientKey)

  window.top.location.href = authUrl.toString()
}

async function exchangeToken (oauthCode) {
  const tokenResponse = await fetch('exchange-token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      code: oauthCode,
      redirect_uri: OAUTH_CONFIG.redirectUri
    })
  })

  if (!tokenResponse.ok) {
    const errorData = await tokenResponse.json()
    throw new Error(errorData.error || 'Failed to exchange token')
  }

  return await tokenResponse.json()
}

async function fetchSessionGrant (accessToken) {
  const sessionGrantResponse = await fetch('session-grant', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      access_token: accessToken
    })
  })

  if (!sessionGrantResponse.ok) {
    const errorData = await sessionGrantResponse.json()
    throw new Error(errorData.error || 'Failed to get session grant')
  }

  return await sessionGrantResponse.json()
}

async function getOrCreatePatient (accessToken) {
  const patientResponse = await fetch('get-or-create-patient', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      access_token: accessToken,
      patient_id: window.patientKey
    })
  })

  if (!patientResponse.ok) {
    const errorData = await patientResponse.json()
    console.warn(errorData.error || 'Failed to get or create patient')

    showError('This patient is missing required information.\nPlease add an email address in Canvas, then reopen the Fullscript application to continue.')

    return { id: null }
  }

  return await patientResponse.json()
}

async function handleTreatmentPlanCreated (treatmentPlanEvent) {
  console.log('Handling treatment plan creation...')
  console.log('Treatment Plan Data:', treatmentPlanEvent)

  try {
    const response = await fetch('treatment-plan-created', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
          treatment: treatmentPlanEvent,
          patient_id: window.patientKey,
          note_id: window.noteId
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to process treatment plan')
    }

    const result = await response.json()
    console.log('Treatment plan processed successfully:', result)
  } catch (error) {
    console.error('Error processing treatment plan:', error)
  }
}

const mountFullscriptApp = (sessionGrantToken, fullScriptPatientId) => {
  const config = {
    secretToken: sessionGrantToken,
    entrypoint: 'catalog',
    patient: {
      id: fullScriptPatientId // Use Fullscript patient ID for exact match
    }
  }

  const platformFeature = fullscriptClient.create('platform', config)

  // Listen to treatment plan events
  platformFeature.on('treatmentPlan.activated', (event) => {
    console.log('Treatment plan activated!', event)
    handleTreatmentPlanCreated(event)
  })
  platformFeature.on('patient.selected', (event) => {
    console.log('Patient selected!', event)
  })

  platformFeature.mount('app')
}

async function initializeFullscript (oauthCode) {
  try {
    const exchangeResponse = await exchangeToken(oauthCode)
    const sessionGrantData = await fetchSessionGrant(exchangeResponse.token)
    const fullScriptPatient = await getOrCreatePatient(exchangeResponse.token)

    console.log('Fullscript Patient ID:', fullScriptPatient.id)

    // Only mount if patient was successfully created/retrieved
    if (fullScriptPatient.id) {
      mountFullscriptApp(sessionGrantData.token, fullScriptPatient.id)
    }
    // Error message already shown by getOrCreatePatient
  } catch (error) {
    console.error('Error initializing Fullscript:', error)
    showError('Error loading Fullscript: ' + error.message)
  }
}

async function tryInitializeWithCachedToken () {
  try {
    const exchangeResponse = await exchangeToken(null)
    const sessionGrantData = await fetchSessionGrant(exchangeResponse.token)
    const fullScriptPatient = await getOrCreatePatient(exchangeResponse.token)

    console.log('Fullscript Patient ID:', fullScriptPatient.id)

    // Only mount if patient was successfully created/retrieved
    if (fullScriptPatient.id) {
      mountFullscriptApp(sessionGrantData.token, fullScriptPatient.id)
      return true
    }
    // Error message already shown by getOrCreatePatient
    return false
  } catch (error) {
    console.log('Cached token failed or expired:', error.message)
    return false
  }
}

document.addEventListener('DOMContentLoaded', async function () {
  const code = window.oauthCode

  if (code) {
    // User returned from OAuth, remove button and initialize
    document.getElementById('oauth-button').remove()
    await initializeFullscript(code)
  } else {
    // Try to exchange token with current access token stored on cache (backend)
    // If success, initialize fullscript directly
    // If not, show OAuth button

    const initialized = await tryInitializeWithCachedToken()

    if (!initialized) {
      // Cached token failed, show OAuth button
      console.log('Showing OAuth button for user to connect')
      document.getElementById('oauth-button').style.display = 'flex'
      document.getElementById('oauth-button').addEventListener('click', startOAuthFlow)
    } else {
      // Successfully initialized with cache, hide button
      document.getElementById('oauth-button').remove()
    }
  }
})
