import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import './WalletTransaction.css'; // Add this for styling

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

  return (
    <div className="wallet-transaction">
      <h2>Wallet Transaction</h2>
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
