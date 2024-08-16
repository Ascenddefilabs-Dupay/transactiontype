import React, { useState } from 'react';
import '../WalletTransactions/WalletTransactions.css'; // Ensure you have the correct path to your CSS file
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // Import the uuid library
import { QrReader } from 'react-qr-reader';

const CurrencyForm = () => {
  const [mobileNumber, setMobileNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('');
  const [message, setMessage] = useState(''); // State to store the success message
  const [scanning, setScanning] = useState(false); // State to manage scanning state

  const currencies = [
    { code: 'USD', name: 'United States Dollar' },
    { code: 'GBP', name: 'British Pound' },
    { code: 'EUR', name: 'Euro' },
    { code: 'INR', name: 'Indian Rupee' },
    { code: 'JPY', name: 'Japanese Yen' },
    // Add more currencies as needed
  ];

  const parseQueryParams = (url) => {
    const params = new URLSearchParams(url.split('?')[1]);
    return {
      mobileNumber: params.get('mobileNumber') || '',
      amount: params.get('amount') || '',
      currency: params.get('currency') || '',
    };
  };

  const handleScan = (result) => {
    if (result) {
      try {
        const url = result.text.trim();
        // Redirect to the URL scanned from the QR code
        window.location.href = url;

        // Optionally parse query parameters if URL includes them
        const { mobileNumber, amount, currency } = parseQueryParams(url);
        if (/^\d{10}$/.test(mobileNumber) && !isNaN(amount) && amount > 0 && currency) {
          setMobileNumber(mobileNumber);
          setAmount(amount);
          setCurrency(currency);
          setScanning(false); // Stop scanning after a successful scan
        } else {
          alert('Scanned data is not valid');
        }
      } catch (error) {
        alert('Scanned data is not a valid URL');
      }
    }
  };

  const handleError = (err) => {
    console.error(err);
    alert('Error scanning the QR code');
  };

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
        user_phone_number: mobileNumber, // Update to match the Django model field name
        transaction_hash: transactionHash, // Include the unique hash
      });
      if (response.data.status === 'failure'){
        alert('Transaction Failure!');
      }else if (response.data.status === 'mobile_failure'){
        alert("Number is not valid")
      }else if (response.data.status === 'currency_failure'){
        alert("Curresncy type must be Same")
      }
      else {
        alert('Transaction successful!');
      }
      
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
