import React from 'react';

function EmptyState({ title, description }) {
  return (
    <div className="empty-state card">
      <p>
        <strong>{title}</strong>
      </p>
      {description && (
        <p>
          {description}
        </p>
      )}
    </div>
  );
}

export default EmptyState;
