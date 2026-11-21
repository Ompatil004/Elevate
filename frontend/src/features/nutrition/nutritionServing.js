export function getFallbackServing(nameStr, calValue) {
  const cal = calValue || 0;
  const name = (nameStr || '').toLowerCase();
  
  // 1. Eggs
  if (name.includes('egg') || name.includes('anda')) {
    const qty = Math.max(1, Math.round(cal / 70));
    return `${qty} piece${qty > 1 ? 's' : ''} (egg)`;
  }
  
  // 2. Roti / Chapati / Paratha / Naan / Bread
  if (name.includes('roti') || name.includes('chapati') || name.includes('phulka')) {
    const qty = Math.max(1, Math.round(cal / 85));
    return `${qty} piece${qty > 1 ? 's' : ''} (roti)`;
  }
  if (name.includes('paratha') || name.includes('parantha')) {
    const qty = Math.max(1, Math.round(cal / 180));
    return `${qty} piece${qty > 1 ? 's' : ''} (paratha)`;
  }
  if (name.includes('naan')) {
    const qty = Math.max(1, Math.round(cal / 250 * 2) / 2);
    return `${qty} piece${qty > 1 ? 's' : ''} (naan)`;
  }
  if (name.includes('bread') || name.includes('toast')) {
    const qty = Math.max(1, Math.round(cal / 80));
    return `${qty} slice${qty > 1 ? 's' : ''}`;
  }
  
  // 3. Idli / Dosa / Uttapam / Vada
  if (name.includes('idli')) {
    const qty = Math.max(1, Math.round(cal / 65));
    return `${qty} piece${qty > 1 ? 's' : ''}`;
  }
  if (name.includes('dosa')) {
    const qty = Math.max(1, Math.round(cal / 150));
    return `${qty} piece${qty > 1 ? 's' : ''} (dosa)`;
  }
  if (name.includes('vada')) {
    const qty = Math.max(1, Math.round(cal / 100));
    return `${qty} piece${qty > 1 ? 's' : ''}`;
  }
  if (name.includes('uttapam')) {
    const qty = Math.max(1, Math.round(cal / 200 * 2) / 2);
    return `${qty} piece${qty > 1 ? 's' : ''}`;
  }
  
  // 4. Whole fruits
  if (/apple|banana|orange|fruit\s*\(/.test(name)) {
    const qty = Math.max(1, Math.round(cal / 85));
    return `${qty} medium fruit${qty > 1 ? 's' : ''}`;
  }
  
  // 5. Beverages & Liquid Shakes (ml/glass)
  if (/juice|milk|smoothie|drink|shake|lassi|chaas|lemonade/.test(name)) {
    const isRich = /lassi|shake|milk|smoothie/.test(name);
    const baseCalPerGlass = isRich ? 150 : 80;
    const glasses = Math.round((cal / baseCalPerGlass) * 2) / 2;
    if (glasses >= 1) {
      return `${glasses} glass${glasses > 1 ? 'es' : ''} (~${Math.round(glasses * 250)}ml)`;
    }
    return `~${Math.round(cal * 2)}ml`;
  }
  
  // 6. Tea & Coffee
  if (name.includes('tea') || name.includes('coffee') || name.includes('chai')) {
    const cups = Math.round((cal / 60) * 2) / 2;
    return `${Math.max(0.5, cups)} cup${cups > 1 ? 's' : ''}`;
  }
  
  // 7. Dal, Sambar, Kadhi, Soups, Salad, Yogurt, Raita
  if (/dal|sambar|kadhi|soup|shorba|raita|yogurt|curd|salad/.test(name)) {
    const isHeavy = /dal|sambar|kadhi|soup|shorba/.test(name);
    const baseCalPerBowl = isHeavy ? 120 : 70;
    const bowls = Math.round((cal / baseCalPerBowl) * 2) / 2;
    return `${Math.max(0.5, bowls)} bowl${bowls > 1 ? 's' : ''}`;
  }
  
  // 8. Rice, Pulao, Biryani, Noodles, Pasta
  if (/rice|pulao|biryani|noodle|pasta|spaghetti|macaroni|chowmein/.test(name)) {
    const plates = Math.round((cal / 200) * 2) / 2;
    return `${Math.max(0.5, plates)} plate${plates > 1 ? 's' : ''}`;
  }
  
  // 9. Protein Bars
  if (name.includes('bar')) {
    const qty = Math.max(1, Math.round(cal / 200));
    return `${qty} bar${qty > 1 ? 's' : ''}`;
  }
  
  // 10. Nuts & Seeds
  if (/almonds|walnuts|cashew|nuts|seeds/.test(name)) {
    const handfuls = Math.round((cal / 160) * 2) / 2;
    const g = Math.round(cal / 160 * 28);
    if (handfuls >= 1) {
      return `${handfuls} handful${handfuls > 1 ? 's' : ''} (~${g}g)`;
    }
    return `~${g}g`;
  }
  
  // Fallback to Grams
  const g = Math.round((cal / 250) * 200 / 25) * 25;
  return `~${Math.max(50, Math.min(400, g))}g`;
}
