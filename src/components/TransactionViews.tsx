import React, { useState, useEffect } from 'react';
import { TRANSLATIONS, Language } from '../translations';
import {
  CreditTransaction,
  loadTransactions,
  saveTransactions,
  getNextTransactionId,
  loadCustomers,
  calculateEnrichedTransactions,
  getTodayDate,
  getCurrentTime,
  loadItems,
  loadPayments,
  getTransactionStatus,
} from '../storage';

interface Props {
  isDark: boolean;
  language: Language;
  view: 'add' | 'view' | 'update' | 'summary';
  selectedTransactionId?: string | null;
  onNavigate: (view: any, transactionId?: string) => void;
}

export const TransactionViews: React.FC<Props> = ({
  isDark,
  language,
  view,
  selectedTransactionId,
  onNavigate,
}) => {
  const t = (key: string) => TRANSLATIONS[language]?.[key] || key;

  const cardBg = isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]';
  const textColor = isDark ? 'text-white' : 'text-neutral-900';
  const subText = isDark ? 'text-neutral-400' : 'text-neutral-500';
  const inputBg = isDark ? 'bg-[#2A2A2A] border-[#444444] text-white' : 'bg-white border-neutral-300 text-neutral-900';

  const custs = loadCustomers();

  // Add state
  const [autoTxnId, setAutoTxnId] = useState(getNextTransactionId());
  const [addCustId, setAddCustId] = useState(custs[0]?.customer_id || '');
  const [addTxnDate, setAddTxnDate] = useState('');
  const [addDueDate, setAddDueDate] = useState('');
  const [addCreatedDate, setAddCreatedDate] = useState('');
  const [addUpdatedDate, setAddUpdatedDate] = useState('');
  const [addAmount, setAddAmount] = useState('');
  const [addNote, setAddNote] = useState('');
  const [addMsg, setAddMsg] = useState({ type: '', text: '' });

  // Update state
  const [updateSelectedId, setUpdateSelectedId] = useState(selectedTransactionId || '');
  const [updateCustId, setUpdateCustId] = useState('');
  const [updateTxnDate, setUpdateTxnDate] = useState('');
  const [updateDueDate, setUpdateDueDate] = useState('');
  const [updateCreatedDate, setUpdateCreatedDate] = useState('');
  const [updateUpdatedDate, setUpdateUpdatedDate] = useState('');
  const [updateAmount, setUpdateAmount] = useState('');
  const [updateNote, setUpdateNote] = useState('');
  const [updateMsg, setUpdateMsg] = useState({ type: '', text: '' });

  const handleLoadTxn = (idToLoad: string) => {
    if (!idToLoad) return;
    const txns = loadTransactions();
    const found = txns.find((tx) => tx.transaction_id === idToLoad);
    if (found) {
      setUpdateCustId(found.customer_id);
      setUpdateTxnDate(found.transaction_date || '');
      setUpdateDueDate(found.due_date || '');
      setUpdateCreatedDate(found.created_date || '');
      setUpdateUpdatedDate(found.updated_date || '');
      setUpdateAmount(String(found.total_amount));
      setUpdateNote(found.note || '');
      setUpdateMsg({ type: '', text: '' });
    }
  };

  useEffect(() => {
    if (view === 'update' && selectedTransactionId) {
      setUpdateSelectedId(selectedTransactionId);
      handleLoadTxn(selectedTransactionId);
    }
  }, [view, selectedTransactionId]);

  const handleSaveAdd = (e: React.FormEvent) => {
    e.preventDefault();
    setAddMsg({ type: '', text: '' });

    if (!addCustId) {
      setAddMsg({ type: 'error', text: `${t('customers')} is required.` });
      return;
    }
    if (!addTxnDate) {
      setAddMsg({ type: 'error', text: `${t('transaction_date')} is required. Please select from calendar.` });
      return;
    }
    if (!addDueDate) {
      setAddMsg({ type: 'error', text: `${t('due_date')} is required. Please select from calendar.` });
      return;
    }
    if (!addCreatedDate) {
      setAddMsg({ type: 'error', text: `${t('created_date')} is required. Please select from calendar.` });
      return;
    }
    if (!addUpdatedDate) {
      setAddMsg({ type: 'error', text: `${t('updated_date')} is required. Please select from calendar.` });
      return;
    }
    if (!addAmount.trim()) {
      setAddMsg({ type: 'error', text: `${t('total_amount')} is required.` });
      return;
    }
    const amt = parseFloat(addAmount);
    if (isNaN(amt) || amt <= 0) {
      setAddMsg({ type: 'error', text: 'Enter valid positive total amount' });
      return;
    }

    const txns = loadTransactions();
    const status = getTransactionStatus(amt, 0, addDueDate);

    const newTxn: CreditTransaction = {
      transaction_id: autoTxnId,
      customer_id: addCustId,
      transaction_date: addTxnDate,
      due_date: addDueDate,
      total_amount: amt,
      payment_status: status,
      note: addNote.trim(),
      created_date: addCreatedDate,
      updated_date: addUpdatedDate,
      time: getCurrentTime(),
    };

    saveTransactions([...txns, newTxn]);
    setAddMsg({ type: 'success', text: t('success_save') });
    setAddAmount('');
    setAddNote('');
    setAddTxnDate('');
    setAddDueDate('');
    setAddCreatedDate('');
    setAddUpdatedDate('');
    setAutoTxnId(getNextTransactionId());
  };

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    setUpdateMsg({ type: '', text: '' });

    if (!updateSelectedId || !updateCustId) {
      setUpdateMsg({ type: 'error', text: 'Select transaction and customer' });
      return;
    }
    if (!updateTxnDate) {
      setUpdateMsg({ type: 'error', text: `${t('transaction_date')} is required. Please select from calendar.` });
      return;
    }
    if (!updateDueDate) {
      setUpdateMsg({ type: 'error', text: `${t('due_date')} is required. Please select from calendar.` });
      return;
    }
    if (!updateCreatedDate) {
      setUpdateMsg({ type: 'error', text: `${t('created_date')} is required. Please select from calendar.` });
      return;
    }
    if (!updateUpdatedDate) {
      setUpdateMsg({ type: 'error', text: `${t('updated_date')} is required. Please select from calendar.` });
      return;
    }
    if (!updateAmount.trim()) {
      setUpdateMsg({ type: 'error', text: `${t('total_amount')} is required.` });
      return;
    }
    const amt = parseFloat(updateAmount);
    if (isNaN(amt) || amt <= 0) {
      setUpdateMsg({ type: 'error', text: 'Enter valid amount' });
      return;
    }

    const txns = loadTransactions();
    const pays = loadPayments().filter((p) => p.transaction_id === updateSelectedId);
    const paid = pays.reduce((sum, p) => sum + p.payment_amount, 0);
    const newStatus = getTransactionStatus(amt, paid, updateDueDate);

    const updated = txns.map((t_row) => {
      if (t_row.transaction_id === updateSelectedId) {
        return {
          ...t_row,
          customer_id: updateCustId,
          transaction_date: updateTxnDate,
          due_date: updateDueDate,
          total_amount: amt,
          payment_status: newStatus,
          note: updateNote.trim(),
          created_date: updateCreatedDate,
          updated_date: updateUpdatedDate,
          time: getCurrentTime(),
        };
      }
      return t_row;
    });

    saveTransactions(updated);
    setUpdateMsg({ type: 'success', text: t('success_update') });
  };

  const handleDelete = (txnId: string) => {
    if (confirm(`Delete transaction ${txnId}?`)) {
      const txns = loadTransactions().filter((t_row) => t_row.transaction_id !== txnId);
      saveTransactions(txns);
      onNavigate('transactions_view');
    }
  };

  // ADD TRANSACTION
  if (view === 'add') {
    return (
      <div className="max-w-md">
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>{t('add_transaction')}</h2>
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
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('transaction_id')}</label>
              <input type="text" value={autoTxnId} disabled className={`w-full px-3 py-1.5 rounded text-sm border opacity-70 ${inputBg}`} />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('customers')} *</label>
              <select
                value={addCustId}
                onChange={(e) => setAddCustId(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="">-- Select Customer --</option>
                {custs.map((c) => (
                  <option key={c.customer_id} value={c.customer_id}>
                    {c.customer_id} - {c.customer_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('transaction_date')} *</label>
                <input
                  type="date"
                  value={addTxnDate}
                  onChange={(e) => setAddTxnDate(e.target.value)}
                  className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                />
              </div>
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('due_date')} *</label>
                <input
                  type="date"
                  value={addDueDate}
                  onChange={(e) => setAddDueDate(e.target.value)}
                  className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('created_date')} *</label>
                <input
                  type="date"
                  value={addCreatedDate}
                  onChange={(e) => setAddCreatedDate(e.target.value)}
                  className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                />
              </div>
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('updated_date')} *</label>
                <input
                  type="date"
                  value={addUpdatedDate}
                  onChange={(e) => setAddUpdatedDate(e.target.value)}
                  className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                />
              </div>
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('total_amount')} (₹) *</label>
              <input
                type="number"
                step="any"
                value={addAmount}
                onChange={(e) => setAddAmount(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="Enter bill total amount"
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('notes')}</label>
              <textarea
                rows={2}
                value={addNote}
                onChange={(e) => setAddNote(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="Optional notes or bill details"
              />
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
                  setAddAmount('');
                  setAddNote('');
                  setAddMsg({ type: '', text: '' });
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

  // VIEW TRANSACTIONS
  if (view === 'view') {
    const txns = calculateEnrichedTransactions();
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className={`text-xl font-bold ${textColor}`}>{t('view_transactions')}</h2>
          <button
            onClick={() => onNavigate('transactions_add')}
            className="px-3 py-1.5 text-xs font-semibold bg-[#1565C0] text-white rounded hover:bg-[#0D47A1]"
          >
            + {t('add_transaction')}
          </button>
        </div>

        <div className={`rounded border overflow-hidden ${cardBg}`}>
          {txns.length === 0 ? (
            <div className={`p-8 text-center text-sm ${subText}`}>{t('no_results')}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className={`${isDark ? 'bg-[#252525] text-neutral-300' : 'bg-neutral-50 text-neutral-600'}`}>
                  <tr>
                    <th className="px-4 py-2.5 font-semibold">{t('transaction_id')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('customer_name')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('transaction_date')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('due_date')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">{t('total_amount')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">{t('total_paid')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">{t('pending_amount')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('payment_status')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 dark:divide-[#333333]">
                  {txns.map((txn) => (
                    <tr key={txn.transaction_id} className="hover:bg-neutral-50 dark:hover:bg-[#252525]">
                      <td className="px-4 py-2.5">
                        <button
                          onClick={() => onNavigate('transaction_summary', txn.transaction_id)}
                          className="font-bold text-[#1565C0] hover:underline"
                        >
                          {txn.transaction_id}
                        </button>
                      </td>
                      <td className={`px-4 py-2.5 font-medium ${textColor}`}>{txn.customer_name}</td>
                      <td className={`px-4 py-2.5 ${subText}`}>{txn.transaction_date}</td>
                      <td className={`px-4 py-2.5 ${subText}`}>{txn.due_date}</td>
                      <td className={`px-4 py-2.5 text-right font-medium tabular-nums ${textColor}`}>
                        ₹{txn.total_amount.toFixed(2)}
                      </td>
                      <td className="px-4 py-2.5 text-right font-medium tabular-nums text-emerald-600">
                        ₹{(txn.total_paid || 0).toFixed(2)}
                      </td>
                      <td className="px-4 py-2.5 text-right font-bold tabular-nums text-amber-600">
                        ₹{(txn.pending_amount || 0).toFixed(2)}
                      </td>
                      <td className="px-4 py-2.5 font-semibold">
                        <span className={
                          txn.payment_status === 'Paid' ? 'text-emerald-600' :
                          txn.payment_status === 'Overdue' ? 'text-red-600' : 'text-amber-600'
                        }>
                          {t(txn.payment_status.toLowerCase())}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-right space-x-2">
                        <button
                          onClick={() => onNavigate('transactions_update', txn.transaction_id)}
                          className="text-xs text-[#1565C0] hover:underline"
                        >
                          {t('update')}
                        </button>
                        <button
                          onClick={() => handleDelete(txn.transaction_id)}
                          className="text-xs text-red-600 hover:underline"
                        >
                          {t('delete')}
                        </button>
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
  }

  // UPDATE TRANSACTION
  if (view === 'update') {
    const rawTxns = loadTransactions();
    return (
      <div className="max-w-md">
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>{t('update_transaction')}</h2>
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
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('transaction_id')}</label>
            <div className="flex gap-2">
              <select
                value={updateSelectedId}
                onChange={(e) => {
                  setUpdateSelectedId(e.target.value);
                  handleLoadTxn(e.target.value);
                }}
                className={`flex-1 px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="">-- Select Transaction --</option>
                {rawTxns.map((tx) => (
                  <option key={tx.transaction_id} value={tx.transaction_id}>
                    {tx.transaction_id} - ₹{tx.total_amount}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => handleLoadTxn(updateSelectedId)}
                className="px-3 py-1.5 rounded text-xs font-semibold bg-[#1565C0] text-white hover:bg-[#0D47A1]"
              >
                {t('load')}
              </button>
            </div>
          </div>

          <form onSubmit={handleUpdate} className="space-y-3">
            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('customers')} *</label>
              <select
                value={updateCustId}
                onChange={(e) => setUpdateCustId(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="">-- Select Customer --</option>
                {custs.map((c) => (
                  <option key={c.customer_id} value={c.customer_id}>
                    {c.customer_id} - {c.customer_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('transaction_date')} *</label>
                <input
                  type="date"
                  value={updateTxnDate}
                  onChange={(e) => setUpdateTxnDate(e.target.value)}
                  className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                />
              </div>
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('due_date')} *</label>
                <input
                  type="date"
                  value={updateDueDate}
                  onChange={(e) => setUpdateDueDate(e.target.value)}
                  className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('created_date')} *</label>
                <input
                  type="date"
                  value={updateCreatedDate}
                  onChange={(e) => setUpdateCreatedDate(e.target.value)}
                  className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                />
              </div>
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('updated_date')} *</label>
                <input
                  type="date"
                  value={updateUpdatedDate}
                  onChange={(e) => setUpdateUpdatedDate(e.target.value)}
                  className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                />
              </div>
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('total_amount')} (₹) *</label>
              <input
                type="number"
                step="any"
                value={updateAmount}
                onChange={(e) => setUpdateAmount(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('notes')}</label>
              <textarea
                rows={2}
                value={updateNote}
                onChange={(e) => setUpdateNote(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>

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
                  setUpdateAmount('');
                  setUpdateNote('');
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

  // TRANSACTION SUMMARY
  const allTxns = calculateEnrichedTransactions();
  const txn = allTxns.find((t_item) => t_item.transaction_id === selectedTransactionId) || allTxns[0];

  if (!txn) {
    return (
      <div className={`p-8 rounded border ${cardBg}`}>
        <div className="text-red-500 mb-2">No transaction found</div>
        <button onClick={() => onNavigate('transactions_view')} className="text-xs text-[#1565C0] underline">Back</button>
      </div>
    );
  }

  const items = loadItems().filter((i) => i.transaction_id === txn.transaction_id);
  const pays = loadPayments().filter((p) => p.transaction_id === txn.transaction_id);

  return (
    <div className="max-w-xl space-y-4">
      <div className="flex items-center gap-3">
        <button onClick={() => onNavigate('transactions_view')} className="text-xs text-[#1565C0] hover:underline font-semibold">
          ← Back
        </button>
        <h2 className={`text-xl font-bold ${textColor}`}>
          {t('transaction_summary')} - {txn.transaction_id}
        </h2>
      </div>

      <div className={`p-6 rounded border space-y-5 ${cardBg}`}>
        {/* Information */}
        <div className="border-b pb-4 dark:border-[#333333]">
          <h3 className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">TRANSACTION INFORMATION</h3>
          <div className="grid grid-cols-2 gap-y-1.5 text-xs">
            <div className={subText}>Transaction ID:</div>
            <div className={`font-mono font-bold ${textColor}`}>{txn.transaction_id}</div>
            <div className={subText}>Customer:</div>
            <div className={`font-semibold ${textColor}`}>{txn.customer_name} ({txn.customer_id})</div>
            <div className={subText}>Transaction Date:</div>
            <div className={textColor}>{txn.transaction_date}</div>
            <div className={subText}>Due Date:</div>
            <div className={textColor}>{txn.due_date}</div>
            <div className={subText}>Total Amount:</div>
            <div className={`font-bold tabular-nums ${textColor}`}>₹{txn.total_amount.toFixed(2)}</div>
            <div className={subText}>Total Paid:</div>
            <div className="font-bold tabular-nums text-emerald-600">₹{(txn.total_paid || 0).toFixed(2)}</div>
            <div className={subText}>Pending Amount:</div>
            <div className="font-bold tabular-nums text-amber-600">₹{(txn.pending_amount || 0).toFixed(2)}</div>
            <div className={subText}>Payment Status:</div>
            <div className={`font-bold ${
              txn.payment_status === 'Paid' ? 'text-emerald-600' :
              txn.payment_status === 'Overdue' ? 'text-red-600' : 'text-amber-600'
            }`}>
              {txn.payment_status}
            </div>
            <div className={subText}>Notes:</div>
            <div className={textColor}>{txn.note || '-'}</div>
          </div>
        </div>

        {/* Credited Items */}
        <div className="border-b pb-4 dark:border-[#333333]">
          <h3 className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">CREDITED ITEMS</h3>
          {items.length === 0 ? (
            <div className={`text-xs ${subText}`}>No items attached to this transaction.</div>
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
        <div>
          <h3 className="text-xs font-bold text-[#1565C0] uppercase tracking-wider mb-2">PAYMENTS</h3>
          {pays.length === 0 ? (
            <div className={`text-xs ${subText}`}>No payments recorded for this bill.</div>
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
      </div>
    </div>
  );
};
