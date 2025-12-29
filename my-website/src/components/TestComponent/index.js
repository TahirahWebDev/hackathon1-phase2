import React from 'react';

const TestComponent = () => {
  console.log('Test component rendered');
  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      backgroundColor: 'red',
      color: 'white',
      padding: '10px',
      zIndex: 9999,
      fontSize: '12px'
    }}>
      Test Component
    </div>
  );
};

export default TestComponent;