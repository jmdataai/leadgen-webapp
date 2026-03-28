import React, { useState, useEffect } from 'react';
import { Button } from '../components/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/Card';
import Navbar from '../components/Navbar';
import api from '../utils/api';

const History = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await api.get('/api/leads/history');
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteJob = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job?')) return;

    try {
      await api.delete(`/api/leads/job/${jobId}`);
      setJobs(jobs.filter((j) => j.id !== jobId));
    } catch (error) {
      alert('Failed to delete job');
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      completed: 'bg-green-100 text-green-700 border-green-200',
      processing: 'bg-blue-100 text-blue-700 border-blue-200',
      pending: 'bg-yellow-100 text-yellow-700 border-yellow-200',
      failed: 'bg-red-100 text-red-700 border-red-200',
    };

    const icons = {
      completed: '✓',
      processing: '⟳',
      pending: '○',
      failed: '✕',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.pending}`}>
        {icons[status]} {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const filteredJobs = jobs.filter((job) => filter === 'all' || job.status === filter);

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2" data-testid="history-title">Job History</h1>
          <p className="text-gray-600">View and manage all your lead searches</p>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {['all', 'completed', 'processing', 'pending', 'failed'].map((status) => (
            <Button
              key={status}
              variant={filter === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(status)}
              data-testid={`filter-${status}`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
              {status === 'all' ? ` (${jobs.length})` : ` (${jobs.filter((j) => j.status === status).length})`}
            </Button>
          ))}
        </div>

        {/* Jobs List */}
        <div className="space-y-4">
          {loading ? (
            <Card>
              <CardContent className="p-12">
                <div className="text-center">
                  <svg className="animate-spin h-8 w-8 mx-auto text-purple-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <p className="text-gray-500 mt-4">Loading history...</p>
                </div>
              </CardContent>
            </Card>
          ) : filteredJobs.length === 0 ? (
            <Card>
              <CardContent className="p-12">
                <div className="text-center" data-testid="empty-history">
                  <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No jobs found</h3>
                  <p className="text-gray-500">No jobs match your current filter</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            filteredJobs.map((job) => (
              <Card key={job.id} className="hover:shadow-lg transition-shadow" data-testid={`history-job-${job.id}`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold text-gray-900">{job.job_name}</h3>
                        {getStatusBadge(job.status)}
                      </div>
                      <p className="text-sm text-gray-600">
                        {job.search_params.job_titles?.join(', ')} • {job.search_params.locations?.join(', ')}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteJob(job.id)}
                      data-testid={`delete-job-${job.id}`}
                    >
                      <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </Button>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Results</p>
                      <p className="text-lg font-semibold text-gray-900">{job.results_count}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Max Items</p>
                      <p className="text-lg font-semibold text-gray-900">{job.search_params.max_items}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Recipient</p>
                      <p className="text-sm font-medium text-gray-900 truncate">{job.search_params.recipient_email}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Created</p>
                      <p className="text-sm font-medium text-gray-900">{formatDate(job.created_at)}</p>
                    </div>
                  </div>

                  {job.search_params.company && (
                    <div className="mt-3">
                      <span className="text-sm text-gray-600">Company: </span>
                      <span className="text-sm font-medium text-gray-900">{job.search_params.company}</span>
                    </div>
                  )}

                  {job.error_message && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-600">
                        <strong>Error:</strong> {job.error_message}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default History;
