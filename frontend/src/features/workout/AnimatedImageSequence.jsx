import React, { useState, useEffect } from 'react';
import { styles } from './workoutStyles';

export default function AnimatedImageSequence({ urls, alt, onError }) {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    if (!urls || urls.length <= 1) return;
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % urls.length);
    }, 1000);
    return () => clearInterval(timer);
  }, [urls]);

  const currentSrc = urls && urls.length > 0 ? urls[index] : '';
  return <img src={currentSrc} alt={alt} style={styles.gifLarge} onError={onError} loading="lazy" />;
}
