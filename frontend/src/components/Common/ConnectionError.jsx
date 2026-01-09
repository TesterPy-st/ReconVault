import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const formatMs = (ms) => {
  if (!ms && ms !== 0) return null;
  if (ms < 1000) return `${ms}ms`;
  return `${Math.ceil(ms / 1000)}s`;
};

const ConnectionError = ({
  show = false,
  apiBaseUrl,
  wsUrl,
  lastError,
  checking = false,
  nextRetryInMs,
  onRetry
}) => {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className="bg-danger-red/15 border-b border-danger-red/40 text-danger-red"
        >
          <div className="max-w-7xl mx-auto px-6 py-3 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
            <div className="min-w-0">
              <div className="flex items-center gap-2 font-mono text-sm">
                <span>⚠️ Backend unavailable</span>
                <span className="text-danger-red/70">
                  {checking
                    ? '(checking...)'
                    : nextRetryInMs != null
                      ? `(retry in ${formatMs(nextRetryInMs)})`
                      : ''}
                </span>
              </div>

              <div className="text-xs text-danger-red/80 font-mono mt-1 break-words space-y-1">
                <div>
                  UI is running with demo data. Configure/start the backend API at{' '}
                  <span className="font-bold">{apiBaseUrl}</span>
                  {wsUrl ? (
                    <>
                      {' '}and WebSocket at <span className="font-bold">{wsUrl}</span>.
                    </>
                  ) : null}
                  {lastError ? <> Last error: <span className="font-bold">{lastError}</span></> : null}
                </div>
                <div>
                  Tip: from the repo root run <span className="font-bold">docker compose up --build backend</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <motion.button
                type="button"
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={onRetry}
                className="px-3 py-2 rounded-lg border border-danger-red/50 text-danger-red font-mono text-xs hover:bg-danger-red/10 transition-colors"
              >
                Retry now
              </motion.button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ConnectionError;
