"use strict";
export function createPowerupSVG(type) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 50 50");
  svg.setAttribute("width", "30");
  svg.setAttribute("height", "30");
  const powerupStyles = {
    'invert': { colors: { main: '#FF69B4', glow: '#FF1493' }, icon: 'M25 15 A10 10 0 1 1 25 35 M25 35 L20 30 M25 35 L30 30' },
    'shrink': { colors: { main: '#FF0000', glow: '#8B0000' }, icon: 'M25 25 L35 15 M33 15 L35 15 L35 17 M25 25 L15 15 M17 15 L15 15 L15 17 M25 25 L35 35 M33 35 L35 35 L35 33 M25 25 L15 35 M17 35 L15 35 L15 33' },
    'ice': { colors: { main: '#00FFFF', glow: '#00CED1' },
      paths: [
        { d: 'M25 10 L25 40 M18 14 L32 36 M32 14 L18 36 M20 25 L30 25', fill: 'none', stroke: 'white', width: 3 },
        { d: 'M25 25 m-3,0 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0', fill: 'white', stroke: 'none', width: 0 }
      ]
    },
    'speed': { colors: { main: '#FFD700', glow: '#FFA500' }, icon: 'M30 10 L20 25 L27 25 L17 40 L32 25 L25 25 L35 10', fill: 'white' },
    'flash': { colors: { main: '#FFFF00', glow: '#FFD700' },
      paths: [
        { d: 'M25 10 m-8,0 a8,8 0 1,0 16,0 a8,8 0 1,0 -16,0', fill: 'white', stroke: 'none', width: 0 },
        { d: 'M25 10 L25 17 M25 33 L25 40 M35 25 L42 25 M8 25 L15 25 M32 18 L37 13 M13 37 L18 32 M32 32 L37 37 M13 13 L18 18', fill: 'none', stroke: 'white', width: 3 }
      ]
    },
    'sticky': { colors: { main: '#32CD32', glow: '#228B22' }, icon: 'M25 10 C15 10 15 20 25 20 C35 20 35 10 25 10 M17 20 C17 40 33 40 33 20', fill: 'white' }
  };
  const style = powerupStyles[type] || powerupStyles['speed'];
  const gradient = document.createElementNS("http://www.w3.org/2000/svg", "radialGradient");
  gradient.id = `${type}Glow`;
  const stops = [
    { offset: '0%', color: style.colors.main, opacity: '1' },
    { offset: '100%', color: style.colors.glow, opacity: '0.6' }
  ];
  stops.forEach(stop => {
    const stopEl = document.createElementNS("http://www.w3.org/2000/svg", "stop");
    stopEl.setAttribute("offset", stop.offset);
    stopEl.setAttribute("stop-color", stop.color);
    stopEl.setAttribute("stop-opacity", stop.opacity);
    gradient.appendChild(stopEl);
  });
  svg.appendChild(gradient);
  const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  circle.setAttribute("cx", "25");
  circle.setAttribute("cy", "25");
  circle.setAttribute("r", "20");
  circle.setAttribute("fill", `url(#${type}Glow)`);
  svg.appendChild(circle);
  if (style.paths) {
    style.paths.forEach(pathData => {
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", pathData.d);
      path.setAttribute("stroke", pathData.stroke);
      path.setAttribute("stroke-width", pathData.width);
      path.setAttribute("fill", pathData.fill);
      svg.appendChild(path);
    });
  } else {
    const icon = document.createElementNS("http://www.w3.org/2000/svg", "path");
    icon.setAttribute("d", style.icon);
    icon.setAttribute("stroke", "white");
    icon.setAttribute("stroke-width", "3");
    icon.setAttribute("fill", style.fill || "none");
    svg.appendChild(icon);
  }
  return `data:image/svg+xml;base64,${btoa(new XMLSerializer().serializeToString(svg))}`;
}

export function createBumperSVG() {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 100 100");
  const whiteGradient = document.createElementNS("http://www.w3.org/2000/svg", "radialGradient");
  whiteGradient.id = "whiteOrbGradient";
  whiteGradient.setAttribute("cx", "40%");
  whiteGradient.setAttribute("cy", "40%");
  whiteGradient.setAttribute("r", "60%");
  const whiteStops = [
    { offset: '0%', color: 'white', opacity: '1' },
    { offset: '90%', color: '#e0e0e0', opacity: '1' }
  ];
  whiteStops.forEach(stop => {
    const stopEl = document.createElementNS("http://www.w3.org/2000/svg", "stop");
    stopEl.setAttribute("offset", stop.offset);
    stopEl.setAttribute("stop-color", stop.color);
    stopEl.setAttribute("stop-opacity", stop.opacity);
    whiteGradient.appendChild(stopEl);
  });
  const blueGradient = document.createElementNS("http://www.w3.org/2000/svg", "radialGradient");
  blueGradient.id = "blueRingGradient";
  blueGradient.setAttribute("cx", "50%");
  blueGradient.setAttribute("cy", "50%");
  blueGradient.setAttribute("r", "50%");
  const blueStops = [
    { offset: '0%', color: '#4169E1', opacity: '1' },
    { offset: '100%', color: '#1E90FF', opacity: '1' }
  ];
  blueStops.forEach(stop => {
    const stopEl = document.createElementNS("http://www.w3.org/2000/svg", "stop");
    stopEl.setAttribute("offset", stop.offset);
    stopEl.setAttribute("stop-color", stop.color);
    stopEl.setAttribute("stop-opacity", stop.opacity);
    blueGradient.appendChild(stopEl);
  });
  const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
  defs.appendChild(whiteGradient);
  defs.appendChild(blueGradient);
  svg.appendChild(defs);
  const ringCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  ringCircle.setAttribute("cx", "50");
  ringCircle.setAttribute("cy", "50");
  ringCircle.setAttribute("r", "45");
  ringCircle.setAttribute("fill", "none");
  ringCircle.setAttribute("stroke", "url(#blueRingGradient)");
  ringCircle.setAttribute("stroke-width", "8");
  const whiteOrb = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  whiteOrb.setAttribute("cx", "50");
  whiteOrb.setAttribute("cy", "50");
  whiteOrb.setAttribute("r", "35");
  whiteOrb.setAttribute("fill", "url(#whiteOrbGradient)");
  const highlight = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  highlight.setAttribute("cx", "50");
  highlight.setAttribute("cy", "50");
  highlight.setAttribute("r", "15");
  highlight.setAttribute("fill", "white");
  highlight.setAttribute("opacity", "0.3");
  svg.appendChild(ringCircle);
  svg.appendChild(whiteOrb);
  svg.appendChild(highlight);
  return `data:image/svg+xml;base64,${btoa(new XMLSerializer().serializeToString(svg))}`;
}
