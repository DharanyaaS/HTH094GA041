import React from 'react';
import { AlertTriangle, HelpCircle, CheckCircle, Flame, AlertOctagon, ShieldCheck, FileSpreadsheet } from 'lucide-react';

export default function StatsOverview({ summary, activeFilter, onFilterChange }) {
  if (!summary) return null;

  const stats = [
    {
      id: 'all',
      label: 'Total Clauses',
      value: summary.total_clauses || 0,
      icon: FileSpreadsheet,
      colorClass: 'stat-total',
      filterKey: 'ALL'
    },
    {
      id: 'conflicts',
      label: 'Conflicts Detected',
      value: summary.conflicts || 0,
      icon: AlertTriangle,
      colorClass: 'stat-conflict',
      filterKey: 'Conflict'
    },
    {
      id: 'high_risk',
      label: 'High Risk',
      value: summary.high_risk || 0,
      icon: Flame,
      colorClass: 'stat-high-risk',
      filterKey: 'High'
    },
    {
      id: 'not_found',
      label: 'Not Found (Grounded)',
      value: summary.not_found || 0,
      icon: HelpCircle,
      colorClass: 'stat-not-found',
      filterKey: 'Not Found'
    },
    {
      id: 'compliant',
      label: 'Compliant Clauses',
      value: summary.compliant || 0,
      icon: ShieldCheck,
      colorClass: 'stat-compliant',
      filterKey: 'Compliant'
    },
    {
      id: 'medium_risk',
      label: 'Medium Risk',
      value: summary.medium_risk || 0,
      icon: AlertOctagon,
      colorClass: 'stat-med-risk',
      filterKey: 'Medium'
    }
  ];

  return (
    <div className="stats-grid">
      {stats.map((stat) => {
        const Icon = stat.icon;
        const isActive = activeFilter === stat.filterKey;
        return (
          <div
            key={stat.id}
            className={`stat-card ${stat.colorClass} ${isActive ? 'active' : ''}`}
            onClick={() => onFilterChange(stat.filterKey)}
            title={`Filter report by ${stat.label}`}
          >
            <div className="stat-card-header">
              <span className="stat-label">{stat.label}</span>
              <Icon size={18} className="stat-icon" />
            </div>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-footer">
              <span className="stat-hint">{isActive ? '✓ Filtering by this' : 'Click to filter'}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
