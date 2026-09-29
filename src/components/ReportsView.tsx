import React, { useState } from 'react';
import { TRANSLATIONS, Language } from '../translations';
import {
  loadCustomers,
  calculateEnrichedTransactions,
  loadItems,
  loadPayments,
  calculateCustomerPerformance,
  getOutstandingBalances,
  getAllCustomerPerformances,
  getTodayDate,
  getCurrentTime,
} from '../storage';

interface Props {
  isDark: boolean;
  language: Language;
}

export const ReportsView: React.FC<Props> = ({ isDark, language }) => {
  const t = (key: string, lang?: Language) => TRANSLATIONS[lang || language]?.[key] || key;

  const cardBg = isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]';
  const textColor = isDark ? 'text-white' : 'text-neutral-900';
  const subText = isDark ? 'text-neutral-400' : 'text-neutral-500';
  const inputBg = isDark ? 'bg-[#2A2A2A] border-[#444444] text-white' : 'bg-white border-neutral-300 text-neutral-900';
  const docBg = isDark ? 'bg-[#181818] border-[#333333] text-neutral-100' : 'bg-white border-neutral-300 text-neutral-900';

  const custs = loadCustomers();
  const txns = calculateEnrichedTransactions();

  const reportTypes = [
    'Customer Report',
    'Credit Transaction Report',
    'Credited Items Report',
    'Payment Report',
    'Outstanding Balance Report',
    'Customer Performance Summary Report',
    'Complete Summary Report',
  ];

  const [reportType, setReportType] = useState('Customer Report');
  const [selectedCustomerId, setSelectedCustomerId] = useState(custs[0]?.customer_id || '');
  const [selectedTxnId, setSelectedTxnId] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [reportLang, setReportLang] = useState<Language>('English');
  const [reportData, setReportData] = useState<any | null>(null);
  const [msg, setMsg] = useState('');

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('');

    if (fromDate && toDate && fromDate > toDate) {
      setMsg('From Date cannot be after To Date');
      return;
    }

    const payload: any = {
      reportType,
      reportLang,
      generatedAt: `${getTodayDate()} ${getCurrentTime()}`,
      customer: null,
      transactions: [],
      items: [],
      payments: [],
      performance: null,
      records: [],
    };

    if (reportType === 'Customer Report') {
      if (!selectedCustomerId) {
        setMsg('Please select a customer');
        return;
      }
      const c = custs.find((cust) => cust.customer_id === selectedCustomerId);
      if (!c) {
        setMsg(t('no_records_report', reportLang));
        return;
      }
      payload.customer = c;

      let cTxns = txns.filter((tx) => tx.customer_id === selectedCustomerId);
      if (fromDate && toDate) {
        cTxns = cTxns.filter((tx) => tx.transaction_date >= fromDate && tx.transaction_date <= toDate);
      }
      payload.transactions = cTxns;

      const cTxnIds = cTxns.map((tx) => tx.transaction_id);
      payload.items = loadItems().filter((i) => cTxnIds.includes(i.transaction_id));

      let cPays = loadPayments().filter((p) => p.customer_id === selectedCustomerId);
      if (fromDate && toDate) {
        cPays = cPays.filter((p) => p.payment_date >= fromDate && p.payment_date <= toDate);
      }
      payload.payments = cPays;
      payload.performance = calculateCustomerPerformance(selectedCustomerId);

    } else if (reportType === 'Credit Transaction Report') {
      let filtered = [...txns];
      if (selectedCustomerId) {
        filtered = filtered.filter((tx) => tx.customer_id === selectedCustomerId);
      }
      if (selectedTxnId) {
        filtered = filtered.filter((tx) => tx.transaction_id === selectedTxnId);
      }
      if (fromDate && toDate) {
        filtered = filtered.filter((tx) => tx.transaction_date >= fromDate && tx.transaction_date <= toDate);
      }
      payload.transactions = filtered;

    } else if (reportType === 'Credited Items Report') {
      let allItems = loadItems();
      if (selectedTxnId) {
        allItems = allItems.filter((i) => i.transaction_id === selectedTxnId);
      }
      if (fromDate && toDate) {
        allItems = allItems.filter((i) => {
          const datePart = i.credited_at.slice(0, 10);
          return datePart >= fromDate && datePart <= toDate;
        });
      }
      payload.items = allItems;

    } else if (reportType === 'Payment Report') {
      let allPays = loadPayments();
      if (selectedCustomerId) {
        allPays = allPays.filter((p) => p.customer_id === selectedCustomerId);
      }
      if (selectedTxnId) {
        allPays = allPays.filter((p) => p.transaction_id === selectedTxnId);
      }
      if (fromDate && toDate) {
        allPays = allPays.filter((p) => p.payment_date >= fromDate && p.payment_date <= toDate);
      }
      payload.payments = allPays;

    } else if (reportType === 'Outstanding Balance Report') {
      let balances = getOutstandingBalances();
      if (selectedCustomerId) {
        balances = balances.filter((b) => b.customer_id === selectedCustomerId);
      }
      payload.records = balances;

    } else if (reportType === 'Customer Performance Summary Report') {
      let perfs = getAllCustomerPerformances();
      if (selectedCustomerId) {
        perfs = perfs.filter((p) => p.customer_id === selectedCustomerId);
      }
      payload.records = perfs;

    } else if (reportType === 'Complete Summary Report') {
      payload.records = custs.map((c) => ({
        customer: c,
        performance: calculateCustomerPerformance(c.customer_id),
      }));
    }

    setReportData(payload);
  };

  const downloadCSV = () => {
    if (!reportData) return;
    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'Nav Durga Super Market - Udhaar Management System\r\n';
    csvContent += `Report Type,${reportData.reportType}\r\n`;
    csvContent += `Generated At,${reportData.generatedAt}\r\n\r\n`;

    if (reportData.records?.length > 0) {
      const keys = Object.keys(reportData.records[0]).filter((k) => typeof reportData.records[0][k] !== 'object');
      csvContent += keys.join(',') + '\r\n';
      reportData.records.forEach((r: any) => {
        csvContent += keys.map((k) => `"${r[k] || ''}"`).join(',') + '\r\n';
      });
    } else if (reportData.transactions?.length > 0) {
      csvContent += 'Transaction ID,Customer Name,Date,Due Date,Total,Paid,Pending,Status\r\n';
      reportData.transactions.forEach((t: any) => {
        csvContent += `"${t.transaction_id}","${t.customer_name || ''}","${t.transaction_date}","${t.due_date}",${t.total_amount},${t.total_paid || 0},${t.pending_amount || 0},"${t.payment_status}"\r\n`;
      });
    } else if (reportData.items?.length > 0) {
      csvContent += 'Item ID,Transaction ID,Item Name,Quantity,Unit Price,Subtotal,Credited At\r\n';
      reportData.items.forEach((i: any) => {
        csvContent += `"${i.item_id}","${i.transaction_id}","${i.item_name}",${i.quantity},${i.unit_price},${i.subtotal},"${i.credited_at}"\r\n`;
      });
    } else if (reportData.payments?.length > 0) {
      csvContent += 'Payment ID,Transaction ID,Customer,Amount,Date,Method,Ref ID\r\n';
      reportData.payments.forEach((p: any) => {
        csvContent += `"${p.payment_id}","${p.transaction_id}","${p.customer_name || p.customer_id}",${p.payment_amount},"${p.payment_date}","${p.payment_method}","${p.reference_id || ''}"\r\n`;
      });
    }

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${reportData.reportType.replace(/\s+/g, '_')}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadPDF = () => {
    if (!reportData) return;
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>${reportData.reportType} - Nav Durga Super Market</title>
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 40px; color: #111; line-height: 1.5; }
            h1 { color: #1565C0; font-size: 20px; text-align: center; margin: 0; }
            h2 { font-size: 14px; text-align: center; margin: 4px 0 16px 0; color: #555; }
            h3 { font-size: 13px; color: #1565C0; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 20px; }
            .meta { text-align: center; font-size: 11px; color: #777; margin-bottom: 20px; }
            .row { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; }
            .item { font-size: 12px; margin-bottom: 4px; }
            hr { border: none; border-top: 1px solid #ddd; margin: 16px 0; }
          </style>
        </head>
        <body>
          <h1>NAV DURGA SUPER MARKET</h1>
          <h2>UDHAAR MANAGEMENT SYSTEM — ${reportData.reportType.toUpperCase()}</h2>
          <div class="meta">Generated: ${reportData.generatedAt} | Language: ${reportData.reportLang}</div>
          <hr />
          ${document.getElementById('report-printable-area')?.innerHTML || ''}
          <script>
            window.onload = function() { window.print(); }
          </script>
        </body>
      </html>
    `;

    printWindow.document.write(html);
    printWindow.document.close();
  };

  return (
    <div className="space-y-6">
      <h2 className={`text-xl font-bold ${textColor}`}>{t('reports')}</h2>

      {/* FILTER PANEL */}
      <div className={`p-6 rounded border ${cardBg}`}>
        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>Report Type</label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                {reportTypes.map((rt) => (
                  <option key={rt} value={rt}>{rt}</option>
                ))}
              </select>
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('customers')}</label>
              <select
                value={selectedCustomerId}
                onChange={(e) => setSelectedCustomerId(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="">All Customers</option>
                {custs.map((c) => (
                  <option key={c.customer_id} value={c.customer_id}>
                    {c.customer_id} - {c.customer_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('credit_transactions')}</label>
              <select
                value={selectedTxnId}
                onChange={(e) => setSelectedTxnId(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="">All Transactions</option>
                {txns.map((tx) => (
                  <option key={tx.transaction_id} value={tx.transaction_id}>
                    {tx.transaction_id} - {tx.customer_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>From Date</label>
              <input
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>To Date</label>
              <input
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>Report Language</label>
              <select
                value={reportLang}
                onChange={(e) => setReportLang(e.target.value as Language)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="English">English</option>
                <option value="Hindi">Hindi (हिंदी)</option>
                <option value="Marathi">Marathi (मराठी)</option>
                <option value="Malwari">Malwari / Rajasthani (मारवाड़ी)</option>
              </select>
            </div>
          </div>

          {msg && <div className="text-xs text-red-500">{msg}</div>}

          <div className="flex flex-wrap gap-3 pt-2">
            <button
              type="submit"
              className="px-5 py-2 rounded text-xs font-semibold bg-[#1565C0] text-white hover:bg-[#0D47A1] transition-colors"
            >
              {t('generate_report', reportLang)}
            </button>
            <button
              type="button"
              onClick={downloadPDF}
              disabled={!reportData}
              className="px-5 py-2 rounded text-xs font-semibold border border-neutral-300 dark:border-neutral-700 text-neutral-800 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 disabled:opacity-50"
            >
              {t('download_pdf', reportLang)}
            </button>
            <button
              type="button"
              onClick={downloadCSV}
              disabled={!reportData}
              className="px-5 py-2 rounded text-xs font-semibold border border-neutral-300 dark:border-neutral-700 text-neutral-800 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 disabled:opacity-50"
            >
              {t('download_csv', reportLang)}
            </button>
          </div>
        </form>
      </div>

      {/* REPORT PREVIEW: VERTICAL PRINTABLE DOCUMENT */}
      <div>
        <h3 className={`text-sm font-bold uppercase tracking-wider mb-2 ${textColor}`}>
          REPORT PREVIEW
        </h3>

        {!reportData ? (
          <div className={`p-8 rounded border text-center text-xs ${cardBg} ${subText}`}>
            Select criteria and click GENERATE REPORT to preview printable document.
          </div>
        ) : (
          <div className={`max-w-2xl mx-auto p-8 rounded border shadow-sm ${docBg}`} id="report-printable-area">
            {/* Header */}
            <div className="text-center pb-4 border-b border-neutral-300 dark:border-neutral-700">
              <h2 className="text-base font-bold text-[#1565C0]">NAV DURGA SUPER MARKET</h2>
              <div className="text-xs font-semibold tracking-wide">UDHAAR MANAGEMENT SYSTEM</div>
              <div className="text-sm font-bold mt-1 uppercase text-neutral-800 dark:text-neutral-100">
                {reportData.reportType}
              </div>
              <div className="text-[11px] text-neutral-500 mt-0.5">
                Generated: {reportData.generatedAt} | Language: {reportData.reportLang}
              </div>
            </div>

            {/* Customer Information */}
            {reportData.customer && (
              <div className="py-4 border-b border-neutral-300 dark:border-neutral-700">
                <div className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">
                  Customer Information
                </div>
                <div className="grid grid-cols-2 gap-y-1 text-xs">
                  <div>Customer ID: <span className="font-mono font-bold">{reportData.customer.customer_id}</span></div>
                  <div>Customer Name: <span className="font-semibold">{reportData.customer.customer_name}</span></div>
                  <div>Mobile: <span className="tabular-nums">{reportData.customer.phone_number}</span></div>
                  <div>Email: <span>{reportData.customer.email || '-'}</span></div>
                  <div className="col-span-2">Address: <span>{reportData.customer.address || '-'}</span></div>
                </div>
              </div>
            )}

            {/* Summary & Performance */}
            {reportData.performance && (
              <div className="py-4 border-b border-neutral-300 dark:border-neutral-700">
                <div className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">
                  Summary & Performance
                </div>
                <div className="grid grid-cols-2 gap-y-1 text-xs">
                  <div>Total Transactions: <span className="font-bold">{reportData.performance.total_transactions}</span></div>
                  <div>Total Credit: <span className="font-bold">₹{reportData.performance.total_credit.toFixed(2)}</span></div>
                  <div>Total Paid: <span className="font-bold text-emerald-600">₹{reportData.performance.total_paid.toFixed(2)}</span></div>
                  <div>Pending Amount: <span className="font-bold text-amber-600">₹{reportData.performance.pending_amount.toFixed(2)}</span></div>
                  <div>Performance %: <span className="font-bold">{reportData.performance.performance_percentage}%</span></div>
                  <div>Status: <span className="font-bold">{reportData.performance.performance_status}</span></div>
                </div>
              </div>
            )}

            {/* Transactions */}
            {reportData.transactions?.length > 0 && (
              <div className="py-4 border-b border-neutral-300 dark:border-neutral-700">
                <div className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">
                  Transactions
                </div>
                <div className="space-y-1 text-xs">
                  {reportData.transactions.map((t_item: any) => (
                    <div key={t_item.transaction_id} className="flex justify-between border-b border-neutral-100 dark:border-neutral-800 py-1">
                      <span>• {t_item.transaction_id} ({t_item.transaction_date})</span>
                      <span className="font-mono">
                        Due: {t_item.due_date} | Total: ₹{t_item.total_amount.toFixed(2)} | Paid: ₹{(t_item.total_paid || 0).toFixed(2)} ({t_item.payment_status})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Credited Items */}
            {reportData.items?.length > 0 && (
              <div className="py-4 border-b border-neutral-300 dark:border-neutral-700">
                <div className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">
                  Credited Items
                </div>
                <div className="space-y-1 text-xs">
                  {reportData.items.map((i_item: any) => (
                    <div key={i_item.item_id} className="flex justify-between border-b border-neutral-100 dark:border-neutral-800 py-1">
                      <span>• {i_item.item_id}: {i_item.item_name} (Qty: {i_item.quantity} × ₹{i_item.unit_price})</span>
                      <span className="font-mono font-medium">₹{i_item.subtotal.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Payments */}
            {reportData.payments?.length > 0 && (
              <div className="py-4 border-b border-neutral-300 dark:border-neutral-700">
                <div className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">
                  Payments
                </div>
                <div className="space-y-1 text-xs">
                  {reportData.payments.map((p_item: any) => (
                    <div key={p_item.payment_id} className="flex justify-between border-b border-neutral-100 dark:border-neutral-800 py-1">
                      <span>• {p_item.payment_id}: {p_item.payment_date} ({p_item.payment_method})</span>
                      <span className="font-mono font-bold text-emerald-600">₹{p_item.payment_amount.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Records */}
            {reportData.records?.length > 0 && (
              <div className="py-4">
                <div className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">
                  Detailed Records
                </div>
                <div className="space-y-1 text-xs">
                  {reportData.records.map((r: any, idx: number) => (
                    <div key={idx} className="flex justify-between border-b border-neutral-100 dark:border-neutral-800 py-1">
                      {r.customer_name && (
                        <span>• {r.customer_id} - {r.customer_name}</span>
                      )}
                      {r.pending_amount !== undefined && (
                        <span className="font-mono font-medium">
                          Due: ₹{r.total_due?.toFixed(2)} | Paid: ₹{r.total_paid?.toFixed(2)} | Pending: ₹{r.pending_amount?.toFixed(2)} ({r.status})
                        </span>
                      )}
                      {r.performance_percentage !== undefined && (
                        <span className="font-mono font-medium">
                          Score: {r.performance_percentage}% ({r.performance_status})
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
