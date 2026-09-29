import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  UserPlus,
  Users,
  UserCog,
  TrendingUp,
  ShoppingCart,
  Package,
  FileEdit,
  CreditCard,
  Receipt,
  FilePenLine,
  FilePlus,
  BookOpen,
  FileText,
  Wallet,
  BarChart3,
  LogOut,
} from 'lucide-react';
import { TRANSLATIONS, Language } from './translations';
import { Admin, searchSystem, loadAdmins } from './storage';
import { LanguageSelect } from './components/LanguageSelect';
import { AdminAuth } from './components/AdminAuth';
import { DashboardView } from './components/DashboardView';
import { CustomerViews } from './components/CustomerViews';
import { CreditItemViews } from './components/CreditItemViews';
import { PaymentViews } from './components/PaymentViews';
import { TransactionViews } from './components/TransactionViews';
import { OutstandingView } from './components/OutstandingView';
import { ReportsView } from './components/ReportsView';

type AppStep = 'language_select' | 'register' | 'login' | 'app';

type ActiveRoute =
  | 'dashboard'
  | 'customers_add'
  | 'customers_view'
  | 'customers_update'
  | 'customer_performance'
  | 'customer_summary'
  | 'items_add'
  | 'items_view'
  | 'items_update'
  | 'payments_add'
  | 'payments_view'
  | 'payments_update'
  | 'transactions_add'
  | 'transactions_view'
  | 'transactions_update'
  | 'transaction_summary'
  | 'outstanding_balance'
  | 'reports';

