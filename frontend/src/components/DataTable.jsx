import React, { useState } from 'react';

// Modern Data Table Component
export const DataTable = ({
  columns,
  data,
  onRowClick = null,
  selectable = false,
  loading = false,
  pagination = true,
  itemsPerPage = 10,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRows, setSelectedRows] = useState(new Set());

  const startIdx = (currentPage - 1) * itemsPerPage;
  const paginatedData = pagination ? data.slice(startIdx, startIdx + itemsPerPage) : data;
  const totalPages = Math.ceil(data.length / itemsPerPage);

  const toggleRow = (rowId) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(rowId)) {
      newSelected.delete(rowId);
    } else {
      newSelected.add(rowId);
    }
    setSelectedRows(newSelected);
  };

  const toggleAllRows = () => {
    if (selectedRows.size === paginatedData.length) {
      setSelectedRows(new Set());
    } else {
      const newSelected = new Set(paginatedData.map((_, i) => i));
      setSelectedRows(newSelected);
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Table Container */}
      <div className="overflow-x-auto rounded-lg border border-slate-200">
        <table className="w-full">
          {/* Table Header */}
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              {selectable && (
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedRows.size === paginatedData.length && paginatedData.length > 0}
                    onChange={toggleAllRows}
                    className="rounded cursor-pointer"
                  />
                </th>
              )}
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wide"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>

          {/* Table Body */}
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length + (selectable ? 1 : 0)} className="px-6 py-8 text-center">
                  <div className="flex justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500" />
                  </div>
                </td>
              </tr>
            ) : paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length + (selectable ? 1 : 0)} className="px-6 py-8 text-center">
                  <div className="text-slate-500">No data available</div>
                </td>
              </tr>
            ) : (
              paginatedData.map((row, rowIdx) => (
                <tr
                  key={rowIdx}
                  onClick={() => onRowClick && onRowClick(row)}
                  className={`border-b border-slate-200 transition-colors ${
                    onRowClick ? 'cursor-pointer hover:bg-slate-50' : ''
                  } ${selectedRows.has(rowIdx) ? 'bg-blue-50' : ''}`}
                >
                  {selectable && (
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedRows.has(rowIdx)}
                        onChange={() => toggleRow(rowIdx)}
                        onClick={(e) => e.stopPropagation()}
                        className="rounded cursor-pointer"
                      />
                    </td>
                  )}
                  {columns.map((col) => (
                    <td key={col.key} className="px-6 py-4 text-sm text-slate-900">
                      {col.render ? col.render(row[col.key], row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-slate-600">
            Showing {startIdx + 1} to {Math.min(startIdx + itemsPerPage, data.length)} of {data.length} results
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Previous
            </button>
            <div className="flex items-center gap-1">
              {[...Array(totalPages)].map((_, i) => (
                <button
                  key={i + 1}
                  onClick={() => setCurrentPage(i + 1)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    currentPage === i + 1
                      ? 'bg-blue-600 text-white'
                      : 'border border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Simplified List Item (for non-table data)
export const ListItem = ({ icon, title, subtitle, action = null, onClick = null }) => (
  <div
    onClick={onClick}
    className={`px-6 py-4 border-b border-slate-200 last:border-b-0 flex items-center justify-between transition-colors ${
      onClick ? 'cursor-pointer hover:bg-slate-50' : ''
    }`}
  >
    <div className="flex items-center gap-4">
      {icon && <div className="text-2xl">{icon}</div>}
      <div>
        <h4 className="font-medium text-slate-900">{title}</h4>
        {subtitle && <p className="text-sm text-slate-600">{subtitle}</p>}
      </div>
    </div>
    {action && <div>{action}</div>}
  </div>
);

export default DataTable;
