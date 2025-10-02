'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';

interface LifePalLogoProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl';
  animated?: boolean;
  pulse?: boolean;
  variant?: 'default' | 'gradient' | 'simple';
}

export default function LifePalLogo({ 
  size = 'md', 
  animated = false, 
  pulse = false,
  variant = 'simple'
}: LifePalLogoProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  
  // Define size classes
  const sizeMap = {
    xs: { width: 20, height: 20, className: 'w-5 h-5' },
    sm: { width: 28, height: 28, className: 'w-7 h-7' },
    md: { width: 36, height: 36, className: 'w-9 h-9' },
    lg: { width: 48, height: 48, className: 'w-12 h-12' },
    xl: { width: 64, height: 64, className: 'w-16 h-16' },
    '2xl': { width: 80, height: 80, className: 'w-20 h-20' },
    '3xl': { width: 96, height: 96, className: 'w-24 h-24' },
    '4xl': { width: 128, height: 128, className: 'w-32 h-32' }
  };
  
  const sizeConfig = sizeMap[size];
  
  // Animation classes
  const animationClasses = animated ? 'transition-transform hover:scale-110 duration-300' : '';
  const pulseClasses = pulse ? 'animate-pulse' : '';
  
  // Variant styles
  const variantClasses = {
    default: 'bg-gradient-to-br from-primary/20 to-secondary/20 backdrop-blur-sm border border-primary/30 shadow-lg',
    gradient: 'bg-gradient-to-br from-primary/10 to-secondary/10',
    simple: '' // No background, just the logo
  };
  
  // Fade-in effect
  useEffect(() => {
    const timer = setTimeout(() => setIsLoaded(true), 100);
    return () => clearTimeout(timer);
  }, []);
  
  return (
    <div 
      className={`
        ${sizeConfig.className}
        rounded-xl
        flex 
        items-center 
        justify-center 
        ${variantClasses[variant]}
        ${animationClasses} 
        ${pulseClasses}
        transition-opacity duration-500
        ${isLoaded ? 'opacity-100' : 'opacity-0'}
      `}
    >
      <Image 
        src="/LifePal-Main-TransparentBG.png" 
        alt="LifePal" 
        width={sizeConfig.width}
        height={sizeConfig.height}
        className="w-full h-full object-contain p-0.5"
        onLoad={() => setIsLoaded(true)}
      />
    </div>
  );
}
