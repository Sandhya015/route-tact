import { useParams } from 'react-router-dom'

const ServiceDetails = () => {
  const { id } = useParams()
  // This would fetch service details by ID
  // For now, just a placeholder
  
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="glass-card p-8">
        <h1 className="text-3xl font-bold mb-4 gradient-text">Service Details</h1>
        <p className="text-slate-600 dark:text-slate-400">
          Service ID: {id}
        </p>
      </div>
    </div>
  )
}

export default ServiceDetails

