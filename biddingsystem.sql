-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 04, 2025 at 11:46 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `biddingsystem`
--

-- --------------------------------------------------------

--
-- Table structure for table `bidding_table`
--

CREATE TABLE `bidding_table` (
  `id` int(11) NOT NULL,
  `item_id` varchar(10) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bidding_table`
--

INSERT INTO `bidding_table` (`id`, `item_id`, `start_time`, `status`) VALUES
(16, '1EDHB', '2025-03-04 06:44:12', 'inactive'),
(17, '4EGSA', '2025-03-04 06:44:19', 'inactive'),
(18, '5AUBM', '2025-03-04 06:45:51', 'inactive'),
(21, 'KI5SH', '2025-03-04 06:49:35', 'inactive'),
(29, 'P5K6N', '2025-03-04 07:09:11', 'inactive'),
(32, 'ZROPH', '2025-03-04 10:41:24', 'inactive');

-- --------------------------------------------------------

--
-- Table structure for table `bids`
--

CREATE TABLE `bids` (
  `bid_id` int(11) NOT NULL,
  `item_id` varchar(10) DEFAULT NULL,
  `item_name` varchar(255) NOT NULL,
  `seller_id` varchar(10) DEFAULT NULL,
  `user_id` varchar(10) DEFAULT NULL,
  `bid_amount` decimal(10,2) NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bids`
--

INSERT INTO `bids` (`bid_id`, `item_id`, `item_name`, `seller_id`, `user_id`, `bid_amount`, `timestamp`) VALUES
(4, 'P5K6N', 'table', '2E4T9', 'FFTFJ', 676767.00, '2025-03-04 10:42:41'),
(5, 'P5K6N', 'table', '2E4T9', 'FFTFJ', 7878778.00, '2025-03-04 10:58:21'),
(6, 'ZROPH', 'doll', 'ZXYWM', 'FFTFJ', 78633.00, '2025-03-04 13:42:00'),
(7, 'ZROPH', 'doll', 'ZXYWM', 'FFTFJ', 42223.00, '2025-03-04 13:42:05'),
(8, 'ZROPH', 'doll', 'ZXYWM', 'FFTFJ', 9049232.00, '2025-03-04 13:42:12');

-- --------------------------------------------------------

--
-- Table structure for table `items`
--

CREATE TABLE `items` (
  `id` varchar(10) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `base_price` decimal(10,2) NOT NULL,
  `seller_id` varchar(10) DEFAULT NULL,
  `end_time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `items`
--

INSERT INTO `items` (`id`, `title`, `description`, `image`, `base_price`, `seller_id`, `end_time`) VALUES
('1EDHB', 'lenovo', '64gb', '1EDHB_move1.jpg', 17000.00, '2E4T9', '2025-03-03 18:19:41'),
('4EGSA', 'walldrobe', 'bigger', '4EGSA_catlog.jpg', 3000.00, 'ZXYWM', '2025-03-03 17:38:32'),
('5AUBM', 'table', '1.5 metres', '5AUBM_house.jpg', 8500.00, '2E4T9', '2025-03-03 18:24:03'),
('KI5SH', 'laptop', '512gb', 'KI5SH_carou3.jpg', 50000.00, '2E4T9', '2025-03-03 18:18:02'),
('P5K6N', 'table', 'good table', 'P5K6N_carou4.jpg', 14.99, '2E4T9', '2025-03-03 18:36:55'),
('ZROPH', 'doll', 'large', 'ZROPH_catlog.jpg', 89.00, 'ZXYWM', '2025-03-03 17:42:57');

-- --------------------------------------------------------

--
-- Table structure for table `sellers`
--

CREATE TABLE `sellers` (
  `seller_id` varchar(10) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `role` varchar(10) NOT NULL DEFAULT 'seller'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sellers`
--

INSERT INTO `sellers` (`seller_id`, `username`, `email`, `password`, `phone`, `address`, `role`) VALUES
('2E4T9', 'max', 'max@gmail.com', '$2b$12$xwWR.af5jxMr8P/cch3UXemd87HNiR0TE1fIjwT.G2hPc4hXX2A6q', '0726587467', 'Machakos, Kenya', 'seller'),
('3P7Z8', 'dan', 'danielsana60@gmail.com', '$2b$12$O/4gM6D6hoLcgHszNsbO5.pBUtwwyr8yWecEEZXdTX4o40qBJYpJe', '0726587467', 'Machakos, Kenya', 'seller'),
('CDYLC', 'sellerUser', 'seller@example.com', '$2b$12$qgGet4xVOQ9N/k9N9ngI0OsRcW1MeWhLLw6gv9kYG2UEdXBM2k0XG', '123-456-7890', '123 Seller St, City, Country', 'seller'),
('ZXYWM', 'dansana', 'danielsana@gmail.com', '$2b$12$Se9YprnPfmENDGsgUC68uurHsbePdnt5earOmc6O8IanZeD7oTWdW', '0726587467', 'Machakos, Kenya', 'seller');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` varchar(10) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `role`) VALUES
('FFTFJ', 'dan', 'danielsana60@gmail.com', '$2b$12$2jpTZZ42.HSAycDkpfsQZeV4xSB50LNT5XR4BjoIMti9yZfJ6XXwi', 'user'),
('QFTMB', 'musau', 'musau@gmail.com', '$2b$12$VRXBEVkmtBJwKTcrEvFAwui3tUDQb2A6tIX0oAeGxKfhBCbSW1042', 'user'),
('XB4VA', 'john_doe', 'john@example.com', '$2b$12$HwCq1Swfeg4ZF0yhLHHYnuvnYvbmjggjECWqCEQwlOl9k75uKZnrm', 'user'),
('ZAXLX', 'admin', 'admin@gmail.com', '$2b$12$t78xYHfMTmuerl/HRldNi.hnk5.eaz0Gy00w0C0Qcj1tihEU/pq4q', 'admin');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bidding_table`
--
ALTER TABLE `bidding_table`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `item_id` (`item_id`);

--
-- Indexes for table `bids`
--
ALTER TABLE `bids`
  ADD PRIMARY KEY (`bid_id`),
  ADD KEY `item_id` (`item_id`),
  ADD KEY `seller_id` (`seller_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `items`
--
ALTER TABLE `items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `sellers`
--
ALTER TABLE `sellers`
  ADD PRIMARY KEY (`seller_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bidding_table`
--
ALTER TABLE `bidding_table`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `bids`
--
ALTER TABLE `bids`
  MODIFY `bid_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bidding_table`
--
ALTER TABLE `bidding_table`
  ADD CONSTRAINT `bidding_table_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`);

--
-- Constraints for table `bids`
--
ALTER TABLE `bids`
  ADD CONSTRAINT `bids_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  ADD CONSTRAINT `bids_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `sellers` (`seller_id`),
  ADD CONSTRAINT `bids_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `items`
--
ALTER TABLE `items`
  ADD CONSTRAINT `items_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `sellers` (`seller_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
