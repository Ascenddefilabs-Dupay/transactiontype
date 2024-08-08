import React, { useState } from 'react';
import '../WalletTransactions/WalletTransactions.css'; // Ensure you have the correct path to your CSS file
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // Import the uuid library

const CurrencyForm = () => {
  const [mobileNumber, setMobileNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('');
  const [message, setMessage] = useState(''); // State to store the success message

  const currencies = [
    { code: 'USD', name: 'United States Dollar' },
    { code: 'GBP', name: 'British Pound' },
    { code: 'EUR', name: 'Euro' },
    { code: 'INR', name: 'Indian Rupee' },
    { code: 'JPY', name: 'Japanese Yen' },
    // Add more currencies as needed
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate mobile number
    const mobileRegex = /^[0-9]{10}$/;
    if (!mobileRegex.test(mobileNumber)) {
      alert('Enter a valid 10-digit mobile number');
      return;
    }

    // Validate amount
    if (isNaN(amount) || amount <= 0) {
      alert('Enter a valid amount');
      return;
    }

    // Validate currency selection
    if (!currency) {
      alert('Select a valid currency');
      return;
    }

    // Generate a unique hash for the transaction
    const transactionHash = uuidv4();

    // If all validations pass, perform form submission logic here
    try {
      const response = await axios.post('http://localhost:8000/api/wallet_transfer/', {
        transaction_type: 'Debit', // Default value
        transaction_amount: amount,
        transaction_currency: currency,
        transaction_status: 'Success', // Default value
        transaction_fee: 0.0, // Default value
        person_phone_number: mobileNumber, // Update to match the Django model field name
        transaction_hash: transactionHash, // Include the unique hash
      });
      alert('Transaction successful!');
      console.log('Transaction successful:', response.data);

      // Reset form fields after successful submission
      setMobileNumber('');
      setAmount('');
      setCurrency('');
    } catch (error) {
      setMessage(error.response ? error.response.data.detail : 'Error submitting transaction');
      console.error('Error submitting transaction:', error.response ? error.response.data : error.message);
    }
  };

  return (
    <form className="currency-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="center-label">Wallet Transactions</label>
        <label htmlFor="mobileNumber">Mobile Number:</label>
        <input
          type="text"
          id="mobileNumber"
          value={mobileNumber}
          onChange={(e) => {
            const value = e.target.value;
            // Only allow digits and limit input to 10 digits
            if (/^\d{0,10}$/.test(value)) {
              setMobileNumber(value);
            }
          }}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="amount">Amount:</label>
        <input
          type="number"
          id="amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="currency">Currency:</label>
        <select
          id="currency"
          value={currency}
          onChange={(e) => setCurrency(e.target.value)}
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
      <button type="submit">Submit</button>
      {message && <p>{message}</p>} {/* Display success or error message */}
    </form>
  );
};

export default CurrencyForm;