import React, { useState, useEffect } from 'react';
import { TRANSLATIONS, Language } from '../translations';
import {
  Payment,
  loadPayments,
  savePayments,
  getNextPaymentId,
  calculateEnrichedTransactions,
} from '../storage';

interface Props {
  isDark: boolean;
  language: Language;
  view: 'add' | 'view' | 'update';
  selectedPaymentId?: string | null;
  onNavigate: (view: any, paymentId?: string) => void;
}

export const PaymentViews: React.FC<Props> = ({
  isDark,
  language,
  view,
  selectedPaymentId,
  onNavigate,
}) => {
  const t = (key: string) => TRANSLATIONS[language]?.[key] || key;

  const cardBg = isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]';
  const textColor = isDark ? 'text-white' : 'text-neutral-900';
  const subText = isDark ? 'text-neutral-400' : 'text-neutral-500';
  const inputBg = isDark ? 'bg-[#2A2A2A] border-[#444444] text-white' : 'bg-white border-neutral-300 text-neutral-900';

  const txns = calculateEnrichedTransactions();

  // Add state
  const [autoPayId, setAutoPayId] = useState(getNextPaymentId());
  const [addTxnId, setAddTxnId] = useState(txns[0]?.transaction_id || '');
  const [addAmount, setAddAmount] = useState('');
  const [addDate, setAddDate] = useState('');
  const [addCreatedDate, setAddCreatedDate] = useState('');
  const [addUpdatedDate, setAddUpdatedDate] = useState('');
  const [addMethod, setAddMethod] = useState('Cash');
  const [addRefId, setAddRefId] = useState('');
  const [addMsg, setAddMsg] = useState({ type: '', text: '' });

  // Update state
  const [updateSelectedId, setUpdateSelectedId] = useState(selectedPaymentId || '');
  const [updateTxnId, setUpdateTxnId] = useState('');
  const [updateCustName, setUpdateCustName] = useState('');
  const [updateAmount, setUpdateAmount] = useState('');
  const [updateDate, setUpdateDate] = useState('');
  const [updateCreatedDate, setUpdateCreatedDate] = useState('');
  const [updateUpdatedDate, setUpdateUpdatedDate] = useState('');
  const [updateMethod, setUpdateMethod] = useState('Cash');
  const [updateRefId, setUpdateRefId] = useState('');
  const [updateMsg, setUpdateMsg] = useState({ type: '', text: '' });

  const handleLoadPayment = (idToLoad: string) => {
    if (!idToLoad) return;
    const pays = loadPayments();
    const found = pays.find((p) => p.payment_id === idToLoad);
    if (found) {
      setUpdateTxnId(found.transaction_id);
      setUpdateCustName(found.customer_name || found.customer_id);
      setUpdateAmount(String(found.payment_amount));
      setUpdateDate(found.payment_date || '');
      setUpdateCreatedDate(found.created_date || found.payment_date || '');
      setUpdateUpdatedDate(found.updated_date || '');
      setUpdateMethod(found.payment_method);
      setUpdateRefId(found.reference_id || '');
      setUpdateMsg({ type: '', text: '' });
    }
  };

  useEffect(() => {
    if (view === 'update' && selectedPaymentId) {
      setUpdateSelectedId(selectedPaymentId);
      handleLoadPayment(selectedPaymentId);
    }
  }, [view, selectedPaymentId]);

  const handleSaveAdd = (e: React.FormEvent) => {
    e.preventDefault();
    setAddMsg({ type: '', text: '' });

    if (!addTxnId) {
      setAddMsg({ type: 'error', text: `${t('transaction_id')} is required.` });
      return;
    }
    if (!addAmount.trim()) {
      setAddMsg({ type: 'error', text: `${t('payment_amount')} is required.` });
      return;
    }
    const amt = parseFloat(addAmount);
    if (isNaN(amt) || amt <= 0) {
      setAddMsg({ type: 'error', text: 'Payment amount must be a positive number greater than 0.' });
      return;
    }
    if (!addDate) {
      setAddMsg({ type: 'error', text: `${t('payment_date')} is required. Please select from calendar.` });
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

    const tObj = txns.find((t_item) => t_item.transaction_id === addTxnId);
    if (!tObj) {
      setAddMsg({ type: 'error', text: 'Transaction not found.' });
      return;
    }

    const pays = loadPayments();
    const newPayment: Payment = {
      payment_id: autoPayId,
      transaction_id: addTxnId,
      customer_id: tObj.customer_id,
      customer_name: tObj.customer_name,
      payment_amount: amt,
      payment_date: addDate,
      created_date: addCreatedDate,
      updated_date: addUpdatedDate,
      payment_method: addMethod,
      reference_id: addRefId.trim(),
    };

    savePayments([...pays, newPayment]);
    setAddMsg({ type: 'success', text: t('success_save') });
    setAddAmount('');
    setAddRefId('');
    setAddDate('');
    setAddCreatedDate('');
    setAddUpdatedDate('');
    setAutoPayId(getNextPaymentId());
  };

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    setUpdateMsg({ type: '', text: '' });

    if (!updateSelectedId) {
      setUpdateMsg({ type: 'error', text: 'Please select a payment to update.' });
      return;
    }
    if (!updateAmount.trim()) {
      setUpdateMsg({ type: 'error', text: `${t('payment_amount')} is required.` });
      return;
    }
    const amt = parseFloat(updateAmount);
    if (isNaN(amt) || amt <= 0) {
      setUpdateMsg({ type: 'error', text: 'Payment amount must be a positive number greater than 0.' });
      return;
    }
    if (!updateDate) {
      setUpdateMsg({ type: 'error', text: `${t('payment_date')} is required. Please select from calendar.` });
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

    const pays = loadPayments();
    const updated = pays.map((p) => {
      if (p.payment_id === updateSelectedId) {
        return {
          ...p,
          payment_amount: amt,
          payment_date: updateDate,
          created_date: updateCreatedDate,
          updated_date: updateUpdatedDate,
          payment_method: updateMethod,
          reference_id: updateRefId.trim(),
        };
      }
      return p;
    });

    savePayments(updated);
    setUpdateMsg({ type: 'success', text: t('success_update') });
  };

  const handleDelete = (paymentId: string) => {
    if (confirm(`Delete payment ${paymentId}?`)) {
      const pays = loadPayments().filter((p) => p.payment_id !== paymentId);
      savePayments(pays);
      onNavigate('payments_view');
    }
  };

  // ADD PAYMENT
  if (view === 'add') {
    return (
      <div className="max-w-md">
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>{t('add_payment')}</h2>
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
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('payment_id')}</label>
              <input type="text" value={autoPayId} disabled className={`w-full px-3 py-1.5 rounded text-sm border opacity-70 ${inputBg}`} />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('transaction_id')} *</label>
              <select
                value={addTxnId}
                onChange={(e) => setAddTxnId(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="">-- Select Transaction --</option>
                {txns.map((t_item) => (
                  <option key={t_item.transaction_id} value={t_item.transaction_id}>
                    {t_item.transaction_id} - {t_item.customer_name} (Pending: ₹{t_item.pending_amount?.toFixed(2)})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('payment_amount')} (₹) *</label>
              <input
                type="number"
                step="any"
                value={addAmount}
                onChange={(e) => setAddAmount(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="Enter paid amount"
              />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('payment_date')} *</label>
              <input
                type="date"
                value={addDate}
                onChange={(e) => setAddDate(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
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
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('payment_method')} *</label>
              <select
                value={addMethod}
                onChange={(e) => setAddMethod(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="Cash">Cash (नकद)</option>
                <option value="UPI">UPI (GPay / PhonePe / Paytm)</option>
                <option value="Bank Transfer">Bank Transfer (बैंक ट्रांसफर)</option>
                <option value="Cheque">Cheque (चेक)</option>
              </select>
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('reference_id')}</label>
              <input
                type="text"
                value={addRefId}
                onChange={(e) => setAddRefId(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="UPI Ref ID, Cheque No, Bank Txn ID"
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
                  setAddDate('');
                  setAddRefId('');
                  setAddCreatedDate('');
                  setAddUpdatedDate('');
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

  // VIEW PAYMENTS
  if (view === 'view') {
    const pays = loadPayments();
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className={`text-xl font-bold ${textColor}`}>{t('view_payments')}</h2>
          <button
            onClick={() => onNavigate('payments_add')}
            className="px-3 py-1.5 text-xs font-semibold bg-[#1565C0] text-white rounded hover:bg-[#0D47A1]"
          >
            + {t('add_payment')}
          </button>
        </div>

        <div className={`rounded border overflow-hidden ${cardBg}`}>
          {pays.length === 0 ? (
            <div className={`p-8 text-center text-sm ${subText}`}>{t('no_results')}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className={`${isDark ? 'bg-[#252525] text-neutral-300' : 'bg-neutral-50 text-neutral-600'}`}>
                  <tr>
                    <th className="px-4 py-2.5 font-semibold">{t('payment_id')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('transaction_id')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('customer_name')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">{t('payment_amount')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('payment_date')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('payment_method')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('reference_id')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 dark:divide-[#333333]">
                  {pays.map((p) => (
                    <tr key={p.payment_id} className="hover:bg-neutral-50 dark:hover:bg-[#252525]">
                      <td className="px-4 py-2.5 font-bold text-[#1565C0]">{p.payment_id}</td>
                      <td className={`px-4 py-2.5 font-mono ${textColor}`}>{p.transaction_id}</td>
                      <td className={`px-4 py-2.5 font-medium ${textColor}`}>{p.customer_name || p.customer_id}</td>
                      <td className="px-4 py-2.5 text-right font-bold text-emerald-600 tabular-nums">
                        ₹{p.payment_amount.toFixed(2)}
                      </td>
                      <td className={`px-4 py-2.5 ${textColor}`}>{p.payment_date}</td>
                      <td className={`px-4 py-2.5 ${textColor}`}>{p.payment_method}</td>
                      <td className={`px-4 py-2.5 font-mono ${subText}`}>{p.reference_id || '-'}</td>
                      <td className="px-4 py-2.5 text-right space-x-2">
                        <button
                          onClick={() => onNavigate('payments_update', p.payment_id)}
                          className="text-xs text-[#1565C0] hover:underline"
                        >
                          {t('update')}
                        </button>
                        <button
                          onClick={() => handleDelete(p.payment_id)}
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

  // UPDATE PAYMENT
  const pays = loadPayments();

  return (
    <div className="max-w-md">
      <h2 className={`text-xl font-bold mb-4 ${textColor}`}>{t('update_payment')}</h2>
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
          <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('payment_id')}</label>
          <div className="flex gap-2">
            <select
              value={updateSelectedId}
              onChange={(e) => {
                setUpdateSelectedId(e.target.value);
                handleLoadPayment(e.target.value);
              }}
              className={`flex-1 px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
            >
              <option value="">-- Select Payment --</option>
              {pays.map((p) => (
                <option key={p.payment_id} value={p.payment_id}>
                  {p.payment_id} - ₹{p.payment_amount} ({p.customer_name || p.customer_id})
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => handleLoadPayment(updateSelectedId)}
              className="px-3 py-1.5 rounded text-xs font-semibold bg-[#1565C0] text-white hover:bg-[#0D47A1]"
            >
              {t('load')}
            </button>
          </div>
        </div>

        <form onSubmit={handleUpdate} className="space-y-3">
          <div>
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('transaction_id')}</label>
            <input
              type="text"
              value={updateTxnId}
              disabled
              className={`w-full px-3 py-1.5 rounded text-sm border opacity-70 ${inputBg}`}
            />
          </div>

          <div>
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('customer_name')}</label>
            <input
              type="text"
              value={updateCustName}
              disabled
              className={`w-full px-3 py-1.5 rounded text-sm border opacity-70 ${inputBg}`}
            />
          </div>

          <div>
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('payment_amount')} (₹) *</label>
            <input
              type="number"
              step="any"
              value={updateAmount}
              onChange={(e) => setUpdateAmount(e.target.value)}
              className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
            />
          </div>

          <div>
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('payment_date')} *</label>
            <input
              type="date"
              value={updateDate}
              onChange={(e) => setUpdateDate(e.target.value)}
              className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
            />
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
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('payment_method')} *</label>
            <select
              value={updateMethod}
              onChange={(e) => setUpdateMethod(e.target.value)}
              className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
            >
              <option value="Cash">Cash (नकद)</option>
              <option value="UPI">UPI (GPay / PhonePe / Paytm)</option>
              <option value="Bank Transfer">Bank Transfer (बैंक ट्रांसफर)</option>
              <option value="Cheque">Cheque (चेक)</option>
            </select>
          </div>

          <div>
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('reference_id')}</label>
            <input
              type="text"
              value={updateRefId}
              onChange={(e) => setUpdateRefId(e.target.value)}
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
                setUpdateDate('');
                setUpdateRefId('');
                setUpdateCreatedDate('');
                setUpdateUpdatedDate('');
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
};
