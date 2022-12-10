-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 10, 2022 at 09:47 AM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.1.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cement`
--

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `ID` smallint(6) NOT NULL,
  `CUSTOMER_NAME` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`ID`, `CUSTOMER_NAME`) VALUES
(1, 'JOHN'),
(2, 'SUSAN');

-- --------------------------------------------------------

--
-- Table structure for table `sales`
--

CREATE TABLE `sales` (
  `DATE` date NOT NULL,
  `INVOICE` smallint(6) NOT NULL,
  `LOCATION` char(3) NOT NULL,
  `CUSTOMER_NAME` varchar(50) NOT NULL,
  `AMOUNT` float(10,2) NOT NULL,
  `SALES_RTN` float(10,2) NOT NULL,
  `PAYMENT` float(10,2) NOT NULL,
  `SURPLUS` float(10,2) NOT NULL,
  `CF_INVOICE` char(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sales`
--

INSERT INTO `sales` (`DATE`, `INVOICE`, `LOCATION`, `CUSTOMER_NAME`, `AMOUNT`, `SALES_RTN`, `PAYMENT`, `SURPLUS`, `CF_INVOICE`) VALUES
('0000-00-00', 14000, 'KIL', 'XXXX', 0.00, 0.00, 0.00, 0.00, NULL),
('2022-12-10', 14001, 'KIL', 'SUSAN', 90000.00, 0.00, 0.00, 700.00, NULL),
('0000-00-00', 16000, 'MUL', 'XXXX', 0.00, 0.00, 0.00, 0.00, NULL),
('2022-12-10', 16001, 'MUL', 'JOHN', 13500.00, 0.00, 10000.00, 0.00, NULL),
('2022-12-10', 16002, 'MUL', 'SUSAN', 9300.00, 0.00, 10000.00, 0.00, '14001');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `ID` smallint(6) NOT NULL,
  `username` varchar(50) NOT NULL,
  `hash` text NOT NULL,
  `email` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`ID`, `username`, `hash`, `email`) VALUES
(6, 'tharanees', 'pbkdf2:sha256:260000$A0nGe1h0YNEDjHPZ$47488d4887f9eb96a1ca123c23807f7f76000c3f86353a10cd528086262a48d0', 'tharaneesjasotharan@gmail.com');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `sales`
--
ALTER TABLE `sales`
  ADD PRIMARY KEY (`INVOICE`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `ID` smallint(6) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `ID` smallint(6) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
