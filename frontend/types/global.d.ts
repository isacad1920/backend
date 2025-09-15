/// <reference types="vite/client" />

declare module '@tanstack/react-query-devtools' {
  // Minimal type surface we actually use
  import * as React from 'react';
  export interface DevtoolsProps { initialIsOpen?: boolean; position?: string; };
  export const ReactQueryDevtools: React.FC<DevtoolsProps>;
}
