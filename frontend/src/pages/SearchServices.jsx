import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Search, MapPin, Phone, MessageCircle, Tractor, Wrench, Truck, Sparkles, Zap } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const SearchServices = () => {
  const [services, setServices] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [serviceType, setServiceType] = useState('')
  const [location, setLocation] = useState({ lat: null, lng: null })
  const [showSuggestions, setShowSuggestions] = useState(true)
  const [searchMode, setSearchMode] = useState('regular') // 'regular' or 'ai'
  const [aiQuery, setAiQuery] = useState('')
  const [extractedIntent, setExtractedIntent] = useState(null)
  const [summary, setSummary] = useState('')
  const navigate = useNavigate()
  const { user } = useAuth()

  const API_URL = import.meta.env.VITE_API_URL || '/api'

  const serviceTypes = [
    { value: 'tractor', label: 'Tractor', icon: Tractor },
    { value: 'jcb', label: 'JCB', icon: Wrench },
    { value: 'auto', label: 'Auto', icon: Truck },
    { value: 'farm_service', label: 'Farm Service', icon: Tractor },
  ]

  useEffect(() => {
    // Get user location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          })
        },
        (error) => {
          console.error('Error getting location:', error)
        }
      )
    }
  }, [])

  useEffect(() => {
    // Load suggestions when user is available
    if (user && user._id) {
      loadSuggestions()
    }
  }, [user])

  const loadSuggestions = async () => {
    if (!user || !user._id) {
      console.log('User not loaded yet')
      return
    }
    
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_URL}/services/suggestions`, {
        params: {
          userId: user._id
        },
        headers: { Authorization: `Bearer ${token}` }
      })
      // API returns array directly, not wrapped in suggestions object
      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        setSuggestions(response.data)
        setShowSuggestions(true)
      }
    } catch (error) {
      console.error('Error loading suggestions:', error)
      console.error('Error details:', error.response?.data)
    }
  }

  const handleSearch = async () => {
    if (!location.lat || !location.lng) {
      alert('Please allow location access to search services')
      return
    }

    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_URL}/services/search`, {
        params: {
          lat: location.lat,
          lng: location.lng,
          type: serviceType,
          search: searchTerm,
          radius: 50 // 50km radius
        },
        headers: { Authorization: `Bearer ${token}` }
      })
      setServices(response.data || [])
      setShowSuggestions(false) // Hide suggestions after search
      setExtractedIntent(null)
      setSummary('')
    } catch (error) {
      console.error('Search error:', error)
      console.error('Error details:', error.response?.data)
      alert('Failed to search services: ' + (error.response?.data?.message || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleAISearch = async () => {
    if (!location.lat || !location.lng) {
      alert('Please allow location access to search services')
      return
    }

    if (!aiQuery.trim()) {
      alert('Please enter your search query')
      return
    }

    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${API_URL}/services/ai-search`,
        {
          query: aiQuery,
          location: {
            lat: location.lat,
            lng: location.lng
          },
          radius: 50
        },
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          }
        }
      )
      setServices(response.data.results || [])
      setExtractedIntent(response.data.extractedIntent || null)
      setSummary(response.data.summary || '')
      setShowSuggestions(false) // Hide suggestions after search
    } catch (error) {
      console.error('AI Search error:', error)
      console.error('Error details:', error.response?.data)
      alert('Failed to search services: ' + (error.response?.data?.message || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCall = (phone) => {
    window.open(`tel:${phone}`)
  }

  const handleWhatsApp = (phone) => {
    window.open(`https://wa.me/${phone.replace(/\D/g, '')}`)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4 gradient-text">Find Services</h1>
        <p className="text-slate-600 dark:text-slate-400">
          Search for tractors, JCBs, autos, and more near you
        </p>
      </div>

      {/* Search Mode Tabs */}
      <div className="glass-card p-4 mb-6">
        <div className="flex space-x-4">
          <button
            onClick={() => {
              setSearchMode('regular')
              setServices([])
              setExtractedIntent(null)
              setSummary('')
            }}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              searchMode === 'regular'
                ? 'bg-primary-600 text-white'
                : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-600'
            }`}
          >
            <Search className="w-4 h-4" />
            <span>Regular Search</span>
          </button>
          <button
            onClick={() => {
              setSearchMode('ai')
              setServices([])
              setExtractedIntent(null)
              setSummary('')
            }}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              searchMode === 'ai'
                ? 'bg-primary-600 text-white'
                : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-600'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>AI Search</span>
            <span className="text-xs bg-yellow-500 text-white px-2 py-0.5 rounded-full">NEW</span>
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="glass-card p-6 mb-8">
        {searchMode === 'regular' ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search by name, village..."
                  className="glass-input pl-10"
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>

            <div>
              <select
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                className="glass-input"
              >
                <option value="">All Services</option>
                {serviceTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={handleSearch}
              disabled={loading}
              className="glass-button disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <Sparkles className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-primary-500" />
              <textarea
                value={aiQuery}
                onChange={(e) => setAiQuery(e.target.value)}
                placeholder="Describe what you need in natural language...&#10;Example: 'I need a tractor to plow my 5-acre rice field this week. Budget around 500 per hour.'"
                className="glass-input pl-10 min-h-[100px] resize-none"
                rows={3}
              />
            </div>
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-600 dark:text-slate-400">
                💡 AI understands your requirements - just describe what you need!
              </p>
              <button
                onClick={handleAISearch}
                disabled={loading || !aiQuery.trim()}
                className="glass-button disabled:opacity-50 flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <Zap className="w-4 h-4 animate-pulse" />
                    <span>AI Searching...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>AI Search</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* AI Extracted Intent Display */}
      {extractedIntent && (
        <div className="glass-card p-4 mb-6 bg-primary-50 dark:bg-primary-900/20 border-2 border-primary-200 dark:border-primary-800">
          <div className="flex items-center space-x-2 mb-3">
            <Zap className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h3 className="font-semibold text-primary-700 dark:text-primary-300">AI Understood:</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            {extractedIntent.serviceType && (
              <div>
                <span className="text-slate-600 dark:text-slate-400">Service:</span>
                <span className="ml-2 font-medium capitalize">{extractedIntent.serviceType}</span>
              </div>
            )}
            {extractedIntent.purpose && (
              <div>
                <span className="text-slate-600 dark:text-slate-400">Purpose:</span>
                <span className="ml-2 font-medium capitalize">{extractedIntent.purpose}</span>
              </div>
            )}
            {extractedIntent.crop && (
              <div>
                <span className="text-slate-600 dark:text-slate-400">Crop:</span>
                <span className="ml-2 font-medium capitalize">{extractedIntent.crop}</span>
              </div>
            )}
            {extractedIntent.acreage && (
              <div>
                <span className="text-slate-600 dark:text-slate-400">Acreage:</span>
                <span className="ml-2 font-medium">{extractedIntent.acreage} acres</span>
              </div>
            )}
            {extractedIntent.urgency && (
              <div>
                <span className="text-slate-600 dark:text-slate-400">Urgency:</span>
                <span className="ml-2 font-medium capitalize">{extractedIntent.urgency}</span>
              </div>
            )}
            {extractedIntent.budget && (
              <div>
                <span className="text-slate-600 dark:text-slate-400">Budget:</span>
                <span className="ml-2 font-medium">₹{extractedIntent.budget}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI Summary */}
      {summary && (
        <div className="glass-card p-4 mb-6 bg-green-50 dark:bg-green-900/20 border-2 border-green-200 dark:border-green-800">
          <p className="text-sm text-green-800 dark:text-green-200">{summary}</p>
        </div>
      )}

      {/* Auto-Suggestions Section */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold gradient-text">
              💡 Suggested for You (Same Location)
            </h2>
            <button
              onClick={() => setShowSuggestions(false)}
              className="text-sm text-slate-600 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400"
            >
              Hide
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {suggestions.map((service, index) => {
              const IconComponent = serviceTypes.find(t => t.value === service.type)?.icon || Tractor
              return (
                <div
                  key={service._id || index}
                  className="glass-card p-6 border-2 border-primary-500/30 relative"
                >
                  <div className="absolute top-2 right-2">
                    <span className="text-xs px-2 py-1 rounded-full bg-primary-500/20 text-primary-600 dark:text-primary-400">
                      {service.matchType === 'same_location' ? '📍 Same Location' : '🔍 Nearby'}
                    </span>
                  </div>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-lg gradient-bg flex items-center justify-center">
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{service.providerName}</h3>
                        <p className="text-sm text-slate-600 dark:text-slate-400 capitalize">
                          {service.type.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
                      <MapPin className="w-4 h-4 mr-2" />
                      {service.village}, {service.district}
                    </div>
                    <div className="text-xs text-primary-600 dark:text-primary-400 font-semibold">
                      {service.matchText}
                    </div>
                    <div className="text-lg font-bold text-primary-600 dark:text-primary-400">
                      ₹{service.pricePerHour || service.pricePerTrip} / {service.pricePerHour ? 'hour' : 'trip'}
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleCall(service.phone)}
                      className="flex-1 glass-button flex items-center justify-center space-x-2"
                    >
                      <Phone className="w-4 h-4" />
                      <span>Call</span>
                    </button>
                    <button
                      onClick={() => handleWhatsApp(service.phone)}
                      className="flex-1 glass-button flex items-center justify-center space-x-2"
                    >
                      <MessageCircle className="w-4 h-4" />
                      <span>WhatsApp</span>
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Services Grid */}
      {services.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service) => {
            const IconComponent = serviceTypes.find(t => t.value === service.type)?.icon || Tractor
            return (
              <div key={service._id} className="glass-card p-6 hover:scale-105 transition-transform relative">
                {service.relevanceScore && searchMode === 'ai' && (
                  <div className="absolute top-3 right-3">
                    <span className="text-xs px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-700 dark:text-yellow-400 font-semibold">
                      Match: {(service.relevanceScore * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
                
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-lg gradient-bg flex items-center justify-center">
                      <IconComponent className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{service.providerName}</h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400 capitalize">
                        {service.type.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
                    <MapPin className="w-4 h-4 mr-2" />
                    {service.village}, {service.district}
                  </div>
                  {service.distance && (
                    <div className="text-sm text-primary-600 dark:text-primary-400">
                      {service.distance.toFixed(1)} km away
                    </div>
                  )}
                  {service.aiExplanation && (
                    <div className="text-sm text-slate-700 dark:text-slate-300 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg mt-2">
                      <div className="flex items-start space-x-2">
                        <Sparkles className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" />
                        <p className="text-xs">{service.aiExplanation}</p>
                      </div>
                    </div>
                  )}
                  <div className="text-lg font-bold text-primary-600 dark:text-primary-400">
                    ₹{service.pricePerHour || service.pricePerTrip} / {service.pricePerHour ? 'hour' : 'trip'}
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => handleCall(service.phone)}
                    className="flex-1 glass-button flex items-center justify-center space-x-2"
                  >
                    <Phone className="w-4 h-4" />
                    <span>Call</span>
                  </button>
                  <button
                    onClick={() => handleWhatsApp(service.phone)}
                    className="flex-1 glass-button flex items-center justify-center space-x-2"
                  >
                    <MessageCircle className="w-4 h-4" />
                    <span>WhatsApp</span>
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="text-center py-12 glass-card">
          <Search className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <p className="text-slate-600 dark:text-slate-400">
            {loading ? 'Searching for services...' : 'Search for services to see results'}
          </p>
        </div>
      )}
    </div>
  )
}

export default SearchServices

