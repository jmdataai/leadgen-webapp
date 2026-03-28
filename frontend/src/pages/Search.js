import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/Card';
import Navbar from '../components/Navbar';
import api from '../utils/api';

const Search = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    job_name: '',
    job_titles: '',
    locations: '',
    company: '',
    max_items: 10,
    recipient_email: '',
    workplace_type: [],
    employment_type: [],
    experience_level: [],
    under_10_applicants: false,
    easy_apply: false,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const payload = {
        ...formData,
        job_titles: formData.job_titles.split(',').map((s) => s.trim()).filter(Boolean),
        locations: formData.locations.split(',').map((s) => s.trim()).filter(Boolean),
        max_items: parseInt(formData.max_items),
      };

      await api.post('/api/leads/search', payload);
      
      alert('Search job created successfully! You can track its progress in the history page.');
      navigate('/history');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckboxChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter((v) => v !== value)
        : [...prev[field], value],
    }));
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2" data-testid="search-title">New Lead Search</h1>
            <p className="text-gray-600">Configure your lead generation campaign</p>
          </div>

          <Card className="shadow-xl">
            <CardHeader>
              <CardTitle>Search Configuration</CardTitle>
              <CardDescription>Fill in the details to find your ideal leads</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm" data-testid="search-error">
                    {error}
                  </div>
                )}

                {/* Basic Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Basic Information</h3>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Job Name *</label>
                    <Input
                      placeholder="e.g., Software Engineers in San Francisco"
                      value={formData.job_name}
                      onChange={(e) => setFormData({ ...formData, job_name: e.target.value })}
                      required
                      data-testid="job-name-input"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Job Titles *</label>
                    <Input
                      placeholder="e.g., Software Engineer, Developer, Full Stack (comma-separated)"
                      value={formData.job_titles}
                      onChange={(e) => setFormData({ ...formData, job_titles: e.target.value })}
                      required
                      data-testid="job-titles-input"
                    />
                    <p className="text-xs text-gray-500">Separate multiple titles with commas</p>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Locations *</label>
                    <Input
                      placeholder="e.g., San Francisco, New York, Remote (comma-separated)"
                      value={formData.locations}
                      onChange={(e) => setFormData({ ...formData, locations: e.target.value })}
                      required
                      data-testid="locations-input"
                    />
                    <p className="text-xs text-gray-500">Separate multiple locations with commas</p>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Company (Optional)</label>
                    <Input
                      placeholder="e.g., Google, Microsoft"
                      value={formData.company}
                      onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                      data-testid="company-input"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">Max Results *</label>
                      <Input
                        type="number"
                        min="1"
                        max="100"
                        value={formData.max_items}
                        onChange={(e) => setFormData({ ...formData, max_items: e.target.value })}
                        required
                        data-testid="max-items-input"
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">Recipient Email *</label>
                      <Input
                        type="email"
                        placeholder="you@example.com"
                        value={formData.recipient_email}
                        onChange={(e) => setFormData({ ...formData, recipient_email: e.target.value })}
                        required
                        data-testid="recipient-email-input"
                      />
                    </div>
                  </div>
                </div>

                {/* Filters */}
                <div className="space-y-4 pt-6 border-t border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Filters (Optional)</h3>
                  
                  <div className="space-y-3">
                    <label className="text-sm font-medium text-gray-700">Workplace Type</label>
                    <div className="flex flex-wrap gap-3">
                      {['On-site', 'Remote', 'Hybrid'].map((type) => (
                        <label key={type} className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                            checked={formData.workplace_type.includes(type)}
                            onChange={() => handleCheckboxChange('workplace_type', type)}
                            data-testid={`workplace-${type.toLowerCase()}`}
                          />
                          <span className="text-sm text-gray-700">{type}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <label className="text-sm font-medium text-gray-700">Employment Type</label>
                    <div className="flex flex-wrap gap-3">
                      {['Full-time', 'Part-time', 'Contract', 'Internship'].map((type) => (
                        <label key={type} className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                            checked={formData.employment_type.includes(type)}
                            onChange={() => handleCheckboxChange('employment_type', type)}
                            data-testid={`employment-${type.toLowerCase()}`}
                          />
                          <span className="text-sm text-gray-700">{type}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <label className="text-sm font-medium text-gray-700">Experience Level</label>
                    <div className="flex flex-wrap gap-3">
                      {['Entry level', 'Mid-Senior level', 'Director', 'Executive'].map((level) => (
                        <label key={level} className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                            checked={formData.experience_level.includes(level)}
                            onChange={() => handleCheckboxChange('experience_level', level)}
                            data-testid={`experience-${level.toLowerCase().replace(' ', '-')}`}
                          />
                          <span className="text-sm text-gray-700">{level}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <label className="text-sm font-medium text-gray-700">Additional Filters</label>
                    <div className="flex flex-wrap gap-4">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                          checked={formData.under_10_applicants}
                          onChange={(e) => setFormData({ ...formData, under_10_applicants: e.target.checked })}
                          data-testid="under-10-applicants"
                        />
                        <span className="text-sm text-gray-700">Under 10 applicants</span>
                      </label>

                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                          checked={formData.easy_apply}
                          onChange={(e) => setFormData({ ...formData, easy_apply: e.target.checked })}
                          data-testid="easy-apply"
                        />
                        <span className="text-sm text-gray-700">Easy Apply</span>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Submit Button */}
                <div className="flex gap-4 pt-6 border-t border-gray-200">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate('/dashboard')}
                    data-testid="cancel-btn"
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={loading} className="flex-1" data-testid="submit-search-btn">
                    {loading ? (
                      <>
                        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Creating Search...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        Start Search
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Search;
