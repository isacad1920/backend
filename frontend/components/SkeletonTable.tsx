import React from 'react';
import { Table, TableBody, TableCell, TableRow } from './ui/table';

interface SkeletonTableProps {
  columns: number;
  rows?: number;
  cellClassName?: string;
}

export const SkeletonTable: React.FC<SkeletonTableProps> = ({ columns, rows = 8, cellClassName }) => {
  return (
    <Table>
      <TableBody>
        {Array.from({ length: rows }).map((_, r) => (
          <TableRow key={r} className="border-white/10 animate-pulse">
            {Array.from({ length: columns }).map((__, c) => (
              <TableCell key={c} className={cellClassName || 'py-3'}>
                <div className="h-4 w-full bg-white/10 rounded" />
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
