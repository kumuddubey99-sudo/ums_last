import React, { useState } from 'react';
import { TRANSLATIONS, Language } from '../translations';
import { loadAdmins, saveAdmins, Admin, getNextId } from '../storage';

interface Props {
  isDark: boolean;
  language: Language;
  mode: 'register' | 'login';
  onSuccess: (admin: Admin) => void;
  onSwitchMode: (mode: 'register' | 'login') => void;
}

export const AdminAuth: React.FC<Props> = ({ isDark, language, mode, onSuccess, onSwitchMode }) => {
  const t = (key: string) => TRANSLATIONS[language]?.[key] || key;

  const [adminName, setAdminName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!adminName.trim()) {
      setErrorMsg(`${t('admin_name')} is required.`);
      return;
    }
    if (!username.trim()) {
      setErrorMsg(`${t('username')} is required.`);
      return;
    }
    if (!password) {
      setErrorMsg(`${t('password')} is required.`);
      return;
    }
    if (!confirmPassword) {
      setErrorMsg(`${t('confirm_password')} is required.`);
      return;
    }
    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    const admins = loadAdmins();
    if (admins.some((a) => a.username.toLowerCase() === username.trim().toLowerCase())) {
      setErrorMsg('Username already exists. Please choose a different username.');
      return;
    }

    const newAdmin: Admin = {
      admin_id: getNextId('ADM', admins, 'admin_id'),
      admin_name: adminName.trim(),
      username: username.trim(),
      password,
    };

    saveAdmins([...admins, newAdmin]);
    setSuccessMsg(t('success_save'));
    setTimeout(() => {
      onSwitchMode('login');
    }, 700);
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (!username.trim()) {
      setErrorMsg(`${t('username')} is required.`);
      return;
    }
    if (!password) {
      setErrorMsg(`${t('password')} is required.`);
      return;
    }

    const admins = loadAdmins();
    const found = admins.find(
      (a) => a.username.toLowerCase() === username.trim().toLowerCase() && a.password === password
    );

    if (found) {
      onSuccess(found);
    } else {
      setErrorMsg('Invalid username or password.');
    }
  };

  const cardBg = isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]';
  const textColor = isDark ? 'text-white' : 'text-neutral-900';
  const inputBg = isDark ? 'bg-[#2A2A2A] border-[#444444] text-white' : 'bg-white border-neutral-300 text-neutral-900';

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 ${isDark ? 'bg-[#121212]' : 'bg-[#F5F7FA]'}`}>
      <div className={`w-full max-w-sm rounded-lg border p-8 shadow-sm ${cardBg}`}>
        <div className="text-center mb-6">
          <div className="text-xs font-semibold text-[#1565C0] uppercase tracking-wider">
            {t('shop_name')}
          </div>
          <h2 className={`text-xl font-bold mt-1 ${textColor}`}>
            {mode === 'register' ? t('admin_registration') : t('login')}
          </h2>
        </div>

        {errorMsg && (
          <div className="mb-4 p-2 text-xs text-red-600 bg-red-50 dark:bg-red-950/40 rounded border border-red-200 dark:border-red-900">
            {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="mb-4 p-2 text-xs text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 rounded border border-emerald-200 dark:border-emerald-900">
            {successMsg}
          </div>
        )}

        <form onSubmit={mode === 'register' ? handleRegister : handleLogin} className="space-y-3.5">
          {mode === 'register' && (
            <div>
              <label className={`block text-xs font-medium mb-1 ${isDark ? 'text-neutral-300' : 'text-neutral-700'}`}>
                {t('admin_name')} *
              </label>
              <input
                type="text"
                value={adminName}
                onChange={(e) => setAdminName(e.target.value)}
                className={`w-full px-3 py-2 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="Enter admin name"
              />
            </div>
          )}

          <div>
            <label className={`block text-xs font-medium mb-1 ${isDark ? 'text-neutral-300' : 'text-neutral-700'}`}>
              {t('username')} *
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={`w-full px-3 py-2 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              placeholder="Enter username"
            />
          </div>

          <div>
            <label className={`block text-xs font-medium mb-1 ${isDark ? 'text-neutral-300' : 'text-neutral-700'}`}>
              {t('password')} *
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`w-full px-3 py-2 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
              placeholder="••••••••"
            />
          </div>

          {mode === 'register' && (
            <div>
              <label className={`block text-xs font-medium mb-1 ${isDark ? 'text-neutral-300' : 'text-neutral-700'}`}>
                {t('confirm_password')} *
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={`w-full px-3 py-2 rounded text-sm border focus:outline-none focus:border-[#1565C0] ${inputBg}`}
                placeholder="••••••••"
              />
            </div>
          )}

          <button
            type="submit"
            className="w-full py-2.5 rounded text-sm font-semibold bg-[#1565C0] text-white hover:bg-[#0D47A1] transition-colors mt-2"
          >
            {mode === 'register' ? t('register') : t('login')}
          </button>
        </form>

        <div className="mt-6 text-center text-xs">
          {mode === 'register' ? (
            <button
              onClick={() => onSwitchMode('login')}
              className="text-[#1565C0] dark:text-blue-400 hover:underline"
            >
              {t('already_registered')}
            </button>
          ) : (
            <button
              onClick={() => onSwitchMode('register')}
              className="text-[#1565C0] dark:text-blue-400 hover:underline"
            >
              Need an account? {t('register')}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
