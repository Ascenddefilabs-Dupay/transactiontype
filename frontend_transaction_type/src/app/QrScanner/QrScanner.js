'use client'
import React, { useState } from 'react';
import { QrReader } from 'react-qr-reader';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; 
import '../QrScanner/qrcode.css'; // Import the CSS file

const QRScanner = () => {
  const [scanning, setScanning] = useState(false);
  const [scannedData, setScannedData] = useState(null);
  const [mobileNumber, setMobileNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');

  const handleClick = () => {
    setScanning(true);
  };

  const handleCancel = () => {
    setScanning(false);
  };

  const handleAmountChange = e => {
    setAmount(e.target.value);
  };

  const handleSubmit = async e => {
    e.preventDefault();
    // Handle form submission logic
    const transactionHash = uuidv4();
    try {
      const response = await axios.post('http://localhost:8000/api/qrcode/', {
        transaction_type: 'Debit', // Default value
        transaction_amount: amount,
        transaction_currency: "IND",
        transaction_status: 'Success', // Default value
        transaction_fee: 0.0, // Default value
        user_phone_number: mobileNumber, // Use extracted mobile number
        transaction_hash: transactionHash, // Include the unique hash
      });
      if (response.data.status === 'failure'){
        alert('Transaction Failure!');
      }else if (response.data.status === 'mobile_failure'){
        alert("Number is not valid")
      }else if (response.data.status === 'currency_failure'){
        alert("Curresncy type must be Same")
      }else {
        alert('Transaction successful!');
      }
      console.log('Transaction successful:', response.data);
      
      setAmount('');
    } catch (error) {
      setMessage(error.response ? error.response.data.detail : 'Error submitting transaction');
      console.error('Error submitting transaction:', error.response ? error.response.data : error.message);
    }
    // 
    // alert(`Amount ${amount} to be paid for ${mobileNumber}`);
  };

  const extractMobileNumber = data => {
    // Assuming the mobile number is a 10-digit number within the scanned data
    const regex = /\b\d{10}\b/;
    const match = data.match(regex);
    return match ? match[0] : null;
  };

  return (
    <div className="qr-scanner-container">
      <h1 className='heading'>Pay Through Scanner</h1>
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
            <button type="submit">Submit</button>
          </div>
        </form>
      )}
    </div>
  );
};

export default QRScanner;
