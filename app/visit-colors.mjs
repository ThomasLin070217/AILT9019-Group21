// Fill colors for the city footprint overlays. Indexes match domain.visitTier.
export const REGION_COLORS = ['#167643', '#199751', '#25bf60', '#75de36'];
export const REGION_OPACITY = [0, .54, .66, .78];

export function pulseVisit(element) {
  if (!element || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  element.animate([
    { scale: 1, filter: 'brightness(1)' },
    { scale: 1.32, filter: 'brightness(1.35)', offset: .32 },
    { scale: 1, filter: 'brightness(1)' },
  ], { duration: 440, easing: 'ease-out' });
}
