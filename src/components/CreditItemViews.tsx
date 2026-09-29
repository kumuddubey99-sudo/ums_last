import React, { useState, useEffect } from 'react';
import { TRANSLATIONS, Language } from '../translations';
import {
  CreditItem,
  loadItems,
  saveItems,
  getNextItemId,
  loadTransactions,
  getCurrentTime,
} from '../storage';

interface Props {
  isDark: boolean;
  language: Language;
  view: 'add' | 'view' | 'update';
  selectedItemId?: string | null;
  onNavigate: (view: any, itemId?: string) => void;
}

export const CreditItemViews: React.FC<Props> = ({
  isDark,
  language,
  view,
  selectedItemId,
  onNavigate,
}) => {
  const t = (key: string) => TRANSLATIONS[language]?.[key] || key;

  const cardBg = isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]';
  const textColor = isDark ? 'text-white' : 'text-neutral-900';
  const subText = isDark ? 'text-neutral-400' : 'text-neutral-500';
  const inputBg = isDark ? 'bg-[#2A2A2A] border-[#444444] text-white' : 'bg-white border-neutral-300 text-neutral-900';

  const txns = loadTransactions();

  // Add Item state
  const [autoItemId, setAutoItemId] = useState(getNextItemId());
  const [addTxnId, setAddTxnId] = useState(txns[0]?.transaction_id || '');
  const [addItemName, setAddItemName] = useState('');
  const [addQty, setAddQty] = useState('1');
  const [addPrice, setAddPrice] = useState('0');
  const [addCreatedDate, setAddCreatedDate] = useState('');
  const [addUpdatedDate, setAddUpdatedDate] = useState('');
  const [addMsg, setAddMsg] = useState({ type: '', text: '' });

  // Update Item state
  const [updateSelectedId, setUpdateSelectedId] = useState(selectedItemId || '');
  const [updateTxnId, setUpdateTxnId] = useState('');
  const [updateItemName, setUpdateItemName] = useState('');
  const [updateQty, setUpdateQty] = useState('1');
  const [updatePrice, setUpdatePrice] = useState('0');
  const [updateCreatedDate, setUpdateCreatedDate] = useState('');
  const [updateUpdatedDate, setUpdateUpdatedDate] = useState('');
  const [updateMsg, setUpdateMsg] = useState({ type: '', text: '' });

  const handleLoadItem = (idToLoad: string) => {
    if (!idToLoad) return;
    const items = loadItems();
    const found = items.find((i) => i.item_id === idToLoad);
    if (found) {
      setUpdateTxnId(found.transaction_id);
      setUpdateItemName(found.item_name);
      setUpdateQty(String(found.quantity));
      setUpdatePrice(String(found.unit_price));
      setUpdateCreatedDate(found.created_date || (found.credited_at ? found.credited_at.slice(0, 10) : ''));
      setUpdateUpdatedDate(found.updated_date || '');
      setUpdateMsg({ type: '', text: '' });
    }
  };

  useEffect(() => {
    if (view === 'update' && selectedItemId) {
      setUpdateSelectedId(selectedItemId);
      handleLoadItem(selectedItemId);
    }
  }, [view, selectedItemId]);

  const handleSaveAdd = (e: React.FormEvent) => {
    e.preventDefault();
    setAddMsg({ type: '', text: '' });

    if (!addTxnId) {
      setAddMsg({ type: 'error', text: `${t('transaction_id')} is required.` });
      return;
    }
    if (!addItemName.trim()) {
      setAddMsg({ type: 'error', text: `${t('item_name')} is required.` });
      return;
    }
    const q = parseFloat(addQty);
    if (isNaN(q) || q <= 0) {
      setAddMsg({ type: 'error', text: 'Quantity must be a positive number greater than 0.' });
      return;
    }
    const p = parseFloat(addPrice);
    if (isNaN(p) || p < 0) {
      setAddMsg({ type: 'error', text: 'Unit price must be a valid non-negative number.' });
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

    const items = loadItems();
    const newItem: CreditItem = {
      item_id: autoItemId,
      transaction_id: addTxnId,
      item_name: addItemName.trim(),
      quantity: q,
      unit_price: p,
      subtotal: Math.round(q * p * 100) / 100,
      credited_at: `${addCreatedDate} ${getCurrentTime()}`,
      created_date: addCreatedDate,
      updated_date: addUpdatedDate,
    };

    saveItems([...items, newItem]);
    setAddMsg({ type: 'success', text: t('success_save') });
    setAddItemName('');
    setAddQty('1');
    setAddPrice('0');
    setAddCreatedDate('');
    setAddUpdatedDate('');
    setAutoItemId(getNextItemId());
  };

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault();
    setUpdateMsg({ type: '', text: '' });

    if (!updateSelectedId) {
      setUpdateMsg({ type: 'error', text: 'Please select an item to update.' });
      return;
    }
    if (!updateTxnId) {
      setUpdateMsg({ type: 'error', text: `${t('transaction_id')} is required.` });
      return;
    }
    if (!updateItemName.trim()) {
      setUpdateMsg({ type: 'error', text: `${t('item_name')} is required.` });
      return;
    }
    const q = parseFloat(updateQty);
    if (isNaN(q) || q <= 0) {
      setUpdateMsg({ type: 'error', text: 'Quantity must be a positive number greater than 0.' });
      return;
    }
    const p = parseFloat(updatePrice);
    if (isNaN(p) || p < 0) {
      setUpdateMsg({ type: 'error', text: 'Unit price must be a valid non-negative number.' });
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

    const items = loadItems();
    const updated = items.map((it) => {
      if (it.item_id === updateSelectedId) {
        return {
          ...it,
          transaction_id: updateTxnId,
          item_name: updateItemName.trim(),
          quantity: q,
          unit_price: p,
          subtotal: Math.round(q * p * 100) / 100,
          created_date: updateCreatedDate,
          updated_date: updateUpdatedDate,
        };
      }
      return it;
    });

    saveItems(updated);
    setUpdateMsg({ type: 'success', text: t('success_update') });
  };

  const handleDelete = (itemId: string) => {
    if (confirm(`Delete credit item ${itemId}?`)) {
      const items = loadItems().filter((i) => i.item_id !== itemId);
      saveItems(items);
      onNavigate('items_view');
    }
  };

  // ADD ITEM
  if (view === 'add') {
    const calcSubtotal = (parseFloat(addQty) || 0) * (parseFloat(addPrice) || 0);
    return (
      <div className="max-w-md">
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>{t('add_credit_item')}</h2>
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
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('item_id')}</label>
              <input type="text" value={autoItemId} disabled className={`w-full px-3 py-1.5 rounded text-sm border opacity-70 ${inputBg}`} />
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('transaction_id')} *</label>
              <select
                value={addTxnId}
                onChange={(e) => setAddTxnId(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              >
                <option value="">-- Select Transaction --</option>
                {txns.map((t_row) => (
                  <option key={t_row.transaction_id} value={t_row.transaction_id}>
                    {t_row.transaction_id} - ₹{t_row.total_amount}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('item_name')} *</label>
              <input
                type="text"
                value={addItemName}
                onChange={(e) => setAddItemName(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="e.g. Sugar 5kg, Basmati Rice"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('quantity')} *</label>
                <input
                  type="number"
                  step="any"
                  value={addQty}
                  onChange={(e) => setAddQty(e.target.value)}
                  className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                />
              </div>
              <div>
                <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('unit_price')} (₹) *</label>
                <input
                  type="number"
                  step="any"
                  value={addPrice}
                  onChange={(e) => setAddPrice(e.target.value)}
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
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('subtotal')} (₹)</label>
              <input
                type="text"
                value={`₹${calcSubtotal.toFixed(2)}`}
                disabled
                className={`w-full px-3 py-1.5 rounded text-sm border font-bold opacity-80 ${inputBg}`}
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
                  setAddItemName('');
                  setAddQty('1');
                  setAddPrice('0');
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

  // VIEW ITEMS
  if (view === 'view') {
    const items = loadItems();
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className={`text-xl font-bold ${textColor}`}>{t('view_credit_items')}</h2>
          <button
            onClick={() => onNavigate('items_add')}
            className="px-3 py-1.5 text-xs font-semibold bg-[#1565C0] text-white rounded hover:bg-[#0D47A1]"
          >
            + {t('add_credit_item')}
          </button>
        </div>

        <div className={`rounded border overflow-hidden ${cardBg}`}>
          {items.length === 0 ? (
            <div className={`p-8 text-center text-sm ${subText}`}>{t('no_results')}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className={`${isDark ? 'bg-[#252525] text-neutral-300' : 'bg-neutral-50 text-neutral-600'}`}>
                  <tr>
                    <th className="px-4 py-2.5 font-semibold">{t('item_id')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('transaction_id')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('item_name')}</th>
                    <th className="px-4 py-2.5 font-semibold text-center">{t('quantity')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">{t('unit_price')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">{t('subtotal')}</th>
                    <th className="px-4 py-2.5 font-semibold">{t('created_date')}</th>
                    <th className="px-4 py-2.5 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 dark:divide-[#333333]">
                  {items.map((it) => (
                    <tr key={it.item_id} className="hover:bg-neutral-50 dark:hover:bg-[#252525]">
                      <td className="px-4 py-2.5 font-bold text-[#1565C0]">{it.item_id}</td>
                      <td className={`px-4 py-2.5 font-mono ${textColor}`}>{it.transaction_id}</td>
                      <td className={`px-4 py-2.5 font-medium ${textColor}`}>{it.item_name}</td>
                      <td className={`px-4 py-2.5 text-center ${textColor}`}>{it.quantity}</td>
                      <td className={`px-4 py-2.5 text-right tabular-nums ${textColor}`}>₹{it.unit_price.toFixed(2)}</td>
                      <td className={`px-4 py-2.5 text-right font-bold tabular-nums ${textColor}`}>₹{it.subtotal.toFixed(2)}</td>
                      <td className={`px-4 py-2.5 ${subText}`}>{it.created_date || it.credited_at}</td>
                      <td className="px-4 py-2.5 text-right space-x-2">
                        <button
                          onClick={() => onNavigate('items_update', it.item_id)}
                          className="text-xs text-[#1565C0] hover:underline"
                        >
                          {t('update')}
                        </button>
                        <button
                          onClick={() => handleDelete(it.item_id)}
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

  // UPDATE ITEM
  const items = loadItems();
  const updateCalcSubtotal = (parseFloat(updateQty) || 0) * (parseFloat(updatePrice) || 0);

  return (
    <div className="max-w-md">
      <h2 className={`text-xl font-bold mb-4 ${textColor}`}>{t('update_credit_item')}</h2>
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
          <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('item_id')}</label>
          <div className="flex gap-2">
            <select
              value={updateSelectedId}
              onChange={(e) => {
                setUpdateSelectedId(e.target.value);
                handleLoadItem(e.target.value);
              }}
              className={`flex-1 px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
            >
              <option value="">-- Select Item --</option>
              {items.map((i) => (
                <option key={i.item_id} value={i.item_id}>
                  {i.item_id} - {i.item_name}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => handleLoadItem(updateSelectedId)}
              className="px-3 py-1.5 rounded text-xs font-semibold bg-[#1565C0] text-white hover:bg-[#0D47A1]"
            >
              {t('load')}
            </button>
          </div>
        </div>

        <form onSubmit={handleUpdate} className="space-y-3">
          <div>
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('transaction_id')} *</label>
            <select
              value={updateTxnId}
              onChange={(e) => setUpdateTxnId(e.target.value)}
              className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
            >
              <option value="">-- Select Transaction --</option>
              {txns.map((t_row) => (
                <option key={t_row.transaction_id} value={t_row.transaction_id}>
                  {t_row.transaction_id} - ₹{t_row.total_amount}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('item_name')} *</label>
            <input
              type="text"
              value={updateItemName}
              onChange={(e) => setUpdateItemName(e.target.value)}
              className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('quantity')} *</label>
              <input
                type="number"
                step="any"
                value={updateQty}
                onChange={(e) => setUpdateQty(e.target.value)}
                className={`w-full px-3 py-1.5 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              />
            </div>
            <div>
              <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('unit_price')} (₹) *</label>
              <input
                type="number"
                step="any"
                value={updatePrice}
                onChange={(e) => setUpdatePrice(e.target.value)}
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
            <label className={`block text-xs font-medium mb-1 ${subText}`}>{t('subtotal')} (₹)</label>
            <input
              type="text"
              value={`₹${updateCalcSubtotal.toFixed(2)}`}
              disabled
              className={`w-full px-3 py-1.5 rounded text-sm border font-bold opacity-80 ${inputBg}`}
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
                setUpdateItemName('');
                setUpdateQty('1');
                setUpdatePrice('0');
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
