import React from 'react';
import { TRANSLATIONS, Language } from '../translations';
import { getDashboardMetrics } from '../storage';

interface Props {
  isDark: boolean;
  language: Language;
  onViewTransaction: (txnId: string) => void;
}

export const DashboardView: React.FC<Props> = ({ isDark, language, onViewTransaction }) => {
  const t = (key: string) => TRANSLATIONS[language]?.[key] || key;
  const metrics = getDashboardMetrics();

  const cardBg = isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]';
  const textColor = isDark ? 'text-white' : 'text-neutral-900';
  const subText = isDark ? 'text-neutral-400' : 'text-neutral-500';

  const getStatusColor = (status: string) => {
    if (status === 'Paid') return 'text-emerald-600 dark:text-emerald-400';
    if (status === 'Overdue') return 'text-red-600 dark:text-red-400';
    return 'text-amber-600 dark:text-amber-400';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className={`text-xl font-bold ${textColor}`}>{t('dashboard')}</h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className={`p-4 rounded border ${cardBg}`}>
          <div className={`text-xs font-medium ${subText}`}>{t('total_customers')}</div>
          <div className={`text-2xl font-bold tabular-nums mt-1 ${textColor}`}>
            {metrics.total_customers}
          </div>
        </div>

        <div className={`p-4 rounded border ${cardBg}`}>
          <div className={`text-xs font-medium ${subText}`}>{t('total_credit')}</div>
          <div className={`text-2xl font-bold tabular-nums mt-1 ${textColor}`}>
            ₹{metrics.total_credit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div className={`p-4 rounded border ${cardBg}`}>
          <div className={`text-xs font-medium ${subText}`}>{t('total_paid')}</div>
          <div className={`text-2xl font-bold tabular-nums mt-1 text-emerald-600 dark:text-emerald-400`}>
            ₹{metrics.total_paid.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div className={`p-4 rounded border ${cardBg}`}>
          <div className={`text-xs font-medium ${subText}`}>{t('outstanding_balance')}</div>
          <div className={`text-2xl font-bold tabular-nums mt-1 text-amber-600 dark:text-amber-400`}>
            ₹{metrics.outstanding_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
        </div>
      </div>

      <div className={`rounded border overflow-hidden ${cardBg}`}>
        <div className={`px-4 py-3 border-b text-sm font-semibold ${isDark ? 'border-[#333333] text-white' : 'border-[#E0E0E0] text-neutral-800'}`}>
          {t('recent_activities')}
        </div>

        {metrics.recent_transactions.length === 0 ? (
          <div className={`p-6 text-center text-sm ${subText}`}>{t('no_results')}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className={`${isDark ? 'bg-[#252525] text-neutral-300' : 'bg-neutral-50 text-neutral-600'}`}>
                <tr>
                  <th className="px-4 py-2.5 font-semibold">{t('transaction_id')}</th>
                  <th className="px-4 py-2.5 font-semibold">{t('customer_name')}</th>
                  <th className="px-4 py-2.5 font-semibold text-right">{t('total_amount')}</th>
                  <th className="px-4 py-2.5 font-semibold">{t('transaction_date')}</th>
                  <th className="px-4 py-2.5 font-semibold">{t('due_date')}</th>
                  <th className="px-4 py-2.5 font-semibold">{t('payment_status')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-[#333333]">
                {metrics.recent_transactions.map((txn) => (
                  <tr key={txn.transaction_id} className={`hover:bg-neutral-50 dark:hover:bg-[#252525]`}>
                    <td className="px-4 py-2.5">
                      <button
                        onClick={() => onViewTransaction(txn.transaction_id)}
                        className="font-bold text-[#1565C0] hover:underline"
                      >
                        {txn.transaction_id}
                      </button>
                    </td>
                    <td className={`px-4 py-2.5 ${textColor}`}>{txn.customer_name}</td>
                    <td className={`px-4 py-2.5 text-right font-medium tabular-nums ${textColor}`}>
                      ₹{txn.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className={`px-4 py-2.5 ${subText}`}>{txn.transaction_date}</td>
                    <td className={`px-4 py-2.5 ${subText}`}>{txn.due_date}</td>
                    <td className={`px-4 py-2.5 font-semibold ${getStatusColor(txn.payment_status)}`}>
                      {t(txn.payment_status.toLowerCase())}
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
