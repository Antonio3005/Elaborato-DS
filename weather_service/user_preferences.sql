USE user_preferences

CREATE TABLE IF NOT EXISTS  `user_preferences` (
    `id` int AUTO_INCREMENT PRIMARY KEY,
    `user_id` varchar(255) NOT NULL,
    `city` varchar(255) NOT NULL,
    `temp_max` varchar(255) NOT NULL,
    `temp_min` varchar(255) NOT NULL,
    `rain_amount` varchar(255) NOT NULL,
    `snow_presence` varchar(255) NOT NULL
    );