import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import './WalletTransaction.css'; // Add this for styling
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const WalletTransaction = () => {
  const [paymentMethod, setPaymentMethod] = useState('');
  const router = useRouter();

  const handlePaymentMethodChange = (event) => {
    setPaymentMethod(event.target.value);
  };

  const handleNextClick = () => {
    if (paymentMethod === 'number') {
      router.push('/WalletTransactions');
    } else if (paymentMethod === 'qrcode') {
      router.push('/QrScanner');
    } else if (paymentMethod === 'walletAddress') {
      router.push('/AddressBasedTransaction');
    }
  };

  const handleBackClick = () => {
    let redirectUrl = '/WalletTransactionInterface';
    router.push(redirectUrl);
  };

  return (
    <div className="wallet-transaction">
      <div className='back_container'>
        <ArrowBackIcon className="setting_back_icon" onClick={handleBackClick} />
        <h2 className='wallet-transaction_heading'>Wallet Transaction</h2>
      </div>
      <div className="form-group">
        <label htmlFor="payment-method">Select Payment Method:</label>
        <select
          id="payment-method"
          value={paymentMethod}
          onChange={handlePaymentMethodChange}
        >
          <option value="">--Choose a method--</option>
          <option value="number">Through Number</option>
          <option value="qrcode">Through QR Code</option>
          <option value="walletAddress">Through Wallet Address</option>
        </select>
      </div>
      <button onClick={handleNextClick} disabled={!paymentMethod} className='button_class'>
        Next
      </button>
    </div>
  );
};

export default WalletTransaction;
