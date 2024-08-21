'use client'
import React, { useState } from 'react';
import { QrReader } from 'react-qr-reader';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; 
import '../QrScanner/qrcode.css'; // Import the CSS file
import ArrowBackIcon from '@mui/icons-material/ArrowBack'; // Import the ArrowBackIcon
import { useRouter } from 'next/navigation'

const QRScanner = () => {
  const [scanning, setScanning] = useState(false);
  const [scannedData, setScannedData] = useState(null);
  const [mobileNumber, setMobileNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');
  const [currency, setCurrency] = useState('');
  const [alertMessage, setAlertMessage] = useState(''); 
  const router = useRouter();

  const currencies = [
    { code: 'USD', name: 'United States Dollar' },
    { code: 'GBP', name: 'British Pound' },
    { code: 'EUR', name: 'Euro' },
    { code: 'INR', name: 'Indian Rupee' },
    { code: 'JPY', name: 'Japanese Yen' },
    // Add more currencies as needed
  ];

  const handleClick = () => {
    setScanning(true);
  };

  const handleCancel = () => {
    setScanning(false);
  };

  const handleAmountChange = e => {
    setAmount(e.target.value);
  };
  const settinghandleBackClick = () => {
    let redirectUrl = '/WalletTransactionInterface';
    router.push(redirectUrl);
  };

  const handleSubmit = async e => {
    e.preventDefault();

    if (!currency) {
      setAlertMessage('Select a valid currency');
      return;
    }
    
    // Handle form submission logic
    const transactionHash = uuidv4();
    try {
      const response = await axios.post('http://localhost:8000/api/qrcode/', {
        transaction_type: 'Debit', // Default value
        transaction_amount: amount,
        transaction_currency: currency,
        transaction_status: 'Success', // Default value
        transaction_fee: 0.0, // Default value
        user_phone_number: mobileNumber, // Use extracted mobile number
        transaction_hash: transactionHash, // Include the unique hash
      });
      if (response.data.status === 'failure'){
        setAlertMessage('Transaction Failure!');
      }else if (response.data.status === 'mobile_failure'){
        setAlertMessage("Number is not valid")
      }else if (response.data.status === 'insufficient_funds'){
        setAlertMessage("Insufficient Amount")
      }else if (response.data.status === 'curreny_error'){
        setAlertMessage('User Does not have Currency')
      }else {
        setAlertMessage('Transaction successful!');
      }
      console.log('Transaction successful:', response.data);
      
      setAmount('');
      setCurrency('');
    } catch (error) {
      setMessage(error.response ? error.response.data.detail : 'Error submitting transaction');
      console.error('Error submitting transaction:', error.response ? error.response.data : error.message);
    }
  };

  const handleCloseAlert = () => {
    setAlertMessage('');
  };

  const extractMobileNumber = data => {
    // Assuming the mobile number is a 10-digit number within the scanned data
    const regex = /\b\d{10}\b/;
    const match = data.match(regex);
    return match ? match[0] : null;
  };

  return (
    <div className="qr-scanner-container">
      {alertMessage && (
        <div className="customAlert">
          <p>{alertMessage}</p>
          <button onClick={handleCloseAlert} className="closeButton">OK</button>
        </div>
      )}
      <div className='back_container'>
        <ArrowBackIcon className="setting_back_icon" onClick={settinghandleBackClick} />
        <h1 className='heading'>Pay Through Scanner</h1>
      </div>
  
      {scanning ? (
        <div className="scanner-wrapper">
          <QrReader
            onResult={(result, error) => {
              if (result) {
                const scannedText = result?.text;
                const mobile = extractMobileNumber(scannedText);
                setMobileNumber(mobile);
                setScannedData(scannedText);
                setScanning(false);
              }

              if (error) {
                console.error(error);
              }
            }}
            constraints={{ facingMode: 'environment' }}
            style={{ width: '100%' }}
          />
          <button className="cancel-button" onClick={handleCancel}>
            Cancel
          </button>
        </div>
      ) : (
        <button className="scan-button" onClick={handleClick}>
          Scan QR Code
        </button>
      )}

      {mobileNumber && (
        <>
          <div className="currency-form">
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

          <form onSubmit={handleSubmit} className="amount-form">
            <label className='amount_label'>
              Enter Amount:
            </label>
            <input
              type="number"
              value={amount}
              onChange={handleAmountChange}
              required
            />
            <div className='button_class'>
              <button type="submit">Transfer</button>
            </div>
          </form>
        </>
      )}
    </div>
  );
};

export default QRScanner;
