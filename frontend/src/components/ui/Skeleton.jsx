import React from 'react';

const Skeleton = ({
  className = '',
  ...props
}) => (
  <div
    className={`skeleton ${className}`}
    {...props}
  />
);

export default Skeleton;
