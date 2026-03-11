'use client';

import { useState } from 'react';

type Operation = '+' | '-' | '*' | '/' | '=' | 'C';

export default function CalculatorPage() {
  const [display, setDisplay] = useState('0');
  const [firstOperand, setFirstOperand] = useState<number | null>(null);
  const [operation, setOperation] = useState<Operation | null>(null);
  const [waitingForSecond, setWaitingForSecond] = useState(false);

  const handleNumber = (num: string) => {
    if (waitingForSecond) {
      setDisplay(num);
      setWaitingForSecond(false);
    } else {
      setDisplay(display === '0' ? num : display + num);
    }
  };

  const handleOperation = (op: Operation) => {
    if (op === 'C') {
      setDisplay('0');
      setFirstOperand(null);
      setOperation(null);
      setWaitingForSecond(false);
      return;
    }

    if (op === '=') {
      if (firstOperand === null || operation === null) return;

      const secondOperand = parseFloat(display);
      let result: number;

      switch (operation) {
        case '+':
          result = firstOperand + secondOperand;
          break;
        case '-':
          result = firstOperand - secondOperand;
          break;
        case '*':
          result = firstOperand * secondOperand;
          break;
        case '/':
          if (secondOperand === 0) {
            setDisplay('Error');
            return;
          }
          result = firstOperand / secondOperand;
          break;
        default:
          return;
      }

      setDisplay(String(result));
      setFirstOperand(null);
      setOperation(null);
      return;
    }

    if (operation && firstOperand !== null && !waitingForSecond) {
      // 连续操作
      const secondOperand = parseFloat(display);
      let result: number;

      switch (operation) {
        case '+':
          result = firstOperand + secondOperand;
          break;
        case '-':
          result = firstOperand - secondOperand;
          break;
        case '*':
          result = firstOperand * secondOperand;
          break;
        case '/':
          if (secondOperand === 0) {
            setDisplay('Error');
            return;
          }
          result = firstOperand / secondOperand;
          break;
        default:
          return;
      }

      setFirstOperand(result);
      setDisplay(String(result));
    } else {
      setFirstOperand(parseFloat(display));
    }

    setOperation(op);
    setWaitingForSecond(true);
  };

  const buttons = [
    ['C', '/', '*', '-'],
    ['7', '8', '9', '+'],
    ['4', '5', '6', '='],
    ['1', '2', '3', '0'],
  ];

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-2xl p-6 shadow-2xl w-full max-w-sm">
        <h1 className="text-2xl font-bold text-white text-center mb-6">计算器</h1>

        <div className="bg-gray-700 rounded-xl p-4 mb-6">
          <div className="text-right text-4xl font-mono text-white truncate">
            {display}
          </div>
        </div>

        <div className="grid grid-cols-4 gap-3">
          {buttons.flat().map((btn, index) => {
            const isOperator = ['+', '-', '*', '/', '=', 'C'].includes(btn);
            const isEquals = btn === '=';
            const isClear = btn === 'C';

            return (
              <button
                key={index}
                onClick={() => {
                  if (['+', '-', '*', '/', '=', 'C'].includes(btn)) {
                    handleOperation(btn as Operation);
                  } else {
                    handleNumber(btn);
                  }
                }}
                className={`
                  h-14 rounded-xl text-xl font-bold transition-all
                  ${isOperator
                    ? isEquals
                      ? 'bg-orange-500 hover:bg-orange-600 text-white col-span-1 row-span-2'
                      : isClear
                        ? 'bg-red-500 hover:bg-red-600 text-white'
                        : 'bg-gray-600 hover:bg-gray-500 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-white'
                  }
                `}
              >
                {btn}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
