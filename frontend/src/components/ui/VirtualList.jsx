import React, { useState, useEffect, useRef, useMemo } from 'react';

const VirtualList = ({
  items = [],
  itemHeight = 60,
  containerHeight = 400,
  overscan = 5,
  renderItem,
  className = '',
  ...props
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef(null);

  const totalHeight = items.length * itemHeight;
  const visibleCount = Math.ceil(containerHeight / itemHeight);
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    startIndex + visibleCount + overscan * 2
  );

  const visibleItems = useMemo(() => {
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      ...item,
      index: startIndex + index,
    }));
  }, [items, startIndex, endIndex]);

  const handleScroll = (e) => {
    setScrollTop(e.target.scrollTop);
  };

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);

  return (
    <div
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      {...props}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${startIndex * itemHeight}px)`,
          }}
        >
          {visibleItems.map((item) => (
            <div
              key={item.index}
              style={{
                height: itemHeight,
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
              }}
            >
              {renderItem(item, item.index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default VirtualList;
