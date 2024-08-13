import React, { useState } from 'react';
import { QrReader } from 'react-qr-reader';
import '../QrScanner/qrcode.css'; // Import the CSS file

const QRScanner = () => {
  const [scanning, setScanning] = useState(false);
  const [scannedData, setScannedData] = useState(null);
  const [amount, setAmount] = useState('');

  const handleClick = () => {
    setScanning(true);
  };

  const handleCancel = () => {
    setScanning(false);
  };

  const handleAmountChange = e => {
    setAmount(e.target.value);
  };

  const handleSubmit = e => {
    e.preventDefault();
    // Handle form submission logic
    alert(`Amount ${amount} to be paid for ${scannedData}`);
  };

  return (
    <div className="qr-scanner-container">
      <h1 className='heading'>Pay Through Scanner</h1>
      {scanning ? (
        <div className="scanner-wrapper">
          <QrReader
            onResult={(result, error) => {
              if (result) {
                setScannedData(result?.text);
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
      {scannedData && (
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
