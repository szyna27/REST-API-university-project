import React from 'react';

function StatusBadge({ status }) {
  const className = `status-badge status-${status.toLowerCase()}`;

  // Tłumaczenie statusów (opcjonalnie)
  const statusTranslations = {
    PENDING: 'Oczekujące',
    COMPLETED: 'Zakończone',
    CANCELLED: 'Anulowane'
  };

  return (
    <span className={className}>
      {statusTranslations[status] || status}
    </span>
  );
}

export default StatusBadge;