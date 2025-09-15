import React from 'react';
import { Button } from './ui/button';

interface ErrorStateProps {
  message?: string | null;
  retry?: () => void;
  colSpan?: number;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ message = 'Something went wrong', retry, colSpan = 1 }) => (
  <tr className="border-white/10">
    <td colSpan={colSpan} className="py-8 text-center text-red-300 text-sm">
      {message}
      {retry && (
        <Button variant="ghost" size="sm" className="ml-2 text-red-200 hover:text-white" onClick={retry}>Retry</Button>
      )}
    </td>
  </tr>
);
