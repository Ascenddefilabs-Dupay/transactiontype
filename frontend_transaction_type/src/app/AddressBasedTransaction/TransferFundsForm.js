


'use client'

import React, { useState } from 'react';
import axios from 'axios';
import './AddressBasedTransactionForm.css';

const AddressBasedTransactionForm = () => {
  const [transactionType, setTransactionType] = useState('');
  const [transactionAmount, setTransactionAmount] = useState('');
  const [transactionCurrency, setTransactionCurrency] = useState('');
  const [fiatAddress, setFiatAddress] = useState('');
  const [message, setMessage] = useState('');

  const currencies = [
    { code: 'USD', name: 'United States Dollar' },
    { code: 'GBP', name: 'British Pound' },
    { code: 'EUR', name: 'Euro' },
    { code: 'INR', name: 'Indian Rupee' },
    { code: 'JPY', name: 'Japanese Yen' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Check fiat address validity
      const addressResponse = await axios.get(`http://localhost:8000/api/address/?fiat_address=${fiatAddress}`);
      if (addressResponse.data.count === 0) {
        alert('Entered fiat address does not exist.');
        return;
      }
    } catch (error) {
      console.error('Error checking fiat address:', error);
      setMessage('Error checking fiat address.');
      return;
    }

    try {
      // Submit transaction
      const response = await axios.post('http://localhost:8000/api/address_based_transfer/', {
        transaction_type: 'Debit',
        transaction_amount: transactionAmount,
        transaction_currency: transactionCurrency,
        transaction_status: 'Success',  // Default value
        fiat_address: fiatAddress,
      });
      alert('Transaction successful!');
      console.log('Transaction successful:', response.data);

      // Reset form fields
      setTransactionType('');
      setTransactionAmount('');
      setTransactionCurrency('');
      setFiatAddress('');
      setMessage('');
    } catch (error) {
      setMessage(error.response ? error.response.data.detail : 'Error submitting transaction');
      console.error('Error submitting transaction:', error.response ? error.response.data : error.message);
    }
  };

  return (
    <div className="address-based-transaction-form-container">
      <h2 className="form-heading">Address Based Transaction</h2>
      <form className="address-based-transaction-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="transactionCurrency">Currency:</label>
          <select
            id="transactionCurrency"
            value={transactionCurrency}
            onChange={(e) => setTransactionCurrency(e.target.value)}
            required
          >
            <option value="">Select a currency</option>
            {currencies.map((currency) => (
              <option key={currency.code} value={currency.code}>
                {currency.name} ({currency.code})
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="transactionAmount">Amount:</label>
          <input
            type="number"
            id="transactionAmount"
            value={transactionAmount}
            onChange={(e) => setTransactionAmount(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="fiatAddress">Fiat Address:</label>
          <input
            type="text"
            id="fiatAddress"
            value={fiatAddress}
            onChange={(e) => setFiatAddress(e.target.value)}
            required
          />
        </div>
        <button type="submit">Submit</button>
        {message && <p className="error-message">{message}</p>}
      </form>
    </div>
  );
};

export default AddressBasedTransactionForm;
