import React, { useState, useEffect } from 'react';
import { TRANSLATIONS, Language } from '../translations';
import {
  Customer,
  loadCustomers,
  saveCustomers,
  getNextCustomerId,
  getTodayDate,
  getCurrentTime,
  calculateCustomerPerformance,
  getAllCustomerPerformances,
  loadTransactions,
  loadPayments,
  loadItems,
} from '../storage';

interface Props {
  isDark: boolean;
  language: Language;
  view: 'add' | 'view' | 'update' | 'summary' | 'performance';
  selectedCustomerId?: string | null;
  onNavigate: (view: any, customerId?: string) => void;
}

export const CustomerViews: React.FC<Props> = ({
  isDark,
  language,
  view,
  selectedCustomerId,
  onNavigate,
}) => {
  const t = (key: string) => TRANSLATIONS[language]?.[key] || key;

  const cardBg = isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]';
  const textColor = isDark ? 'text-white' : 'text-neutral-900';
  const subText = isDark ? 'text-neutral-400' : 'text-neutral-500';
  const inputBg = isDark ? 'bg-[#2A2A2A] border-[#444444] text-white' : 'bg-white border-neutral-300 text-neutral-900';

  // State for Add Customer
  const [addName, setAddName] = useState('');
  const [addPhone, setAddPhone] = useState('');
  const [addAltPhone, setAddAltPhone] = useState('');
  const [addEmail, setAddEmail] = useState('');
  const [addAddress, setAddAddress] = useState('');
  const [addMsg, setAddMsg] = useState({ type: '', text: '' });
  const [autoCustId, setAutoCustId] = useState(getNextCustomerId());

  // State for Update Customer
  const [updateSelectedId, setUpdateSelectedId] = useState(selectedCustomerId || '');
  const [updateName, setUpdateName] = useState('');
  const [updatePhone, setUpdatePhone] = useState('');
  const [updateAltPhone, setUpdateAltPhone] = useState('');
  const [updateEmail, setUpdateEmail] = useState('');
  const [updateAddress, setUpdateAddress] = useState('');
  const [updateCreatedDate, setUpdateCreatedDate] = useState('');
  const [updateMsg, setUpdateMsg] = useState({ type: '', text: '' });

  // Load customer on select for Update
  const handleLoadCustomer = (idToLoad: string) => {
    if (!idToLoad) return;
    const custs = loadCustomers();
    const found = custs.find((c) => c.customer_id === idToLoad);
    if (found) {
      setUpdateName(found.customer_name);
      setUpdatePhone(found.phone_number);
      setUpdateAltPhone(found.alternate_number || '');
      setUpdateEmail(found.email || '');
      setUpdateAddress(found.address || '');
      setUpdateCreatedDate(found.created_date);
      setUpdateMsg({ type: '', text: '' });
    }
  };

  useEffect(() => {
    if (view === 'update' && selectedCustomerId) {
      setUpdateSelectedId(selectedCustomerId);
      handleLoadCustomer(selectedCustomerId);
    }
  }, [view, selectedCustomerId]);

  const handleSaveAdd = (e: React.FormEvent) => {
    e.preventDefault();
    setAddMsg({ type: '', text: '' });

    if (!addName.trim() || !addPhone.trim()) {
      setAddMsg({ type: 'error', text: t('error_required') });
      return;
    }

    const custs = loadCustomers();
    if (custs.some((c) => c.phone_number === addPhone.trim())) {
      setAddMsg({ type: 'error', text: t('error_unique_phone') });
      return;
    }

    const newCust: Customer = {
      customer_id: autoCustId,
      customer_name: addName.trim(),
      phone_number: addPhone.trim(),
      alternate_number: addAltPhone.trim(),
      email: addEmail.trim(),
      address: addAddress.trim(),
      created_date: getTodayDate(),
      updated_date: getTodayDate(),
      time: getCurrentTime(),
    };

    saveCustomers([...custs, newCust]);
    setAddMsg({ type: 'success', text: t('success_save') });
    setAddName('');
    setAddPhone('');
    setAddAltPhone('');
    setAddEmail('');
    setAddAddress('');
    setAutoCustId(getNextCustomerId());
  };

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    setUpdateMsg({ type: '', text: '' });

    if (!updateSelectedId) {
      setUpdateMsg({ type: 'error', text: 'Please select a customer' });
      return;
    }
    if (!updateName.trim() || !updatePhone.trim()) {
      setUpdateMsg({ type: 'error', text: t('error_required') });
      return;
    }

    const custs = loadCustomers();
    if (custs.some((c) => c.phone_number === updatePhone.trim() && c.customer_id !== updateSelectedId)) {
      setUpdateMsg({ type: 'error', text: t('error_unique_phone') });
      return;
    }

    const updated = custs.map((c) => {
      if (c.customer_id === updateSelectedId) {
        return {
          ...c,
          customer_name: updateName.trim(),
          phone_number: updatePhone.trim(),
          alternate_number: updateAltPhone.trim(),
          email: updateEmail.trim(),
          address: updateAddress.trim(),
          updated_date: getTodayDate(),
          time: getCurrentTime(),
        };
      }
      return c;
    });

    saveCustomers(updated);
    setUpdateMsg({ type: 'success', text: t('success_update') });
  };

  const handleDelete = (customerId: string) => {
    const txns = loadTransactions().filter((t) => t.customer_id === customerId);
    if (txns.length > 0) {
      alert(t('error_delete_restricted'));
      return;
    }
    if (confirm(`Delete customer ${customerId}?`)) {
      const custs = loadCustomers().filter((c) => c.customer_id !== customerId);
      saveCustomers(custs);
      onNavigate('customers_view');
    }
  };

  // ADD CUSTOMER
  if (view === 'add') {
    return (
      <div className="max-w-md">
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>{t('add_customer')}</h2>
        <div className={`p-6 rounded border ${cardBg}`}>
          {addMsg.text && (
            <div className={`mb-4 p-2 text-xs rounded border ${
              addMsg.type === 'error'
                ? 'text-red-600 bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-900'
                : 'text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900'
            }`}>
              {addMsg.text}
            </div>
          )}

          <form onSubmit={handleSaveAdd} className="space-y-3">
            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('customer_id')}</label>
              <input type="text" value={autoCustId} disabled className={`w-full px-3 py-1.5 rounded text-sm border opacity-70 ${inputBg}`} />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('customer_name')} *</label>
              <input
                type="text"
                value={addName}
                onChange={(e) => setAddName(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="Enter customer name"
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('mobile_number')} *</label>
              <input
                type="text"
                value={addPhone}
                onChange={(e) => setAddPhone(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="10-digit mobile number"
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('alternate_number')}</label>
              <input
                type="text"
                value={addAltPhone}
                onChange={(e) => setAddAltPhone(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="Optional secondary number"
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('email')}</label>
              <input
                type="email"
                value={addEmail}
                onChange={(e) => setAddEmail(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="example@mail.com"
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('address')}</label>
              <textarea
                rows={2}
                value={addAddress}
                onChange={(e) => setAddAddress(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="Residential or shop address"
              />
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs text-neutral-400 pt-1">
              <div>Created Date: <span className="font-mono">{getTodayDate()}</span></div>
              <div>Time: <span className="font-mono">{getCurrentTime()}</span></div>
            </div>

            <div className="flex gap-3 pt-3">
              <button
                type="submit"
                className="px-5 py-2 rounded text-xs font-semibold bg-[#1565C0] text-white hover:bg-[#0D47A1] transition-colors"
              >
                {t('save')}
              </button>
              <button
                type="button"
                onClick={() => {
                  setAddName('');
                  setAddPhone('');
                  setAddAltPhone('');
                  setAddEmail('');
                  setAddAddress('');
                  setAddMsg({ type: '', text: '' });
                }}
                className="px-5 py-2 rounded text-xs font-semibold border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800"
              >
                {t('clear')}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // VIEW CUSTOMERS
  if (view === 'view') {
    const custs = loadCustomers();
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className={`text-xl font-bold ${textColor}`}>{t('view_customers')}</h2>
          <button
            onClick={() => onNavigate('customers_add')}
            className="px-3 py-1.5 text-xs font-semibold bg-[#1565C0] text-white rounded hover:bg-[#0D47A1]"
          >
            + {t('add_customer')}
          </button>
        </div>

        <div className={`rounded border overflow-hidden ${cardBg}`}>
          {custs.length === 0 ? (
            <div className={`p-8 text-center text-sm ${subText}`}>{t('no_results')}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className={`${isDark ? 'bg-[#252525] text-neutral-300' : 'bg-neutral-50 text-neutral-600'}`}>
                  <tr>
                    <th className="px-4 py-2.5 font-semibold">{t('customer_id')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('customer_name')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('mobile_number')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('email')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('customer_performance')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 dark:divide-[#333333]">
                  {custs.map((c) => {
                    const perf = calculateCustomerPerformance(c.customer_id);
                    return (
                      <tr key={c.customer_id} className="hover:bg-neutral-50 dark:hover:bg-[#252525]">
                        <td className="px-4 py-2.5">
                          <button
                            onClick={() => onNavigate('customer_summary', c.customer_id)}
                            className="font-bold text-[#1565C0] hover:underline"
                          >
                            {c.customer_id}
                          </button>
                        </td>
                        <td className={`px-4 py-2.5 font-medium ${textColor}`}>{c.customer_name}</td>
                        <td className={`px-4 py-2.5 tabular-nums ${textColor}`}>{c.phone_number}</td>
                        <td className={`px-4 py-2.5 ${subText}`}>{c.email || '-'}</td>
                        <td className="px-4 py-2.5 font-medium">
                          <span className={
                            perf.performance_status === 'Excellent' ? 'text-emerald-600' :
                            perf.performance_status === 'Good' ? 'text-[#1565C0]' :
                            perf.performance_status === 'Average' ? 'text-amber-600' : 'text-red-600'
                          }>
                            {t(perf.performance_status.toLowerCase())} ({perf.performance_percentage}%)
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-right space-x-2">
                          <button
                            onClick={() => onNavigate('customers_update', c.customer_id)}
                            className="text-xs text-[#1565C0] hover:underline"
                          >
                            {t('update')}
                          </button>
                          <button
                            onClick={() => handleDelete(c.customer_id)}
                            className="text-xs text-red-600 hover:underline"
                          >
                            {t('delete')}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    );
  }

  // UPDATE CUSTOMER
  if (view === 'update') {
    const custs = loadCustomers();
    return (
      <div className="max-w-md">
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>{t('update_customer')}</h2>
        <div className={`p-6 rounded border ${cardBg}`}>
          {updateMsg.text && (
            <div className={`mb-4 p-2 text-xs rounded border ${
              updateMsg.type === 'error'
                ? 'text-red-600 bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-900'
                : 'text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900'
            }`}>
              {updateMsg.text}
            </div>
          )}

          <div className="mb-4">
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('customer_id')}</label>
            <div className="flex gap-2">
              <select
                value={updateSelectedId}
                onChange={(e) => {
                  setUpdateSelectedId(e.target.value);
                  handleLoadCustomer(e.target.value);
                }}
                className={`flex-1 px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="">-- Select Customer --</option>
                {custs.map((c) => (
                  <option key={c.customer_id} value={c.customer_id}>
                    {c.customer_id} - {c.customer_name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => handleLoadCustomer(updateSelectedId)}
                className="px-3 py-1.5 rounded text-xs font-semibold bg-[#1565C0] text-white hover:bg-[#0D47A1]"
              >
                {t('load')}
              </button>
            </div>
          </div>

          <form onSubmit={handleUpdate} className="space-y-3">
            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('customer_name')} *</label>
              <input
                type="text"
                value={updateName}
                onChange={(e) => setUpdateName(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('mobile_number')} *</label>
              <input
                type="text"
                value={updatePhone}
                onChange={(e) => setUpdatePhone(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('alternate_number')}</label>
              <input
                type="text"
                value={updateAltPhone}
                onChange={(e) => setUpdateAltPhone(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('email')}</label>
              <input
                type="email"
                value={updateEmail}
                onChange={(e) => setUpdateEmail(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('address')}</label>
              <textarea
                rows={2}
                value={updateAddress}
                onChange={(e) => setUpdateAddress(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>

            {updateCreatedDate && (
              <div className="text-xs text-neutral-400">Created Date: {updateCreatedDate}</div>
            )}

            <div className="flex gap-3 pt-3">
              <button
                type="submit"
                className="px-5 py-2 rounded text-xs font-semibold bg-[#1565C0] text-white hover:bg-[#0D47A1] transition-colors"
              >
                {t('update')}
              </button>
              <button
                type="button"
                onClick={() => {
                  setUpdateName('');
                  setUpdatePhone('');
                  setUpdateAltPhone('');
                  setUpdateEmail('');
                  setUpdateAddress('');
                  setUpdateCreatedDate('');
                  setUpdateMsg({ type: '', text: '' });
                }}
                className="px-5 py-2 rounded text-xs font-semibold border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300"
              >
                {t('clear')}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // CUSTOMER SUMMARY (Vertical scrollable layout)
  if (view === 'summary') {
    const custs = loadCustomers();
    const cust = custs.find((c) => c.customer_id === selectedCustomerId) || custs[0];

    if (!cust) {
      return (
        <div className={`p-8 rounded border ${cardBg}`}>
          <div className="text-red-500 mb-2">No customer found</div>
          <button onClick={() => onNavigate('customers_view')} className="text-xs text-[#1565C0] underline">Back</button>
        </div>
      );
    }

    const txns = loadTransactions().filter((t) => t.customer_id === cust.customer_id);
    const txnIds = txns.map((t) => t.transaction_id);
    const items = loadItems().filter((i) => txnIds.includes(i.transaction_id));
    const pays = loadPayments().filter((p) => p.customer_id === cust.customer_id);
    const perf = calculateCustomerPerformance(cust.customer_id);

    return (
      <div className="max-w-xl space-y-4">
        <div className="flex items-center gap-3">
          <button onClick={() => onNavigate('customers_view')} className="text-xs text-[#1565C0] hover:underline font-semibold">
            ← Back
          </button>
          <h2 className={`text-xl font-bold ${textColor}`}>
            {t('customer_summary')} - {cust.customer_name} ({cust.customer_id})
          </h2>
        </div>

        <div className={`p-6 rounded border space-y-5 ${cardBg}`}>
          {/* Information */}
          <div className="border-b pb-4 dark:border-[#333333]">
            <h3 className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">CUSTOMER INFORMATION</h3>
            <div className="grid grid-cols-2 gap-y-1.5 text-xs">
              <div className={subText}>Customer ID:</div>
              <div className={`font-mono ${textColor}`}>{cust.customer_id}</div>
              <div className={subText}>Name:</div>
              <div className={`font-semibold ${textColor}`}>{cust.customer_name}</div>
              <div className={subText}>Mobile:</div>
              <div className={`tabular-nums ${textColor}`}>{cust.phone_number}</div>
              <div className={subText}>Alternate:</div>
              <div className={textColor}>{cust.alternate_number || '-'}</div>
              <div className={subText}>Email:</div>
              <div className={textColor}>{cust.email || '-'}</div>
              <div className={subText}>Address:</div>
              <div className={textColor}>{cust.address || '-'}</div>
            </div>
          </div>

          {/* Transactions summary */}
          <div className="border-b pb-4 dark:border-[#333333]">
            <h3 className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">TRANSACTIONS</h3>
            <div className="grid grid-cols-2 gap-y-1.5 text-xs">
              <div className={subText}>Total Transactions:</div>
              <div className={`font-bold tabular-nums ${textColor}`}>{txns.length}</div>
              <div className={subText}>Total Credit:</div>
              <div className={`font-bold tabular-nums ${textColor}`}>₹{perf.total_credit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
              <div className={subText}>Total Paid:</div>
              <div className="font-bold tabular-nums text-emerald-600">₹{perf.total_paid.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
              <div className={subText}>Pending:</div>
              <div className="font-bold tabular-nums text-amber-600">₹{perf.pending_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
            </div>
          </div>

          {/* Credited Items */}
          <div className="border-b pb-4 dark:border-[#333333]">
            <h3 className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">CREDITED ITEMS</h3>
            {items.length === 0 ? (
              <div className={`text-xs ${subText}`}>No credited items recorded.</div>
            ) : (
              <div className="space-y-1.5 text-xs">
                {items.map((it) => (
                  <div key={it.item_id} className="flex justify-between">
                    <span className={textColor}>{it.item_name} (Qty: {it.quantity} × ₹{it.unit_price})</span>
                    <span className="font-mono font-medium text-neutral-800 dark:text-neutral-200">₹{it.subtotal.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Payments */}
          <div className="border-b pb-4 dark:border-[#333333]">
            <h3 className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">PAYMENTS</h3>
            {pays.length === 0 ? (
              <div className={`text-xs ${subText}`}>No payments made yet.</div>
            ) : (
              <div className="space-y-1.5 text-xs">
                {pays.map((p) => (
                  <div key={p.payment_id} className="flex justify-between">
                    <span className={textColor}>{p.payment_date} ({p.payment_method})</span>
                    <span className="font-mono font-bold text-emerald-600">₹{p.payment_amount.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Performance & Outstanding */}
          <div>
            <h3 className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">PERFORMANCE & STATUS</h3>
            <div className="grid grid-cols-2 gap-y-1.5 text-xs">
              <div className={subText}>Score:</div>
              <div className={`font-semibold ${textColor}`}>{perf.performance_percentage}% ({t(perf.performance_status.toLowerCase())})</div>
              <div className={subText}>Overdue Count:</div>
              <div className={perf.overdue_count > 0 ? 'text-red-600 font-bold' : textColor}>{perf.overdue_count}</div>
              <div className={subText}>Overall Status:</div>
              <div className={`font-bold ${perf.pending_amount <= 0 ? 'text-emerald-600' : 'text-amber-600'}`}>
                {perf.pending_amount <= 0 ? 'Paid' : 'Pending'}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // CUSTOMER PERFORMANCE VIEW
  const performances = getAllCustomerPerformances();
  return (
    <div className="space-y-4">
      <h2 className={`text-xl font-bold ${textColor}`}>{t('customer_performance')}</h2>
      <div className={`rounded border overflow-hidden ${cardBg}`}>
        {performances.length === 0 ? (
          <div className={`p-8 text-center text-sm ${subText}`}>{t('no_results')}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className={`${isDark ? 'bg-[#252525] text-neutral-300' : 'bg-neutral-50 text-neutral-600'}`}>
                <tr>
                  <th className="px-4 py-2.5 font-semibold">{t('customer_id')}</th>
                  <th className="px-4 py-2.5 font-semibold">{t('customer_name')}</th>
                  <th className="px-4 py-2.5 font-semibold text-center">Txns</th>
                  <th className="px-4 py-2.5 font-semibold text-right">{t('total_credit')}</th>
                  <th className="px-4 py-2.5 font-semibold text-right">{t('total_paid')}</th>
                  <th className="px-4 py-2.5 font-semibold text-right">{t('pending_amount')}</th>
                  <th className="px-4 py-2.5 font-semibold text-center">{t('overdue_count')}</th>
                  <th className="px-4 py-2.5 font-semibold text-right">{t('performance_percentage')}</th>
                  <th className="px-4 py-2.5 font-semibold">{t('performance_status')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-[#333333]">
                {performances.map((perf) => (
                  <tr key={perf.customer_id} className="hover:bg-neutral-50 dark:hover:bg-[#252525]">
                    <td className="px-4 py-2.5">
                      <button
                        onClick={() => onNavigate('customer_summary', perf.customer_id)}
                        className="font-bold text-[#1565C0] hover:underline"
                      >
                        {perf.customer_id}
                      </button>
                    </td>
                    <td className={`px-4 py-2.5 font-medium ${textColor}`}>{perf.customer_name}</td>
                    <td className={`px-4 py-2.5 text-center ${textColor}`}>{perf.total_transactions}</td>
                    <td className={`px-4 py-2.5 text-right tabular-nums ${textColor}`}>₹{perf.total_credit.toFixed(2)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums text-emerald-600">₹{perf.total_paid.toFixed(2)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums text-amber-600 font-medium">₹{perf.pending_amount.toFixed(2)}</td>
                    <td className={`px-4 py-2.5 text-center ${perf.overdue_count > 0 ? 'text-red-600 font-bold' : textColor}`}>
                      {perf.overdue_count}
                    </td>
                    <td className={`px-4 py-2.5 text-right font-bold tabular-nums ${textColor}`}>{perf.performance_percentage}%</td>
                    <td className="px-4 py-2.5 font-bold">
                      <span className={
                        perf.performance_status === 'Excellent' ? 'text-emerald-600' :
                        perf.performance_status === 'Good' ? 'text-[#1565C0]' :
                        perf.performance_status === 'Average' ? 'text-amber-600' : 'text-red-600'
                      }>
                        {t(perf.performance_status.toLowerCase())}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
