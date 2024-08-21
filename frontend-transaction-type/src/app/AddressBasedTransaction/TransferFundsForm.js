
// 'use client'

// import { v4 as uuidv4 } from 'uuid'; 
// import React, { useState } from 'react';
// import axios from 'axios';
// import './AddressBasedTransactionForm.css'; // Ensure the path to your CSS file is correct

// const AddressBasedTransactionForm = () => {
//   const [transactionAmount, setTransactionAmount] = useState('');
//   const [transactionCurrency, setTransactionCurrency] = useState('');
//   const [fiatAddress, setFiatAddress] = useState('');
//   const [message, setMessage] = useState(''); // State to store the message

//   const currencies = [
//     { code: 'USD', name: 'United States Dollar' },
//     { code: 'GBP', name: 'British Pound' },
//     { code: 'EUR', name: 'Euro' },
//     { code: 'INR', name: 'Indian Rupee' },
//     { code: 'JPY', name: 'Japanese Yen' },
//     // Add more currencies as needed
//   ];

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     // Validate amount
//     if (isNaN(transactionAmount) || transactionAmount <= 0) {
//       setMessage('Enter a valid amount');
//       return;
//     }

//     // Validate currency selection
//     if (!transactionCurrency) {
//       setMessage('Select a valid currency');
//       return;
//     }

//     // Validate fiat address
//     if (!fiatAddress) {
//       setMessage('Enter a valid fiat address');
//       return;
//     }

//     const transactionHash = uuidv4();
//     const transactionDescription = 'fiat address transaction';

//     try {
//       const response = await axios.post('http://localhost:8000/api/address-transfer/', {
//         transaction_amount: transactionAmount,
//         transaction_currency: transactionCurrency,
//         transaction_type: 'Debit',
//         transaction_status: 'Success',
//         fiat_address: fiatAddress,
//         transaction_fee: 0.0,
//         transaction_hash: transactionHash,
//         transaction_description: transactionDescription,
//       });

//       if (response.data.status === 'address_failure') {
//         alert('Entered fiat address does not exist.');
//       } else if (response.data.status === 'currency_failure') {
//         alert('Currency must be the same.');
//       } else if (response.data.status === 'failure') {
//         alert('Insufficient funds for the transaction.');
//       } else {
//         alert('Transaction successful!');
//         setTransactionAmount('');
//         setTransactionCurrency('');
//         setFiatAddress('');
//       }

//     } catch (error) {
//       setMessage(error.response ? error.response.data.error : 'Error submitting transaction');
//       console.error('Error submitting transaction:', error.response ? error.response.data : error.message);
//     }
//   };

//   return (
    
//     <div className="address-based-transaction-form-container">
//       <form className="address-based-transaction-form" onSubmit={handleSubmit}>
//         <h2 className="form-heading">Fiat Wallet Transaction</h2>
//         <div className="form-group">
//           <label htmlFor="transactionCurrency">Currency:</label>
//           <select
//             id="transactionCurrency"
//             value={transactionCurrency}
//             onChange={(e) => setTransactionCurrency(e.target.value)}
//             required
//           >
//             <option value="">Select a currency</option>
//             {currencies.map((currency) => (
//               <option key={currency.code} value={currency.code}>
//                 {currency.name} ({currency.code})
//               </option>
//             ))}
//           </select>
//         </div>
//         <div className="form-group">
//           <label htmlFor="transactionAmount">Amount:</label>
//           <input
//             type="number"
//             id="transactionAmount"
//             value={transactionAmount}
//             onChange={(e) => setTransactionAmount(e.target.value)}
//             required
//           />
//         </div>
//         <div className="form-group">
//           <label htmlFor="fiatAddress">Fiat Address:</label>
//           <input
//             type="text"
//             id="fiatAddress"
//             value={fiatAddress}
//             onChange={(e) => setFiatAddress(e.target.value)}
//             required
//           />
//         </div>
//         <button type="submit">Transfer</button>
//         {message && <p className="message">{message}</p>}
//       </form>
//     </div>
//   );
// };

// export default AddressBasedTransactionForm;


'use client'

import { v4 as uuidv4 } from 'uuid'; 
import React, { useState } from 'react';
import axios from 'axios';
import './AddressBasedTransactionForm.css'; // Ensure the path to your CSS file is correct
import ArrowBackIcon from '@mui/icons-material/ArrowBack'; // Import the ArrowBackIcon
import { useRouter } from 'next/navigation'

const AddressBasedTransactionForm = () => {
  const [transactionAmount, setTransactionAmount] = useState('');
  const [transactionCurrency, setTransactionCurrency] = useState('');
  const [fiatAddress, setFiatAddress] = useState('');
  const [alertMessage, setAlertMessage] = useState(''); // State for alert message
  const [loading, setLoading] = useState(false);
  const router = useRouter();

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

    // Validate amount
    if (isNaN(transactionAmount) || transactionAmount <= 0) {
      setAlertMessage('Enter a valid amount');
      return;
    }

    // Validate currency selection
    if (!transactionCurrency) {
      setAlertMessage('Select a valid currency');
      return;
    }

    // Validate fiat address
    if (!fiatAddress) {
      setAlertMessage('Enter a valid fiat address');
      return;
    }

    setLoading(true);
    const transactionHash = uuidv4();
    const transactionDescription = 'fiat address transaction';

    try {
      const response = await axios.post('http://localhost:8000/api/address-transfer/', {
        transaction_amount: transactionAmount,
        transaction_currency: transactionCurrency,
        transaction_type: 'Debit',
        transaction_status: 'Success',
        fiat_address: fiatAddress,
        transaction_fee: 0.0,
        transaction_hash: transactionHash,
        transaction_description: transactionDescription,
      });

      if (response.data.status === 'address_failure') {
        setAlertMessage('Entered fiat address does not exist.');
      } else if (response.data.status === 'currency_failure') {
        setAlertMessage('Selected currency not found in the wallet.');
      } else if (response.data.status === 'failure') {
        setAlertMessage('Insufficient funds for the transaction.');
      } else {
        setAlertMessage('Transaction successful!');
        setTransactionAmount('');
        setTransactionCurrency('');
        setFiatAddress('');
      }

    } catch (error) {
      setAlertMessage(error.response ? error.response.data.error : 'Error submitting transaction');
      console.error('Error submitting transaction:', error.response ? error.response.data : error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseAlert = () => {
    setAlertMessage('');
    window.location.href = 'http://localhost:3003/Dashboard';
  };

  const settinghandleBackClick = () => {
    let redirectUrl = '/WalletTransactionInterface';
    router.push(redirectUrl);
  };

  return (
    <div className="address-based-transaction-form-container">
      {alertMessage && (
        <div className="customAlert">
          <p>{alertMessage}</p>
          <button onClick={handleCloseAlert} className="closeButton">OK</button>
        </div>
      )}
      <form className="address-based-transaction-form" onSubmit={handleSubmit}>
        <div className='back_container'>
           <ArrowBackIcon className="setting_back_icon" onClick={settinghandleBackClick} />
           <h2 className="form-heading">Fiat Wallet Transaction</h2>
        </div>
        
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
        <button type="submit" disabled={loading} className='button_class'>
          {loading ? 'Processing...' : 'Transfer'}
        </button>
      </form>
    </div>
  );
};

export default AddressBasedTransactionForm;
