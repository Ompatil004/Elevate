import React from 'react';
import { styles } from './nutritionStyles';

export default function MacroStat({ value, label, color, icon }) {
  return (
    <div style={styles.macroStat} className="macro-stat-hover">
      {icon && <div style={{ fontSize: "20px", marginBottom: "8px" }}>{icon}</div>}
      <div style={{ ...styles.macroValue, color }}>{value}</div>
      <div style={styles.macroLabel}>{label}</div>
    </div>
  );
}