export default function App() {
  const [step, setStep] = useState<AppStep>('language_select');
  const [language, setLanguage] = useState<Language>('English');
  const [isDark, setIsDark] = useState<boolean>(false);
  const [activeRoute, setActiveRoute] = useState<ActiveRoute>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [currentAdmin, setCurrentAdmin] = useState<Admin | null>(null);

  // Cross-screen selection pointers
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const [selectedTransactionId, setSelectedTransactionId] = useState<string | null>(null);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const [selectedPaymentId, setSelectedPaymentId] = useState<string | null>(null);

  // Header Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any | null>(null);
  const [langMenuOpen, setLangMenuOpen] = useState(false);

  const t = (key: string) => TRANSLATIONS[language]?.[key] || key;

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const handleSearch = (q: string) => {
    setSearchQuery(q);
    if (!q.trim()) {
      setSearchResults(null);
    } else {
      setSearchResults(searchSystem(q));
    }
  };

  const handleNavigate = (route: ActiveRoute, id?: string) => {
    setActiveRoute(route);
    setSearchResults(null);
    setSearchQuery('');

    if (id) {
      if (route.startsWith('customer')) setSelectedCustomerId(id);
      if (route.startsWith('transaction')) setSelectedTransactionId(id);
      if (route.startsWith('item')) setSelectedItemId(id);
      if (route.startsWith('payment')) setSelectedPaymentId(id);
    }
  };

  const handleLogout = () => {
    setCurrentAdmin(null);
    setStep('language_select');
  };

  // STEP 1: LANGUAGE SELECTION FIRST
  if (step === 'language_select') {
    return (
      <LanguageSelect
        isDark={isDark}
        onSelectLanguage={(lang) => {
          setLanguage(lang);
          const admins = loadAdmins();
          if (admins.length > 0) {
            setStep('login');
          } else {
            setStep('register');
          }
        }}
      />
    );
  }

  // STEP 2: ADMIN REGISTRATION
  if (step === 'register') {
    return (
      <AdminAuth
        isDark={isDark}
        language={language}
        mode="register"
        onSuccess={() => setStep('login')}
        onSwitchMode={(m) => setStep(m)}
        onBackToLanguageSelect={() => setStep('language_select')}
      />
    );
  }

  // STEP 3: LOGIN
  if (step === 'login') {
    return (
      <AdminAuth
        isDark={isDark}
        language={language}
        mode="login"
        onSuccess={(admin) => {
          setCurrentAdmin(admin);
          setStep('app');
          setActiveRoute('dashboard');
        }}
        onSwitchMode={(m) => setStep(m)}
        onBackToLanguageSelect={() => setStep('language_select')}
      />
    );
  }

  // STEP 4: MAIN APP
  const headerBg = isDark ? 'bg-[#1F1F1F]' : 'bg-[#1565C0]';
  const footerBg = isDark ? 'bg-[#1A1A1A] border-[#333333]' : 'bg-[#ECEFF1] border-[#E0E0E0]';
  const mainBg = isDark ? 'bg-[#121212]' : 'bg-[#F5F7FA]';
  const sidebarBg = isDark ? 'bg-[#1F1F1F] border-[#333333]' : 'bg-white border-[#E0E0E0]';
  const textColor = isDark ? 'text-white' : 'text-neutral-900';

  const menuSections = [
    {
      items: [
        {
          route: 'dashboard' as ActiveRoute,
          label: t('dashboard'),
          icon: <LayoutDashboard size={15} className="shrink-0" />,
        },
      ],
    },
    {
      header: t('customers'),
      items: [
        {
          route: 'customers_add' as ActiveRoute,
          label: t('add_customer'),
          icon: <UserPlus size={15} className="shrink-0" />,
        },
        {
          route: 'customers_view' as ActiveRoute,
          label: t('view_customers'),
          icon: <Users size={15} className="shrink-0" />,
        },
        {
          route: 'customers_update' as ActiveRoute,
          label: t('update_customer'),
          icon: <UserCog size={15} className="shrink-0" />,
        },
        {
          route: 'customer_performance' as ActiveRoute,
          label: t('customer_performance'),
          icon: <TrendingUp size={15} className="shrink-0" />,
        },
      ],
    },
    {
      header: t('credit_items'),
      items: [
        {
          route: 'items_add' as ActiveRoute,
          label: t('add_credit_item'),
          icon: <ShoppingCart size={15} className="shrink-0" />,
        },
        {
          route: 'items_view' as ActiveRoute,
          label: t('view_credit_items'),
          icon: <Package size={15} className="shrink-0" />,
        },
        {
          route: 'items_update' as ActiveRoute,
          label: t('update_credit_item'),
          icon: <FileEdit size={15} className="shrink-0" />,
        },
      ],
    },
    {
      header: t('payments'),
      items: [
        {
          route: 'payments_add' as ActiveRoute,
          label: t('add_payment'),
          icon: <CreditCard size={15} className="shrink-0" />,
        },
        {
          route: 'payments_view' as ActiveRoute,
          label: t('view_payments'),
          icon: <Receipt size={15} className="shrink-0" />,
        },
        {
          route: 'payments_update' as ActiveRoute,
          label: t('update_payment'),
          icon: <FilePenLine size={15} className="shrink-0" />,
        },
      ],
    },
    {
      header: t('credit_transactions'),
      items: [
        {
          route: 'transactions_add' as ActiveRoute,
          label: t('add_transaction'),
          icon: <FilePlus size={15} className="shrink-0" />,
        },
        {
          route: 'transactions_view' as ActiveRoute,
          label: t('view_transactions'),
          icon: <BookOpen size={15} className="shrink-0" />,
        },
        {
          route: 'transactions_update' as ActiveRoute,
          label: t('update_transaction'),
          icon: <FileText size={15} className="shrink-0" />,
        },
      ],
    },
    {
      header: t('reports'),
      items: [
        {
          route: 'outstanding_balance' as ActiveRoute,
          label: t('outstanding_balance'),
          icon: <Wallet size={15} className="shrink-0" />,
        },
        {
          route: 'reports' as ActiveRoute,
          label: t('reports'),
          icon: <BarChart3 size={15} className="shrink-0" />,
        },
      ],
    },
  ];

  return (
    <div className={`min-h-screen flex flex-col ${mainBg}`}>
      {/* HEADER */}
      <header className={`px-4 py-3 flex items-center justify-between text-white ${headerBg} shadow-sm z-20`}>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 rounded hover:bg-black/15 text-xl font-bold focus:outline-none"
            title="Menu"
          >
            ☰
          </button>
          <div className="flex items-center gap-2">
            <span className="text-xl">💳</span>
            <span className="text-lg font-bold tracking-tight">{t('app_title')}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Header search: ~360px wide */}
          <div className="w-[340px] max-w-[360px]">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder={t('search_placeholder')}
              className={`w-full px-3 py-1.5 rounded text-xs focus:outline-none ${
                isDark
                  ? 'bg-[#2A2A2A] border border-[#444444] text-white placeholder-neutral-400'
                  : 'bg-white border border-transparent text-neutral-900 placeholder-neutral-400'
              }`}
            />
          </div>

          {/* Language Selector */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setLangMenuOpen(!langMenuOpen)}
              className="px-2.5 py-1 rounded text-xs font-semibold bg-white/10 hover:bg-white/20 transition-colors whitespace-nowrap flex items-center gap-1.5 focus:outline-none"
              title="Change Language"
            >
              <span className="text-sm">🌐</span>
              <span>
                {language === 'Hindi'
                  ? 'हिंदी'
                  : language === 'Marathi'
                  ? 'मराठी'
                  : language === 'Marwari'
                  ? 'मारवाड़ी'
                  : 'English'}
              </span>
              <span className="text-[9px] opacity-75">▼</span>
            </button>

            {langMenuOpen && (
              <div
                className={`absolute right-0 mt-1.5 w-36 rounded shadow-lg border py-1 z-50 text-xs font-medium ${
                  isDark
                    ? 'bg-[#252525] border-[#444444] text-neutral-200'
                    : 'bg-white border-neutral-200 text-neutral-800'
                }`}
              >
                {[
                  { code: 'English' as Language, label: 'English' },
                  { code: 'Hindi' as Language, label: 'हिंदी (Hindi)' },
                  { code: 'Marathi' as Language, label: 'मराठी (Marathi)' },
                  { code: 'Marwari' as Language, label: 'मारवाड़ी (Marwari)' },
                ].map((item) => (
                  <button
                    key={item.code}
                    type="button"
                    onClick={() => {
                      setLanguage(item.code);
                      setLangMenuOpen(false);
                    }}
                    className={`w-full text-left px-3 py-1.5 hover:bg-[#1565C0] hover:text-white transition-colors ${
                      language === item.code ? 'font-bold text-[#1565C0] dark:text-blue-400' : ''
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Dark Mode toggle */}
          <button
            onClick={() => setIsDark(!isDark)}
            className="px-2.5 py-1 rounded text-xs font-semibold bg-white/10 hover:bg-white/20 transition-colors whitespace-nowrap"
          >
            {isDark ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>
      </header>

      {/* BODY WITH SIDEBAR */}
      <div className="flex-1 flex overflow-hidden">
        {/* SIDEBAR */}
        {sidebarOpen && (
          <aside className={`w-60 shrink-0 border-r flex flex-col justify-between overflow-y-auto ${sidebarBg}`}>
            <div className="p-3">
              <div className={`px-3 py-2 text-xs font-bold border-b mb-3 flex items-center gap-2 ${isDark ? 'border-[#333333] text-neutral-300' : 'border-[#E0E0E0] text-neutral-800'}`}>
                <span className="text-xl">💳</span>
                <span>{t('shop_name')}</span>
              </div>

              <nav className="space-y-4">
                {menuSections.map((sec, idx) => (
                  <div key={idx} className="space-y-1">
                    {sec.header && (
                      <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-neutral-500">
                        {sec.header}
                      </div>
                    )}
                    {sec.items.map((item) => {
                      const isActive = activeRoute === item.route;
                      return (
                        <button
                          key={item.route}
                          onClick={() => handleNavigate(item.route)}
                          className={`w-full flex items-center gap-2.5 text-left px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                            isActive
                              ? 'bg-[#1565C0] text-white'
                              : isDark
                              ? 'text-neutral-300 hover:bg-[#2A2A2A]'
                              : 'text-neutral-700 hover:bg-neutral-100'
                          }`}
                        >
                          {item.icon}
                          <span className="truncate">{item.label}</span>
                        </button>
                      );
                    })}
                  </div>
                ))}
              </nav>
            </div>

            <div className="p-3 border-t dark:border-[#333333]">
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 text-left px-3 py-2 text-xs font-bold text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 rounded transition-colors"
              >
                <LogOut size={15} className="shrink-0" />
                <span>{t('logout')}</span>
              </button>
            </div>
          </aside>
        )}

        {/* MAIN VIEWPORT */}
        <main className={`flex-1 p-6 overflow-y-auto ${mainBg}`}>
          {/* SEARCH OVERLAY IF SEARCHING */}
          {searchResults ? (
            <div className={`p-6 rounded border space-y-4 ${isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]'}`}>
              <div className="flex justify-between items-center">
                <h3 className={`text-base font-bold ${textColor}`}>Search Results for "{searchQuery}"</h3>
                <button onClick={() => { setSearchQuery(''); setSearchResults(null); }} className="text-xs text-[#1565C0]">Close</button>
              </div>

              {searchResults.customers?.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-[#1565C0] uppercase mb-1.5">Matching Customers</h4>
                  <div className="space-y-1 text-xs">
                    {searchResults.customers.map((c: any) => (
                      <button
                        key={c.customer_id}
                        onClick={() => handleNavigate('customer_summary', c.customer_id)}
                        className="block text-left w-full hover:underline font-medium text-neutral-800 dark:text-neutral-200"
                      >
                        • {c.customer_id} - {c.customer_name} ({c.phone_number})
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {searchResults.transactions?.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-[#1565C0] uppercase mb-1.5">Matching Transactions</h4>
                  <div className="space-y-1 text-xs">
                    {searchResults.transactions.map((tx: any) => (
                      <button
                        key={tx.transaction_id}
                        onClick={() => handleNavigate('transaction_summary', tx.transaction_id)}
                        className="block text-left w-full hover:underline font-medium text-neutral-800 dark:text-neutral-200"
                      >
                        • {tx.transaction_id} - {tx.customer_name} (₹{tx.total_amount.toFixed(2)})
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {searchResults.customers?.length === 0 && searchResults.transactions?.length === 0 && (
                <div className="text-xs text-neutral-500">{t('no_results')}</div>
              )}
            </div>
          ) : (
            <>
              {activeRoute === 'dashboard' && (
                <DashboardView
                  isDark={isDark}
                  language={language}
                  onViewTransaction={(tid) => handleNavigate('transaction_summary', tid)}
                  onUpdateTransaction={(tid) => handleNavigate('transactions_update', tid)}
                />
              )}

              {activeRoute === 'customers_add' && (
                <CustomerViews
                  isDark={isDark}
                  language={language}
                  view="add"
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'customers_view' && (
                <CustomerViews
                  isDark={isDark}
                  language={language}
                  view="view"
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'customers_update' && (
                <CustomerViews
                  isDark={isDark}
                  language={language}
                  view="update"
                  selectedCustomerId={selectedCustomerId}
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'customer_summary' && (
                <CustomerViews
                  isDark={isDark}
                  language={language}
                  view="summary"
                  selectedCustomerId={selectedCustomerId}
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'customer_performance' && (
                <CustomerViews
                  isDark={isDark}
                  language={language}
                  view="performance"
                  onNavigate={handleNavigate}
                />
              )}

              {activeRoute === 'items_add' && (
                <CreditItemViews
                  isDark={isDark}
                  language={language}
                  view="add"
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'items_view' && (
                <CreditItemViews
                  isDark={isDark}
                  language={language}
                  view="view"
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'items_update' && (
                <CreditItemViews
                  isDark={isDark}
                  language={language}
                  view="update"
                  selectedItemId={selectedItemId}
                  onNavigate={handleNavigate}
                />
              )}

              {activeRoute === 'payments_add' && (
                <PaymentViews
                  isDark={isDark}
                  language={language}
                  view="add"
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'payments_view' && (
                <PaymentViews
                  isDark={isDark}
                  language={language}
                  view="view"
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'payments_update' && (
                <PaymentViews
                  isDark={isDark}
                  language={language}
                  view="update"
                  selectedPaymentId={selectedPaymentId}
                  onNavigate={handleNavigate}
                />
              )}

              {activeRoute === 'transactions_add' && (
                <TransactionViews
                  isDark={isDark}
                  language={language}
                  view="add"
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'transactions_view' && (
                <TransactionViews
                  isDark={isDark}
                  language={language}
                  view="view"
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'transactions_update' && (
                <TransactionViews
                  isDark={isDark}
                  language={language}
                  view="update"
                  selectedTransactionId={selectedTransactionId}
                  onNavigate={handleNavigate}
                />
              )}
              {activeRoute === 'transaction_summary' && (
                <TransactionViews
                  isDark={isDark}
                  language={language}
                  view="summary"
                  selectedTransactionId={selectedTransactionId}
                  onNavigate={handleNavigate}
                />
              )}

              {activeRoute === 'outstanding_balance' && (
                <OutstandingView
                  isDark={isDark}
                  language={language}
                  onViewCustomer={(cid) => handleNavigate('customer_summary', cid)}
                  onUpdateCustomer={(cid) => handleNavigate('customers_update', cid)}
                />
              )}

              {activeRoute === 'reports' && (
                <ReportsView
                  isDark={isDark}
                  language={language}
                />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
