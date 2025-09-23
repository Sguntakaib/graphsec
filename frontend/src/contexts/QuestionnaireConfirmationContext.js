import React, { createContext, useContext, useState } from 'react';
import { AlertTriangle, Info, X } from 'lucide-react';
import { Button } from '../components/ui/button';

const QuestionnaireConfirmationContext = createContext();

export const useQuestionnaireConfirmation = () => {
  const context = useContext(QuestionnaireConfirmationContext);
  if (!context) {
    throw new Error('useQuestionnaireConfirmation must be used within QuestionnaireConfirmationProvider');
  }
  return context;
};

const ConfirmationModal = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  unansweredCount, 
  totalQuestions,
  unansweredQuestions = []
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg border border-gray-600 p-6 max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-yellow-400" />
            <h3 className="text-lg font-medium text-white">Incomplete Questionnaire</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="mb-6">
          <p className="text-gray-300 mb-4">
            <span className="font-semibold text-yellow-400">{unansweredCount}</span> out of{' '}
            <span className="font-semibold">{totalQuestions}</span> questions have not been answered. 
            Do you wish to continue?
          </p>

          {/* Info box */}
          <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-3">
            <div className="flex items-start space-x-2">
              <Info className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-blue-300">
                If question answers are missed, vulnerability analysis for this node will be incomplete.
              </p>
            </div>
          </div>

          {/* Show list of unanswered questions if available */}
          {unansweredQuestions.length > 0 && (
            <div className="mt-4">
              <p className="text-sm text-gray-400 mb-2">Unanswered questions:</p>
              <div className="max-h-32 overflow-y-auto">
                {unansweredQuestions.map((question, index) => (
                  <div key={index} className="text-xs text-gray-500 mb-1 pl-2 border-l-2 border-gray-600">
                    • {question}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex space-x-3 justify-end">
          <Button
            onClick={onClose}
            variant="outline"
            className="bg-gray-700 border-gray-600 text-white hover:bg-gray-600"
          >
            No, Continue Editing
          </Button>
          <Button
            onClick={onConfirm}
            className="bg-yellow-600 hover:bg-yellow-700 text-white"
          >
            Yes, Complete Anyway
          </Button>
        </div>
      </div>
    </div>
  );
};

export const QuestionnaireConfirmationProvider = ({ children }) => {
  const [modalState, setModalState] = useState({
    isOpen: false,
    unansweredCount: 0,
    totalQuestions: 0,
    unansweredQuestions: [],
    onConfirm: null,
    onCancel: null
  });

  const showConfirmation = ({ 
    unansweredCount, 
    totalQuestions, 
    unansweredQuestions = [], 
    onConfirm, 
    onCancel 
  }) => {
    return new Promise((resolve) => {
      setModalState({
        isOpen: true,
        unansweredCount,
        totalQuestions,
        unansweredQuestions,
        onConfirm: () => {
          setModalState(prev => ({ ...prev, isOpen: false }));
          if (onConfirm) onConfirm();
          resolve(true);
        },
        onCancel: () => {
          setModalState(prev => ({ ...prev, isOpen: false }));
          if (onCancel) onCancel();
          resolve(false);
        }
      });
    });
  };

  const closeModal = () => {
    setModalState(prev => ({ ...prev, isOpen: false }));
    if (modalState.onCancel) modalState.onCancel();
  };

  return (
    <QuestionnaireConfirmationContext.Provider value={{ showConfirmation }}>
      {children}
      <ConfirmationModal
        isOpen={modalState.isOpen}
        onClose={closeModal}
        onConfirm={modalState.onConfirm}
        unansweredCount={modalState.unansweredCount}
        totalQuestions={modalState.totalQuestions}
        unansweredQuestions={modalState.unansweredQuestions}
      />
    </QuestionnaireConfirmationContext.Provider>
  );
};