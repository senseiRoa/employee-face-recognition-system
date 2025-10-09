/**
 * Composable for timezone detection and handling
 * Provides utilities for capturing and validating timezone information
 */
import { ref, computed } from 'vue'

export function useTimezone() {
  const currentTimezone = ref('')
  const timezoneOffset = ref('')
  const isTimezoneSupported = ref(true)

  /**
   * Get the device/client timezone using Intl API
   * @returns {string} IANA timezone name or 'UTC' as fallback
   */
  const getDeviceTimezone = () => {
    try {
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
      currentTimezone.value = timezone
      return timezone
    } catch (error) {
      console.warn('Could not detect timezone, using UTC as fallback:', error)
      isTimezoneSupported.value = false
      currentTimezone.value = 'UTC'
      return 'UTC'
    }
  }

  /**
   * Get GMT offset format (e.g., "GMT-05", "GMT+09")
   * @returns {string} GMT offset string
   */
  const getGMTOffset = () => {
    try {
      const offset = new Date().getTimezoneOffset()
      const hours = Math.abs(Math.floor(offset / 60))
      const sign = offset > 0 ? '-' : '+'
      
      const gmtOffset = `GMT${sign}${hours.toString().padStart(2, '0')}`
      timezoneOffset.value = gmtOffset
      return gmtOffset
    } catch (error) {
      console.warn('Could not calculate GMT offset, using UTC:', error)
      timezoneOffset.value = 'UTC'
      return 'UTC'
    }
  }

  /**
   * Validate timezone string format
   * @param {string} timezone - Timezone string to validate
   * @returns {boolean} Whether the timezone is valid
   */
  const validateTimezone = (timezone) => {
    if (!timezone || typeof timezone !== 'string') {
      return false
    }

    const validPatterns = [
      /^UTC$/,                                    // UTC
      /^GMT[+-]\d{1,2}(:\d{2})?$/,               // GMT±H, GMT±HH, GMT±HH:MM
      /^GMT$/,                                    // GMT (equivalent to UTC)
      /^[A-Z]{3,4}$/,                            // EST, PST, etc.
      /^[A-Za-z_]+\/[A-Za-z_]+$/,               // America/New_York
      /^[A-Za-z_]+\/[A-Za-z_]+\/[A-Za-z_]+$/    // America/Argentina/Buenos_Aires
    ]

    return validPatterns.some(pattern => pattern.test(timezone))
  }

  /**
   * Sanitize timezone string with fallback to UTC
   * @param {string} timezone - Timezone string to sanitize
   * @returns {string} Valid timezone string or 'UTC'
   */
  const sanitizeTimezone = (timezone) => {
    if (!timezone || typeof timezone !== 'string') {
      return 'UTC'
    }

    const cleaned = timezone.trim()
    
    if (validateTimezone(cleaned)) {
      return cleaned
    }

    console.warn(`Invalid timezone format: ${timezone}, using UTC as fallback`)
    return 'UTC'
  }

  /**
   * Get timezone with automatic fallback handling
   * @returns {string} GMT format timezone string (e.g., "GMT-05")
   */
  const getTimezoneWithFallback = () => {
    try {
      // Return GMT offset format instead of IANA timezone name
      return getGMTOffset()
    } catch (error) {
      console.warn('Could not detect timezone:', error)
      return 'UTC'
    }
  }

  /**
   * Format timezone for display
   * @param {string} timezone - Timezone string
   * @returns {string} Formatted timezone for display
   */
  const formatTimezoneForDisplay = (timezone = currentTimezone.value) => {
    if (!timezone) return 'Unknown'
    
    // For IANA names, show a more readable format
    if (timezone.includes('/')) {
      const parts = timezone.split('/')
      return parts[parts.length - 1].replace('_', ' ')
    }
    
    return timezone
  }

  /**
   * Get current timezone info object
   * @returns {object} Timezone information
   */
  const getTimezoneInfo = () => {
    const timezone = getTimezoneWithFallback()
    const offset = getGMTOffset()
    
    return {
      timezone,
      offset,
      display: formatTimezoneForDisplay(timezone),
      isSupported: isTimezoneSupported.value
    }
  }

  // Computed properties
  const timezoneInfo = computed(() => getTimezoneInfo())
  const timezoneDisplay = computed(() => formatTimezoneForDisplay())

  // Initialize timezone on composable creation
  getTimezoneWithFallback()
  getGMTOffset()

  return {
    // Reactive refs
    currentTimezone,
    timezoneOffset,
    isTimezoneSupported,
    
    // Computed
    timezoneInfo,
    timezoneDisplay,
    
    // Methods
    getDeviceTimezone,
    getGMTOffset,
    validateTimezone,
    sanitizeTimezone,
    getTimezoneWithFallback,
    formatTimezoneForDisplay,
    getTimezoneInfo
  }
}