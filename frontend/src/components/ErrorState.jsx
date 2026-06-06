import React from 'react';

function ErrorState({ message = "Wystąpił błąd." }) {
  return (
    <div className="state-box error-box error-message">
      <p>{message}</p>
    </div>
  );
}

export default ErrorState;
