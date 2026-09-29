import React from 'react';
import { TRANSLATIONS, Language } from '../translations';
import { getOutstandingBalances } from '../storage';

interface Props {
  isDark: boolean;
  language: Language;
  onViewCustomer: (customerId: string) => void;
}

export const OutstandingView: React.FC<Props> = ({ isDark, language, onViewCustomer }) => {
  const t = (key: string) => TRANSLATIONS[language]?.[key] || key;
  const records = getOutstandingBalances();

  const cardBg = isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]';
  const textColor = isDark ? 'text-white' : 'text-neutral-900';
  const subText = isDark ? 'text-neutral-400' : 'text-neutral-500';

  return (
    <div className="space-y-4">
      <h2 className={`text-xl font-bold ${textColor}`}>{t('outstanding_balance')}</h2>

      <div className={`rounded border overflow-hidden ${cardBg}`}>
        {records.length === 0 ? (
          <div className={`p-8 text-center text-sm ${subText}`}>{t('no_results')}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className={`${isDark ? 'bg-[#252525] text-neutral-300' : 'bg-neutral-50 text-neutral-600'}`}>
                <tr>
                  <th className="px-4 py-2.5 font-semibold">{t('customer_id')}</th>
                  <th className="px-4 py-2.5 font-semibold">{t('customer_name')}</th>
                  <th className="px-4 py-2.5 font-semibold text-right">Total Due</th>
                  <th className="px-4 py-2.5 font-semibold text-right">{t('total_paid')}</th>
                  <th className="px-4 py-2.5 font-semibold text-right">{t('pending_amount')}</th>
                  <th className="px-4 py-2.5 font-semibold">{t('due_date')}</th>
                  <th className="px-4 py-2.5 font-semibold">{t('payment_status')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-[#333333]">
                {records.map((r) => (
                  <tr key={r.customer_id} className="hover:bg-neutral-50 dark:hover:bg-[#252525]">
                    <td className="px-4 py-2.5">
                      <button
                        onClick={() => onViewCustomer(r.customer_id)}
                        className="font-bold text-[#1565C0] hover:underline"
                      >
                        {r.customer_id}
                      </button>
                    </td>
                    <td className={`px-4 py-2.5 font-medium ${textColor}`}>{r.customer_name}</td>
                    <td className={`px-4 py-2.5 text-right tabular-nums ${textColor}`}>₹{r.total_due.toFixed(2)}</td>
                    <td className="px-4 py-2.5 text-right tabular-nums text-emerald-600">₹{r.total_paid.toFixed(2)}</td>
                    <td className="px-4 py-2.5 text-right font-bold tabular-nums text-amber-600">₹{r.pending_amount.toFixed(2)}</td>
                    <td className={`px-4 py-2.5 ${subText}`}>{r.due_date}</td>
                    <td className="px-4 py-2.5 font-semibold">
                      <span className={
                        r.status === 'Paid' ? 'text-emerald-600' :
                        r.status === 'Overdue' ? 'text-red-600' : 'text-amber-600'
                      }>
                        {t(r.status.toLowerCase())}
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
